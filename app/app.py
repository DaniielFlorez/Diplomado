from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, make_response
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
import mysql.connector
import jwt  # Asegúrate de importar jwt
from Crypto.PublicKey import RSA  # Importa RSA para generar llaves
import os  # Para manejar archivos
import io  # Para manejar el almacenamiento temporal 
import hashlib

app = Flask(__name__)
app.secret_key = '2030'

# Configuración de la base de datos
db_config = {
    'user': 'usuario',
    'password': 'usuario-12345',
    'host': 'persistencia',
    'database': 'persistencia',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

# Decorador para verificar si el usuario está autenticado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'jwt_token' not in session:
            return redirect(url_for('index'))
        try:
            token = session['jwt_token']
            jwt.decode(token, app.secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            flash('La sesión ha expirado, por favor inicia sesión de nuevo', 'error')
            return redirect(url_for('index'))
        except jwt.InvalidTokenError:
            flash('Token inválido, por favor inicia sesión de nuevo', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Página principal que muestra el formulario de inicio de sesión o registro
@app.route('/', methods=['GET'])
def index():
    return render_template('login_register.html', mode='login')

# Manejo del inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    
    query = "SELECT id, password FROM usuarios WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    
    cursor.close()
    connection.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        token = jwt.encode({
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.secret_key, algorithm='HS256')

        session['jwt_token'] = token
        flash('Inicio de sesión exitoso', 'success')

        # Redirigir a 'menu.html' después del inicio de sesión
        return redirect(url_for('menu'))
    else:
        flash('Nombre de usuario o contraseña incorrectos', 'error')
        return redirect(url_for('index'))

# Ruta para desplegar el menú
@app.route('/menu', methods=['GET'])
@login_required  # Solo usuarios autenticados pueden acceder
def menu():
    return render_template('menu.html')  # Renderiza la plantilla del menú

# Manejo del registro de usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        try:
            query = "INSERT INTO usuarios (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, hashed_password.decode('utf-8')))
            connection.commit()
            flash('Usuario registrado con éxito', 'success')
        except mysql.connector.IntegrityError:
            flash('El nombre de usuario o correo electrónico ya existe', 'error')
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('index'))
    else:
        return render_template('register.html')

# Cerrar sesión
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('jwt_token', None)
    session.pop('private_key', None)  # Limpiar llave privada al cerrar sesión
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('index'))

# Ruta para la generación de llaves
@app.route('/key_generation', methods=['GET'])
@login_required  # Asegúrate de que solo los usuarios autenticados puedan acceder
def key_generation():
    private_key = session.get('private_key')  # Obtén la llave privada de la sesión
    return render_template('key_generation.html', private_key=private_key)  # Pasa la llave privada a la plantilla

# Ruta para manejar la generación de llaves (POST)
@app.route('/key_generator', methods=['POST'])
@login_required  # Solo usuarios autenticados pueden acceder
def key_generator():
    # Generación de llaves RSA
    key = RSA.generate(2048)  # Generar una llave RSA de 2048 bits
    private_key = key.export_key()  # Exportar la llave privada
    public_key = key.publickey().export_key()  # Exportar la llave pública

    # Guardar la llave pública en la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "INSERT INTO llaves (nombre_clave, llave_publica) VALUES (%s, %s)"
        cursor.execute(query, ('Llave Generada', public_key.decode('utf-8')))
        connection.commit()
        flash('Llave pública guardada en la base de datos', 'success')
        
        # Guardar la llave privada en la sesión
        session['private_key'] = private_key.decode('utf-8')  # Guarda la llave privada en la sesión
    except Exception as e:
        flash(f'Error al guardar la llave: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()

    # Redirigir a la página de generación de llaves con la llave privada visible
    return redirect(url_for('key_generation'))  # Redirigir a la ruta 'key_generation'

# Ruta para manejar la descarga de la llave privada
@app.route('/download_private_key', methods=['GET'])
@login_required
def download_private_key():
    # Asegúrate de que la llave privada esté almacenada en la sesión
    private_key = session.get('private_key')  # Obtén la llave privada de la sesión

    if private_key:  # Verifica que la llave privada existe
        response = make_response(private_key)  # Crea la respuesta con la llave privada
        response.headers['Content-Disposition'] = 'attachment; filename=private_key.pem'  # Establece las cabeceras para la descarga
        response.headers['Content-Type'] = 'application/x-pem-file'  # Tipo de contenido

        return response  # Devuelve la respuesta que permite descargar la llave privada
    else:
        flash('No hay ninguna llave privada disponible para descargar', 'error')  # Mensaje de error
        return redirect(url_for('key_generation'))  # Redirige si no hay llave privada

# Ruta para manejar la subida de archivos
@app.route('/files', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No se ha subido ningún archivo', 'error')
        return redirect(url_for('file_signature'))

    file = request.files['file']
    if file.filename == '':
        flash('No se ha seleccionado ningún archivo', 'error')
        return redirect(url_for('file_signature'))

    # Asegúrate de que la carpeta 'uploads' existe
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Guardar el archivo en el sistema de archivos
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Calcular el hash del archivo utilizando SHA-256
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    file_hash = sha256_hash.hexdigest()  # Obtiene el hash en formato hexadecimal

    # Usamos el mismo hash como firma por simplicidad
    firma = file_hash  # O puedes generar una firma separada si es necesario

    # Guardar información del archivo y su hash en la base de datos
    user_id = jwt.decode(session['jwt_token'], app.secret_key, algorithms=['HS256'])['username']  # Obtén el nombre de usuario del token
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Busca el ID del usuario basado en el nombre de usuario
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            user_id = user[0]  # Obtén el ID del usuario
            query = "INSERT INTO archivos (usuario_id, nombre_archivo, hash_archivo, firma) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (user_id, file.filename, file_hash, firma))
            connection.commit()
            flash('Archivo subido y guardado en la base de datos con éxito', 'success')
        else:
            flash('Usuario no encontrado', 'error')
    except Exception as e:
        flash(f'Error al guardar el archivo: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('file_signature'))



@app.route('/file_signature')
@login_required
def file_signature():
    # Lógica para manejar la visualización de archivos y firmas
    return render_template('file_signature.html')

@app.route('/atras', methods=['POST'])
@login_required
def atras():
    # Lógica para manejar la acción al presionar "atras"
    return redirect(url_for('menu'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


from flask import Flask, render_template, request, jsonify
from Crypto.PublicKey import RSA
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import mysql.connector
import bcrypt

app = Flask(__name__)

# Configuración de JWT
app.config['JWT_SECRET_KEY'] = '2030'  # Cambia esto a una clave secreta más segura
jwt = JWTManager(app)

# Conexión a la base de datos
def get_db_connection():
    connection = mysql.connector.connect(
        host='persistencia',  # Cambia esto por el nombre correcto de tu contenedor de MariaDB
        user='usuario',       # Cambia esto por tu usuario de base de datos
        password='usuario-12345',  # Cambia esto por tu contraseña de base de datos
        database='persistencia'     # Cambia esto por el nombre de tu base de datos
    )
    return connection

class KeyGenerator:
    @staticmethod
    def generate_keys():
        key = RSA.generate(2048)
        private_key = key.export_key().decode('utf-8')
        return private_key

@app.route('/')
def index():
    return render_template('index.html')

# Ruta para generar llaves
@app.route('/generate', methods=['POST'])
def generate():
    private_key = KeyGenerator.generate_keys()
    return jsonify({'private_key': private_key})

# Ruta de registro de usuario
@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        email = request.form['email']  # Captura el email
        password = request.form['password'].encode('utf-8')

        # Verificar si el usuario ya existe
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nombre = %s", (username,))
        if cursor.fetchone() is not None:
            return jsonify({'success': False, 'error': 'El usuario ya existe'}), 409

        # Hash de la contraseña antes de almacenarla
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # Insertar nuevo usuario en la base de datos
        cursor.execute("INSERT INTO usuarios (nombre, email, contrasena) VALUES (%s, %s, %s)",
                       (username, email, hashed_password))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'success': True}), 201
    except Exception as e:
         return jsonify({'message': 'Error al registrar el usuario.'}), 500

# Ruta de login de usuario
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password'].encode('utf-8')

    # Buscar al usuario en la base de datos
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nombre = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user is None or not bcrypt.checkpw(password, user[3].encode('utf-8')):  # user[3] es la contraseña
        return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

    # Generar un JWT
    token = create_access_token(identity=username)
    return jsonify({'success': True, 'token': token}), 200

if __name__ == '__main__':
    app.run(debug=True)


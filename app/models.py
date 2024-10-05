import bcrypt
import jwt
import datetime

# Esta lista representará tu base de datos de usuarios.
users_db = []

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = self.hash_password(password)

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

def register_user(username, password):
    for user in users_db:
        if user.username == username:
            return False  # Usuario ya existe
    new_user = User(username, password)
    users_db.append(new_user)
    return True  # Registro exitoso

def generate_token(username):
    # Definimos la clave secreta y el tiempo de expiración
    secret_key = 'your_secret_key'  # Cambia esto a algo seguro y privado
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
    token = jwt.encode({'username': username, 'exp': expiration}, secret_key, algorithm='HS256')
    return token

def verify_token(token):
    secret_key = 'your_secret_key'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


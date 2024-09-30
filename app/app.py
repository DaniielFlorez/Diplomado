from flask import Flask, request, jsonify
from Crypto.PublicKey import RSA

app = Flask(__name__)

class KeyGenerator:
    @staticmethod
    def generate_keys():
        key = RSA.generate(2048)
        private_key = key.export_key().decode('utf-8')
        return private_key

@app.route('/generate', methods=['POST'])
def generate_keys():
    username = request.form.get('username')
    
    if not username:
        return jsonify({"error": "Nombre de usuario es requerido"}), 400

    private_key = KeyGenerator.generate_keys()
    return jsonify(private_key=private_key)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

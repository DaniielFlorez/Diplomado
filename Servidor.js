const express = require('express');
const bodyParser = require('body-parser');
const { generarLlaves } = require('./Main/generarLlaves');
const mysql = require('mysql2/promise');
require('dotenv').config();

const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(express.static('Web'));

// Configuración de conexión a la base de datos
const dbConfig = {
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
};

// Ruta para generar llaves
app.post('/generar-llaves', async (req, res) => {
    const { nombreUsuario } = req.body;  // Cambié 'nombreClave' a 'nombreUsuario'

    if (!nombreUsuario) {
        return res.status(400).json({ message: 'El nombre de usuario es requerido.' });
    }

    try {
        // Generar las llaves
        const { publicKey, privateKeyBase64 } = await generarLlaves(nombreUsuario); // Cambié a await para obtener las llaves

        // Persistir el nombre de usuario y la llave pública en la base de datos
        const connection = await mysql.createConnection(dbConfig);
        await connection.execute('INSERT INTO llaves (nombre_clave, llave_publica) VALUES (?, ?)', [nombreUsuario, publicKey]);

        res.json({ 
            message: 'Llaves generadas y persistidas correctamente.', 
            llavePrivada: privateKeyBase64 // También puedes devolver la llave privada en la respuesta si es necesario
        });
    } catch (error) {
        console.error('Error al generar llaves:', error);
        res.status(500).json({ message: 'Error al generar llaves.' });
    }
});

app.listen(port, () => {
    console.log(`Servidor corriendo en http://localhost:${port}`);
});
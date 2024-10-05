CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS llaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_clave VARCHAR(255) NOT NULL,
    llave_publica TEXT NOT NULL
);


-- Insertar datos de ejemplo
INSERT INTO llaves (nombre_clave, llave_publica) VALUES 
('Yesica', 'ejemplo_llave_publica_1'),
('Daniel', 'ejemplo_llave_publica_2');

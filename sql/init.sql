-- Crear la base de datos con una collation compatible
CREATE DATABASE IF NOT EXISTS persistencia CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE persistencia;

-- Crear la tabla usuarios con charset y collation adecuados
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- Crear la tabla llaves con charset y collation adecuados
CREATE TABLE IF NOT EXISTS llaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_clave VARCHAR(100) NOT NULL,
    llave_publica TEXT NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- Crear la tabla archivos con la referencia al id de usuarios
CREATE TABLE IF NOT EXISTS archivos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_archivo VARCHAR(255) NOT NULL,
    hash_archivo VARCHAR(255) NOT NULL,
    firma TEXT NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

------------------------------------------------------------------------------------


-- Insertar datos de ejemplo en la tabla usuarios primero
INSERT INTO usuarios (username, email, password) VALUES
('Yesica', 'yesica@example.com', 'password1'),
('Daniel', 'daniel@example.com', 'password2');

-- Insertar datos de ejemplo en la tabla llaves
INSERT INTO llaves (nombre_clave, llave_publica) VALUES 
('Yesica', 'ejemplo_llave_publica_1'),
('Daniel', 'ejemplo_llave_publica_2');

-- Insertar datos de ejemplo en la tabla archivos con referencia a usuario_id
INSERT INTO archivos (nombre_archivo, hash_archivo, firma, usuario_id) VALUES 
('archivo1.txt', 'ejemplo_hash_1', 'ejemplo_firma_1', 1),  -- 1 corresponde al id del usuario Yesica
('archivo2.txt', 'ejemplo_hash_2', 'ejemplo_firma_2', 2);  -- 2 corresponde al id del usuario Daniel

# Usa una imagen base de Node.js
FROM node:14

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copia los archivos de dependencia de Node.js
COPY package*.json ./

# Instala las dependencias de la aplicación
RUN npm install

# Copia todos los archivos del proyecto al contenedor
COPY . .

# Expone el puerto de la aplicación
EXPOSE 3000

# Comando para iniciar la aplicación
CMD ["node", "server.js"]

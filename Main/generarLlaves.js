// generarLlaves.js

async function generarLlaves() {
    // Obtener el nombre de usuario del input
    const nombreUsuario = document.getElementById("content").value;

    if (!nombreUsuario) {
        alert("Por favor, ingresa un nombre de usuario.");
        return;
    }

    try {
        // Generar un par de llaves RSA
        const clave = await window.crypto.subtle.generateKey(
            {
                name: "RSA-OAEP",
                modulusLength: 2048, // Longitud de la llave en bits
                publicExponent: new Uint8Array([1, 0, 1]),
                hash: "SHA-256",
            },
            true, // La clave puede ser exportada
            ["encrypt", "decrypt"] // Usos permitidos
        );

        // Exportar la llave privada
        const llavePrivada = await window.crypto.subtle.exportKey("pkcs8", clave.privateKey);
        const llavePublica = await window.crypto.subtle.exportKey("spki", clave.publicKey);

        // Convertir las llaves a formato Base64 para mostrarlas
        const llavePrivadaBase64 = arrayBufferToBase64(llavePrivada);
        const llavePublicaBase64 = arrayBufferToBase64(llavePublica);

        // Imprimir la llave privada en el textarea
        document.getElementById("llave").value = llavePrivadaBase64;

        console.log(`Llave pública para ${nombreUsuario}:`, llavePublicaBase64);
        console.log(`Llave privada para ${nombreUsuario}:`, llavePrivadaBase64);

        // Enviar el nombre de usuario y la llave pública al servidor
        await enviarDatos(nombreUsuario, llavePublicaBase64);

    } catch (error) {
        console.error("Error al generar las llaves:", error);
    }
}

async function enviarDatos(nombreUsuario, llavePublica) {
    try {
        const response = await fetch('http://localhost:8080/generar-llaves', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nombreUsuario }) // Envía solo el nombre de usuario
        });

        if (!response.ok) {
            throw new Error('Error al enviar los datos al servidor.');
        }

        const data = await response.json();
        console.log(data.message);
        // Puedes manejar la respuesta que contenga la llave privada si es necesario
    } catch (error) {
        console.error("Error al enviar datos:", error);
        alert("Error al guardar los datos. Intenta nuevamente.");
    }
}

function descargarArchivo() {
    const llavePrivada = document.getElementById("llave").value;

    if (!llavePrivada) {
        alert("No hay llave privada para descargar.");
        return;
    }

    // Crear un blob de la llave privada
    const blob = new Blob([llavePrivada], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    // Crear un enlace para la descarga
    const a = document.createElement('a');
    a.href = url;
    a.download = 'llave_privada.txt'; // Nombre del archivo de descarga
    document.body.appendChild(a);
    a.click(); // Simula un clic para iniciar la descarga
    document.body.removeChild(a); // Limpia el DOM

    // Liberar el objeto URL
    URL.revokeObjectURL(url);
}

// Función para convertir un ArrayBuffer a Base64
function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
}
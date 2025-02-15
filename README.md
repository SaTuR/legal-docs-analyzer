📖 Documentación - Abogado Virtual con GPT-4 y RAG

🚀 Introducción

Este proyecto implementa un abogado virtual basado en GPT-4 con RAG (Retrieval-Augmented Generation), utilizando FastAPI, FAISS, Elasticsearch y PostgreSQL para procesar documentos legales y responder consultas con precisión.

🛠️ Instalación y Despliegue en DigitalOcean

Para desplegar el sistema en DigitalOcean, sigue estos pasos:

1️⃣ Conectar al servidor

ssh usuario@tu-ip-del-servidor

2️⃣ Descargar y ejecutar el script de instalación

wget https://tu-repo.com/install_digitalocean.sh
chmod +x install_digitalocean.sh
./install_digitalocean.sh

3️⃣ Verificar que la API esté en funcionamiento

curl http://$(curl -s ifconfig.me)/docs

Si ves la documentación de FastAPI, la instalación fue exitosa. 🎉

🏗️ Estructura del Proyecto

📂 backend_fastapi.py → API en FastAPI para subir documentos y realizar consultas.📂 install_digitalocean.sh → Script de instalación para despliegue en DigitalOcean.📂 documentation.md → Instrucciones de uso.

🔄 Uso de la API

1️⃣ Subir un documento

POST /upload

📌 **Ejemplo con **``:

curl -X 'POST' 'http://tu-servidor/upload' \
-H 'accept: application/json' \
-H 'Content-Type: multipart/form-data' \
-F 'file=@contrato.pdf'

2️⃣ Hacer una consulta legal

POST /ask

📌 **Ejemplo con **``:

curl -X 'POST' 'http://tu-servidor/ask' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{"question": "¿Cuáles son las obligaciones del arrendatario?"}'

🔹 Respuesta esperada: GPT-4 analiza los documentos y responde con la cláusula correspondiente.

🛠️ Mantenimiento y Optimización

🔄 Reconstruir el índice de búsqueda (FAISS + Elasticsearch)

GET /build_index

📌 Ejemplo:

curl -X 'GET' 'http://tu-servidor/build_index'

🔄 Optimizar la base de datos y búsqueda

GET /optimize

📌 Ejemplo:

curl -X 'GET' 'http://tu-servidor/optimize'

📌 Conclusión

Tu abogado virtual está listo para responder preguntas legales basadas en documentos reales, utilizando búsqueda semántica avanzada con FAISS y GPT-4. 🚀

Si necesitas mejoras o nuevas funciones, ¡hazmelo saber! 🎯


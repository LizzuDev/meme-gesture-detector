<div align="center">

# 🐹 Meme Gesture Detector (Web Edition)

**Detección de gestos manuales y expresiones faciales en tiempo real que disparan memes en tu navegador.**

![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![React](https://img.shields.io/badge/React-18-61dafb?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-red?style=flat-square)

<br/>

> *Levanta tus manos → aparece el mapache Pedro. Apunta con tu dedo → "¡Freeze!". Todo procesado por IA en tiempo real.*

</div>

---

## 🚀 Inicio Rápido (Con Docker)

La forma más fácil y recomendada de levantar el proyecto en cualquier computadora sin instalar librerías manualmente es usando Docker. 

**Requisitos previos:** Tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado.

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/meme-gesture-detector.git
   cd meme-gesture-detector
   ```

2. **Levantar la aplicación:**
   ```bash
   docker compose up --build
   ```
   *(Este comando descargará Python, Node.js, instalará todas las dependencias y arrancará tanto el servidor de IA como la interfaz web automáticamente).*

3. **Abrir el navegador:**
   Ve a `http://localhost:5173`. 
   Da permisos a tu cámara web y ¡listo!

---

## 💻 Inicio Manual (Sin Docker)

Si prefieres correrlo nativamente en tu máquina:

### 1. Servidor Backend (Python / FastAPI)
```bash
# Crear entorno virtual e instalar dependencias
python -m venv venv
.\venv\Scripts\activate   # En Windows
pip install -r requirements.txt

# Ejecutar servidor en el puerto 8000
python server.py
```

### 2. Interfaz Frontend (Node.js / Vite)
Abre *otra* terminal:
```bash
cd frontend
npm install -g pnpm       # Si no tienes pnpm instalado
pnpm install
pnpm run dev
```
Ve a `http://localhost:5173`.

---

## 🎭 Gestos Soportados

El sistema detecta formas de las manos y expresiones de la cara.

### Gestos con las manos:
* **Pistola (Apuntar):** Índice y pulgar extendidos hacia afuera.
* **Corazón Coreano:** Índice y pulgar cruzados.
* **Mapache Pedro:** Levanta **ambas** manos completamente abiertas.
* **Saludar:** Levanta una mano abierta y ladéala hacia un lado.
* **Paz:** Dedo índice y medio arriba.
* **Pulgar arriba / abajo:** Para aprobar o desaprobar.
* **Gafas (OK):** Haz círculos con índice y pulgar en ambas manos.

### Expresiones Faciales:
* **Sonrisa:** Sonríe frente a la cámara (boca abierta o cerrada).
* **Sorpresa:** Abre la boca formando una "O" y levanta tus cejas.
* **Guiño:** Cierra claramente un ojo.
* **Lengua:** Abre ligeramente la boca con los ojos relajados.

---

## 🏗️ Arquitectura del Sistema

La aplicación está dividida en dos capas modernas:

1. **Frontend (React + Three.js):**
   * Captura la webcam desde tu navegador y envía los cuadros de imagen ligeros por WebSocket.
   * Dibuja los memes en la pantalla.
   * Renderiza un modelo 3D (Visor Holográfico) que gira según tus gestos.

2. **Backend (Python + FastAPI + MediaPipe):**
   * Recibe las imágenes vía WebSocket.
   * Procesa la geometría de tus manos (21 puntos clave) y cara (blendshapes).
   * Clasifica qué gesto estás haciendo basándose en distancias matemáticas y ángulos.
   * Devuelve el resultado al instante a la interfaz.

---

## 📝 Personalizar Memes

Si quieres agregar tus propios memes:
1. Pega tu archivo (ej. `mi-meme.jpg`) en la carpeta `frontend/public/memes/`.
2. Ve a `overlay.py` en el backend y asigna tu archivo a un GESTO.
3. Ve a `App.tsx` en el frontend y agrega la misma asignación.
¡Se actualizará en tiempo real!

---

<div align="center">
Desarrollado combinando Visión Computacional Clásica con Tecnologías Web Modernas 🚀
</div>

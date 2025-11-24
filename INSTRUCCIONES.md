# Instrucciones Rápidas - CCTV Viewer

## 📦 Paso 1: Subir la Imagen a DockerHub (Tu PC Actual)

1. **Crear cuenta en DockerHub** (si no tienes):
   - Ve a https://hub.docker.com/
   - Regístrate gratis
   - Verifica tu email

2. **Subir la imagen**:
   ```bash
   cd /home/freddybautista/cctv-viewer-fastapi
   ./deploy.sh TU_USUARIO_DOCKERHUB
   ```

   Ejemplo:
   ```bash
   ./deploy.sh freddybautista
   ```

3. **Anota el nombre de la imagen**:
   ```
   TU_USUARIO/cctv-viewer:latest
   ```

---

## 💻 Paso 2: Instalación en el ChromeOS del Cliente

### 2.1. Transferir archivos necesarios

Copia estos dos archivos al ChromeOS:
- `install-docker-chromeos.sh`
- `quick-start.sh`

Puedes usar USB, Google Drive, o email.

### 2.2. Instalar Docker

```bash
# En el ChromeOS, abre Terminal Linux
bash install-docker-chromeos.sh
```

**IMPORTANTE**: Después de instalar, **cierra la terminal completamente y abre una nueva**.

### 2.3. Ejecutar el Visor

```bash
bash quick-start.sh
```

El script te pedirá:
1. Tu usuario de DockerHub
2. Credenciales de las cámaras (si no hay archivo .env)

Luego descargará y ejecutará todo automáticamente.

### 2.4. Acceder al Visor

Abre el navegador en:
```
http://localhost:8000
```

---

## 🔧 Comandos Útiles (ChromeOS)

```bash
# Ver logs en tiempo real
docker logs -f cctv-viewer

# Detener el visor
docker stop cctv-viewer

# Iniciar el visor
docker start cctv-viewer

# Reiniciar el visor
docker restart cctv-viewer

# Volver a ejecutar todo desde cero
bash quick-start.sh
```

---

## ⚡ Mejoras Realizadas

1. **Latencia reducida**: De 6-10 segundos a 2-4 segundos
   - Segmentos HLS de 1 segundo (antes 2 segundos)
   - Buffer reducido a 2 segmentos (antes 3)
   - Sin cache del navegador

2. **Deployment simplificado**:
   - Un solo comando para subir a DockerHub
   - Script de instalación automática de Docker
   - Script de inicio rápido para el cliente

3. **Configuración optimizada**:
   - GOP optimizado para 30 fps
   - Transcoding directo (copy) para mejor rendimiento
   - Auto-restart del contenedor

---

## 📋 Archivo .env (Configuración)

Si necesitas editar la configuración manualmente:

```bash
nano .env
```

Contenido:
```env
CAM_USER=admin
CAM_PASS=tu_contraseña
CAM_IP=192.168.1.100
CAM_PORT=554
TOTAL_CAMERAS=16
```

---

## 🆘 Problemas Comunes

### "docker: command not found"
- Cierra y vuelve a abrir la terminal después de instalar Docker
- O ejecuta: `newgrp docker`

### "Las cámaras no se ven"
- Verifica credenciales en el archivo .env
- Verifica que la IP y puerto son correctos
- Revisa los logs: `docker logs cctv-viewer`

### "Puerto 8000 ya está en uso"
- Cambia el puerto al ejecutar:
  ```bash
  docker run -d --name cctv-viewer -p 8080:8000 --env-file .env tuusuario/cctv-viewer:latest
  ```
- Luego accede a `http://localhost:8080`

---

## 📞 Estructura del Proyecto

```
cctv-viewer-fastapi/
├── main.py                          # Aplicación FastAPI principal
├── settings.py                      # Configuración
├── index.html                       # Frontend
├── requirements.txt                 # Dependencias Python
├── Dockerfile                       # Imagen Docker
├── docker-compose.yml              # Docker Compose
├── .env.example                    # Plantilla de configuración
├── deploy.sh                       # Script para subir a DockerHub
├── install-docker-chromeos.sh     # Instalador de Docker
├── quick-start.sh                 # Inicio rápido para cliente
├── DEPLOYMENT.md                  # Guía completa de deployment
├── INSTRUCCIONES.md              # Este archivo (resumen)
└── README.md                     # Documentación del proyecto
```

---

## ✅ Checklist de Deployment

**En tu PC:**
- [ ] Crear cuenta en DockerHub
- [ ] Ejecutar `./deploy.sh tu_usuario`
- [ ] Anotar el nombre de la imagen

**En el ChromeOS del cliente:**
- [ ] Copiar archivos `install-docker-chromeos.sh` y `quick-start.sh`
- [ ] Ejecutar `bash install-docker-chromeos.sh`
- [ ] Cerrar y reabrir terminal
- [ ] Ejecutar `bash quick-start.sh`
- [ ] Acceder a http://localhost:8000

---

¡Listo! El visor de cámaras debería estar funcionando con baja latencia.

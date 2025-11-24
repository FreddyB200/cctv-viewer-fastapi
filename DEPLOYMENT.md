# Guía de Deployment - CCTV Viewer

Esta guía te ayudará a desplegar el visor de cámaras en un ChromeOS con contenedor Debian.

## 📋 Tabla de Contenidos
1. [Subir imagen a DockerHub (desde tu PC actual)](#1-subir-imagen-a-dockerhub)
2. [Instalar Docker en ChromeOS/Debian](#2-instalar-docker-en-chromeos-debian)
3. [Descargar y ejecutar la aplicación](#3-descargar-y-ejecutar-la-aplicaci%C3%B3n)

---

## 1. Subir Imagen a DockerHub

### Desde tu PC actual (Linux):

```bash
# 1. Navega al directorio del proyecto
cd /home/freddybautista/cctv-viewer-fastapi

# 2. Ejecuta el script de deployment
# Reemplaza 'tuusuario' con tu nombre de usuario de DockerHub
./deploy.sh tuusuario

# El script te pedirá:
# - Tu contraseña de DockerHub
# - Construirá la imagen
# - La subirá automáticamente
```

**Si no tienes cuenta en DockerHub:**
1. Ve a https://hub.docker.com/
2. Crea una cuenta gratis
3. Verifica tu email
4. Usa ese usuario en el comando anterior

---

## 2. Instalar Docker en ChromeOS / Debian

### 2.1. Abrir Terminal Linux en ChromeOS

1. Abre la app **Terminal** en ChromeOS
2. Esto abrirá un contenedor Debian

### 2.2. Instalar Docker (Método Rápido)

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y ca-certificates curl gnupg

# Agregar la clave GPG oficial de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Agregar el repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Actualizar e instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Agregar tu usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER

# Recargar los grupos (o reinicia la terminal)
newgrp docker

# Verificar que Docker está instalado correctamente
docker --version
```

**Nota:** Si el comando `newgrp docker` no funciona, **cierra y vuelve a abrir la terminal**.

### 2.3. Script de Instalación Automática (Alternativa)

Si prefieres un script automático:

```bash
# Descargar e instalar Docker automáticamente
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar la terminal
```

---

## 3. Descargar y Ejecutar la Aplicación

### 3.1. Crear archivo de configuración

```bash
# Crear directorio para la aplicación
mkdir -p ~/cctv-viewer
cd ~/cctv-viewer

# Crear archivo .env con tus credenciales
nano .env
```

**Contenido del archivo .env:**
```env
CAM_USER=admin
CAM_PASS=tu_contraseña_de_camaras
CAM_IP=192.168.1.100
CAM_PORT=554
TOTAL_CAMERAS=16
```

Presiona `Ctrl+O` para guardar, `Enter` para confirmar, y `Ctrl+X` para salir.

### 3.2. Descargar y ejecutar la imagen

```bash
# Descargar la imagen de DockerHub
# Reemplaza 'tuusuario' con tu usuario de DockerHub
docker pull tuusuario/cctv-viewer:latest

# Ejecutar el contenedor
docker run -d \
  --name cctv-viewer \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  tuusuario/cctv-viewer:latest

# Verificar que está corriendo
docker ps
```

### 3.3. Ver los logs (opcional)

```bash
# Ver los logs en tiempo real
docker logs -f cctv-viewer

# Ver las últimas 50 líneas
docker logs --tail 50 cctv-viewer
```

### 3.4. Acceder a la aplicación

Abre tu navegador y ve a:
```
http://localhost:8000
```

O desde otro dispositivo en la misma red:
```
http://IP_DEL_CHROMEOS:8000
```

---

## 🔧 Comandos Útiles

### Gestión del Contenedor

```bash
# Detener el contenedor
docker stop cctv-viewer

# Iniciar el contenedor
docker start cctv-viewer

# Reiniciar el contenedor
docker restart cctv-viewer

# Eliminar el contenedor
docker rm -f cctv-viewer

# Ver información del contenedor
docker inspect cctv-viewer
```

### Actualizar a una Nueva Versión

```bash
# Detener y eliminar el contenedor actual
docker stop cctv-viewer
docker rm cctv-viewer

# Descargar la nueva versión
docker pull tuusuario/cctv-viewer:latest

# Ejecutar la nueva versión
docker run -d \
  --name cctv-viewer \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  tuusuario/cctv-viewer:latest
```

### Limpiar Imágenes Antiguas

```bash
# Ver imágenes instaladas
docker images

# Eliminar imágenes sin usar
docker image prune -a
```

---

## 🐛 Solución de Problemas

### El contenedor no inicia

```bash
# Ver los logs de error
docker logs cctv-viewer

# Verificar que el archivo .env existe y tiene las credenciales correctas
cat .env
```

### No se ven las cámaras

1. Verifica que las credenciales en `.env` son correctas
2. Verifica que la IP y puerto de las cámaras son correctos
3. Asegúrate de que el ChromeOS puede acceder a la red de las cámaras
4. Revisa los logs: `docker logs cctv-viewer`

### Puerto 8000 ya está en uso

```bash
# Usar otro puerto (ejemplo: 8080)
docker run -d \
  --name cctv-viewer \
  --restart unless-stopped \
  -p 8080:8000 \
  --env-file .env \
  tuusuario/cctv-viewer:latest

# Luego accede a http://localhost:8080
```

### Docker no funciona después de instalarlo

1. Cierra completamente la terminal
2. Abre una nueva terminal
3. Verifica: `docker --version`
4. Si sigue sin funcionar: `sudo systemctl start docker`

---

## ⚡ Optimizaciones de Latencia

Esta versión incluye optimizaciones para **baja latencia**:
- Segmentos HLS de 1 segundo (vs 2-3 segundos antes)
- Buffer reducido a 2 segmentos (vs 3-5 antes)
- Sin cache del navegador
- GOP optimizado

**Latencia esperada: 2-4 segundos** (antes era 6-10 segundos)

---

## 📊 Recursos del Sistema

Para 16 cámaras en 720p/1080p:
- **RAM:** ~2-4 GB
- **CPU:** 2-4 cores recomendado
- **Ancho de banda:** ~10-20 Mbps

---

## 🔒 Seguridad

**Importante:** Esta aplicación NO debe exponerse directamente a Internet sin las siguientes medidas:

1. Usar HTTPS con certificado SSL
2. Agregar autenticación (usuario/contraseña)
3. Usar un firewall o VPN
4. Cambiar las contraseñas por defecto

Para uso en red local (LAN), está bien tal como está.

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `docker logs cctv-viewer`
2. Verifica el archivo .env
3. Asegúrate de que Docker está corriendo: `docker ps`
4. Verifica conectividad a las cámaras: `ping IP_DE_CAMARA`

---

## 🎉 ¡Listo!

Tu visor de cámaras CCTV está funcionando con baja latencia optimizada.

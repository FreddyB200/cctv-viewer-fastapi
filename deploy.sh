#!/bin/bash

# Script para construir y subir la imagen Docker a DockerHub
# Uso: ./deploy.sh [tu_usuario_dockerhub]

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== CCTV Viewer Docker Deployment ===${NC}"

# Verificar que se proporcionó el usuario de DockerHub
if [ -z "$1" ]; then
    echo -e "${YELLOW}Uso: ./deploy.sh [tu_usuario_dockerhub]${NC}"
    echo -e "${YELLOW}Ejemplo: ./deploy.sh freddybautista${NC}"
    exit 1
fi

DOCKERHUB_USER=$1
IMAGE_NAME="cctv-viewer"
VERSION="latest"
FULL_IMAGE_NAME="${DOCKERHUB_USER}/${IMAGE_NAME}:${VERSION}"

echo -e "${GREEN}1. Verificando que Docker está instalado...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker no está instalado. Por favor instala Docker primero.${NC}"
    exit 1
fi
echo -e "${GREEN}   ✓ Docker instalado${NC}"

echo -e "${GREEN}2. Construyendo imagen Docker...${NC}"
docker build -t ${IMAGE_NAME}:${VERSION} .
echo -e "${GREEN}   ✓ Imagen construida: ${IMAGE_NAME}:${VERSION}${NC}"

echo -e "${GREEN}3. Etiquetando imagen para DockerHub...${NC}"
docker tag ${IMAGE_NAME}:${VERSION} ${FULL_IMAGE_NAME}
echo -e "${GREEN}   ✓ Imagen etiquetada: ${FULL_IMAGE_NAME}${NC}"

echo -e "${GREEN}4. Iniciando sesión en DockerHub...${NC}"
echo -e "${YELLOW}   Por favor ingresa tu contraseña de DockerHub:${NC}"
docker login -u ${DOCKERHUB_USER}

echo -e "${GREEN}5. Subiendo imagen a DockerHub...${NC}"
docker push ${FULL_IMAGE_NAME}
echo -e "${GREEN}   ✓ Imagen subida exitosamente${NC}"

echo ""
echo -e "${GREEN}=== DEPLOYMENT COMPLETADO ===${NC}"
echo ""
echo -e "${GREEN}Tu imagen está disponible en DockerHub:${NC}"
echo -e "${YELLOW}   docker pull ${FULL_IMAGE_NAME}${NC}"
echo ""
echo -e "${GREEN}Para ejecutar en otra máquina:${NC}"
echo -e "${YELLOW}   1. Crea un archivo .env con tus credenciales${NC}"
echo -e "${YELLOW}   2. docker run -d --name cctv-viewer \\${NC}"
echo -e "${YELLOW}      -p 8000:8000 \\${NC}"
echo -e "${YELLOW}      --env-file .env \\${NC}"
echo -e "${YELLOW}      ${FULL_IMAGE_NAME}${NC}"
echo ""

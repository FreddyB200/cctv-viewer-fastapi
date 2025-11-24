#!/bin/bash

# Script de inicio rápido para el visor de cámaras CCTV
# Este script configura y ejecuta el visor de cámaras

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   CCTV Viewer - Inicio Rápido        ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker no está instalado.${NC}"
    echo -e "${YELLOW}Por favor ejecuta primero: bash install-docker-chromeos.sh${NC}"
    exit 1
fi

# Verificar si el contenedor ya existe
if docker ps -a --format '{{.Names}}' | grep -q '^cctv-viewer$'; then
    echo -e "${YELLOW}El contenedor 'cctv-viewer' ya existe.${NC}"
    echo ""
    echo "Opciones:"
    echo "  1) Iniciar el contenedor existente"
    echo "  2) Reiniciar el contenedor"
    echo "  3) Eliminar y crear uno nuevo"
    echo "  4) Ver logs"
    echo "  5) Salir"
    echo ""
    read -p "Selecciona una opción (1-5): " option

    case $option in
        1)
            echo -e "${GREEN}Iniciando contenedor...${NC}"
            docker start cctv-viewer
            echo -e "${GREEN}✓ Contenedor iniciado${NC}"
            ;;
        2)
            echo -e "${GREEN}Reiniciando contenedor...${NC}"
            docker restart cctv-viewer
            echo -e "${GREEN}✓ Contenedor reiniciado${NC}"
            ;;
        3)
            echo -e "${YELLOW}Eliminando contenedor existente...${NC}"
            docker rm -f cctv-viewer
            echo -e "${GREEN}✓ Contenedor eliminado${NC}"
            # Continuar con la creación de uno nuevo
            ;;
        4)
            echo -e "${GREEN}Mostrando logs (Ctrl+C para salir)...${NC}"
            docker logs -f cctv-viewer
            exit 0
            ;;
        5)
            echo -e "${GREEN}Saliendo...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opción inválida${NC}"
            exit 1
            ;;
    esac

    if [ "$option" != "3" ]; then
        echo ""
        echo -e "${GREEN}Accede al visor en: ${YELLOW}http://localhost:8000${NC}"
        echo -e "${GREEN}Ver logs: ${YELLOW}docker logs -f cctv-viewer${NC}"
        exit 0
    fi
fi

# Pedir información de usuario de DockerHub
echo -e "${GREEN}Configuración inicial${NC}"
echo ""
read -p "Ingresa tu usuario de DockerHub: " DOCKERHUB_USER

if [ -z "$DOCKERHUB_USER" ]; then
    echo -e "${RED}ERROR: Debes ingresar un usuario de DockerHub${NC}"
    exit 1
fi

IMAGE_NAME="${DOCKERHUB_USER}/cctv-viewer:latest"

# Verificar si el archivo .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}No se encontró archivo .env. Creando uno nuevo...${NC}"
    echo ""
    echo -e "${GREEN}Por favor ingresa la configuración de tus cámaras:${NC}"

    read -p "Usuario de las cámaras [admin]: " CAM_USER
    CAM_USER=${CAM_USER:-admin}

    read -s -p "Contraseña de las cámaras: " CAM_PASS
    echo ""

    read -p "IP del DVR/NVR: " CAM_IP

    read -p "Puerto RTSP [554]: " CAM_PORT
    CAM_PORT=${CAM_PORT:-554}

    read -p "Número de cámaras [16]: " TOTAL_CAMERAS
    TOTAL_CAMERAS=${TOTAL_CAMERAS:-16}

    # Crear archivo .env
    cat > .env << EOF
# Configuración de cámaras CCTV
CAM_USER=${CAM_USER}
CAM_PASS=${CAM_PASS}
CAM_IP=${CAM_IP}
CAM_PORT=${CAM_PORT}
TOTAL_CAMERAS=${TOTAL_CAMERAS}
EOF

    echo -e "${GREEN}✓ Archivo .env creado${NC}"
else
    echo -e "${GREEN}✓ Archivo .env encontrado${NC}"
fi

echo ""
echo -e "${GREEN}Descargando imagen de DockerHub...${NC}"
docker pull ${IMAGE_NAME}

echo ""
echo -e "${GREEN}Iniciando contenedor...${NC}"
docker run -d \
  --name cctv-viewer \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  ${IMAGE_NAME}

echo ""
echo -e "${GREEN}✓ Contenedor iniciado exitosamente${NC}"
echo ""

# Esperar 3 segundos para que el contenedor inicie
echo -e "${YELLOW}Verificando estado del contenedor...${NC}"
sleep 3

if docker ps --format '{{.Names}}' | grep -q '^cctv-viewer$'; then
    echo -e "${GREEN}✓ Contenedor ejecutándose correctamente${NC}"
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           ¡TODO LISTO!                ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Accede al visor en:${NC}"
    echo -e "${YELLOW}   http://localhost:8000${NC}"
    echo ""
    echo -e "${GREEN}O desde otro dispositivo en la misma red:${NC}"
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    echo -e "${YELLOW}   http://${LOCAL_IP}:8000${NC}"
    echo ""
    echo -e "${GREEN}Comandos útiles:${NC}"
    echo -e "${YELLOW}   Ver logs:       docker logs -f cctv-viewer${NC}"
    echo -e "${YELLOW}   Detener:        docker stop cctv-viewer${NC}"
    echo -e "${YELLOW}   Reiniciar:      docker restart cctv-viewer${NC}"
    echo -e "${YELLOW}   Ver estado:     docker ps${NC}"
    echo ""
else
    echo -e "${RED}ERROR: El contenedor no está ejecutándose${NC}"
    echo -e "${YELLOW}Ver logs de error: docker logs cctv-viewer${NC}"
    exit 1
fi

#!/bin/bash

# Script para instalar Docker en ChromeOS/Debian
# Ejecutar con: bash install-docker-chromeos.sh

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Instalador de Docker para ChromeOS/Debian ===${NC}"
echo ""

# Verificar si Docker ya está instalado
if command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker ya está instalado:${NC}"
    docker --version
    echo ""
    read -p "¿Deseas reinstalar Docker? (s/N): " reinstall
    if [[ ! $reinstall =~ ^[Ss]$ ]]; then
        echo -e "${GREEN}Instalación cancelada.${NC}"
        exit 0
    fi
fi

echo -e "${GREEN}1. Actualizando el sistema...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${GREEN}2. Instalando dependencias...${NC}"
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo -e "${GREEN}3. Agregando la clave GPG de Docker...${NC}"
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo -e "${GREEN}4. Agregando el repositorio de Docker...${NC}"
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo -e "${GREEN}5. Instalando Docker...${NC}"
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo -e "${GREEN}6. Configurando permisos de usuario...${NC}"
sudo usermod -aG docker $USER

echo -e "${GREEN}7. Iniciando Docker...${NC}"
sudo systemctl start docker
sudo systemctl enable docker

echo ""
echo -e "${GREEN}=== INSTALACIÓN COMPLETADA ===${NC}"
echo ""
echo -e "${YELLOW}IMPORTANTE: Debes cerrar esta terminal y abrir una nueva para que los cambios surtan efecto.${NC}"
echo ""
echo -e "${GREEN}Para verificar la instalación (en la nueva terminal):${NC}"
echo -e "${YELLOW}   docker --version${NC}"
echo -e "${YELLOW}   docker run hello-world${NC}"
echo ""
echo -e "${GREEN}Siguiente paso: Sigue las instrucciones en DEPLOYMENT.md para descargar y ejecutar el visor de cámaras.${NC}"
echo ""

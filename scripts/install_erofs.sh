#!/bin/bash
set -e

echo "=== Instalando dependencias de EROFS (erofs-utils) ==="

if command -v pacman >/dev/null 2>&1; then
    echo "Ejecutando: pacman -S --noconfirm erofs-utils"
    pacman -Sy --noconfirm erofs-utils
    echo "¡Instalación completada con éxito!"
else
    echo "[ERROR] Este script solo admite Arch Linux/CachyOS (pacman). Por favor, instala 'erofs-utils' manualmente en tu distribución." >&2
    exit 1
fi

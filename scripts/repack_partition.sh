#!/bin/bash
set -e

# scripts/repack_partition.sh <output_dir> <partition_name>
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <output_dir> <partition_name>" >&2
    exit 1
fi

OUTPUT_DIR="$1"
PART_NAME="$2"

IMG_FILE="$OUTPUT_DIR/${PART_NAME}.img"
EXTRACT_DIR="$OUTPUT_DIR/${PART_NAME}_extracted"

if [ ! -d "$EXTRACT_DIR" ]; then
    echo "Error: La carpeta de origen '$EXTRACT_DIR' no existe." >&2
    exit 1
fi

echo "=== Reconstruyendo partición: $PART_NAME ==="
echo "Carpeta origen: $EXTRACT_DIR"
echo "Archivo destino: $IMG_FILE"

# Crear copia de seguridad de la imagen anterior
if [ -f "$IMG_FILE" ]; then
    echo "Creando copia de seguridad de la imagen anterior..."
    mv "$IMG_FILE" "${IMG_FILE}.bak"
fi

if ! command -v mkfs.erofs >/dev/null 2>&1; then
    echo "[ERROR] 'mkfs.erofs' no está instalado. Instale 'erofs-utils' primero." >&2
    # Restaurar backup si existía
    [ -f "${IMG_FILE}.bak" ] && mv "${IMG_FILE}.bak" "$IMG_FILE"
    exit 1
fi

echo "Ejecutando mkfs.erofs con compresión LZ4..."
# -z lz4 es la compresión estándar compatible con la mayoría de kernels Android
if mkfs.erofs -z lz4 "$IMG_FILE" "$EXTRACT_DIR"; then
    echo "=== Reconstrucción Finalizada con Éxito ==="
    ls -lh "$IMG_FILE"
    rm -f "${IMG_FILE}.bak"
else
    echo "[ERROR] Falló la reconstrucción de la imagen EROFS." >&2
    if [ -f "${IMG_FILE}.bak" ]; then
        echo "Restaurando la imagen anterior desde la copia de seguridad..."
        mv "${IMG_FILE}.bak" "$IMG_FILE"
    fi
    exit 1
fi

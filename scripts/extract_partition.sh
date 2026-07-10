#!/bin/bash
set -e

# scripts/extract_partition.sh <output_dir> <partition_name>
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <output_dir> <partition_name>" >&2
    exit 1
fi

OUTPUT_DIR="$1"
PART_NAME="$2"

IMG_FILE="$OUTPUT_DIR/${PART_NAME}.img"
EXTRACT_DIR="$OUTPUT_DIR/${PART_NAME}_extracted"

if [ ! -f "$IMG_FILE" ]; then
    echo "Error: El archivo de partición '$IMG_FILE' no existe." >&2
    exit 1
fi

echo "=== Extrayendo partición: $PART_NAME ==="
echo "Archivo origen: $IMG_FILE"
echo "Carpeta destino: $EXTRACT_DIR"

# Limpiar carpeta de destino si existe
if [ -d "$EXTRACT_DIR" ]; then
    echo "La carpeta de destino ya existe. Eliminándola..."
    rm -rf "$EXTRACT_DIR"
fi

mkdir -p "$EXTRACT_DIR"

# Detectar tipo de sistema de archivos usando file
if file "$IMG_FILE" | grep -q -i "erofs"; then
    echo "Detectado sistema de archivos EROFS."
    if ! command -v fsck.erofs >/dev/null 2>&1; then
        echo "[ERROR] 'fsck.erofs' no está instalado. Instale 'erofs-utils' primero." >&2
        exit 1
    fi
    echo "Ejecutando fsck.erofs --extract..."
    # fsck.erofs extrae el contenido al directorio de salida
    fsck.erofs --extract="$EXTRACT_DIR" "$IMG_FILE"
else
    echo "No es EROFS o es formato desconocido. Intentando montar de solo lectura para copiar..."
    # Si es ext4 u otro formato, intentamos montarlo y copiar el contenido
    TEMP_MOUNT="/tmp/mnt_extract_${PART_NAME}_$$"
    mkdir -p "$TEMP_MOUNT"
    
    cleanup() {
        if mountpoint -q "$TEMP_MOUNT" 2>/dev/null; then
            sudo umount "$TEMP_MOUNT"
        fi
        rm -rf "$TEMP_MOUNT"
    }
    trap cleanup EXIT
    
    if sudo mount -o loop,ro "$IMG_FILE" "$TEMP_MOUNT"; then
        echo "Montado con éxito. Copiando archivos..."
        cp -a "$TEMP_MOUNT"/. "$EXTRACT_DIR/"
        echo "Copia completada con éxito."
    else
        echo "[ERROR] No se pudo montar la imagen '$IMG_FILE' para extracción." >&2
        exit 1
    fi
fi

echo "=== Extracción Finalizada con Éxito ==="
echo "Contenido extraído en: $EXTRACT_DIR"
echo "Permisos ajustados para edición local."
chmod -R 777 "$EXTRACT_DIR"

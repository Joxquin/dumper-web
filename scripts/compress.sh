#!/bin/bash
set -e

# compress.sh <output_dir> <mount_dir> <new_super_img_path> [is_sparse]
if [ "$#" -lt 3 ]; then
    echo "Uso: $0 <output_dir> <mount_dir> <new_super_img_path> [is_sparse]" >&2
    exit 1
fi

OUTPUT_DIR="$1"
MOUNT_DIR="$2"
NEW_SUPER="$3"
IS_SPARSE="${4:-false}"

SCRIPT_DIR=$(dirname "$0")

echo "=== Iniciando Repack de super.img ==="
echo "Carpeta origen: $OUTPUT_DIR"
echo "Carpeta montaje: $MOUNT_DIR"
echo "Imagen destino: $NEW_SUPER"
echo "Sparse output: $IS_SPARSE"

# 1. Asegurar desmontaje de las particiones
echo "[1/2] Desmontando particiones para asegurar consistencia..."
bash "$SCRIPT_DIR/unmount.sh" "$MOUNT_DIR"

# 2. Ejecutar empaquetado usando lpmake mediante el helper de python
echo "[2/2] Reconstruyendo super.img..."
python3 "$SCRIPT_DIR/compress_helper.py" "$OUTPUT_DIR" "$NEW_SUPER" "$IS_SPARSE"

echo "=== Repack Finalizado con Éxito ==="
ls -lh "$NEW_SUPER"

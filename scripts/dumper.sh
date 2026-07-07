#!/bin/bash
set -e

# dumper.sh <super_img> <output_dir>
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <super_img> <output_dir>" >&2
    exit 1
fi

SUPER_IMG="$1"
OUTPUT_DIR="$2"

if [ ! -f "$SUPER_IMG" ]; then
    echo "Error: El archivo '$SUPER_IMG' no existe." >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Limpiar logs anteriores si existen
echo "=== Iniciando Descompresión ==="
echo "Archivo: $SUPER_IMG"
echo "Destino: $OUTPUT_DIR"

# Detectar si es una imagen sparse
# Sparse magic en hex: 3aff26ed
MAGIC=$(od -An -tx4 -N4 "$SUPER_IMG" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')

SUPER_RAW="$OUTPUT_DIR/super.raw"

if [ "$MAGIC" = "3aff26ed" ]; then
    echo "[1/4] Detectada imagen SPARSE. Convirtiendo a RAW con simg2img..."
    simg2img "$SUPER_IMG" "$SUPER_RAW"
else
    echo "[1/4] Detectada imagen RAW. Creando enlace simbólico..."
    # Si ya es raw, hacemos un symlink para ahorrar espacio y tiempo
    ln -sf "$(realpath "$SUPER_IMG")" "$SUPER_RAW"
fi

echo "[2/4] Generando metadatos de la imagen super..."
lpdump -j "$SUPER_RAW" > "$OUTPUT_DIR/metadata.json"
lpdump "$SUPER_RAW" > "$OUTPUT_DIR/metadata.txt"

echo "[3/4] Desempaquetando particiones con lpunpack..."
lpunpack "$SUPER_RAW" "$OUTPUT_DIR"

# Borrar el enlace simbólico o archivo temporal si no lo necesitamos, para no duplicar en el repack.
# Pero espera! lpmake creará el nuevo super en otra ruta, así que el super.raw en la carpeta de salida
# no molesta y nos sirve como referencia.
echo "[4/4] ¡Descompresión completada con éxito!"
echo "Particiones extraídas en: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"

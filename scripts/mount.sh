#!/bin/bash
set -e

# mount.sh <output_dir> <mount_dir> [single_partition]
if [ "$#" -lt 2 ]; then
    echo "Uso: $0 <output_dir> <mount_dir> [single_partition]" >&2
    exit 1
fi

OUTPUT_DIR="$1"
MOUNT_DIR="$2"
SINGLE_PARTITION="${3:-}"

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "La carpeta de particiones '$OUTPUT_DIR' no existe. Creándola..."
    mkdir -p "$OUTPUT_DIR"
fi

mkdir -p "$MOUNT_DIR"

echo "=== Iniciando Montaje de Particiones ==="
echo "Carpeta origen: $OUTPUT_DIR"
echo "Carpeta montaje: $MOUNT_DIR"

# Encontrar archivos .img en la carpeta de origen
# Ignoramos super.img o nuevo_super.img
for img_file in "$OUTPUT_DIR"/*.img; do
    [ -e "$img_file" ] || continue
    
    filename=$(basename "$img_file")
    partition_name="${filename%.img}"
    
    # Ignorar la imagen super original o reconstruida si se guardaron en la misma carpeta
    if [ "$partition_name" = "super" ] || [ "$partition_name" = "nuevo_super" ]; then
        continue
    fi
    
    # Si se especificó una partición única, ignorar el resto
    if [ -n "$SINGLE_PARTITION" ] && [ "$partition_name" != "$SINGLE_PARTITION" ]; then
        continue
    fi
    
    part_mount_path="$MOUNT_DIR/$partition_name"
    mkdir -p "$part_mount_path"
    
    # Verificar si ya está montado (buscando coincidencia exacta en /proc/mounts)
    if mountpoint -q "$part_mount_path" 2>/dev/null || grep -q -E "[[:space:]]${part_mount_path}[[:space:]]" /proc/mounts; then
        echo "La partición '$partition_name' ya está montada en $part_mount_path"
        continue
    fi
    
    echo "Montando '$partition_name'..."
    # Intentar montar en modo Lectura/Escritura (RW)
    if sudo mount -o loop,rw "$img_file" "$part_mount_path" 2>/dev/null; then
        echo " -> Montado con éxito en modo Lectura-Escritura (RW)."
    else
        echo " -> [!] No se pudo montar en modo RW (posiblemente EROFS o formato no compatible)."
        echo " -> Intentando montar en modo Solo Lectura (RO)..."
        if sudo mount -o loop,ro "$img_file" "$part_mount_path"; then
            echo " -> Montado con éxito en modo Solo Lectura (RO)."
        else
            echo " -> [ERROR] Falló el montaje de '$partition_name'." >&2
        fi
    fi
done

echo "=== Montaje Finalizado ==="
df -h | grep "$MOUNT_DIR" || true

#!/bin/bash
set -e

# unmount.sh <mount_dir> [single_partition]
if [ "$#" -lt 1 ]; then
    echo "Uso: $0 <mount_dir> [single_partition]" >&2
    exit 1
fi

MOUNT_DIR="$1"
SINGLE_PARTITION="${2:-}"

if [ ! -d "$MOUNT_DIR" ]; then
    echo "Carpeta de montaje '$MOUNT_DIR' no existe o ya está limpia."
    exit 0
fi

echo "=== Iniciando Desmontaje de Particiones ==="
echo "Carpeta montaje: $MOUNT_DIR"

# Buscar directorios montados bajo MOUNT_DIR
# Leer /proc/mounts es más seguro para listar puntos de montaje reales
# que correspondan a subcarpetas de MOUNT_DIR.
ABS_MOUNT_DIR=$(realpath "$MOUNT_DIR")

# Filtrar puntos de montaje que contengan la ruta absoluta
if [ -n "$SINGLE_PARTITION" ]; then
    # Filtrar solo el punto de montaje exacto (evitando que 'system' coincida con 'system_ext')
    mount_points=$(grep -oE "[[:space:]]$ABS_MOUNT_DIR/$SINGLE_PARTITION[[:space:]]" /proc/mounts | awk '{print $1}' | uniq)
else
    mount_points=$(grep -oE "[[:space:]]$ABS_MOUNT_DIR/[^[:space:]]+" /proc/mounts | awk '{print $1}' | sort -r | uniq)
fi

if [ -z "$mount_points" ]; then
    echo "No se encontraron particiones montadas bajo '$MOUNT_DIR'."
else
    for mp in $mount_points; do
        echo "Desmontando '$mp'..."
        if sudo umount -l "$mp"; then
            echo " -> Desmontado con éxito (lazy unmount)."
            # Opcional: Eliminar la carpeta vacía si se desmontó bien
            rmdir "$mp" || true
        else
            echo " -> [ERROR] No se pudo desmontar '$mp'." >&2
        fi
    done
fi

echo "=== Desmontaje Finalizado ==="

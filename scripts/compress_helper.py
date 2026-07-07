#!/usr/bin/env python3
import json
import os
import re
import sys
import subprocess

def main():
    if len(sys.argv) < 4:
        print("Uso: compress_helper.py <output_dir> <new_super_img> <is_sparse>", file=sys.stderr)
        sys.exit(1)
        
    output_dir = sys.argv[1]
    new_super = sys.argv[2]
    is_sparse = sys.argv[3].lower() == 'true'
    
    metadata_json_path = os.path.join(output_dir, 'metadata.json')
    metadata_txt_path = os.path.join(output_dir, 'metadata.txt')
    
    if not os.path.exists(metadata_json_path) or not os.path.exists(metadata_txt_path):
        print(f"Error: No se encuentran los archivos de metadatos en {output_dir}", file=sys.stderr)
        sys.exit(1)
        
    with open(metadata_json_path) as f:
        meta = json.load(f)
        
    with open(metadata_txt_path) as f:
        txt = f.read()
        
    # Encontrar el tamaño máximo de metadatos y número de slots
    metadata_size = 65536
    metadata_slots = 2
    m_size = re.search(r'Metadata max size: (\d+)', txt)
    if m_size: 
        metadata_size = int(m_size.group(1))
    m_slots = re.search(r'Metadata slot count: (\d+)', txt)
    if m_slots: 
        metadata_slots = int(m_slots.group(1))
    
    # Encontrar los atributos de las particiones (readonly / none)
    partition_attrs = {}
    part_blocks = re.findall(r'Name:\s*(\S+)\s*[\r\n]+\s*Group:\s*(\S+)\s*[\r\n]+\s*Attributes:\s*(\S+)', txt)
    for name, group, attrs in part_blocks:
        partition_attrs[name] = attrs
        
    # Configuración de los dispositivos de bloque
    block_device = meta['block_devices'][0]
    device_size = block_device['size']
    block_size = block_device.get('block_size', '4096')
    alignment = block_device.get('alignment', '1048576')
    super_name = block_device.get('name', 'super')
    
    cmd = [
        'lpmake',
        f'--device-size={device_size}',
        f'--metadata-size={metadata_size}',
        f'--metadata-slots={metadata_slots}',
        f'--block-size={block_size}',
        f'--alignment={alignment}',
        f'--super-name={super_name}',
        f'--output={new_super}'
    ]
    
    if is_sparse:
        cmd.append('--sparse')
        
    # Añadir grupos de particiones
    for group in meta['groups']:
        name = group['name']
        if name == 'default':
            continue
        max_size = group.get('maximum_size', '0')
        cmd.append(f'--group={name}:{max_size}')
        
    # Añadir particiones e imágenes asociadas
    for part in meta['partitions']:
        name = part['name']
        group_name = part['group_name']
        attrs = partition_attrs.get(name, 'readonly')
        
        img_path = os.path.join(output_dir, f'{name}.img')
        if os.path.exists(img_path):
            size = os.path.getsize(img_path)
            # Alinear tamaño a sectores de 512 bytes
            if size % 512 != 0:
                size = ((size // 512) + 1) * 512
            cmd.append(f'--partition={name}:{attrs}:{size}:{group_name}')
            cmd.append(f'--image={name}={img_path}')
        else:
            size = part['size']
            cmd.append(f'--partition={name}:{attrs}:{size}:{group_name}')
            
    print("Ejecutando comando lpmake:")
    print(" ".join(cmd))
    
    # Ejecutar el comando lpmake
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error al ejecutar lpmake:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
        
    print("¡lpmake finalizado con éxito!")

if __name__ == '__main__':
    main()

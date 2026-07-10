#!/usr/bin/env python3
import os
import sys
import json
import urllib.parse

def get_params():
    params = {}
    query = os.environ.get('QUERY_STRING', '')
    if query:
        for k, v in urllib.parse.parse_qs(query).items():
            params[k] = v[0]
    return params

print("Content-Type: application/json")
print("Access-Control-Allow-Origin: *")
print("")

params = get_params()
output_dir = params.get('output_dir')

if not output_dir:
    print(json.dumps({"error": "Falta el parámetro 'output_dir'"}))
    sys.exit(0)

output_dir = os.path.abspath(output_dir)
metadata_json = os.path.join(output_dir, 'metadata.json')

if not os.path.exists(metadata_json):
    print(json.dumps({"error": f"No se encuentra metadata.json en {output_dir}"}))
    sys.exit(0)

def detect_fs_type(img_path):
    if not os.path.exists(img_path) or os.path.getsize(img_path) < 2048:
        return "none"
    try:
        with open(img_path, 'rb') as f:
            f.seek(1024)
            sb = f.read(100)
            if len(sb) >= 4 and sb[0:4] == b'\xe2\xe1\xf5\xe0':
                return "erofs"
            if len(sb) >= 58 and sb[56:58] == b'\x53\xef':
                return "ext4"
            if len(sb) >= 4 and sb[0:4] == b'\x10\x20\xf5\xf2':
                return "f2fs"
    except Exception:
        pass
    return "unknown"

try:
    with open(metadata_json) as f:
        data = json.load(f)
except Exception as e:
    print(json.dumps({"error": f"Error al leer metadata.json: {str(e)}"}))
    sys.exit(0)

# Obtener lista de montajes activos desde /proc/mounts
mounted_list = []
try:
    with open('/proc/mounts', 'r') as f:
        for line in f:
            if 'loop' in line:
                parts = line.split()
                if len(parts) >= 2:
                    mounted_list.append(parts[1])
except Exception:
    pass

# Enriquecer las particiones con estado de imagen y extracción
partitions = data.get("partitions", [])
for part in partitions:
    name = part.get("name")
    img_path = os.path.join(output_dir, f"{name}.img")
    extracted_dir = os.path.join(output_dir, f"{name}_extracted")
    
    part["img_exists"] = os.path.exists(img_path)
    part["is_extracted"] = os.path.isdir(extracted_dir)
    part["extracted_path"] = extracted_dir if part["is_extracted"] else ""
    part["fs_type"] = detect_fs_type(img_path) if part["img_exists"] else "none"

response = {
    "partitions": partitions,
    "groups": data.get("groups", []),
    "mounted_list": mounted_list
}

print(json.dumps(response, indent=2))

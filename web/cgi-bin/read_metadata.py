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

response = {
    "partitions": data.get("partitions", []),
    "groups": data.get("groups", []),
    "mounted_list": mounted_list
}

print(json.dumps(response, indent=2))

#!/usr/bin/env python3
import os
import sys
import json
import urllib.parse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import job_manager

def get_params():
    params = {}
    query = os.environ.get('QUERY_STRING', '')
    if query:
        for k, v in urllib.parse.parse_qs(query).items():
            params[k] = v[0]
            
    if os.environ.get('REQUEST_METHOD', '').upper() == 'POST':
        try:
            content_length = int(os.environ.get('CONTENT_LENGTH', 0))
            if content_length > 0:
                post_data = sys.stdin.read(content_length)
                for k, v in urllib.parse.parse_qs(post_data).items():
                    params[k] = v[0]
        except Exception:
            pass
            
    return params

print("Content-Type: application/json")
print("Access-Control-Allow-Origin: *")
print("")

params = get_params()
output_dir = params.get('output_dir')
mount_dir = params.get('mount_dir')
new_super = params.get('new_super')
is_sparse = params.get('is_sparse', 'false')

if not output_dir or not mount_dir or not new_super:
    print(json.dumps({
        "status": "error",
        "message": "Faltan parámetros requeridos: 'output_dir', 'mount_dir' y 'new_super'"
    }))
    sys.exit(0)

output_dir = os.path.abspath(output_dir)
mount_dir = os.path.abspath(mount_dir)
new_super = os.path.abspath(new_super)

script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
compress_script = os.path.join(script_dir, 'scripts', 'compress.sh')

# Iniciar el trabajo en segundo plano
try:
    pid = job_manager.start_job(
        job_name="compress",
        cmd_list=['bash', compress_script, output_dir, mount_dir, new_super, is_sparse],
        message=f"Reconstruyendo super.img en {new_super} (sparse={is_sparse})..."
    )
    print(json.dumps({
        "status": "success",
        "message": "Empaquetado iniciado con éxito",
        "pid": pid
    }))
except Exception as e:
    print(json.dumps({
        "status": "error",
        "message": f"No se pudo iniciar el proceso: {str(e)}"
    }))

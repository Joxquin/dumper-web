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
action = params.get('action')
output_dir = params.get('output_dir')
partition = params.get('partition')

script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not action:
    print(json.dumps({
        "status": "error",
        "message": "Falta el parámetro requerido: 'action'"
    }))
    sys.exit(0)

if action == 'install_erofs':
    install_script = os.path.join(script_dir, 'scripts', 'install_erofs.sh')
    cmd = ['bash', install_script]
    msg = "Instalando dependencias de EROFS (erofs-utils)..."
    job_name = "install_erofs"

elif action in ['extract', 'repack']:
    if not output_dir or not partition:
        print(json.dumps({
            "status": "error",
            "message": "Faltan parámetros requeridos: 'output_dir' y 'partition'"
        }))
        sys.exit(0)
        
    output_dir = os.path.abspath(output_dir)
    
    if action == 'extract':
        extract_script = os.path.join(script_dir, 'scripts', 'extract_partition.sh')
        cmd = ['bash', extract_script, output_dir, partition]
        msg = f"Extrayendo archivos de la partición '{partition}'..."
        job_name = "extract"
    else:
        repack_script = os.path.join(script_dir, 'scripts', 'repack_partition.sh')
        cmd = ['bash', repack_script, output_dir, partition]
        msg = f"Reempaquetando archivos a la imagen '{partition}.img' (EROFS)..."
        job_name = "repack"

else:
    print(json.dumps({
        "status": "error",
        "message": f"Acción desconocida: '{action}'. Use 'extract', 'repack' o 'install_erofs'"
    }))
    sys.exit(0)

# Iniciar el trabajo en segundo plano
try:
    pid = job_manager.start_job(
        job_name=job_name,
        cmd_list=cmd,
        message=msg
    )
    print(json.dumps({
        "status": "success",
        "message": f"Operación de {action} iniciada con éxito",
        "pid": pid
    }))
except Exception as e:
    print(json.dumps({
        "status": "error",
        "message": f"No se pudo iniciar el proceso: {str(e)}"
    }))

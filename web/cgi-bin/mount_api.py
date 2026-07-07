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
action = params.get('action', 'mount')
mount_dir = params.get('mount_dir')

if not mount_dir:
    print(json.dumps({
        "status": "error",
        "message": "Falta el parámetro requerido: 'mount_dir'"
    }))
    sys.exit(0)

mount_dir = os.path.abspath(mount_dir)
script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

partition = params.get('partition')

if action == 'mount':
    output_dir = params.get('output_dir')
    if not output_dir:
        print(json.dumps({
            "status": "error",
            "message": "Falta el parámetro requerido para montar: 'output_dir'"
        }))
        sys.exit(0)
    
    output_dir = os.path.abspath(output_dir)
    mount_script = os.path.join(script_dir, 'scripts', 'mount.sh')
    cmd = ['bash', mount_script, output_dir, mount_dir]
    if partition:
        cmd.append(partition)
        msg = f"Montando partición '{partition}' de {output_dir} en {mount_dir}/{partition}..."
    else:
        msg = f"Montando particiones de {output_dir} en {mount_dir}..."
    job_name = "mount"
    
elif action == 'unmount':
    unmount_script = os.path.join(script_dir, 'scripts', 'unmount.sh')
    cmd = ['bash', unmount_script, mount_dir]
    if partition:
        cmd.append(partition)
        msg = f"Desmontando partición '{partition}' de {mount_dir}..."
    else:
        msg = f"Desmontando particiones de {mount_dir}..."
    job_name = "unmount"
    
else:
    print(json.dumps({
        "status": "error",
        "message": f"Acción desconocida: '{action}'. Utilice 'mount' o 'unmount'"
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
        "message": f"Operación de {action} iniciada",
        "pid": pid
    }))
except Exception as e:
    print(json.dumps({
        "status": "error",
        "message": f"No se pudo iniciar el proceso: {str(e)}"
    }))

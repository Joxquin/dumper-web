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
                # En algunos servidores CGI, leer sys.stdin de esta manera funciona
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
super_img = params.get('super_img')
output_dir = params.get('output_dir')

if not super_img or not output_dir:
    print(json.dumps({
        "status": "error",
        "message": "Faltan parámetros requeridos: 'super_img' y 'output_dir'"
    }))
    sys.exit(0)

# Resolver rutas absolutas para evitar problemas con directorios relativos en el demonio
super_img = os.path.abspath(super_img)
output_dir = os.path.abspath(output_dir)

# Ruta absoluta al script dumper.sh
script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dumper_script = os.path.join(script_dir, 'scripts', 'dumper.sh')

# Iniciar el trabajo en segundo plano
try:
    pid = job_manager.start_job(
        job_name="dumper",
        cmd_list=['bash', dumper_script, super_img, output_dir],
        message=f"Desempaquetando super.img ({os.path.basename(super_img)}) en {output_dir}..."
    )
    print(json.dumps({
        "status": "success",
        "message": "Descompresión iniciada con éxito",
        "pid": pid
    }))
except Exception as e:
    print(json.dumps({
        "status": "error",
        "message": f"No se pudo iniciar el proceso: {str(e)}"
    }))

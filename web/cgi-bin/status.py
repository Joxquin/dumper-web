#!/usr/bin/env python3
import json
import subprocess
import sys
import os

# Asegurar que el directorio de scripts esté en el path si es necesario
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import job_manager

print("Content-Type: application/json")
print("Access-Control-Allow-Origin: *") # Habilitar CORS por si acaso
print("")

status_info = job_manager.get_status()

# Agregar información de diagnóstico del sistema
try:
    # Ruta absoluta al script de verificación
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scripts', 'packagesVerification.sh')
    diag_output = subprocess.check_output(['bash', script_path], text=True)
    status_info["diagnostics"] = json.loads(diag_output)
except Exception as e:
    status_info["diagnostics"] = {"error": f"Error ejecutando diagnóstico: {str(e)}"}

# Agregar información sobre particiones montadas bajo /proc/mounts
# Esto ayudará al frontend a saber qué particiones están montadas actualmente
mounted_partitions = []
try:
    with open('/proc/mounts', 'r') as f:
        for line in f:
            if 'loop' in line:
                parts = line.split()
                # Si el punto de montaje contiene mnt_system o es de nuestro interés
                if len(parts) >= 2:
                    mounted_partitions.append({
                        "device": parts[0],
                        "mount_point": parts[1],
                        "fs_type": parts[2],
                        "options": parts[3]
                    })
except Exception:
    pass

status_info["mounted_partitions"] = mounted_partitions

# Retornar el JSON
print(json.dumps(status_info, indent=2))

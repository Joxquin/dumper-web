import os
import sys
import json
import shlex
import subprocess

TMP_DIR = '/tmp/dumper_web'
PID_PATH = os.path.join(TMP_DIR, 'job.pid')
LOG_PATH = os.path.join(TMP_DIR, 'job.log')
EXIT_PATH = os.path.join(TMP_DIR, 'job.exit')
INFO_PATH = os.path.join(TMP_DIR, 'job.info')

def is_pid_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def start_job(job_name, cmd_list, message="Ejecutando..."):
    os.makedirs(TMP_DIR, exist_ok=True)
    
    # Limpiar archivos anteriores
    for p in [PID_PATH, LOG_PATH, EXIT_PATH, INFO_PATH]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass
                
    # Guardar información del trabajo
    info = {
        "job": job_name,
        "message": message
    }
    with open(INFO_PATH, 'w') as f:
        json.dump(info, f)
        
    # Construir comando wrapper de forma segura usando shlex.quote
    safe_cmd = ' '.join(shlex.quote(arg) for arg in cmd_list)
    # Escribimos el código de salida al archivo exit_path
    wrapper_script = f'{safe_cmd} > {shlex.quote(LOG_PATH)} 2>&1; echo $? > {shlex.quote(EXIT_PATH)}'
    
    # Lanzar el proceso en una nueva sesión para que persista
    p = subprocess.Popen(
        ['bash', '-c', wrapper_script],
        start_new_session=True
    )
    
    # Escribir el PID
    with open(PID_PATH, 'w') as f:
        f.write(str(p.pid))
        
    return p.pid

def get_status():
    status_info = {
        "job": "none",
        "status": "idle",
        "message": "Ningún trabajo activo",
        "log": "",
        "exit_code": None
    }
    
    if not os.path.exists(INFO_PATH):
        return status_info
        
    try:
        with open(INFO_PATH) as f:
            info = json.load(f)
            status_info["job"] = info.get("job", "unknown")
            status_info["message"] = info.get("message", "")
    except Exception:
        pass
        
    # Leer el log si existe
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH) as f:
                # Leer las últimas 100 líneas del log para no saturar
                lines = f.readlines()
                status_info["log"] = "".join(lines[-100:])
        except Exception as e:
            status_info["log"] = f"Error leyendo log: {str(e)}"
            
    # Determinar estado basándose en el PID y el archivo exit
    pid = None
    if os.path.exists(PID_PATH):
        try:
            with open(PID_PATH) as f:
                pid = int(f.read().strip())
        except Exception:
            pass
            
    if pid is not None:
        if is_pid_running(pid):
            status_info["status"] = "running"
        else:
            # Si el proceso terminó, verificamos el archivo exit
            if os.path.exists(EXIT_PATH):
                try:
                    with open(EXIT_PATH) as f:
                        exit_code = int(f.read().strip())
                        status_info["exit_code"] = exit_code
                        if exit_code == 0:
                            status_info["status"] = "success"
                        else:
                            status_info["status"] = "failed"
                except Exception:
                    status_info["status"] = "failed"
            else:
                # El proceso no está corriendo y no hay archivo de salida
                status_info["status"] = "failed"
                status_info["message"] += " (Terminado inesperadamente)"
                
    return status_info

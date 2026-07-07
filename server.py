#!/usr/bin/env python3
import os
import sys
import http.server

# Evitar que CGIHTTPRequestHandler cambie el UID al usuario 'nobody' cuando se ejecuta como root.
# De esta forma, el CGI conserva los privilegios de root para poder montar imágenes y evita errores de permisos.
http.server.nobody_uid = lambda: os.getuid()

PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

class CustomCGIHandler(http.server.CGIHTTPRequestHandler):
    # Enable running CGI scripts anywhere under /cgi-bin
    def is_cgi(self):
        # CGIHTTPRequestHandler uses self.cgi_directories to check if path is a CGI script
        # By default, it requires the script to be in a cgi-bin folder.
        return super().is_cgi()

def run():
    # Make sure we change directory to the web folder
    if not os.path.exists(WEB_DIR):
        os.makedirs(WEB_DIR, exist_ok=True)
        
    os.chdir(WEB_DIR)
    os.makedirs('cgi-bin', exist_ok=True)
    os.makedirs('css', exist_ok=True)
    
    server_address = ('', PORT)
    # We configure the CGI directories (must start with /)
    CustomCGIHandler.cgi_directories = ['/cgi-bin']
    
    httpd = http.server.HTTPServer(server_address, CustomCGIHandler)
    print(f"==========================================================")
    print(f" Servidor CGI Dumper-Web iniciado en http://localhost:{PORT}")
    print(f" Directorio raíz de la web: {WEB_DIR}")
    print(f"==========================================================")
    print(f"IMPORTANTE: Si vas a montar imágenes, ejecuta con sudo:")
    print(f"  sudo python3 server.py")
    print(f"==========================================================")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
        sys.exit(0)

if __name__ == '__main__':
    run()

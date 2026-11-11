"""Dashboard local del sitio multicategoría de Vexloi LLC.

Corre solo en tu PC (127.0.0.1): nadie más puede entrar.
Ejecutar desde esta carpeta:   python dashboard.py
(o doble clic en abrir_dashboard.bat). Se abre el navegador solo.
Solo usa la librería estándar de Python.
"""
import io
import json
import mimetypes
import subprocess
import sys
import threading
import webbrowser
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

import build_site

HERE = Path(__file__).resolve().parent
CONFIG = HERE / 'config.json'
PANEL = HERE / 'dashboard' / 'dashboard.html'
HOST, PORT = '127.0.0.1', 8770
ALLOWED_HOSTS = {f'127.0.0.1:{PORT}', f'localhost:{PORT}'}


def git(*args):
    r = subprocess.run(['git', *args], cwd=HERE, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def is_git_repo():
    try:
        return git('rev-parse', '--is-inside-work-tree')[0] == 0
    except FileNotFoundError:
        return False


def state():
    cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
    return {
        'config': cfg,
        'inventory': build_site.source_inventory(cfg),
        'sourceCategories': build_site.source_category_names(cfg),
        'git': is_git_repo(),
    }


def run_build():
    buf = io.StringIO()
    lines = []
    with redirect_stdout(buf):
        try:
            build_site.build(log=lines.append)
            ok = True
        except Exception as e:  # se muestra en el panel
            lines.append(f'ERROR: {e}')
            ok = False
    extra = buf.getvalue().strip()
    return ok, '\n'.join(([extra] if extra else []) + lines)


def publish(message):
    if not is_git_repo():
        return False, ('Esta carpeta todavía no está conectada a un repositorio de GitHub. '
                       'Cuando definamos el dominio la conectamos y este botón publicará.')
    out = []
    for args in (['add', '-A'], ['commit', '-m', message or 'Actualizar sitio desde el dashboard'], ['push']):
        code, text = git(*args)
        out.append(f'$ git {" ".join(args)}\n{text}')
        if code != 0 and not (args[0] == 'commit' and 'nothing to commit' in text):
            return False, '\n\n'.join(out)
    return True, '\n\n'.join(out)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _host_ok(self):
        if self.headers.get('Host') not in ALLOWED_HOSTS:
            self.send_error(403)
            return False
        return True

    def _json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path):
        if not path.is_file():
            self.send_error(404)
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self._host_ok():
            return
        path = unquote(urlparse(self.path).path)
        if path in ('/', '/dashboard'):
            return self._file(PANEL)
        if path == '/api/state':
            return self._json(200, state())
        if path == '/site' or path.startswith('/site/'):
            rel = path[len('/site/'):] or 'index.html'
            target = (HERE / rel).resolve()
            if target.is_dir():
                target = target / 'index.html'
            if HERE not in target.parents and target != HERE:
                return self.send_error(403)
            return self._file(target)
        self.send_error(404)

    def do_POST(self):
        if not self._host_ok():
            return
        # Un sitio externo no puede enviar este encabezado sin permiso: evita envíos desde otras páginas
        if self.headers.get('X-Vexloi-Dashboard') != '1':
            return self.send_error(403)
        length = int(self.headers.get('Content-Length') or 0)
        try:
            data = json.loads(self.rfile.read(length) or b'{}')
        except json.JSONDecodeError:
            return self._json(400, {'ok': False, 'log': 'JSON inválido'})
        path = urlparse(self.path).path
        if path == '/api/save':
            cfg = data.get('config')
            if not isinstance(cfg, dict) or 'site' not in cfg or 'categories' not in cfg:
                return self._json(400, {'ok': False, 'log': 'Configuración incompleta'})
            CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            if data.get('build'):
                ok, log = run_build()
                return self._json(200, {'ok': ok, 'log': 'Guardado.\n' + log})
            return self._json(200, {'ok': True, 'log': 'Guardado.'})
        if path == '/api/build':
            ok, log = run_build()
            return self._json(200, {'ok': ok, 'log': log})
        if path == '/api/publish':
            ok, log = run_build()
            if not ok:
                return self._json(200, {'ok': False, 'log': log})
            ok2, log2 = publish(data.get('message', ''))
            return self._json(200, {'ok': ok2, 'log': log + '\n\n' + log2})
        self.send_error(404)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f'http://{HOST}:{PORT}/'
    print(f'Dashboard en {url}  (cierra esta ventana o pulsa Ctrl+C para salir)')
    if '--no-browser' not in sys.argv:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

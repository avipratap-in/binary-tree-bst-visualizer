import http.server
import socketserver
from pathlib import Path

PORT = 8085
DIST_DIR = Path(__file__).resolve().parent.parent / "dist"

class SubpathHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def translate_path(self, path):
        prefix = "/binary-tree-bst-visualizer"
        if path.startswith(prefix):
            path = path[len(prefix):]
            if not path or path.startswith("?"):
                path = "/" + path
        return super().translate_path(path)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), SubpathHandler) as httpd:
        print(f"Serving dist at http://localhost:{PORT}/binary-tree-bst-visualizer/", flush=True)
        httpd.serve_forever()

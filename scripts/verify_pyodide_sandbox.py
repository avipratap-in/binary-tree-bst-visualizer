#!/usr/bin/env python3
"""Pyodide sandbox verification script.

Simulates the Pyodide in-browser runtime by copying ONLY the files listed in
dist/py/manifest.json into an isolated temporary folder, completely blocking
Flask from sys.modules, and executing core API handle() routes.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def verify_sandbox(project_root: Path | None = None) -> None:
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent

    dist_py = project_root / "dist" / "py"
    manifest_path = dist_py / "manifest.json"

    if not manifest_path.exists():
        print(f"FATAL: Manifest file not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    files = manifest.get("files", [])
    if not files:
        print("FATAL: Manifest contains no files!", file=sys.stderr)
        sys.exit(1)

    temp_dir = Path(tempfile.mkdtemp(prefix="pyodide_sandbox_"))
    try:
        sandbox_pkg = temp_dir / "bt_visualizer"
        sandbox_pkg.mkdir(parents=True, exist_ok=True)

        for rel in files:
            src = dist_py / rel
            dest = sandbox_pkg / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

        test_code = f"""
import sys, json

# Ensure ONLY the sandbox directory is searched for visualizer code (keep stdlib)
stdlib_paths = [p for p in sys.path if "DSAP_Capstone" not in p and p != ""]
sys.path = [{repr(str(temp_dir))}] + stdlib_paths

# Strictly block Flask and related server frameworks
sys.modules["flask"] = None
sys.modules["flask_cors"] = None

# Import handlers in pure browser mode
import bt_visualizer.api.handlers as handlers

# 1. Probe health
res = json.loads(handlers.handle("api/health", "{{}}"))
assert res["status"] == 200, f"Health route failed: {{res}}"
assert res["body"]["service"] == "bt_visualizer"

# 2. Random numeric tree
res = json.loads(handlers.handle("api/random", json.dumps({{"type": "binary", "n": 6, "labels": "numbers"}})))
assert res["status"] == 200, f"Random numeric failed: {{res}}"
assert "numeric" in res["body"]["steps"][-1]["message"]

# 3. Random alphabetic tree
res = json.loads(handlers.handle("api/random", json.dumps({{"type": "binary", "n": 6, "labels": "letters"}})))
assert res["status"] == 200, f"Random alphabetic failed: {{res}}"
assert "alphabetic" in res["body"]["steps"][-1]["message"]

# 4. Traversal
tree = res["body"]["steps"][-1]["tree"]
res = json.loads(handlers.handle("api/traverse", json.dumps({{"tree": tree, "order": "in"}})))
assert res["status"] == 200, f"Traversal failed: {{res}}"

# 5. Build from traversal
build_req = {{
    "mode": "in+pre",
    "seq1": ["D", "B", "E", "A", "C"],
    "seq2": ["A", "B", "D", "E", "C"]
}}
res = json.loads(handlers.handle("api/build", json.dumps(build_req)))
assert res["status"] == 200, f"Build from traversal failed: {{res}}"

print(f"Verified {len(files)} files: all Pyodide sandbox routes succeeded without Flask.")
"""

        res = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            print(f"Pyodide sandbox simulation FAILED!\nStderr:\n{res.stderr}\nStdout:\n{res.stdout}", file=sys.stderr)
            sys.exit(1)

        print(res.stdout.strip())
        print("Pyodide sandbox verification passed successfully.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    verify_sandbox()

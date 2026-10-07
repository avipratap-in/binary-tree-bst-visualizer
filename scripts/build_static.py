#!/usr/bin/env python3
"""Build script for static GitHub Pages deployment.

Produces a deterministic, standalone dist/ directory containing:
- All static assets from bt_visualizer/static/
- Python source modules packaged into dist/py/
- Deterministic dist/py/manifest.json
- Empty dist/.nojekyll file
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Optional


def build_static(project_root: Optional[Path] = None) -> Path:
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent

    static_src = project_root / "bt_visualizer" / "static"
    core_src = project_root / "bt_visualizer" / "core"
    recorder_src = project_root / "bt_visualizer" / "recorder"
    api_handlers_src = project_root / "bt_visualizer" / "api" / "handlers.py"
    api_init_src = project_root / "bt_visualizer" / "api" / "__init__.py"
    pkg_init_src = project_root / "bt_visualizer" / "__init__.py"

    dist_dir = project_root / "dist"

    print(f"Building static distribution in: {dist_dir}")

    # 1. Clean previous dist/ directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    # 2. Copy static folder to dist/
    def ignore_pycache(dir_path: str, names: list[str]) -> set[str]:
        return {name for name in names if name == "__pycache__" or name.endswith((".pyc", ".pyo"))}

    for item in static_src.iterdir():
        if item.name == "__pycache__" or item.name == "py":
            continue
        dest = dist_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=ignore_pycache)
        else:
            shutil.copy2(item, dest)

    print("Copied static web assets.")

    # 3. Create dist/py and copy python modules
    dist_py = dist_dir / "py"
    dist_py.mkdir(parents=True, exist_ok=True)

    # Package root __init__.py
    if pkg_init_src.exists():
        shutil.copy2(pkg_init_src, dist_py / "__init__.py")

    # Package core/
    shutil.copytree(core_src, dist_py / "core", ignore=ignore_pycache)

    # Package recorder/
    shutil.copytree(recorder_src, dist_py / "recorder", ignore=ignore_pycache)

    # Package api/
    api_dist = dist_py / "api"
    api_dist.mkdir(parents=True, exist_ok=True)
    if api_init_src.exists():
        shutil.copy2(api_init_src, api_dist / "__init__.py")
    shutil.copy2(api_handlers_src, api_dist / "handlers.py")

    print("Copied Python source modules to dist/py/.")

    # 4. Generate deterministic py/manifest.json
    manifest_files: list[str] = []
    for file_path in dist_py.rglob("*.py"):
        rel = file_path.relative_to(dist_py).as_posix()
        manifest_files.append(rel)

    manifest_files.sort()  # Deterministic ordering

    manifest_data = {
        "version": "1.0.0",
        "files": manifest_files,
    }

    manifest_json_path = dist_py / "manifest.json"
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, sort_keys=True)
        f.write("\n")

    print(f"Generated manifest with {len(manifest_files)} Python files.")

    # 5. Create empty .nojekyll in dist/
    nojekyll_path = dist_dir / ".nojekyll"
    nojekyll_path.write_text("", encoding="utf-8")
    print("Created dist/.nojekyll.")

    print(f"\nStatic build complete! Output ready at: {dist_dir}")
    return dist_dir


if __name__ == "__main__":
    build_static()

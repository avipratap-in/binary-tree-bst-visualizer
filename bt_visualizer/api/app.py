"""Flask application serving API endpoints and static visualizer assets.

Stateless REST API receiving current tree state as JSON and delegating
to core handlers in api/handlers.py.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
from flask import Flask, jsonify, request, send_from_directory

from bt_visualizer.api.handlers import (
    deserialize_tree,
    handle_bst_create,
    handle_bst_operation,
    handle_build,
    handle_examples,
    handle_health,
    handle_properties,
    handle_random,
    handle_random_build,
    handle_traverse,
    handle_validate_build,
)

STATIC_FOLDER = Path(__file__).resolve().parent.parent / "static"


def create_app() -> Flask:
    """Application factory for the Binary Tree Visualizer Flask app."""
    app = Flask(
        __name__,
        static_folder=str(STATIC_FOLDER),
        static_url_path="",
    )

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint confirming API service status."""
        body, status = handle_health()
        return jsonify(body), status

    @app.route("/", methods=["GET"])
    def index():
        """Serve the primary visualization single-page application."""
        return send_from_directory(str(STATIC_FOLDER), "index.html")

    @app.route("/api/bst/create", methods=["POST"])
    def bst_create():
        """POST /api/bst/create {values: [..]}"""
        payload = request.get_json(silent=True)
        body, status = handle_bst_create(payload)
        return jsonify(body), status

    @app.route("/api/bst/operation", methods=["POST"])
    def bst_operation():
        """POST /api/bst/operation {tree: <tree>, op: "insert|remove|search|min|max|pred|succ|rank|select", value: n}"""
        payload = request.get_json(silent=True)
        body, status = handle_bst_operation(payload)
        return jsonify(body), status

    @app.route("/api/traverse", methods=["POST"])
    def traverse():
        """POST /api/traverse {tree: <tree>, order: "pre|in|post|level"}"""
        payload = request.get_json(silent=True)
        body, status = handle_traverse(payload)
        return jsonify(body), status

    @app.route("/api/properties", methods=["POST"])
    def tree_properties():
        """POST /api/properties {tree: <tree>} -> returns calculated properties."""
        payload = request.get_json(silent=True)
        body, status = handle_properties(payload)
        return jsonify(body), status

    @app.route("/api/build", methods=["POST"])
    def build_tree():
        """POST /api/build {mode: "in+pre|in+post|in+level|pre+post|bst-pre|bst-post", seq1: [..]|"..", seq2: [..]|".."}"""
        payload = request.get_json(silent=True)
        body, status = handle_build(payload)
        return jsonify(body), status

    @app.route("/api/build/validate", methods=["POST"])
    def validate_build():
        """POST /api/build/validate {mode: "..", seq1: "..", seq2: ".."} -> diagnostics & suggestions."""
        payload = request.get_json(silent=True)
        body, status = handle_validate_build(payload)
        return jsonify(body), status

    @app.route("/api/build/random", methods=["GET"])
    def random_build_pair():
        """GET /api/build/random?mode=..&n=..&labels=letters|numbers -> valid sequences."""
        params = dict(request.args)
        body, status = handle_random_build(params)
        return jsonify(body), status

    @app.route("/api/random", methods=["GET"])
    def random_tree():
        """GET /api/random?type=bst|binary&n=..&labels=numbers|letters"""
        params = dict(request.args)
        body, status = handle_random(params)
        return jsonify(body), status

    @app.route("/api/examples", methods=["GET"])
    def examples():
        """GET /api/examples -> Pre-packaged trees (balanced, skewed, with duplicates, full)."""
        body, status = handle_examples()
        return jsonify(body), status

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

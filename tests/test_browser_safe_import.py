"""Test that bt_visualizer.api.handlers and core DSA can be imported and executed

without Flask or any non-standard-library dependencies installed or available.
"""
from __future__ import annotations

import json
import subprocess
import sys


def test_import_and_handle_without_flask():
    """Verify handlers.handle works in an isolated environment where Flask is blocked."""
    code = """
import json
import sys

# Explicitly block Flask and Flask extensions
sys.modules["flask"] = None
sys.modules["flask_cors"] = None

# Import handlers without triggering Flask
import bt_visualizer.api.handlers as handlers

# 1. Test health check
res1_raw = handlers.handle("api/health", "{}")
res1 = json.loads(res1_raw)
assert res1["status"] == 200, f"Health check failed: {res1}"
assert res1["body"]["service"] == "bt_visualizer"

# 2. Test random numeric binary tree
res2_raw = handlers.handle("api/random", json.dumps({"type": "binary", "n": 5, "labels": "numbers"}))
res2 = json.loads(res2_raw)
assert res2["status"] == 200, f"Random numbers failed: {res2}"
assert "numeric" in res2["body"]["steps"][-1]["message"]

# 3. Test random alphabetic binary tree
res3_raw = handlers.handle("api/random", json.dumps({"type": "binary", "n": 6, "labels": "letters"}))
res3 = json.loads(res3_raw)
assert res3["status"] == 200, f"Random letters failed: {res3}"
assert "alphabetic" in res3["body"]["steps"][-1]["message"]

# 4. Test traversal
tree_dict = res3["body"]["steps"][-1]["tree"]
res4_raw = handlers.handle("api/traverse", json.dumps({"tree": tree_dict, "order": "in"}))
res4 = json.loads(res4_raw)
assert res4["status"] == 200, f"Traverse failed: {res4}"

# 5. Test build from traversal
build_payload = {
    "mode": "in+pre",
    "seq1": ["D", "B", "E", "A", "C"],
    "seq2": ["A", "B", "D", "E", "C"]
}
res5_raw = handlers.handle("api/build", json.dumps(build_payload))
res5 = json.loads(res5_raw)
assert res5["status"] == 200, f"Build failed: {res5}"
print("All isolated browser-safe handler tests passed successfully.")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Isolated test failed with stderr:\n{result.stderr}\nstdout:\n{result.stdout}"

/**
 * Pyodide Web Worker for in-browser client-side Python execution.
 * Pinned to stable Pyodide v0.27.3 from jsDelivr.
 */

const PYODIDE_VERSION = 'v0.27.3';
const PYODIDE_CDN_BASE = `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/`;
const PYODIDE_SCRIPT_URL = `${PYODIDE_CDN_BASE}pyodide.js`;

let pyodide = null;

async function fetchWithCache(url) {
  if (typeof caches !== 'undefined') {
    try {
      const cache = await caches.open('bt-visualizer-cache-v1');
      const cached = await cache.match(url);
      if (cached) {
        return cached;
      }
      const res = await fetch(url);
      if (res.ok) {
        cache.put(url, res.clone());
      }
      return res;
    } catch (e) {
      // Fallback to direct network fetch
    }
  }
  return fetch(url);
}

function ensureDir(fs, filePath) {
  const parts = filePath.split('/').filter(Boolean);
  let current = '';
  // Traverse up to directory portion
  for (let i = 0; i < parts.length - 1; i++) {
    current += '/' + parts[i];
    try {
      fs.mkdir(current);
    } catch (e) {
      // Ignore if directory already exists
    }
  }
}

async function initPyodideWorker(baseUrl = '') {
  postMessage({ type: 'progress', message: 'Loading Python engine from CDN...', percent: 15 });

  // Import Pyodide script
  importScripts(PYODIDE_SCRIPT_URL);

  postMessage({ type: 'progress', message: 'Initializing Pyodide runtime...', percent: 35 });
  pyodide = await loadPyodide({
    indexURL: PYODIDE_CDN_BASE,
  });

  postMessage({ type: 'progress', message: 'Fetching Python module manifest...', percent: 55 });

  const manifestUrl = (baseUrl ? baseUrl.replace(/\/+$/, '') + '/' : '') + 'py/manifest.json';
  const manifestRes = await fetchWithCache(manifestUrl);
  if (!manifestRes.ok) {
    throw new Error(`Failed to load manifest from ${manifestUrl} (HTTP ${manifestRes.status})`);
  }
  const manifest = await manifestRes.json();
  const files = manifest.files || [];

  postMessage({ type: 'progress', message: 'Mounting Python files into virtual environment...', percent: 70 });

  const totalFiles = files.length;
  for (let i = 0; i < totalFiles; i++) {
    const relPath = files[i];
    const fileUrl = (baseUrl ? baseUrl.replace(/\/+$/, '') + '/' : '') + 'py/' + relPath;
    const fileRes = await fetchWithCache(fileUrl);
    if (!fileRes.ok) {
      throw new Error(`Failed to fetch Python module ${relPath} (HTTP ${fileRes.status})`);
    }
    const code = await fileRes.text();

    // Write to /home/pyodide/<relPath>
    const dest1 = '/home/pyodide/' + relPath;
    ensureDir(pyodide.FS, dest1);
    pyodide.FS.writeFile(dest1, code);

    // Also write to /home/pyodide/bt_visualizer/<relPath>
    const dest2 = '/home/pyodide/bt_visualizer/' + relPath;
    ensureDir(pyodide.FS, dest2);
    pyodide.FS.writeFile(dest2, code);

    const pct = 70 + Math.floor(((i + 1) / totalFiles) * 20);
    postMessage({ type: 'progress', message: `Loading ${relPath}...`, percent: pct });
  }

  // Ensure __init__.py exists for bt_visualizer package
  try {
    pyodide.FS.writeFile('/home/pyodide/bt_visualizer/__init__.py', '"""bt_visualizer package"""\n');
  } catch (e) {
    // Ignore
  }

  postMessage({ type: 'progress', message: 'Importing visualizer engine...', percent: 95 });

  // Initialize sys.path and import handlers
  await pyodide.runPythonAsync(`
import sys
if '/home/pyodide' not in sys.path:
    sys.path.insert(0, '/home/pyodide')
if '/home/pyodide/bt_visualizer' not in sys.path:
    sys.path.insert(0, '/home/pyodide/bt_visualizer')

import api.handlers
`);

  postMessage({ type: 'progress', message: 'Python engine ready!', percent: 100 });
}

self.onmessage = async (e) => {
  const data = e.data;
  if (!data) return;

  if (data.type === 'init') {
    try {
      await initPyodideWorker(data.baseUrl || '');
      postMessage({ type: 'ready' });
    } catch (err) {
      postMessage({
        type: 'init_error',
        error: err.message || String(err),
      });
    }
  } else if (data.type === 'call') {
    const { id, route, payload } = data;
    if (!pyodide) {
      postMessage({ id, type: 'error', error: 'Pyodide is not initialized.' });
      return;
    }

    try {
      const payloadJson = payload !== undefined && payload !== null ? JSON.stringify(payload) : '{}';
      pyodide.globals.set('__req_route', route);
      pyodide.globals.set('__req_payload', payloadJson);

      const resultJson = pyodide.runPython('api.handlers.handle(__req_route, __req_payload)');
      const res = JSON.parse(resultJson);
      postMessage({
        id,
        type: 'response',
        status: res.status,
        body: res.body,
      });
    } catch (err) {
      postMessage({
        id,
        type: 'error',
        error: err.message || String(err),
      });
    }
  }
};

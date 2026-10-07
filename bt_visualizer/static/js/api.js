/**
 * Unified API Client supporting both Flask (local server) and Pyodide (client-side Web Worker).
 */

const Api = {
  mode: null, // 'flask' | 'pyodide'
  worker: null,
  isReady: false,
  readyPromise: null,
  requestId: 0,
  pendingRequests: new Map(),

  async init() {
    if (this.readyPromise) return this.readyPromise;

    this.readyPromise = (async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const forcedMode = urlParams.get('mode');

      if (forcedMode === 'flask') {
        this.mode = 'flask';
        this.isReady = true;
        this._updateUiModeBadge('Flask (Server)');
        return;
      }

      if (forcedMode === 'pyodide') {
        await this._initPyodide();
        return;
      }

      // Auto-detect: probe relative api/health
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 1200);
        const res = await fetch('api/health', { method: 'GET', signal: controller.signal });
        clearTimeout(timeoutId);
        if (res.ok) {
          const data = await res.json();
          if (data && data.service === 'bt_visualizer') {
            this.mode = 'flask';
            this.isReady = true;
            this._updateUiModeBadge('Flask (Server)');
            return;
          }
        }
      } catch (e) {
        // Fallback to Pyodide
      }

      // If Flask is not responding, switch to Pyodide
      await this._initPyodide();
    })();

    return this.readyPromise;
  },

  _updateUiModeBadge(label) {
    const badge = document.getElementById('engineBadge');
    if (badge) {
      badge.textContent = label;
      badge.title = `Execution Engine: ${label}`;
    }
  },

  _showLoading(message, percent = null) {
    const overlay = document.getElementById('pyodideLoadingOverlay');
    const text = document.getElementById('pyodideLoadingText');
    const bar = document.getElementById('pyodideProgressBarFill');
    if (overlay) overlay.style.display = 'flex';
    if (text) text.textContent = message;
    if (bar && percent !== null) bar.style.width = `${percent}%`;

    // Disable all action buttons
    document.querySelectorAll('.form-btn, .btn-utility').forEach(btn => {
      btn.dataset.engineDisabled = 'true';
      btn.disabled = true;
    });
  },

  _hideLoading() {
    const overlay = document.getElementById('pyodideLoadingOverlay');
    if (overlay) overlay.style.display = 'none';

    // Re-enable action buttons
    document.querySelectorAll('.form-btn, .btn-utility').forEach(btn => {
      if (btn.dataset.engineDisabled === 'true') {
        delete btn.dataset.engineDisabled;
        btn.disabled = false;
      }
    });

    // Update undo button state if UI exists
    if (window.UI && typeof window.UI.updateUndoButton === 'function') {
      window.UI.updateUndoButton();
    }
  },

  _showError(message) {
    const text = document.getElementById('pyodideLoadingText');
    const bar = document.getElementById('pyodideProgressBarFill');
    const errorBox = document.getElementById('pyodideErrorContainer');
    const errorText = document.getElementById('pyodideErrorText');
    if (text) text.textContent = 'Failed to load Python Engine';
    if (bar) bar.style.width = '0%';
    if (errorBox) errorBox.style.display = 'block';
    if (errorText) {
      errorText.textContent = `${message}. Please check your internet connection and click Retry.`;
    }
  },

  getBaseUrl() {
    let base = document.baseURI || window.location.href;
    base = base.split('#')[0].split('?')[0];
    if (!base.endsWith('/')) {
      if (base.endsWith('.html') || base.endsWith('.htm')) {
        base = base.substring(0, base.lastIndexOf('/') + 1);
      } else {
        base = base + '/';
      }
    }
    return base;
  },

  async _initPyodide() {
    this.mode = 'pyodide';
    this._updateUiModeBadge('Pyodide (In-Browser)');
    this._showLoading('Loading Python engine...', 10);

    return new Promise((resolve, reject) => {
      try {
        const baseUrl = this.getBaseUrl();
        const workerUrl = new URL('js/pyodide-worker.js', baseUrl).href;
        this.worker = new Worker(workerUrl);

        this.worker.onmessage = (e) => {
          const data = e.data;
          if (!data) return;

          if (data.type === 'progress') {
            this._showLoading(data.message, data.percent);
          } else if (data.type === 'ready') {
            this.isReady = true;
            this._hideLoading();
            resolve();
          } else if (data.type === 'init_error') {
            this._showError(data.error);
            reject(new Error(data.error));
          } else if (data.type === 'response') {
            const req = this.pendingRequests.get(data.id);
            if (req) {
              this.pendingRequests.delete(data.id);
              if (data.status >= 200 && data.status < 300) {
                req.resolve(data.body);
              } else {
                const msg = data.body?.message || data.body?.error || `Error ${data.status}`;
                req.reject(new Error(msg));
              }
            }
          } else if (data.type === 'error') {
            const req = this.pendingRequests.get(data.id);
            if (req) {
              this.pendingRequests.delete(data.id);
              req.reject(new Error(data.error));
            }
          }
        };

        this.worker.onerror = (err) => {
          this._showError(err.message || 'Worker initialization failed');
          reject(err);
        };

        const buildId = '1.0.1-' + Date.now();
        this.worker.postMessage({ type: 'init', baseUrl, version: buildId });
      } catch (err) {
        this._showError(err.message || 'Worker creation failed');
        reject(err);
      }
    });
  },

  async retryPyodide() {
    const errorBox = document.getElementById('pyodideErrorContainer');
    if (errorBox) errorBox.style.display = 'none';
    this.readyPromise = null;
    this.isReady = false;
    return this.init();
  },

  async callApi(route, payload = null) {
    if (!this.isReady) {
      await this.init();
    }

    const cleanRoute = route.replace(/^\/+/, '');

    if (this.mode === 'flask') {
      return this._callFlask(cleanRoute, payload);
    } else {
      return this._callPyodide(cleanRoute, payload);
    }
  },

  async _callFlask(route, payload) {
    // Relative URL - NO leading slash!
    const isGet = ['api/health', 'api/examples'].includes(route) ||
                  route.startsWith('api/random') ||
                  route.startsWith('api/build/random');

    let url = route;
    let options = {};

    if (isGet) {
      if (payload && typeof payload === 'object' && Object.keys(payload).length > 0) {
        const params = new URLSearchParams();
        for (const [k, v] of Object.entries(payload)) {
          if (v !== null && v !== undefined) {
            params.append(k, String(v));
          }
        }
        const qs = params.toString();
        if (qs) {
          url += (url.includes('?') ? '&' : '?') + qs;
        }
      }
      options = { method: 'GET' };
    } else {
      options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload || {}),
      };
    }

    const response = await fetch(url, options);
    const resJson = await response.json();
    if (!response.ok) {
      throw new Error(resJson.message || resJson.error || `HTTP ${response.status}: Error occurred.`);
    }
    return resJson;
  },

  _callPyodide(route, payload) {
    return new Promise((resolve, reject) => {
      const id = ++this.requestId;
      this.pendingRequests.set(id, { resolve, reject });
      this.worker.postMessage({
        id,
        type: 'call',
        route,
        payload,
      });
    });
  },

  // High-level API convenience wrappers
  async checkHealth() {
    return this.callApi('api/health');
  },

  async createBST(values) {
    return this.callApi('api/bst/create', { values });
  },

  async bstOperation(tree, op, value = null) {
    const payload = { tree, op };
    if (value !== null && value !== undefined) {
      payload.value = value;
    }
    return this.callApi('api/bst/operation', payload);
  },

  async traverse(tree, order) {
    return this.callApi('api/traverse', { tree, order });
  },

  async build(mode, seq1, seq2 = null) {
    const payload = { mode, seq1 };
    if (seq2 !== null && seq2 !== undefined) {
      payload.seq2 = seq2;
    }
    return this.callApi('api/build', payload);
  },

  async validateBuild(mode, seq1, seq2 = null) {
    return this.callApi('api/build/validate', { mode, seq1, seq2 });
  },

  async getRandomBuild(mode = 'in+pre', n = 7, labels = 'letters') {
    return this.callApi('api/build/random', { mode, n, labels });
  },

  async getRandom(type = 'bst', n = 7, labels = 'numbers') {
    return this.callApi('api/random', { type, n, labels });
  },

  async getExamples() {
    return this.callApi('api/examples');
  },

  async getProperties(tree) {
    return this.callApi('api/properties', { tree });
  }
};

window.Api = Api;
window.callApi = (route, payload) => Api.callApi(route, payload);

if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => {
    Api.init().catch(err => console.warn('Api init:', err));
  });
}

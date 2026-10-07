# Binary Tree & BST Visualizer

[![Deploy to GitHub Pages](https://github.com/avipratap-in/binary-tree-bst-visualizer/actions/workflows/deploy.yml/badge.svg)](https://github.com/avipratap-in/binary-tree-bst-visualizer/actions/workflows/deploy.yml)
[![Live Demo](https://img.shields.io/badge/demo-online-green.svg)](https://avipratap-in.github.io/binary-tree-bst-visualizer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

An interactive, step-by-step educational visualizer for Binary Trees and Binary Search Trees (BST), inspired by the VisuAlgo design aesthetic. Built for the Data Structures & Algorithms using Python (DSAP) Capstone project, it demonstrates pure Python standard-library algorithmic implementations running both on a local Flask development server and completely serverless in modern web browsers via Pyodide Web Workers on GitHub Pages.

🔗 **Live Demo:** [https://avipratap-in.github.io/binary-tree-bst-visualizer/](https://avipratap-in.github.io/binary-tree-bst-visualizer/)

---

## 🌟 Features

- **Binary Tree Traversals:**
  - Preorder, Inorder, and Postorder implemented both recursively and iteratively using an explicit stack.
  - Level-Order traversal implemented with a FIFO queue (`collections.deque`).
  - Live visited sequence badges highlighting each visited node in real time.
- **Tree Structural Properties:**
  - Dynamic computation of Size, Height, Leaf Count, and Internal Node Count.
  - Analyzers for Full, Complete, Perfect, and Height-Balanced (AVL criterion) binary trees.
- **Build from Traversal (Reconstruction):**
  - Reconstruct binary trees from Inorder + Preorder, Inorder + Postorder, and Inorder + Level-Order.
  - Preorder + Postorder reconstruction with ambiguity detection for non-full binary trees.
  - Single-sequence BST construction from Preorder or Postorder.
  - Live validation engine with smart suggestions and error diagnostics.
- **Comprehensive BST Operations:**
  - Search, Insertion, and Deletion covering all structural cases (Leaf, One child, and Two children via Inorder Successor).
  - Frequency-based duplicate handling preserving strict BST ordering ($O(\log n)$ average height).
  - Extremes: Minimum and Maximum.
  - Predecessor and Successor.
  - Order Statistics: Rank and Select ($k$-th smallest element).
- **Random Generation:**
  - Generate random BSTs and general binary trees with numeric (1–99) or alphabetic (A–Z) labels.
- **Interactive Step-by-Step Player:**
  - Play, Pause, Step Backward, Step Forward, Skip to Start, Skip to End, and Replay.
  - Variable playback speed ($0.25\times$ to $4.0\times$) and interactive scrubber slider.
  - Keyboard shortcuts (<kbd>Space</kbd>, <kbd>&larr;</kbd>, <kbd>&rarr;</kbd>, <kbd>Ctrl</kbd>+<kbd>Z</kbd>).
- **Pseudocode Panel & Status Messages:**
  - VisuAlgo-styled signature yellow status box explaining algorithmic steps in plain English.
  - Signature pink pseudocode panel with real-time active line highlighting.
- **Export & Share:**
  - Export tree state to JSON and high-resolution PNG image.
  - Copy shareable URL with tree state encoded in URL hash and query string.
- **Dual Themes & Responsive Layout:**
  - Modern sleek dark theme (default) and crisp light theme with instant toggle.
  - Interactive SVG canvas with smooth pan, zoom in, zoom out, and reset.

---

## 📸 Screenshots

<!-- TODO: Capture 2-3 live production screenshots and place in docs/screenshots/ -->
- **Visualizer Overview:** Full UI with BST operations and step playback.  
  *(Screenshot placeholder: `docs/screenshots/overview.png` - TODO)*
- **Step-by-Step Traversal:** Level-order and DFS visited animation.  
  *(Screenshot placeholder: `docs/screenshots/traversal_step.png` - TODO)*
- **Reconstruction with Diagnostics:** Live validation suggestions for traversal pairs.  
  *(Screenshot placeholder: `docs/screenshots/build_reconstruction.png` - TODO)*

---

## 📐 Architecture Overview

The visualizer separates algorithm logic, timeline recording, API transport, and frontend rendering into distinct layers:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Static Frontend (Web UI)                        │
│      index.html • CSS Design Tokens • SVG Renderer • Animation Player   │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
                       callApi(route, payload)
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          │                                                   │
  [Flask Transport]                                   [Pyodide Transport]
  fetch() relative HTTP REST                          Web Worker (pyodide-worker.js)
  Local dev server                                    In-browser WASM runtime
          │                                                   │
          └─────────────────────────┬─────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Unified API Dispatcher (handlers.py)                 │
│              handle(route: str, payload_json: str) -> str              │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┘
│                       Step Recorder (recorder/)                        │
│       Timeline generation capturing tree states, highlights & pseudo   │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┘
│                     Pure Python Core (core/)                           │
│        BinaryTree • BinarySearchTree • Traversals • Builders • Props   │
│                 (100% Python Standard Library, Zero Deps)              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Running Locally

### Option 1: Local Flask Server (Development Mode)
1. **Clone the repository:**
   ```bash
   git clone https://github.com/avipratap-in/binary-tree-bst-visualizer.git
   cd binary-tree-bst-visualizer
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask server:**
   ```bash
   python -m bt_visualizer.api.app
   ```
   Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

---

### Option 2: Serverless Static Build (Pyodide Mode)
You can test the exact static bundle deployed to GitHub Pages without running Flask:

1. **Build the static distribution:**
   ```bash
   python scripts/build_static.py
   ```
   This generates the self-contained `dist/` directory containing all web assets, the `py/` directory with packaged Python modules, `py/manifest.json`, and `.nojekyll`.

2. **Serve `dist/` with Python's built-in HTTP server:**
   ```bash
   python -m http.server 8000 --directory dist
   ```
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser. The app will automatically detect static hosting and initialize Pyodide in the background.

---

## 🧪 Running Tests

Run the full automated test suite using `pytest`:
```bash
pytest -v
```
All 156 unit and API integration tests cover:
- Binary tree operations and frequency-based duplicate handling.
- Recursive and iterative tree traversals.
- Tree reconstruction algorithms and ambiguity edge cases.
- Tree property calculators.
- Step timeline recorders.
- Plain Python `handle()` dispatcher and Flask endpoints.

---

## 🌐 GitHub Pages Deployment

Deployment is fully automated with GitHub Actions:
1. Every push to the `main` branch triggers `.github/workflows/deploy.yml`.
2. The workflow checks out the code, sets up Python 3.11, and installs `requirements.txt`.
3. Runs all `pytest` unit tests (the deployment halts immediately if any test fails).
4. Executes `python scripts/build_static.py` to produce `dist/`.
5. Uploads `dist/` as a Pages artifact and deploys it via `actions/deploy-pages`.

---

## 📊 Algorithm Complexity Reference

| Algorithm / Operation | Average Time | Worst-Case Time | Space Complexity | Description |
| :--- | :--- | :--- | :--- | :--- |
| **BST Search** | $O(\log n)$ | $O(n)$ | $O(1)$ | Standard binary search tree lookup |
| **BST Insert** | $O(\log n)$ | $O(n)$ | $O(h)$ | Frequency counter increment on duplicate |
| **BST Remove** | $O(\log n)$ | $O(n)$ | $O(h)$ | Leaf, 1-child, or 2-children via Inorder Successor |
| **BST Min / Max** | $O(\log n)$ | $O(n)$ | $O(1)$ | Extremes by traversing leftmost / rightmost spine |
| **BST Pred / Succ** | $O(\log n)$ | $O(n)$ | $O(1)$ | Inorder predecessor and successor search |
| **BST Rank / Select** | $O(\log n)$ | $O(n)$ | $O(h)$ | Order statistics using subtree sizes |
| **BST From Array** | $O(n \log n)$ | $O(n^2)$ | $O(n)$ | Sequential insertion of array elements |
| **DFS Traversals** | $O(n)$ | $O(n)$ | $O(h)$ | Preorder, Inorder, Postorder (recursive & iterative) |
| **BFS Level-Order** | $O(n)$ | $O(n)$ | $O(w) \le O(n)$ | Breadth-first search using FIFO queue |
| **Property Analyzers** | $O(n)$ | $O(n)$ | $O(h)$ | Leaf/internal count, height, Full, Complete, AVL |
| **Build: In + Pre** | $O(n)$ | $O(n)$ | $O(n)$ | Unique reconstruction using Inorder & Preorder |
| **Build: In + Post** | $O(n)$ | $O(n)$ | $O(n)$ | Unique reconstruction using Inorder & Postorder |
| **Build: In + Level** | $O(n^2)$ | $O(n^2)$ | $O(n)$ | Reconstruction using Inorder & Level-Order |
| **Build: Pre + Post** | $O(n)$ | $O(n)$ | $O(n)$ | Valid for Full Binary Trees; ambiguity checks |
| **Build: BST Pre/Post**| $O(n)$ | $O(n)$ | $O(n)$ | Range-bounded BST linear reconstruction |

*For in-depth mathematical formulations and pseudocode walkthroughs, refer to [docs/ALGORITHMS.md](docs/ALGORITHMS.md).*

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| <kbd>Space</kbd> | Toggle Play / Pause |
| <kbd>&larr;</kbd> (Left Arrow) | Step Backward |
| <kbd>&rarr;</kbd> (Right Arrow) | Step Forward |
| <kbd>Home</kbd> | Skip to Beginning |
| <kbd>End</kbd> | Skip to End |
| <kbd>Ctrl</kbd> + <kbd>Z</kbd> | Undo Last Operation |

---

## 📄 License & Typography Notices

- **Source Code:** Released under the [MIT License](LICENSE).
- **Rouge Script Font:** Created by Brenda Gallo, self-hosted in `static/fonts/` for offline capstone evaluation, licensed under the [SIL Open Font License (OFL)](http://scripts.sil.org/OFL).

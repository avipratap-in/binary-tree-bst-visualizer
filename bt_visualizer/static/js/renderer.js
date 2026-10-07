/**
 * SVG Tree Renderer module with Interactive Pan & Zoom.
 *
 * Computes node coordinates via:
 * - x = inorder traversal index
 * - y = node depth
 *
 * Features:
 * - Interactive Pan & Zoom (mouse drag, wheel zoom, touch gestures, and reset button).
 * - Render edges first, then nodes.
 * - Formats node text as "val" or "val-freq" when freq > 1.
 * - Highlighted nodes/edges in orange and visited nodes in emerald green.
 */

// =============================================================================
// Zoom & Pan Configuration
// =============================================================================
const ZOOM_CONFIG = {
  WHEEL_SENSITIVITY: 0.0008, // Lower = less sensitive wheel zoom
  BUTTON_STEP: 1.1,          // Each + or - click changes scale by 10%
  PINCH_SENSITIVITY: 0.6,    // Multiplier applied to touch pinch scale change
  MIN_SCALE: 0.3,            // Minimum zoom scale (30%)
  MAX_SCALE: 3.0,            // Maximum zoom scale (300%)
  SMOOTHING: true,           // Eased animations for buttons and reset
  ANIMATION_MS: 120,         // Duration of button/reset transition in ms
  TRACKPAD_MULTIPLIER: 4.0,  // Multiplier for trackpad pinch (ctrlKey wheel events)
  MAX_DELTA_Y: 100,          // Maximum deltaY clamped per wheel event
};

const Renderer = {
  svgElement: null,
  viewportTransform: null,
  edgesGroup: null,
  nodesGroup: null,
  statsBadge: null,
  statusBox: null,
  pseudoList: null,

  width: 900,
  height: 500,
  nodeRadius: 20,

  // Pan & Zoom state
  scale: 1,
  panX: 0,
  panY: 0,
  isPanning: false,
  startX: 0,
  startY: 0,
  animFrameId: null,

  init(svgId = 'treeCanvas') {
    this.svgElement = document.getElementById(svgId);
    this.viewportTransform = document.getElementById('viewportTransform');
    this.edgesGroup = document.getElementById('edgesLayer');
    this.nodesGroup = document.getElementById('nodesLayer');
    this.statsBadge = document.getElementById('statsBadge');
    this.statusBox = document.getElementById('statusBox');
    this.pseudoList = document.getElementById('pseudoList');

    this.bindPanZoom();
  },

  getSvgPoint(clientX, clientY) {
    if (!this.svgElement) return { x: this.width / 2, y: this.height / 2 };
    const pt = this.svgElement.createSVGPoint();
    pt.x = clientX;
    pt.y = clientY;
    const ctm = this.svgElement.getScreenCTM();
    if (!ctm) return { x: this.width / 2, y: this.height / 2 };
    return pt.matrixTransform(ctm.inverse());
  },

  bindPanZoom() {
    if (!this.svgElement) return;

    // 1. Mouse Drag Panning
    this.svgElement.addEventListener('mousedown', (e) => {
      // Only pan on primary mouse button
      if (e.button !== 0) return;
      if (this.animFrameId) {
        cancelAnimationFrame(this.animFrameId);
        this.animFrameId = null;
      }
      this.isPanning = true;
      this.startX = e.clientX - this.panX;
      this.startY = e.clientY - this.panY;
      this.svgElement.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', (e) => {
      if (!this.isPanning) return;
      this.panX = e.clientX - this.startX;
      this.panY = e.clientY - this.startY;
      this.applyTransform();
    });

    window.addEventListener('mouseup', () => {
      if (this.isPanning) {
        this.isPanning = false;
        if (this.svgElement) this.svgElement.style.cursor = 'grab';
      }
    });

    // 2. Mouse Wheel & Trackpad Zoom (Exponential, Normalized, Cursor-Anchored)
    this.svgElement.addEventListener('wheel', (e) => {
      e.preventDefault();

      if (this.animFrameId) {
        cancelAnimationFrame(this.animFrameId);
        this.animFrameId = null;
      }

      // Normalize deltaY across pixel (0), line (1), and page (2) modes
      let deltaY = e.deltaY;
      if (e.deltaMode === 1) {
        deltaY *= 20; // 1 line ~ 20px
      } else if (e.deltaMode === 2) {
        deltaY *= 400; // 1 page
      }

      // Trackpad pinch gesture arrives as wheel event with ctrlKey = true
      let sensitivity = ZOOM_CONFIG.WHEEL_SENSITIVITY;
      if (e.ctrlKey) {
        sensitivity *= ZOOM_CONFIG.TRACKPAD_MULTIPLIER;
      }

      // Clamp deltaY to a sane range to prevent large jumps on fast flicks
      const clampedDeltaY = Math.max(-ZOOM_CONFIG.MAX_DELTA_Y, Math.min(ZOOM_CONFIG.MAX_DELTA_Y, deltaY));

      // Exponential zoom: newScale = oldScale * exp(-deltaY * sensitivity)
      const targetScale = Math.max(
        ZOOM_CONFIG.MIN_SCALE,
        Math.min(ZOOM_CONFIG.MAX_SCALE, this.scale * Math.exp(-clampedDeltaY * sensitivity))
      );

      // Keep point under the cursor stationary
      const svgPt = this.getSvgPoint(e.clientX, e.clientY);
      this.zoomTo(targetScale, svgPt.x, svgPt.y);
    }, { passive: false });

    // 3. Touch Support (Mobile Pan & Pinch Zoom)
    let lastTouchDist = 0;
    this.svgElement.addEventListener('touchstart', (e) => {
      if (this.animFrameId) {
        cancelAnimationFrame(this.animFrameId);
        this.animFrameId = null;
      }
      if (e.touches.length === 1) {
        this.isPanning = true;
        this.startX = e.touches[0].clientX - this.panX;
        this.startY = e.touches[0].clientY - this.panY;
      } else if (e.touches.length === 2) {
        this.isPanning = false;
        lastTouchDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
      }
    }, { passive: true });

    this.svgElement.addEventListener('touchmove', (e) => {
      if (e.touches.length === 1 && this.isPanning) {
        this.panX = e.touches[0].clientX - this.startX;
        this.panY = e.touches[0].clientY - this.startY;
        this.applyTransform();
      } else if (e.touches.length === 2) {
        const dist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        if (lastTouchDist > 0 && dist > 0) {
          const rawRatio = dist / lastTouchDist;
          const factor = 1 + (rawRatio - 1) * ZOOM_CONFIG.PINCH_SENSITIVITY;
          const targetScale = Math.max(
            ZOOM_CONFIG.MIN_SCALE,
            Math.min(ZOOM_CONFIG.MAX_SCALE, this.scale * factor)
          );

          // Zoom around midpoint between the two touches
          const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
          const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
          const svgPt = this.getSvgPoint(midX, midY);

          this.zoomTo(targetScale, svgPt.x, svgPt.y);
        }
        lastTouchDist = dist;
      }
    }, { passive: true });

    this.svgElement.addEventListener('touchend', () => {
      this.isPanning = false;
      lastTouchDist = 0;
    });

    if (this.svgElement) this.svgElement.style.cursor = 'grab';
  },

  zoomTo(newScale, focalX, focalY) {
    newScale = Math.max(ZOOM_CONFIG.MIN_SCALE, Math.min(ZOOM_CONFIG.MAX_SCALE, newScale));
    if (Math.abs(newScale - this.scale) < 1e-5) return;

    const k = newScale / this.scale;
    this.panX = focalX - k * (focalX - this.panX);
    this.panY = focalY - k * (focalY - this.panY);
    this.scale = newScale;
    this.applyTransform();
  },

  animateTransform(targetScale, targetPanX, targetPanY, durationMs = ZOOM_CONFIG.ANIMATION_MS) {
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }

    targetScale = Math.max(ZOOM_CONFIG.MIN_SCALE, Math.min(ZOOM_CONFIG.MAX_SCALE, targetScale));

    if (!ZOOM_CONFIG.SMOOTHING || durationMs <= 0) {
      this.scale = targetScale;
      this.panX = targetPanX;
      this.panY = targetPanY;
      this.applyTransform();
      return;
    }

    const startScale = this.scale;
    const startPanX = this.panX;
    const startPanY = this.panY;
    const startTime = performance.now();

    const step = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / durationMs);
      // Cubic ease-out
      const ease = 1 - Math.pow(1 - progress, 3);

      this.scale = startScale + (targetScale - startScale) * ease;
      this.panX = startPanX + (targetPanX - startPanX) * ease;
      this.panY = startPanY + (targetPanY - startPanY) * ease;
      this.applyTransform();

      if (progress < 1) {
        this.animFrameId = requestAnimationFrame(step);
      } else {
        this.animFrameId = null;
      }
    };

    this.animFrameId = requestAnimationFrame(step);
  },

  zoomIn() {
    const targetScale = Math.max(
      ZOOM_CONFIG.MIN_SCALE,
      Math.min(ZOOM_CONFIG.MAX_SCALE, this.scale * ZOOM_CONFIG.BUTTON_STEP)
    );
    const focalX = this.width / 2;
    const focalY = this.height / 2;
    const k = targetScale / this.scale;
    const targetPanX = focalX - k * (focalX - this.panX);
    const targetPanY = focalY - k * (focalY - this.panY);
    this.animateTransform(targetScale, targetPanX, targetPanY);
  },

  zoomOut() {
    const targetScale = Math.max(
      ZOOM_CONFIG.MIN_SCALE,
      Math.min(ZOOM_CONFIG.MAX_SCALE, this.scale / ZOOM_CONFIG.BUTTON_STEP)
    );
    const focalX = this.width / 2;
    const focalY = this.height / 2;
    const k = targetScale / this.scale;
    const targetPanX = focalX - k * (focalX - this.panX);
    const targetPanY = focalY - k * (focalY - this.panY);
    this.animateTransform(targetScale, targetPanX, targetPanY);
  },

  resetView() {
    this.animateTransform(1, 0, 0);
  },

  applyTransform() {
    if (!this.viewportTransform) return;
    this.viewportTransform.setAttribute(
      'transform',
      `translate(${this.panX}, ${this.panY}) scale(${this.scale})`
    );

    const badge = document.getElementById('zoomPercentBadge');
    if (badge) {
      badge.textContent = `${Math.round(this.scale * 100)}%`;
    }
  },

  /**
   * Main entry point: render a single step frame conforming to the step contract.
   */
  renderStep(step, pseudocode = null) {
    if (!this.svgElement) this.init();
    if (!step) return;

    // 1. Update Stats badge (N=.., h=..)
    if (this.statsBadge) {
      const n = step.stats ? step.stats.n : 0;
      const h = step.stats ? step.stats.h : 0;
      this.statsBadge.textContent = `N=${n}, h=${h}`;
    }

    // 2. Update Status Box (Yellow panel)
    if (this.statusBox && step.message !== undefined) {
      this.statusBox.textContent = step.message || 'Ready.';
    }

    // 3. Update Pseudocode panel (Pink panel)
    if (pseudocode && this.pseudoList) {
      this.renderPseudocode(pseudocode, step.pseudo_line);
    } else if (step.pseudo_line !== undefined && this.pseudoList) {
      this.highlightPseudoLine(step.pseudo_line);
    }

    // 4. Compute coordinates and draw SVG tree
    const layout = this.computeTreeLayout(step.tree);
    this.drawTree(layout, step);
  },

  computeTreeLayout(root) {
    if (!root) {
      return { nodes: [], edges: [] };
    }

    const inorderNodes = [];
    let maxDepth = 0;

    function traverse(node, depth, parent = null) {
      if (!node) return;
      if (depth > maxDepth) maxDepth = depth;

      traverse(node.left, depth + 1, node);
      inorderNodes.push({ node, depth, parent });
      traverse(node.right, depth + 1, node);
    }

    traverse(root, 0, null);

    const totalNodes = inorderNodes.length;
    // Graceful spacing calculation
    const marginX = 60;
    const marginY = 60;
    const usableWidth = this.width - 2 * marginX;
    const levelHeight = maxDepth > 0 ? Math.min(85, (this.height - 2 * marginY) / maxDepth) : 0;

    const nodeMap = new Map();
    const layoutNodes = [];

    inorderNodes.forEach((item, index) => {
      let x = this.width / 2;
      if (totalNodes > 1) {
        x = marginX + (index / (totalNodes - 1)) * usableWidth;
      }
      const y = marginY + item.depth * levelHeight;

      const nodeData = {
        id: String(item.node.id),
        val: item.node.val !== undefined ? item.node.val : item.node.value,
        freq: item.node.freq || 1,
        x,
        y,
        parentId: item.parent ? String(item.parent.id) : null,
      };

      nodeMap.set(nodeData.id, nodeData);
      layoutNodes.push(nodeData);
    });

    const layoutEdges = [];
    layoutNodes.forEach(node => {
      if (node.parentId && nodeMap.has(node.parentId)) {
        const parent = nodeMap.get(node.parentId);
        layoutEdges.push({
          parentId: parent.id,
          childId: node.id,
          x1: parent.x,
          y1: parent.y,
          x2: node.x,
          y2: node.y,
        });
      }
    });

    return { nodes: layoutNodes, edges: layoutEdges };
  },

  drawTree(layout, step) {
    if (!this.edgesGroup || !this.nodesGroup) return;

    this.clear();

    const highlightNodesSet = new Set((step.highlight_nodes || []).map(String));
    const visitedValsSet = new Set((step.visited || []).map(String));
    const highlightEdgesSet = new Set(
      (step.highlight_edges || []).map(edge => `${edge[0]}->${edge[1]}`)
    );

    const svgNS = 'http://www.w3.org/2000/svg';

    // 1. Draw Edges First
    layout.edges.forEach(edge => {
      const line = document.createElementNS(svgNS, 'line');
      line.setAttribute('x1', edge.x1);
      line.setAttribute('y1', edge.y1);
      line.setAttribute('x2', edge.x2);
      line.setAttribute('y2', edge.y2);
      line.classList.add('tree-edge');

      const edgeKey = `${edge.parentId}->${edge.childId}`;
      if (highlightEdgesSet.has(edgeKey)) {
        line.classList.add('highlighted');
      }

      this.edgesGroup.appendChild(line);
    });

    // 2. Draw Nodes Second
    layout.nodes.forEach(node => {
      const g = document.createElementNS(svgNS, 'g');
      g.classList.add('node-group');
      g.setAttribute('transform', `translate(${node.x}, ${node.y})`);

      const rawValStr = String(node.val);
      const displayVal = node.freq > 1 ? `${rawValStr}-${node.freq}` : rawValStr;
      const labelLen = displayVal.length;

      // Dynamic radius and font size for labels longer than 2 characters
      let currentRadius = this.nodeRadius;
      let fontSize = 13;
      if (labelLen > 2) {
        currentRadius = Math.max(this.nodeRadius, 14 + (labelLen - 2) * 5);
        fontSize = Math.max(9, 14 - Math.floor(labelLen / 2));
      }

      const circle = document.createElementNS(svgNS, 'circle');
      circle.setAttribute('r', currentRadius);
      circle.classList.add('node-circle');

      if (highlightNodesSet.has(node.id)) {
        circle.classList.add('highlighted');
      } else if (visitedValsSet.has(rawValStr)) {
        circle.classList.add('visited');
      }

      const text = document.createElementNS(svgNS, 'text');
      text.classList.add('node-text');
      text.setAttribute('font-size', `${fontSize}px`);
      text.textContent = displayVal;

      g.appendChild(circle);
      g.appendChild(text);
      this.nodesGroup.appendChild(g);
    });
  },

  renderPseudocode(lines, activeIndex) {
    if (!this.pseudoList) return;
    this.pseudoList.innerHTML = '';

    lines.forEach((line, index) => {
      const li = document.createElement('li');
      li.classList.add('pseudo-line-item');
      li.textContent = line;
      if (index === activeIndex) {
        li.classList.add('active');
      }
      this.pseudoList.appendChild(li);
    });
  },

  highlightPseudoLine(activeIndex) {
    if (!this.pseudoList) return;
    const items = this.pseudoList.querySelectorAll('.pseudo-line-item');
    items.forEach((item, index) => {
      if (index === activeIndex) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  },

  clear() {
    if (this.edgesGroup) this.edgesGroup.innerHTML = '';
    if (this.nodesGroup) this.nodesGroup.innerHTML = '';
  }
};

window.Renderer = Renderer;

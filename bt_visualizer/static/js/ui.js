/**
 * Definition strings per section for the empty-canvas state overlay.
 */
const DEFINITIONS = {
  binary: {
    title: "Binary Tree",
    body: "A binary tree is a hierarchical data structure in which every node has at most two children, called the left child and the right child. Formally, it is either empty or consists of a root node together with a left subtree and a right subtree, each of which is itself a binary tree.",
    hint: "Use the panel on the left to create a tree."
  },
  bst: {
    title: "Binary Search Tree (BST)",
    body: "A binary search tree is a binary tree in which, for every node, all values in its left subtree are smaller than the node's value and all values in its right subtree are greater. Because of this ordering, an inorder traversal visits the values in sorted order, and search, insert and remove take O(h) time, where h is the height of the tree.",
    hint: "Use the panel on the left to create a tree."
  },
  build: {
    title: "Build from Traversal",
    body: "A binary tree can be reconstructed from two of its traversal sequences. The inorder sequence together with the preorder, postorder or level-order sequence identifies the tree uniquely, as long as all values are distinct. Preorder with postorder alone is unique only for full binary trees.",
    hint: "Use the panel on the left to create a tree."
  }
};

const UI = {
  currentTree: null,
  historyStack: [],
  isBusy: false,

  init() {
    this.bindNavigation();
    this.bindTheme();
    this.bindSidebar();
    this.bindZoomControls();
    this.bindBSTOperations();
    this.bindBinaryTreeOperations();
    this.bindBuildOperations();
    this.bindUtilities();
    this.loadPresets();
    this.checkUrlHash();

    // Hook player step changes to update visited bar
    this.hookPlayer();

    // Initial empty state check
    this.updateEmptyState();
  },

  getCurrentTab() {
    const activeTab = document.querySelector('.nav-tabs .tab-btn.active');
    return activeTab?.getAttribute('data-tab') || 'bst';
  },

  updateEmptyState() {
    const card = document.getElementById('emptyCanvasCard');
    const titleEl = document.getElementById('emptyCardTitle');
    const bodyEl = document.getElementById('emptyCardBody');
    const hintEl = document.getElementById('emptyCardHint');
    if (!card) return;

    const isEmpty = !this.currentTree;
    if (isEmpty) {
      const tab = this.getCurrentTab();
      const def = DEFINITIONS[tab] || DEFINITIONS.binary;
      if (titleEl) titleEl.textContent = def.title;
      if (bodyEl) bodyEl.textContent = def.body;
      if (hintEl) hintEl.textContent = def.hint;
      card.classList.add('visible');
    } else {
      card.classList.remove('visible');
    }
  },

  bindZoomControls() {
    document.getElementById('btnZoomIn')?.addEventListener('click', () => {
      window.Renderer?.zoomIn();
    });
    document.getElementById('btnZoomOut')?.addEventListener('click', () => {
      window.Renderer?.zoomOut();
    });
    document.getElementById('btnZoomReset')?.addEventListener('click', () => {
      window.Renderer?.resetView();
    });
  },


  setBusy(busy, message = '') {
    this.isBusy = busy;
    const buttons = document.querySelectorAll('.form-btn, .btn-utility');
    buttons.forEach(btn => {
      btn.disabled = busy;
    });

    if (busy && message) {
      const statusBox = document.getElementById('statusBox');
      if (statusBox) statusBox.textContent = message;
    }
  },

  saveHistory() {
    if (this.currentTree) {
      this.historyStack.push(JSON.parse(JSON.stringify(this.currentTree)));
    } else {
      this.historyStack.push(null);
    }
    // Limit history stack size to 30
    if (this.historyStack.length > 30) {
      this.historyStack.shift();
    }
    this.updateUndoButton();
  },

  updateUndoButton() {
    const btnUndo = document.getElementById('btnUndo');
    if (btnUndo) {
      btnUndo.disabled = this.historyStack.length === 0 || this.isBusy;
    }
  },

  async applyTimelineResult(timeline, shouldAutoPlay = true) {
    if (!timeline || !timeline.steps || timeline.steps.length === 0) {
      return;
    }

    // Save final tree as new currentTree
    const finalStep = timeline.steps[timeline.steps.length - 1];
    if (finalStep && finalStep.tree !== undefined) {
      this.currentTree = finalStep.tree;
    }

    // Load into player
    if (window.PlayerInstance) {
      window.PlayerInstance.loadTimeline(timeline);
      if (shouldAutoPlay && timeline.steps.length > 1) {
        window.PlayerInstance.play();
      }
    }

    await this.updateProperties();
    this.updateVisitedBar(timeline.steps[0]);
    this.updateEmptyState();
  },

  updateVisitedBar(step) {
    const visitedBar = document.getElementById('visitedBadgeBar');
    if (!visitedBar) return;

    if (step && step.visited && step.visited.length > 0) {
      visitedBar.textContent = `Visited Sequence: [ ${step.visited.join(', ')} ]`;
      visitedBar.classList.add('visible');
    } else {
      visitedBar.classList.remove('visible');
    }
  },

  hookPlayer() {
    if (!window.PlayerInstance) return;
    const originalRender = window.PlayerInstance.renderCurrentStep.bind(window.PlayerInstance);
    window.PlayerInstance.renderCurrentStep = () => {
      originalRender();
      const currentStep = window.PlayerInstance.getCurrentStep();
      this.updateVisitedBar(currentStep);
    };
  },

  async updateProperties() {
    try {
      const res = await window.Api.getProperties(this.currentTree);
      if (res && res.properties) {
        const p = res.properties;
        const setVal = (id, val) => {
          const el = document.getElementById(id);
          if (el) el.textContent = String(val);
        };

        setVal('propLeaves', p.leaf_count);
        setVal('propInternal', p.internal_node_count);
        setVal('propHeight', p.height);
        setVal('propFull', p.is_full ? 'Yes' : 'No');
        setVal('propComplete', p.is_complete ? 'Yes' : 'No');
        setVal('propPerfect', p.is_perfect ? 'Yes' : 'No');
        setVal('propBalanced', p.is_balanced ? 'Yes' : 'No');
      }
    } catch (e) {
      // Non-blocking
    }
  },

  showError(msg) {
    const statusBox = document.getElementById('statusBox');
    if (statusBox) {
      statusBox.textContent = `Error: ${msg}`;
    }
  },

  // =========================================================================
  // Navigation & Theme
  // =========================================================================

  bindNavigation() {
    const tabs = document.querySelectorAll('.nav-tabs .tab-btn');
    const title = document.getElementById('sidebarTitle');

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        const tabKey = tab.getAttribute('data-tab');
        document.getElementById('tabContentBST').style.display = tabKey === 'bst' ? 'block' : 'none';
        document.getElementById('tabContentBinary').style.display = tabKey === 'binary' ? 'block' : 'none';
        document.getElementById('tabContentBuild').style.display = tabKey === 'build' ? 'block' : 'none';

        if (title) {
          if (tabKey === 'bst') title.textContent = 'BST Operations';
          else if (tabKey === 'binary') title.textContent = 'Binary Tree Operations';
          else title.textContent = 'Reconstruction Operations';
        }

        this.updateEmptyState();
      });
    });
  },

  bindTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeLabel = document.getElementById('themeLabel');
    let theme = 'dark';

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        theme = theme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', theme);
        themeIcon.textContent = theme === 'light' ? '\u2600' : '\u263E';
        themeLabel.textContent = theme === 'light' ? 'Light' : 'Dark';
      });
    }
  },

  bindSidebar() {
    const sidebarPanel = document.getElementById('sidebarPanel');
    const collapseBtn = document.getElementById('collapseBtn');
    const panelToggleTrigger = document.getElementById('panelToggleTrigger');

    if (collapseBtn && sidebarPanel) {
      collapseBtn.addEventListener('click', () => {
        sidebarPanel.classList.add('collapsed');
        if (panelToggleTrigger) panelToggleTrigger.style.display = 'block';
      });
    }

    if (panelToggleTrigger && sidebarPanel) {
      panelToggleTrigger.addEventListener('click', () => {
        sidebarPanel.classList.remove('collapsed');
        panelToggleTrigger.style.display = 'none';
      });
      panelToggleTrigger.style.display = 'none';
    }
  },

  // =========================================================================
  // BST Tab Operations
  // =========================================================================

  bindBSTOperations() {
    const parseSingleVal = (id) => {
      const raw = document.getElementById(id)?.value?.trim();
      if (!raw) return null;
      return /^-?\d+(\.\d+)?$/.test(raw) ? Number(raw) : raw;
    };

    // 1. Random BST
    document.getElementById('btnBSTRandom')?.addEventListener('click', async () => {
      const n = parseInt(document.getElementById('bstRandomN').value, 10) || 7;
      this.saveHistory();
      this.setBusy(true, 'Generating random BST...');
      try {
        const timeline = await window.Api.getRandom('bst', n);
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    // 2. Custom Array Load
    document.getElementById('btnBSTCustom')?.addEventListener('click', async () => {
      const raw = document.getElementById('bstCustomArr').value.trim();
      if (!raw) return;
      const rawTokens = raw.split(/[\s,;|]+/).filter(t => t.length > 0);
      if (rawTokens.length === 0) {
        this.showError('Please enter values for the BST.');
        return;
      }
      const isPureNumber = (str) => /^-?\d+(\.\d+)?$/.test(str);
      const anyNum = rawTokens.some(isPureNumber);
      const allNum = rawTokens.every(isPureNumber);
      if (anyNum && !allNum) {
        this.showError('BST values must be either all numbers or all letters/strings (cannot mix both).');
        return;
      }
      const values = allNum ? rawTokens.map(Number) : rawTokens;
      this.saveHistory();
      this.setBusy(true, 'Building BST from values...');
      try {
        const timeline = await window.Api.createBST(values);
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    // 3. Insert (Single or Multiple values)
    document.getElementById('btnBSTInsert')?.addEventListener('click', async () => {
      const raw = document.getElementById('bstInsertVal').value.trim();
      if (!raw) return;
      const rawTokens = raw.split(/[\s,;|]+/).filter(t => t.length > 0);
      if (rawTokens.length === 0) return;
      const isPureNumber = (str) => /^-?\d+(\.\d+)?$/.test(str);
      const anyNum = rawTokens.some(isPureNumber);
      const allNum = rawTokens.every(isPureNumber);
      if (anyNum && !allNum) {
        this.showError('Cannot mix numbers and letters in BST insertion.');
        return;
      }
      const vals = allNum ? rawTokens.map(Number) : rawTokens;

      this.saveHistory();
      this.setBusy(true, `Inserting ${vals.join(', ')}...`);
      try {
        let lastTimeline = null;
        for (const val of vals) {
          lastTimeline = await window.Api.bstOperation(this.currentTree, 'insert', val);
          const finalStep = lastTimeline.steps[lastTimeline.steps.length - 1];
          if (finalStep && finalStep.tree !== undefined) {
            this.currentTree = finalStep.tree;
          }
        }
        document.getElementById('bstInsertVal').value = '';
        await this.applyTimelineResult(lastTimeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    // 4. Search
    document.getElementById('btnBSTSearch')?.addEventListener('click', async () => {
      const val = parseSingleVal('bstSearchVal');
      if (val === null) return;
      this.setBusy(true, `Searching for ${val}...`);
      try {
        const timeline = await window.Api.bstOperation(this.currentTree, 'search', val);
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    // 5. Remove
    document.getElementById('btnBSTRemove')?.addEventListener('click', async () => {
      const val = parseSingleVal('bstRemoveVal');
      if (val === null) return;
      this.saveHistory();
      this.setBusy(true, `Removing ${val}...`);
      try {
        const timeline = await window.Api.bstOperation(this.currentTree, 'remove', val);
        document.getElementById('bstRemoveVal').value = '';
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    // 6. Min & Max
    document.getElementById('btnBSTMin')?.addEventListener('click', async () => {
      this.setBusy(true, 'Finding minimum...');
      try {
        const timeline = await window.Api.bstOperation(this.currentTree, 'min');
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    document.getElementById('btnBSTMax')?.addEventListener('click', async () => {
      this.setBusy(true, 'Finding maximum...');
      try {
        const timeline = await window.Api.bstOperation(this.currentTree, 'max');
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    // 7. Predecessor & Successor
    document.getElementById('btnBSTPred')?.addEventListener('click', async () => {
      const val = parseSingleVal('bstPredSuccVal');
      if (val === null) return;
      this.setBusy(true, `Finding predecessor of ${val}...`);
      try {
        const timeline = await window.Api.bstOperation(this.currentTree, 'pred', val);
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    document.getElementById('btnBSTSucc')?.addEventListener('click', async () => {
      const val = parseSingleVal('bstPredSuccVal');
      if (val === null) return;
      this.setBusy(true, `Finding successor of ${val}...`);
      try {
        const timeline = await window.Api.bstOperation(this.currentTree, 'succ', val);
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    // 8. Rank & Select
    document.getElementById('btnBSTRank')?.addEventListener('click', async () => {
      const val = parseSingleVal('bstRankVal');
      if (val === null) return;
      this.setBusy(true, `Computing rank of ${val}...`);
      try {
        const timeline = await window.Api.bstOperation(this.currentTree, 'rank', val);
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    document.getElementById('btnBSTSelect')?.addEventListener('click', async () => {
      const k = parseInt(document.getElementById('bstSelectK').value, 10);
      if (isNaN(k) || k < 1) return;
      this.setBusy(true, `Selecting ${k}-th smallest element...`);
      try {
        const timeline = await window.Api.bstOperation(this.currentTree, 'select', k);
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });
  },

  // =========================================================================
  // Binary Tree Tab Operations
  // =========================================================================

  bindBinaryTreeOperations() {
    const toggleContainer = document.getElementById('btLabelTypeToggle');
    const nInput = document.getElementById('btRandomN');
    const levelOrderInput = document.getElementById('btLevelOrderInput');
    const levelOrderHint = document.getElementById('btLevelOrderHint');

    const getBTLabelType = () => {
      return localStorage.getItem('bt_random_label_type') || 'numbers';
    };

    const setBTLabelType = (type, updateUI = true) => {
      localStorage.setItem('bt_random_label_type', type);
      if (updateUI && toggleContainer) {
        toggleContainer.querySelectorAll('.segment-btn').forEach(btn => {
          const isActive = btn.getAttribute('data-type') === type;
          btn.classList.toggle('active', isActive);
          btn.setAttribute('aria-checked', isActive ? 'true' : 'false');
        });
      }
      if (nInput) {
        nInput.max = type === 'letters' ? 26 : 30;
      }
    };

    // Restore saved choice on load
    setBTLabelType(getBTLabelType(), true);

    toggleContainer?.querySelectorAll('.segment-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const type = btn.getAttribute('data-type') || 'numbers';
        setBTLabelType(type, true);
      });
    });

    // 1. Random Binary Tree
    document.getElementById('btnBTRandom')?.addEventListener('click', async () => {
      const rawN = nInput ? nInput.value.trim() : '';
      const labelType = getBTLabelType();
      let n = parseInt(rawN, 10);

      // Validate count: empty or invalid -> default 6
      if (isNaN(n) || n < 1) {
        n = 6;
        if (nInput) nInput.value = '6';
        const statusBox = document.getElementById('statusBox');
        if (statusBox) statusBox.textContent = 'Count was empty or invalid; defaulted to 6 nodes.';
      } else if (labelType === 'letters' && n > 26) {
        n = 26;
        if (nInput) nInput.value = '26';
        const statusBox = document.getElementById('statusBox');
        if (statusBox) statusBox.textContent = 'Alphabetic mode supports maximum 26 unique letters (A-Z). Clamped count to 26.';
      } else if (labelType === 'numbers' && n > 30) {
        n = 30;
        if (nInput) nInput.value = '30';
        const statusBox = document.getElementById('statusBox');
        if (statusBox) statusBox.textContent = 'Clamped numeric count to maximum 30 nodes.';
      }

      this.saveHistory();
      this.setBusy(true, `Generating random binary tree with ${n} ${labelType === 'letters' ? 'alphabetic' : 'numeric'} nodes...`);
      try {
        const timeline = await window.Api.getRandom('binary', n, labelType);
        await this.applyTimelineResult(timeline, false);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    // Helper to parse lenient level-order list
    const parseLevelOrderInput = (raw) => {
      if (!raw || !raw.trim()) return [];
      let cleaned = raw.trim();
      if ((cleaned.startsWith('[') && cleaned.endsWith(']')) ||
          (cleaned.startsWith('(') && cleaned.endsWith(')'))) {
        cleaned = cleaned.slice(1, -1).trim();
      }
      const rawTokens = cleaned.split(/[\s,;|]+/).filter(t => t.length > 0);
      return rawTokens.map(tok => {
        const lower = tok.toLowerCase();
        if (tok === '-' || lower === 'null' || tok === '#' || lower === 'none') {
          return null;
        }
        if (/^-?\d+(\.\d+)?$/.test(tok)) {
          return parseInt(tok, 10);
        }
        return tok;
      });
    };

    // Live hint & type auto-detection as user types
    levelOrderInput?.addEventListener('input', () => {
      const raw = levelOrderInput.value;
      if (!raw.trim()) {
        if (levelOrderHint) {
          levelOrderHint.textContent = '';
          levelOrderHint.className = 'field-hint';
        }
        return;
      }
      const items = parseLevelOrderInput(raw);
      if (items.length === 0) {
        if (levelOrderHint) {
          levelOrderHint.textContent = 'Empty or unparseable';
          levelOrderHint.className = 'field-hint error';
        }
        return;
      }

      // Auto-detect type from non-null items
      const nonNull = items.filter(x => x !== null);
      if (nonNull.length > 0) {
        const allLetters = nonNull.every(x => typeof x === 'string' && /^[a-zA-Z]+$/.test(x));
        const allNumbers = nonNull.every(x => typeof x === 'number');
        if (allLetters) {
          setBTLabelType('letters', true);
        } else if (allNumbers) {
          setBTLabelType('numbers', true);
        }
      }

      if (levelOrderHint) {
        const formatted = items.map(x => x === null ? '-' : x).join(', ');
        levelOrderHint.textContent = `Interpreted as: [ ${formatted} ]`;
        levelOrderHint.className = 'field-hint success';
      }
    });

    // 2. Custom Level-Order List (e.g. 1, 2, 3, null, 4 or A, B, C, -, D)
    document.getElementById('btnBTCustom')?.addEventListener('click', async () => {
      const raw = levelOrderInput?.value.trim();
      if (!raw) return;

      const items = parseLevelOrderInput(raw);
      if (items.length === 0 || items[0] === null) {
        this.showError('Please provide valid level-order values (root cannot be null).');
        return;
      }

      this.saveHistory();
      this.setBusy(true, 'Constructing tree from level-order list...');
      try {
        const root = this.buildLevelOrderClient(items);
        this.currentTree = root;
        const timeline = await window.Api.traverse(this.currentTree, 'level');
        await this.applyTimelineResult(timeline, false);
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    // 3. Traversals
    const setupTraverseBtn = (btnId, order, name) => {
      document.getElementById(btnId)?.addEventListener('click', async () => {
        this.setBusy(true, `Running ${name} traversal...`);
        try {
          const timeline = await window.Api.traverse(this.currentTree, order);
          await this.applyTimelineResult(timeline, true);
        } catch (err) {
          this.showError(err.message);
        } finally {
          this.setBusy(false);
        }
      });
    };

    setupTraverseBtn('btnTraversePre', 'pre', 'Preorder');
    setupTraverseBtn('btnTraverseIn', 'in', 'Inorder');
    setupTraverseBtn('btnTraversePost', 'post', 'Postorder');
    setupTraverseBtn('btnTraverseLevel', 'level', 'Level Order');
  },

  buildLevelOrderClient(values) {
    if (!values || values.length === 0 || values[0] === null) return null;
    let idCounter = 1;
    const root = { id: `node_${idCounter++}`, value: values[0], freq: 1, left: null, right: null };
    const queue = [root];
    let idx = 1;

    while (queue.length > 0 && idx < values.length) {
      const curr = queue.shift();
      if (idx < values.length) {
        const lVal = values[idx++];
        if (lVal !== null) {
          curr.left = { id: `node_${idCounter++}`, value: lVal, freq: 1, left: null, right: null };
          queue.push(curr.left);
        }
      }
      if (idx < values.length) {
        const rVal = values[idx++];
        if (rVal !== null) {
          curr.right = { id: `node_${idCounter++}`, value: rVal, freq: 1, left: null, right: null };
          queue.push(curr.right);
        }
      }
    }
    return root;
  },

  // =========================================================================
  // Build from Traversal Operations
  // =========================================================================

  bindBuildOperations() {
    const modeSelect = document.getElementById('buildModeSelect');
    const warning = document.getElementById('buildAmbiguityWarning');
    const seq1Label = document.getElementById('buildSeq1Label');
    const seq2Label = document.getElementById('buildSeq2Label');
    const seq2Group = document.getElementById('buildSeq2Group');
    const seq1Input = document.getElementById('buildSeq1Input');
    const seq2Input = document.getElementById('buildSeq2Input');
    const seq1Hint = document.getElementById('buildSeq1Hint');
    const seq2Hint = document.getElementById('buildSeq2Hint');
    const valBox = document.getElementById('buildValidationBox');
    const btnRandom = document.getElementById('btnBuildRandom');
    const labelTypeSelect = document.getElementById('buildLabelTypeSelect');
    const chkImmediate = document.getElementById('chkBuildImmediate');
    const btnBuild = document.getElementById('btnBuildAnimate');

    let debounceTimer = null;

    const isTwoSeqMode = (m) => ['in+pre', 'in+post', 'in+level', 'pre+post'].includes(m);

    const updateModeUI = () => {
      const mode = modeSelect.value;
      if (warning) {
        warning.style.display = mode === 'pre+post' ? 'block' : 'none';
      }

      if (mode === 'in+pre') {
        seq1Label.textContent = 'Inorder Sequence';
        seq2Label.textContent = 'Preorder Sequence';
        seq2Group.style.display = 'block';
        seq1Input.placeholder = 'e.g. D, B, E, A, C or 4, 2, 5, 1, 6';
        seq2Input.placeholder = 'e.g. A, B, D, E, C or 1, 2, 4, 5, 6';
      } else if (mode === 'in+post') {
        seq1Label.textContent = 'Inorder Sequence';
        seq2Label.textContent = 'Postorder Sequence';
        seq2Group.style.display = 'block';
        seq1Input.placeholder = 'e.g. D, B, E, A, C or 4, 2, 5, 1, 6';
        seq2Input.placeholder = 'e.g. D, E, B, C, A or 4, 5, 2, 6, 1';
      } else if (mode === 'in+level') {
        seq1Label.textContent = 'Inorder Sequence';
        seq2Label.textContent = 'Level Order Sequence';
        seq2Group.style.display = 'block';
        seq1Input.placeholder = 'e.g. D, B, E, A, C or 4, 2, 5, 1, 6';
        seq2Input.placeholder = 'e.g. A, B, C, D, E or 1, 2, 6, 4, 5';
      } else if (mode === 'pre+post') {
        seq1Label.textContent = 'Preorder Sequence';
        seq2Label.textContent = 'Postorder Sequence';
        seq2Group.style.display = 'block';
        seq1Input.placeholder = 'e.g. A, B, D, E, C';
        seq2Input.placeholder = 'e.g. D, E, B, C, A';
      } else if (mode === 'bst-pre') {
        seq1Label.textContent = 'Preorder Sequence (numbers or case-sensitive letters)';
        seq2Group.style.display = 'none';
        seq1Input.placeholder = 'e.g. 50, 25, 10, 30, 75 or M, G, B, K, T';
      } else if (mode === 'bst-post') {
        seq1Label.textContent = 'Postorder Sequence (numbers or case-sensitive letters)';
        seq2Group.style.display = 'none';
        seq1Input.placeholder = 'e.g. 10, 30, 25, 75, 50 or B, K, G, T, M';
      }

      triggerValidation();
    };

    const renderValidation = (res) => {
      if (!res) return;
      const isTwo = isTwoSeqMode(modeSelect.value);

      // 1. Seq1 Hint
      if (seq1Hint) {
        if (res.seq1 && res.seq1.tokens && res.seq1.tokens.length > 0) {
          const note = res.seq1.notes && res.seq1.notes.length > 0 ? ` (${res.seq1.notes[0]})` : '';
          const tokStr = res.seq1.tokens.join(', ');
          if (res.valid) {
            seq1Hint.textContent = `✓ Interpreted as: ${tokStr}${note}`;
            seq1Hint.className = 'field-hint success';
          } else {
            seq1Hint.textContent = `Interpreted as: ${tokStr}${note}`;
            seq1Hint.className = 'field-hint';
          }
        } else if (seq1Input.value.trim()) {
          seq1Hint.textContent = 'Empty or unparseable';
          seq1Hint.className = 'field-hint error';
        } else {
          seq1Hint.textContent = '';
          seq1Hint.className = 'field-hint';
        }
      }

      // 2. Seq2 Hint
      if (seq2Hint) {
        if (isTwo) {
          if (res.seq2 && res.seq2.tokens && res.seq2.tokens.length > 0) {
            const note = res.seq2.notes && res.seq2.notes.length > 0 ? ` (${res.seq2.notes[0]})` : '';
            const tokStr = res.seq2.tokens.join(', ');
            if (res.valid) {
              seq2Hint.textContent = `✓ Interpreted as: ${tokStr}${note}`;
              seq2Hint.className = 'field-hint success';
            } else {
              seq2Hint.textContent = `Interpreted as: ${tokStr}${note}`;
              seq2Hint.className = 'field-hint';
            }
          } else if (seq2Input.value.trim()) {
            seq2Hint.textContent = 'Empty or unparseable';
            seq2Hint.className = 'field-hint error';
          } else {
            seq2Hint.textContent = '';
            seq2Hint.className = 'field-hint';
          }
        } else {
          seq2Hint.textContent = '';
          seq2Hint.className = 'field-hint';
        }
      }

      // 3. Validation Box
      if (!valBox) return;
      valBox.innerHTML = '';

      if (res.status === 'neutral' || !res.message) {
        valBox.style.display = 'none';
        return;
      }

      valBox.style.display = 'block';
      const card = document.createElement('div');
      card.className = `validation-card ${res.status}`;

      let icon = 'ℹ';
      if (res.status === 'success') icon = '✓';
      else if (res.status === 'warning') icon = '⚠';
      else if (res.status === 'error') icon = '✕';

      let html = `<div class="msg"><strong>${icon}</strong> ${res.message}</div>`;

      if (res.suggestions && res.suggestions.length > 0) {
        html += '<div class="suggestions" style="margin-top: 8px;">';
        res.suggestions.forEach((s, idx) => {
          if (s.type === 'replace') {
            html += `<div style="margin-top: 6px; font-size: 0.85rem; display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap;">
              <span>Did you mean <strong>${s.field === 'seq1' ? 'Sequence 1' : 'Sequence 2'}</strong>: <code>${s.value}</code></span>
              <button type="button" class="suggestion-pill" data-idx="${idx}" data-field="${s.field}" data-val="${s.value}">Use this</button>
            </div>`;
          } else if (s.type === 'swap_fields') {
            html += `<div style="margin-top: 6px;">
              <button type="button" class="suggestion-pill" data-idx="${idx}" data-action="swap">⇄ Swap Sequences</button>
            </div>`;
          } else if (s.type === 'switch_mode') {
            html += `<div style="margin-top: 6px;">
              <button type="button" class="suggestion-pill" data-idx="${idx}" data-action="mode" data-mode="${s.mode}">Switch mode to ${s.label}</button>
            </div>`;
          }
        });
        html += '</div>';
      }

      card.innerHTML = html;
      valBox.appendChild(card);

      // Bind suggestion clicks
      card.querySelectorAll('.suggestion-pill').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const action = btn.getAttribute('data-action');
          if (action === 'swap') {
            const tmp = seq1Input.value;
            seq1Input.value = seq2Input.value;
            seq2Input.value = tmp;
            performValidation();
          } else if (action === 'mode') {
            const newMode = btn.getAttribute('data-mode');
            if (newMode) {
              modeSelect.value = newMode;
              updateModeUI();
              performValidation();
            }
          } else {
            const field = btn.getAttribute('data-field');
            const val = btn.getAttribute('data-val');
            if (field === 'seq1') {
              seq1Input.value = val;
            } else if (field === 'seq2') {
              seq2Input.value = val;
            }
            performValidation();
          }
        });
      });
    };

    const performValidation = async () => {
      const mode = modeSelect.value;
      const raw1 = seq1Input.value;
      const raw2 = isTwoSeqMode(mode) ? seq2Input.value : '';

      if (!raw1.trim() && !raw2.trim()) {
        if (seq1Hint) { seq1Hint.textContent = ''; seq1Hint.className = 'field-hint'; }
        if (seq2Hint) { seq2Hint.textContent = ''; seq2Hint.className = 'field-hint'; }
        if (valBox) { valBox.style.display = 'none'; valBox.innerHTML = ''; }
        return;
      }

      try {
        const diagnostics = await window.Api.validateBuild(mode, raw1, raw2);
        renderValidation(diagnostics);
      } catch (err) {
        console.error('Validation request failed', err);
      }
    };

    const triggerValidation = () => {
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(performValidation, 300);
    };

    if (modeSelect) {
      modeSelect.addEventListener('change', updateModeUI);
      updateModeUI();
    }

    seq1Input?.addEventListener('input', triggerValidation);
    seq2Input?.addEventListener('input', triggerValidation);

    // Random Sequence Generator Button
    btnRandom?.addEventListener('click', async () => {
      const mode = modeSelect.value;
      const labelType = labelTypeSelect?.value || 'letters';
      // Pick random N between 3 and 9 (for pre+post must be odd)
      let n = Math.floor(Math.random() * 5) + 3; // 3 to 7
      if (mode === 'pre+post' && n % 2 === 0) {
        n += 1;
      }

      this.setBusy(true, 'Generating random valid traversal pair...');
      try {
        const res = await window.Api.getRandomBuild(mode, n, labelType);
        if (res) {
          seq1Input.value = res.seq1 || '';
          if (res.seq2) {
            seq2Input.value = res.seq2;
          } else {
            seq2Input.value = '';
          }
          await performValidation();

          if (chkImmediate && chkImmediate.checked) {
            btnBuild?.click();
          }
        }
      } catch (err) {
        this.showError(err.message);
      } finally {
        this.setBusy(false);
      }
    });

    // Build and Animate Button
    btnBuild?.addEventListener('click', async () => {
      const mode = modeSelect.value;
      const raw1 = seq1Input.value.trim();
      const isTwo = isTwoSeqMode(mode);
      const raw2 = isTwo ? seq2Input.value.trim() : null;

      if (!raw1 || (isTwo && !raw2)) {
        this.showError('Please provide the required traversal sequence(s).');
        return;
      }

      // Pre-validate on submit
      await performValidation();

      this.saveHistory();
      this.setBusy(true, 'Building tree from traversal sequences...');
      try {
        const timeline = await window.Api.build(mode, raw1, raw2);
        await this.applyTimelineResult(timeline, true);
      } catch (err) {
        // Stale-tree problem fix: when build request fails, show the error
        // and do not leave the old tree looking like the result! Clear canvas and show failure step.
        this.currentTree = null;
        if (window.PlayerInstance) {
          window.PlayerInstance.loadTimeline({
            operation: 'build_failed',
            pseudocode: ['Tree reconstruction failed: sequences could not form a valid binary tree.'],
            steps: [{
              tree: null,
              highlight_nodes: [],
              highlight_edges: [],
              visited: [],
              message: `Reconstruction Error: ${err.message}`,
              pseudo_line: 0,
              stats: { n: 0, h: 0 }
            }]
          });
        }
        this.showError(err.message);
        this.updateEmptyState();
      } finally {
        this.setBusy(false);
      }
    });
  },

  // =========================================================================
  // Global Utilities: Undo, Clear, Export, Share
  // =========================================================================

  bindUtilities() {
    // 1. Undo
    document.getElementById('btnUndo')?.addEventListener('click', () => {
      if (this.historyStack.length === 0 || this.isBusy) return;
      this.currentTree = this.historyStack.pop();
      this.updateUndoButton();

      const timeline = {
        operation: 'undo',
        pseudocode: ['reverted to previous tree state'],
        steps: [{
          tree: this.currentTree,
          highlight_nodes: [],
          highlight_edges: [],
          visited: [],
          message: 'Undid last operation. Reverted tree state.',
          pseudo_line: 0,
          stats: {
            n: this.currentTree ? (window.Renderer?.computeTreeLayout(this.currentTree)?.nodes?.length || 0) : 0,
            h: 0,
          }
        }]
      };
      this.applyTimelineResult(timeline, false);
      this.updateEmptyState();
    });

    // Keyboard shortcut for Undo (Ctrl+Z)
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
        if (!['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
          e.preventDefault();
          document.getElementById('btnUndo')?.click();
        }
      }
    });

    // 2. Clear
    document.getElementById('btnClear')?.addEventListener('click', () => {
      this.saveHistory();
      this.currentTree = null;
      if (window.PlayerInstance) {
        window.PlayerInstance.loadTimeline({
          operation: 'clear',
          pseudocode: ['tree cleared'],
          steps: [{
            tree: null,
            highlight_nodes: [],
            highlight_edges: [],
            visited: [],
            message: 'Tree cleared.',
            pseudo_line: 0,
            stats: { n: 0, h: 0 }
          }]
        });
      }
      this.updateVisitedBar(null);
      this.updateProperties();
      this.updateEmptyState();
    });

    // 3. Export JSON
    document.getElementById('btnExportJson')?.addEventListener('click', () => {
      if (!this.currentTree) {
        const statusBox = document.getElementById('statusBox');
        if (statusBox) statusBox.textContent = 'Canvas is empty; nothing to export.';
        return;
      }
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.currentTree, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', 'tree.json');
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    });

    // 4. Export PNG
    document.getElementById('btnExportPng')?.addEventListener('click', () => {
      if (!this.currentTree) {
        const statusBox = document.getElementById('statusBox');
        if (statusBox) statusBox.textContent = 'Canvas is empty; nothing to export.';
        return;
      }
      const svg = document.getElementById('treeCanvas');
      if (!svg) return;

      const svgData = new XMLSerializer().serializeToString(svg);
      const canvas = document.createElement('canvas');
      canvas.width = 1800; // 2x high-res
      canvas.height = 1000;
      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        // Draw background
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        ctx.fillStyle = isDark ? '#0b0f19' : '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        const a = document.createElement('a');
        a.download = 'tree.png';
        a.href = canvas.toDataURL('image/png');
        document.body.appendChild(a);
        a.click();
        a.remove();
      };

      img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    });

    // 5. Share URL
    document.getElementById('btnShareUrl')?.addEventListener('click', () => {
      if (!this.currentTree) {
        this.showError('No tree to share.');
        return;
      }
      try {
        const encoded = encodeURIComponent(JSON.stringify(this.currentTree));
        const url = `${window.location.origin}${window.location.pathname}#tree=${encoded}`;
        window.location.hash = `tree=${encoded}`;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(() => {
            const statusBox = document.getElementById('statusBox');
            if (statusBox) statusBox.textContent = 'Shareable URL copied to clipboard!';
          }).catch(() => {
            prompt('Copy shareable URL:', url);
          });
        } else {
          prompt('Copy shareable URL:', url);
        }
      } catch (e) {
        this.showError('Could not generate shareable URL.');
      }
    });
  },

  async loadPresets() {
    try {
      const res = await window.Api.getExamples();
      const select = document.getElementById('bstPresets');
      if (select && res.examples) {
        res.examples.forEach(ex => {
          const opt = document.createElement('option');
          opt.value = ex.id;
          opt.textContent = `${ex.name} (${ex.description})`;
          select.appendChild(opt);
        });

        select.addEventListener('change', async (e) => {
          const selected = res.examples.find(x => x.id === e.target.value);
          if (selected) {
            this.saveHistory();
            this.setBusy(true, `Loading preset: ${selected.name}...`);
            try {
              if (selected.values) {
                const timeline = await window.Api.createBST(selected.values);
                await this.applyTimelineResult(timeline, true);
              } else if (selected.tree) {
                this.currentTree = selected.tree;
                const timeline = await window.Api.traverse(this.currentTree, 'level');
                await this.applyTimelineResult(timeline, false);
              }
            } catch (err) {
              this.showError(err.message);
            } finally {
              this.setBusy(false);
            }
          }
        });
      }
    } catch (e) {
      // Non-blocking
    }
  },

  async checkUrlHash() {
    let jsonStr = null;
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('tree')) {
      jsonStr = urlParams.get('tree');
    } else if (window.location.hash && window.location.hash.startsWith('#tree=')) {
      jsonStr = decodeURIComponent(window.location.hash.substring(6));
    }

    if (jsonStr) {
      try {
        const parsedTree = JSON.parse(jsonStr);
        if (parsedTree) {
          this.currentTree = parsedTree;
          if (window.Api) {
            await window.Api.init();
            const tl = await window.Api.traverse(this.currentTree, 'level');
            await this.applyTimelineResult(tl, false);
          }
        }
      } catch (e) {
        console.error('Failed to parse tree from URL query/hash', e);
      }
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  UI.init();
});

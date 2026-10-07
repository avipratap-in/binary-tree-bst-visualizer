/**
 * Animation player and playback controller.
 *
 * Coordinates timeline navigation, auto-playback, slider scrubbing,
 * speed adjustments, and keyboard shortcuts.
 */

class Player {
  constructor() {
    this.steps = [];
    this.pseudocode = [];
    this.currentIndex = 0;
    this.isPlaying = false;
    this.timerId = null;
    this.baseDelayMs = 1000;
    this.speedMultiplier = 1.0;

    // DOM Elements
    this.btnSkipStart = null;
    this.btnStepBack = null;
    this.btnPlay = null;
    this.btnStepForward = null;
    this.btnSkipEnd = null;
    this.progressSlider = null;
    this.stepCounter = null;
    this.speedSelect = null;

    this.initDOM();
  }

  initDOM() {
    this.btnSkipStart = document.getElementById('btnSkipStart');
    this.btnStepBack = document.getElementById('btnStepBack');
    this.btnPlay = document.getElementById('btnPlay');
    this.btnStepForward = document.getElementById('btnStepForward');
    this.btnSkipEnd = document.getElementById('btnSkipEnd');
    this.progressSlider = document.getElementById('progressSlider');
    this.stepCounter = document.getElementById('stepCounter');
    this.speedSelect = document.getElementById('speedSelect');

    this.bindEvents();
  }

  bindEvents() {
    if (this.btnSkipStart) {
      this.btnSkipStart.addEventListener('click', () => this.skipToStart());
    }
    if (this.btnStepBack) {
      this.btnStepBack.addEventListener('click', () => this.stepBack());
    }
    if (this.btnPlay) {
      this.btnPlay.addEventListener('click', () => this.togglePlay());
    }
    if (this.btnStepForward) {
      this.btnStepForward.addEventListener('click', () => this.stepForward());
    }
    if (this.btnSkipEnd) {
      this.btnSkipEnd.addEventListener('click', () => this.skipToEnd());
    }

    if (this.progressSlider) {
      this.progressSlider.addEventListener('input', (e) => {
        this.pause();
        this.goToIndex(parseInt(e.target.value, 10));
      });
    }

    if (this.speedSelect) {
      this.speedSelect.addEventListener('change', (e) => {
        const val = parseFloat(e.target.value);
        if (!isNaN(val) && val > 0) {
          this.speedMultiplier = val;
        }
      });
    }

    // Keyboard Shortcuts: Space = play/pause, Left = step back, Right = step forward
    window.addEventListener('keydown', (e) => {
      // Ignore if user is currently typing inside an input or textarea
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
        return;
      }

      if (e.code === 'Space') {
        e.preventDefault();
        this.togglePlay();
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        this.pause();
        this.stepBack();
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        this.pause();
        this.stepForward();
      }
    });
  }

  /**
   * Loads a new timeline into the player.
   * Accepts either { operation, pseudocode, steps } or a raw steps array.
   */
  loadTimeline(timeline) {
    this.pause();

    if (Array.isArray(timeline)) {
      this.steps = timeline;
      this.pseudocode = [];
    } else if (timeline && Array.isArray(timeline.steps)) {
      this.steps = timeline.steps;
      this.pseudocode = timeline.pseudocode || [];
    } else {
      this.steps = [];
      this.pseudocode = [];
    }

    this.currentIndex = 0;

    // Handle initial render and UI state
    if (this.progressSlider) {
      const maxVal = Math.max(0, this.steps.length - 1);
      this.progressSlider.min = '0';
      this.progressSlider.max = String(maxVal);
      this.progressSlider.value = '0';
      this.progressSlider.disabled = this.steps.length <= 1;
    }

    this.renderCurrentStep();
    this.updateControlsUI();
  }

  getCurrentStep() {
    if (this.steps.length === 0) return null;
    return this.steps[this.currentIndex];
  }

  getDelay() {
    return Math.max(50, this.baseDelayMs / this.speedMultiplier);
  }

  play() {
    if (this.steps.length <= 1) return;

    // If at the end, replay from start
    if (this.currentIndex >= this.steps.length - 1) {
      this.currentIndex = 0;
    }

    this.isPlaying = true;
    this.updatePlayButton();
    this.scheduleNextStep();
  }

  pause() {
    this.isPlaying = false;
    if (this.timerId) {
      clearTimeout(this.timerId);
      this.timerId = null;
    }
    this.updatePlayButton();
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  scheduleNextStep() {
    if (!this.isPlaying) return;

    this.timerId = setTimeout(() => {
      if (!this.isPlaying) return;

      if (this.currentIndex < this.steps.length - 1) {
        this.goToIndex(this.currentIndex + 1);
        this.scheduleNextStep();
      } else {
        // Reached end of playback
        this.pause();
      }
    }, this.getDelay());
  }

  stepForward() {
    this.pause();
    if (this.currentIndex < this.steps.length - 1) {
      this.goToIndex(this.currentIndex + 1);
    }
  }

  stepBack() {
    this.pause();
    if (this.currentIndex > 0) {
      this.goToIndex(this.currentIndex - 1);
    }
  }

  skipToStart() {
    this.pause();
    this.goToIndex(0);
  }

  skipToEnd() {
    this.pause();
    if (this.steps.length > 0) {
      this.goToIndex(this.steps.length - 1);
    }
  }

  goToIndex(index) {
    if (this.steps.length === 0) {
      this.currentIndex = 0;
    } else {
      this.currentIndex = Math.max(0, Math.min(index, this.steps.length - 1));
    }

    if (this.progressSlider) {
      this.progressSlider.value = String(this.currentIndex);
    }

    this.renderCurrentStep();
    this.updateControlsUI();
  }

  renderCurrentStep() {
    const step = this.getCurrentStep();
    if (window.Renderer) {
      window.Renderer.renderStep(step, this.pseudocode);
    }
  }

  updateControlsUI() {
    const total = this.steps.length;

    // Update Step counter label
    if (this.stepCounter) {
      if (total === 0) {
        this.stepCounter.textContent = '0 / 0';
      } else {
        this.stepCounter.textContent = `${this.currentIndex + 1} / ${total}`;
      }
    }

    // Disable / Enable buttons based on position and step count
    const isSingleOrEmpty = total <= 1;
    const isAtStart = this.currentIndex === 0;
    const isAtEnd = this.currentIndex === total - 1;

    if (this.btnSkipStart) this.btnSkipStart.disabled = isSingleOrEmpty || isAtStart;
    if (this.btnStepBack) this.btnStepBack.disabled = isSingleOrEmpty || isAtStart;
    if (this.btnStepForward) this.btnStepForward.disabled = isSingleOrEmpty || isAtEnd;
    if (this.btnSkipEnd) this.btnSkipEnd.disabled = isSingleOrEmpty || isAtEnd;
    if (this.btnPlay) this.btnPlay.disabled = isSingleOrEmpty;

    this.updatePlayButton();
  }

  updatePlayButton() {
    if (!this.btnPlay) return;

    if (this.isPlaying) {
      this.btnPlay.innerHTML = '&#9208;'; // Pause icon
      this.btnPlay.title = 'Pause (Space)';
    } else {
      if (this.steps.length > 1 && this.currentIndex === this.steps.length - 1) {
        this.btnPlay.innerHTML = '&#8634;'; // Replay icon
        this.btnPlay.title = 'Replay (Space)';
      } else {
        this.btnPlay.innerHTML = '&#9654;'; // Play icon
        this.btnPlay.title = 'Play (Space)';
      }
    }
  }
}

// Global instance
window.PlayerInstance = new Player();

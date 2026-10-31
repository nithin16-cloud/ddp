/**
 * LabLine Diagnostics Motion Engine
 * High-performance 60fps canvas engine for clinical diagnostic portal.
 * Features ambient concentric waves, mouse parallax,
 * dynamic CSS variable color binding, and login transition wave.
 */
(function() {
  'use strict';

  // Feature detection
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isLowPowerDevice = (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4) ||
                           (navigator.connection && (navigator.connection.saveData || navigator.connection.effectiveType === '2g'));

  let canvas, ctx;
  let width = 0, height = 0, dpr = 1;
  let animId = null;
  let isPaused = false;

  // Colors parsed from CSS variables
  let accentColor = 'rgba(13, 148, 136, 1)';
  let accentLight = 'rgba(45, 212, 191, 0.4)';
  let accentSubtle = 'rgba(13, 148, 136, 0.12)';

  function updateThemeColors() {
    try {
      const styles = getComputedStyle(document.documentElement);
      const accent = styles.getPropertyValue('--accent').trim() || '#0d9488';
      
      // Convert hex/rgb to rgba components
      const tempEl = document.createElement('div');
      tempEl.style.color = accent;
      document.body.appendChild(tempEl);
      const computed = getComputedStyle(tempEl).color;
      document.body.removeChild(tempEl);

      const m = computed.match(/\d+/g);
      if (m && m.length >= 3) {
        accentColor = `rgba(${m[0]}, ${m[1]}, ${m[2]}, 1)`;
        accentLight = `rgba(${m[0]}, ${m[1]}, ${m[2]}, 0.45)`;
        accentSubtle = `rgba(${m[0]}, ${m[1]}, ${m[2]}, 0.12)`;
      }
    } catch (e) {
      accentColor = 'rgba(13, 148, 136, 1)';
      accentLight = 'rgba(45, 212, 191, 0.45)';
      accentSubtle = 'rgba(13, 148, 136, 0.12)';
    }
  }

  // Mouse Parallax State
  let targetMouseX = 0, targetMouseY = 0;
  let mouseX = 0, mouseY = 0;

  // Ripples list
  const interactiveRipples = [];
  let ambientTime = 0;

  class InteractiveRipple {
    constructor(x, y, maxRadius = 260, duration = 1200, isMajor = false) {
      this.x = x;
      this.y = y;
      this.maxRadius = maxRadius;
      this.duration = duration;
      this.startTime = performance.now();
      this.isMajor = isMajor;
    }

    draw(now, ctx) {
      const elapsed = now - this.startTime;
      if (elapsed > this.duration) return false;

      // Cubic-bezier(0.22, 1, 0.36, 1) easeOut approximation
      const progress = Math.min(1, elapsed / this.duration);
      const ease = 1 - Math.pow(1 - progress, 3);

      const currentRadius = ease * this.maxRadius;
      const alpha = Math.max(0, (1 - ease) * (this.isMajor ? 0.9 : 0.65));

      ctx.save();
      ctx.beginPath();
      ctx.arc(this.x, this.y, currentRadius, 0, Math.PI * 2);
      ctx.strokeStyle = accentLight.replace(/[\d\.]+\)$/, `${alpha})`);
      ctx.lineWidth = this.isMajor ? 3 * (1 - ease * 0.5) : 1.75;
      ctx.stroke();

      // Subtle inner secondary ring for shockwave density
      if (this.isMajor && currentRadius > 20) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, currentRadius * 0.75, 0, Math.PI * 2);
        ctx.strokeStyle = accentSubtle.replace(/[\d\.]+\)$/, `${alpha * 0.5})`);
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      ctx.restore();
      return true;
    }
  }

  function resize() {
    if (!canvas || !canvas.parentElement) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
    dpr = Math.min(window.devicePixelRatio || 1, 2);

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';

    if (ctx) {
      ctx.scale(dpr, dpr);
    }
  }

  function render(now) {
    if (isPaused) return;

    ctx.clearRect(0, 0, width, height);

    // Smooth mouse parallax interpolation
    mouseX += (targetMouseX - mouseX) * 0.04;
    mouseY += (targetMouseY - mouseY) * 0.04;

    // Pulse Origin Point (Near the LabLine Brand Header)
    const originX = 54 + mouseX * 24;
    const originY = 58 + mouseY * 24;

    // Draw Ambient Concentric Shockwaves
    if (!prefersReducedMotion) {
      ambientTime = (now % 8000) / 8000; // 8-second cycle

      const ringCount = 3;
      for (let i = 0; i < ringCount; i++) {
        // Staggered ring offsets
        const offset = i / ringCount;
        let t = (ambientTime + offset) % 1;
        
        // Easing: fast expansion initially, decelerating at perimeter
        const ease = 1 - Math.pow(1 - t, 2.5);
        const radius = 28 + ease * (Math.max(width, height) * 0.72);
        const alpha = Math.max(0, (1 - ease) * 0.45);

        ctx.save();
        ctx.beginPath();
        ctx.arc(originX, originY, radius, 0, Math.PI * 2);
        ctx.strokeStyle = accentLight.replace(/[\d\.]+\)$/, `${alpha})`);
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Faint tertiary harmonic ring
        if (t > 0.25) {
          ctx.beginPath();
          ctx.arc(originX, originY, radius * 0.94, 0, Math.PI * 2);
          ctx.strokeStyle = accentSubtle.replace(/[\d\.]+\)$/, `${alpha * 0.4})`);
          ctx.lineWidth = 0.75;
          ctx.stroke();
        }
        ctx.restore();
      }
    }

    // Render interactive ripples
    for (let j = interactiveRipples.length - 1; j >= 0; j--) {
      const active = interactiveRipples[j].draw(now, ctx);
      if (!active) {
        interactiveRipples.splice(j, 1);
      }
    }

    animId = requestAnimationFrame(render);
  }

  function handleMouseMove(e) {
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const nx = (e.clientX - rect.left) / (width || 1) - 0.5;
    const ny = (e.clientY - rect.top) / (height || 1) - 0.5;
    targetMouseX = Math.max(-1, Math.min(1, nx));
    targetMouseY = Math.max(-1, Math.min(1, ny));
  }

  // Public API: Trigger expanding shockwave transition on successful authentication
  window.triggerLoginShockwave = function(callback) {
    if (!canvas) {
      if (typeof callback === 'function') callback();
      return;
    }

    const centerX = width / 2;
    const centerY = height / 2;

    interactiveRipples.push(new InteractiveRipple(centerX, centerY, Math.max(width, height) * 1.5, 650, true));
    interactiveRipples.push(new InteractiveRipple(centerX, centerY, Math.max(width, height) * 1.2, 550, true));

    setTimeout(() => {
      if (typeof callback === 'function') callback();
    }, 450);
  };

  function init() {
    canvas = document.getElementById('shockwave-canvas');
    if (!canvas) return;
    ctx = canvas.getContext('2d');

    updateThemeColors();
    resize();

    // Listeners (resize and subtle parallax only, no tap/click bubbles)
    window.addEventListener('resize', resize, { passive: true });
    window.addEventListener('mousemove', handleMouseMove, { passive: true });

    // Theme mutation observer to update colors dynamically
    const observer = new MutationObserver(() => {
      updateThemeColors();
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    window.addEventListener('themechange', updateThemeColors);

    // Tab visibility handling
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        isPaused = true;
        if (animId) cancelAnimationFrame(animId);
      } else {
        isPaused = false;
        animId = requestAnimationFrame(render);
      }
    });

    // Start loop
    animId = requestAnimationFrame(render);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();


(function() {
  function fixVideos() {
    document.querySelectorAll('video').forEach((video) => {
      video.setAttribute('playsinline', '');
      video.setAttribute('webkit-playsinline', '');
      video.setAttribute('preload', 'metadata');
      const source = video.querySelector('source');
      if (source && source.src && !video.src) {
        video.src = source.src;
      }
      video.load();
    });
  }

  setTimeout(fixVideos, 300);
  setTimeout(fixVideos, 800);

  const videoObserver = new MutationObserver(() => setTimeout(fixVideos, 100));
  videoObserver.observe(document.documentElement, { childList: true, subtree: true });

  function formatStatsRTE() {
    document.querySelectorAll('.results-rich-text').forEach((rte) => {
      if (rte.dataset.formatted === 'true') return;
      const headings = rte.querySelectorAll('h2');
      if (headings.length === 0) return;

      headings.forEach((h2) => {
        const p = h2.nextElementSibling;
        if (p && p.tagName === 'P') {
          const card = document.createElement('div');
          card.className = 'stat-card';
          h2.parentNode.insertBefore(card, h2);
          card.appendChild(h2);
          card.appendChild(p);
        }
      });

      rte.dataset.formatted = 'true';
    });
  }

  const statsObserver = new MutationObserver(() => {
    if (document.querySelector('.results-rich-text:not([data-formatted="true"])')) {
      formatStatsRTE();
    }
  });
  statsObserver.observe(document.documentElement, { childList: true, subtree: true });
  formatStatsRTE();

  function initBeforeAfterSliders() {
    document.querySelectorAll('.ba-container').forEach((container) => {
      if (container.dataset.baReady === 'true') return;
      const slider = container.querySelector('.ba-slider');
      if (!slider) return;

      let isDragging = false;
      const moveSlider = (e) => {
        if (!isDragging) return;
        const rect = container.getBoundingClientRect();
        let x = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
        x = Math.max(0, Math.min(x - rect.left, rect.width));
        container.style.setProperty('--expose', `${(x / rect.width) * 100}%`);
      };

      slider.addEventListener('mousedown', () => { isDragging = true; });
      window.addEventListener('mouseup', () => { isDragging = false; });
      window.addEventListener('mousemove', moveSlider);
      slider.addEventListener('touchstart', () => { isDragging = true; });
      window.addEventListener('touchend', () => { isDragging = false; });
      window.addEventListener('touchmove', moveSlider);
      container.dataset.baReady = 'true';
    });
  }

  const baObserver = new MutationObserver(() => {
    if (document.querySelector('.ba-container:not([data-ba-ready="true"])')) {
      initBeforeAfterSliders();
    }
  });
  baObserver.observe(document.documentElement, { childList: true, subtree: true });
  initBeforeAfterSliders();
})();

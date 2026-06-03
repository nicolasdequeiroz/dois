(function () {
  function initHeroSlider() {
    const step1 = document.getElementById('step-01');
    const step2 = document.getElementById('step-02');
    const step3 = document.getElementById('step-03');

    if (!step1 || !step2 || !step3) return false;
    if (step1.dataset.sliderInit === 'true') return true;
    if (typeof gsap === 'undefined') return false;

    const steps = [step1, step2, step3];

    gsap.set(step1, { position: 'relative', zIndex: 2, opacity: 1 });
    gsap.set(step2, { position: 'relative', zIndex: 1, opacity: 0, marginTop: '-100vh' });
    gsap.set(step3, { position: 'relative', zIndex: 1, opacity: 0, marginTop: '-100vh' });

    steps.forEach((step) => {
      const metEl = step.querySelector('.met');
      if (!metEl || metEl.querySelector('.met-progress')) return;

      metEl.style.display = 'inline-flex';
      metEl.style.alignItems = 'center';
      metEl.style.gap = '12px';
      metEl.style.pointerEvents = 'auto';

      metEl.insertAdjacentHTML(
        'afterbegin',
        `<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" style="transform: rotate(-90deg); flex-shrink: 0; pointer-events: none;">
          <circle cx="12" cy="12" r="10" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="2"></circle>
          <circle class="met-progress" cx="12" cy="12" r="10" fill="none" stroke="#ffffff" stroke-width="2" stroke-dasharray="63" stroke-dashoffset="63" stroke-linecap="round"></circle>
        </svg>`
      );

      const nextBtn = document.createElement('button');
      nextBtn.type = 'button';
      nextBtn.className = 'met-next-btn';
      nextBtn.setAttribute('aria-label', 'Próxima etapa');
      nextBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M5 12h14"></path>
          <path d="M12 5l7 7-7 7"></path>
        </svg>`;
      metEl.appendChild(nextBtn);
    });

    let currentIndex = 0;
    const tl = gsap.timeline({ repeat: -1 });

    steps.forEach((step, i) => {
      const nextStep = steps[(i + 1) % steps.length];
      const timer = step.querySelector('.met-progress');

      tl.add(() => {
        currentIndex = i;
      }, `step_${i}_start`);

      if (timer) {
        tl.fromTo(
          timer,
          { strokeDashoffset: 63 },
          { strokeDashoffset: 0, duration: 10, ease: 'none' },
          `step_${i}_start`
        );
      } else {
        tl.to({}, { duration: 10 }, `step_${i}_start`);
      }

      tl.addLabel(`step_${i}_fade`);
      tl.set(nextStep, { zIndex: 3 }, `step_${i}_fade`)
        .to(nextStep, { opacity: 1, duration: 1.2, ease: 'power2.inOut' }, `step_${i}_fade`)
        .set(step, { opacity: 0, zIndex: 1 });

      if (timer) tl.set(timer, { strokeDashoffset: 63 });
      tl.set(nextStep, { zIndex: 2 });
    });

    document.querySelectorAll('.met-next-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        tl.play(`step_${currentIndex}_fade`);
      });
    });

    step1.dataset.sliderInit = 'true';
    return true;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHeroSlider);
  } else {
    initHeroSlider();
  }

  let attempts = 0;
  const watcher = setInterval(() => {
    if (initHeroSlider() || attempts > 30) clearInterval(watcher);
    attempts += 1;
  }, 200);
})();

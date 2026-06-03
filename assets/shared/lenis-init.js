(function() {
  function initLenisGlobal() {
    // Se já existir um Lenis rodando (ex: usuário trocou de página), destruímos o antigo
    if (window.myGlobalLenis) {
      window.myGlobalLenis.destroy();
    }

    // Configuração Premium de inércia
    const lenis = new Lenis({
      duration: 1.2, 
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), 
      smoothWheel: true,
      smoothTouch: false, // Mantém o touch natural do celular
    });

    window.myGlobalLenis = lenis;

    // Loop de renderização NATIVO DO NAVEGADOR (Não depende do GSAP)
    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // Tenta conectar o Lenis ao ScrollTrigger (se ele existir na página)
    // O setInterval garante a conexão mesmo se o script do GSAP carregar um pouco depois
    let tries = 0;
    let connectGsap = setInterval(() => {
      if (typeof ScrollTrigger !== 'undefined') {
        lenis.on('scroll', ScrollTrigger.update);
        clearInterval(connectGsap);
      }
      // Desiste de procurar após 2 segundos (ex: numa página "Contato" que não tem GSAP)
      tries++;
      if (tries > 20) clearInterval(connectGsap); 
    }, 100);
  }

  // Inicia com um pequeno atraso de 300ms para garantir que o Ycode desenhou o Body
  setTimeout(initLenisGlobal, 300);

  // Vigia de SPA: Reinicia o Lenis sempre que a URL mudar
  let lastUrl = location.href;
  new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      setTimeout(initLenisGlobal, 300);
    }
  }).observe(document.body, { childList: true, subtree: true });

})();

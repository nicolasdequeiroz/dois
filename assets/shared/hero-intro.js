// ==========================================
// 1. SCRIPT DE ANIMAÇÃO GSAP (INTRO + HERO)
// ==========================================
(function() {
  function runIntroAnimation() {
    const heroText = document.querySelector("#hero-text");
    
    if (!heroText || heroText.dataset.animado === "true") return;
    heroText.dataset.animado = "true";

    const loadingOverlay = document.querySelector("#loading-overlay");
    const holeWrap = document.querySelector("#hole-wrapper");
    const firstFrame = document.querySelector("#intro-first-frame");
    const firstText = document.querySelector("#intro-first-text");
    const helloLeft = document.querySelector("#hello-left");
    const helloRight = document.querySelector("#hello-right");
    const holeImg = document.querySelector("#hole-image");

    const navbar = document.querySelector("#site-navbar");
    const heroImg1 = document.querySelector("#hero-img-1");
    const heroImg2 = document.querySelector("#hero-img-2");
    const extraImg1 = document.querySelector("#extra-img-1");
    const extraImg2 = document.querySelector("#extra-img-2");

    if (loadingOverlay) gsap.set(loadingOverlay, { display: "flex" });

    // Lógica Condicional de Eixos
    const isMobile = window.innerWidth < 768;
    const holeWidth = isMobile ? "80vw" : "24vw"; 
    const holeHeight = isMobile ? "30vh" : "13.5vw"; 
    const pushAmount = isMobile ? "18vh" : "14vw"; // Valor do empurrão dinâmico

    if (holeWrap) {
      gsap.set(holeWrap, { 
        position: "absolute", top: "50%", left: "50%", xPercent: -50, yPercent: -50, 
        width: "0vw", height: "0vh", borderRadius: "8px" 
      });
    }
    
    if (holeImg) gsap.set(holeImg, { width: "100vw", height: "100vh", scale: 1.2, transformOrigin: "center center" });
    if (firstText) gsap.set(firstText, { opacity: 0, y: 30 }); 

    // Setup de partida diferente para Mobile e Desktop
    if (isMobile) {
      // Mobile: Eixo Y (Vertical) - Alinhados no centro, empurrando cima/baixo
      if (helloLeft) gsap.set(helloLeft, { position: "absolute", bottom: "50%", left: "50%", xPercent: -50, marginBottom: "1vh", opacity: 0, y: 20 });
      if (helloRight) gsap.set(helloRight, { position: "absolute", top: "50%", left: "50%", xPercent: -50, marginTop: "1vh", opacity: 0, y: -20 });
    } else {
      // Desktop: Eixo X (Horizontal) - Alinhados no centro, empurrando esquerda/direita
      if (helloLeft) gsap.set(helloLeft, { position: "absolute", top: "50%", right: "50%", yPercent: -50, marginRight: "1vw", opacity: 0, x: 20 });
      if (helloRight) gsap.set(helloRight, { position: "absolute", top: "50%", left: "50%", yPercent: -50, marginLeft: "1vw", opacity: 0, x: -20 });
    }
    
    if(navbar) gsap.set(navbar, { opacity: 0 }); 
    if(heroImg1) gsap.set(heroImg1, { opacity: 0 }); 
    if(heroImg2) gsap.set(heroImg2, { opacity: 0 }); 
    if(heroText) gsap.set(heroText, { opacity: 0 }); 
    if(extraImg1) gsap.set(extraImg1, { opacity: 0 }); 
    if(extraImg2) gsap.set(extraImg2, { opacity: 0 }); 

    document.body.style.overflow = "hidden";

    // TIMELINE GSAP
    const tl = gsap.timeline({
      delay: 0.1, 
      onComplete: () => {
        if (loadingOverlay) {
          gsap.to(loadingOverlay, { 
            opacity: 0, 
            duration: 0.3, 
            onComplete: () => {
              gsap.set(loadingOverlay, { display: "none" });
              document.body.style.overflow = ""; 
            }
          });
        } else {
          document.body.style.overflow = ""; 
        }
      }
    });

    if (firstText && firstFrame && helloLeft && holeWrap && holeImg) {
      tl.to(firstText, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" })
        .to(firstText, { scale: 0.94, opacity: 0, duration: 0.4, ease: "power2.out" }, "+=0.3")
        .set(firstFrame, { display: "none" })
        
        // Retorna a posição X ou Y a zero suavemente
        .to([helloLeft, helloRight], { opacity: 1, x: 0, y: 0, duration: 0.5, ease: "power2.out" }, "-=0.2")
        
        .to(holeWrap, { width: holeWidth, height: holeHeight, duration: 0.6, ease: "power3.out" }, "<");

      // Direciona o empurrão (Eixo Y no mobile, Eixo X no desktop)
      if (isMobile) {
        tl.to(helloLeft, { marginBottom: pushAmount, duration: 0.6, ease: "power3.out" }, "<")
          .to(helloRight, { marginTop: pushAmount, duration: 0.6, ease: "power3.out" }, "<");
      } else {
        tl.to(helloLeft, { marginRight: pushAmount, duration: 0.6, ease: "power3.out" }, "<")
          .to(helloRight, { marginLeft: pushAmount, duration: 0.6, ease: "power3.out" }, "<");
      }
        
      tl.to(holeWrap, { width: "100vw", height: "100vh", borderRadius: "0px", duration: 0.9, ease: "power3.inOut" }, "+=0.4")
        .to(holeImg, { scale: 1, duration: 0.9, ease: "power3.inOut" }, "<") 
        .to([helloLeft, helloRight], { opacity: 0, scale: 0.9, duration: 0.3, ease: "power2.in" }, "<+=0.2");
    }

    const imgs = [heroImg1, heroImg2].filter(Boolean);
    const extras = [heroText, extraImg1, extraImg2].filter(Boolean);

    const timing = (firstText && holeWrap) ? "-=0.4" : 0; 

    if (navbar) tl.fromTo(navbar, { yPercent: -100, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.8, ease: "power3.out" }, timing);
    if (imgs.length) tl.fromTo(imgs, { y: 150, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8, ease: "power3.out" }, "<");
    if (extras.length) tl.fromTo(extras, { opacity: 0 }, { opacity: 1, duration: 0.8, ease: "power2.inOut" }, "-=0.5");
  }

  runIntroAnimation();

  const observer = new MutationObserver((mutations) => {
    const checkHero = document.querySelector("#hero-text");
    if (checkHero && checkHero.dataset.animado !== "true") {
      runIntroAnimation();
    }
  });

  observer.observe(document.documentElement, { childList: true, subtree: true });
})();

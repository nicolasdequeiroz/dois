(function() {
  function initMobileMenu() {
    const siteNavbar = document.getElementById('site-navbar');
    const menuBtn = document.getElementById('menu-btn');
    const menuLinks = document.getElementById('menu-links');
    const menuCta = document.getElementById('menu-cta');
    
    if (!menuBtn || !menuLinks || !siteNavbar || menuBtn.dataset.menuInit === "true") return;

    let menuOpen = false;
    const isMobile = window.matchMedia("(max-width: 1023px)");

    function handleResize(e) {
      if (e.matches) {
        siteNavbar.style.overflow = 'visible';
        
        // Removidos os filtros de blur do clearProps
        gsap.set([menuLinks, menuCta], { 
          opacity: 0, 
          y: -10, 
          display: 'none', 
          clearProps: "position,top,left,right,width,backgroundColor,padding,flexDirection,alignItems,gap" 
        });
        
        const links = menuLinks.querySelectorAll('a');
        gsap.set(links, { clearProps: "margin,padding,fontSize" });
        
        menuOpen = false;
      } else {
        siteNavbar.style.overflow = ''; 
        gsap.set([menuLinks, menuCta], { clearProps: "all" });
        const links = menuLinks.querySelectorAll('a');
        gsap.set(links, { clearProps: "all" });
        menuOpen = false;
      }
    }

    handleResize(isMobile);
    isMobile.addListener(handleResize);

    menuBtn.style.cursor = 'pointer';
    
    menuBtn.addEventListener('click', (event) => {
      if (!isMobile.matches) return;
      event.stopPropagation(); 

      const navHeight = siteNavbar.offsetHeight;

      if (menuOpen) {
        // Fechar Menu
        gsap.to([menuLinks, menuCta], {
          y: -10,
          opacity: 0,
          duration: 0.3,
          ease: "power2.in",
          onComplete: () => gsap.set([menuLinks, menuCta], { display: 'none' })
        });
      } else {
        // Abrir Menu
        gsap.set(menuLinks, { 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'flex-start',
          gap: '4px', 
          position: 'absolute', 
          top: `${navHeight}px`, 
          left: '16px',  
          right: '16px', 
          width: 'auto', 
          // Fundo chapado em 95% (cinza 900 quase sem transparência)
          backgroundColor: 'rgba(23, 23, 23, 0.95)',
          padding: '24px 24px 80px 24px', 
          borderRadius: '16px',
          zIndex: 90
        });

        const links = menuLinks.querySelectorAll('a');
        gsap.set(links, { 
            margin: '0', 
            paddingTop: '6px', 
            paddingBottom: '6px', 
            fontSize: '14px' 
        });

        const menuHeight = menuLinks.offsetHeight; 
        
        gsap.set(menuCta, { 
          display: 'flex',
          position: 'absolute',
          top: `${navHeight + menuHeight - 64}px`, 
          left: '40px', 
          xPercent: 0, 
          zIndex: 91
        });

        gsap.to([menuLinks, menuCta], {
          y: 0,
          opacity: 1,
          duration: 0.4,
          ease: "power3.out",
          stagger: 0.05
        });
      }
      menuOpen = !menuOpen;
    });

    document.addEventListener('click', (event) => {
      if (menuOpen && isMobile.matches && !menuLinks.contains(event.target) && !menuCta.contains(event.target) && !menuBtn.contains(event.target)) {
        gsap.to([menuLinks, menuCta], {
          y: -10,
          opacity: 0,
          duration: 0.3,
          ease: "power2.in",
          onComplete: () => gsap.set([menuLinks, menuCta], { display: 'none' })
        });
        menuOpen = false;
      }
    });

    menuBtn.dataset.menuInit = "true";
  }

  initMobileMenu();

  const observer = new MutationObserver(() => {
    const btn = document.getElementById('menu-btn');
    if (btn && btn.dataset.menuInit !== "true") {
      initMobileMenu();
    }
  });
  
  observer.observe(document.documentElement, { childList: true, subtree: true });
})();

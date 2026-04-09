/**
 * App Shell - Controle da navegação lateral (sidebar)
 * Compatível com Chrome, Firefox, Safari, Edge e navegadores mobile
 */

(function() {
    'use strict';

    function init() {
        var hamburgerBtn = document.getElementById('hamburgerBtn');
        var sidebar = document.getElementById('sidebar');
        var sidebarOverlay = document.getElementById('sidebarOverlay');
        var sidebarCloseBtn = document.getElementById('sidebarCloseBtn');

        if (!sidebar || !sidebarOverlay) return;

        function openSidebar() {
            sidebar.classList.add('active');
            sidebarOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            document.documentElement.style.overflow = 'hidden';
            // Focus trap: focar no botão fechar
            if (sidebarCloseBtn) {
                setTimeout(function() { sidebarCloseBtn.focus(); }, 300);
            }
        }

        function closeSidebar() {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
            document.documentElement.style.overflow = '';
            // Retornar foco ao hamburguer
            if (hamburgerBtn) {
                hamburgerBtn.focus();
            }
        }

        function toggleSidebar() {
            if (sidebar.classList.contains('active')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        }

        // Botão hamburguer
        if (hamburgerBtn) {
            hamburgerBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                toggleSidebar();
            });
        }

        // Botão fechar da sidebar (X)
        if (sidebarCloseBtn) {
            sidebarCloseBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeSidebar();
            });
        }

        // Overlay - fechar ao clicar
        sidebarOverlay.addEventListener('click', function(e) {
            e.preventDefault();
            closeSidebar();
        });

        // Overlay - fechar ao tocar (mobile)
        sidebarOverlay.addEventListener('touchstart', function(e) {
            closeSidebar();
        }, { passive: true });

        // Fechar sidebar ao clicar em um link do menu
        var navLinks = sidebar.querySelectorAll('.nav-link-custom');
        for (var i = 0; i < navLinks.length; i++) {
            navLinks[i].addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    closeSidebar();
                }
            });
        }

        // Fechar sidebar no resize para desktop (com debounce)
        var resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (window.innerWidth > 768) {
                    closeSidebar();
                }
            }, 250);
        });

        // Scroll interno da sidebar sem afetar o body
        sidebar.addEventListener('touchmove', function(e) {
            e.stopPropagation();
        }, { passive: true });

        // ESC fecha a sidebar
        document.addEventListener('keydown', function(e) {
            if ((e.key === 'Escape' || e.keyCode === 27) && sidebar.classList.contains('active')) {
                closeSidebar();
            }
        });
    }

    // Iniciar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();


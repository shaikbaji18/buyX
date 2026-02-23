/* =============================================
   XAVIER MOBILES - PRO UI INTERACTIONS
   Theme Switcher, Animations & Effects
   ============================================= */

document.addEventListener('DOMContentLoaded', function() {
    
    // ================================
    // THEME SWITCHER
    // ================================
    const themeToggle = document.getElementById('theme-toggle');
    
    // Check for saved theme preference or default to dark
    const savedTheme = localStorage.getItem('xavier-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Save to localStorage
            localStorage.setItem('xavier-theme', newTheme);
            
            // Apply theme
            document.documentElement.setAttribute('data-theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
    
    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'light') {
            icon.className = 'fas fa-moon';
        } else {
            icon.className = 'fas fa-sun';
        }
    }
    
    // ================================
    // REVEAL ANIMATIONS ON SCROLL
    // ================================
    const revealElements = document.querySelectorAll('.reveal, .fade-in, .scale-in');
    
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    revealElements.forEach(el => {
        revealObserver.observe(el);
    });
    
    // ================================
    // CARD HOVER EFFECTS
    // ================================
    const cards = document.querySelectorAll('.card-glass');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.zIndex = '10';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.zIndex = '1';
        });
    });
    
    // ================================
    // SMOOTH SCROLL
    // ================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ================================
    // NAVBAR SCROLL EFFECT
    // ================================
    const navbar = document.querySelector('.navbar-glass');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.style.backdropFilter = 'blur(30px)';
                navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.3)';
            } else {
                navbar.style.backdropFilter = 'blur(20px)';
                navbar.style.boxShadow = 'none';
            }
        });
    }
    
    // ================================
    // TOAST NOTIFICATIONS
    // ================================
    window.showToast = function(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `alert-glass alert-${type}`;
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-20px)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };
    
    // ================================
    // AUTO-DISMISS ALERTS
    // ================================
    const alerts = document.querySelectorAll('.alert-glass');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    // ================================
    // PRELOAD ANIMATIONS
    // ================================
    window.addEventListener('load', () => {
        document.body.classList.add('loaded');
        
        // Trigger initial animations with stagger
        setTimeout(() => {
            revealElements.forEach((el, index) => {
                setTimeout(() => {
                    el.classList.add('active');
                }, index * 100);
            });
        }, 100);
    });
});

/* ================================
 * THEME DETECTION FOR SYSTEM PREFERENCE
 * ================================ */
if (!localStorage.getItem('xavier-theme')) {
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    if (prefersDarkScheme.matches) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('xavier-theme', 'dark');
    }
    
    prefersDarkScheme.addEventListener('change', (e) => {
        if (!localStorage.getItem('xavier-theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('xavier-theme', newTheme);
        }
    });
}

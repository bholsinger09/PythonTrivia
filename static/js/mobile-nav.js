/**
 * Mobile Navigation Enhancement
 * Improves mobile UX with responsive navigation and touch interactions
 */

class MobileNavManager {
    constructor() {
        this.navToggle = null;
        this.navLinks = null;
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        this.createMobileToggle();
        this.setupEventListeners();
        this.enhanceTouch();
    }
    
    createMobileToggle() {
        // Check if we need to create mobile navigation
        const navbar = document.querySelector('.nav-container');
        const existingToggle = document.querySelector('.mobile-nav-toggle');
        
        if (!navbar || existingToggle) return;
        
        // Create mobile toggle button
        this.navToggle = document.createElement('button');
        this.navToggle.className = 'mobile-nav-toggle';
        this.navToggle.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        this.navToggle.setAttribute('aria-label', 'Toggle navigation menu');
        
        // Get nav links
        this.navLinks = document.querySelector('.nav-links');
        
        // Insert toggle button
        navbar.appendChild(this.navToggle);
        
        // Add mobile classes
        document.body.classList.add('mobile-nav-enhanced');
    }
    
    setupEventListeners() {
        if (!this.navToggle || !this.navLinks) return;
        
        // Toggle button click
        this.navToggle.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleNav();
        });
        
        // Close nav when clicking on links
        this.navLinks.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-link')) {
                this.closeNav();
            }
        });
        
        // Close nav when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && 
                !this.navToggle.contains(e.target) && 
                !this.navLinks.contains(e.target)) {
                this.closeNav();
            }
        });
        
        // Close nav on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeNav();
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768 && this.isOpen) {
                this.closeNav();
            }
        });
    }
    
    toggleNav() {
        if (this.isOpen) {
            this.closeNav();
        } else {
            this.openNav();
        }
    }
    
    openNav() {
        this.isOpen = true;
        this.navToggle.classList.add('active');
        this.navLinks.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
        
        // Add animation classes to nav items
        const navItems = this.navLinks.querySelectorAll('.nav-link');
        navItems.forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
            item.classList.add('animate-slide-in');
        });
    }
    
    closeNav() {
        this.isOpen = false;
        this.navToggle.classList.remove('active');
        this.navLinks.classList.remove('active');
        document.body.style.overflow = '';
        
        // Remove animation classes
        const navItems = this.navLinks.querySelectorAll('.nav-link');
        navItems.forEach((item) => {
            item.style.animationDelay = '';
            item.classList.remove('animate-slide-in');
        });
    }
    
    enhanceTouch() {
        // Add touch enhancements for better mobile experience
        const buttons = document.querySelectorAll('.btn, .btn-choice');
        
        buttons.forEach(button => {
            // Add touch ripple effect
            button.addEventListener('touchstart', this.createRipple.bind(this));
            
            // Prevent double-tap zoom on buttons
            button.addEventListener('touchend', (e) => {
                e.preventDefault();
                button.click();
            });
        });
        
        // Enhance swipe gestures on flip cards
        const flipCards = document.querySelectorAll('.flip-card');
        flipCards.forEach(card => {
            this.addSwipeGestures(card);
        });
    }
    
    createRipple(e) {
        const button = e.currentTarget;
        const ripple = document.createElement('div');
        
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.touches[0].clientX - rect.left - size / 2;
        const y = e.touches[0].clientY - rect.top - size / 2;
        
        ripple.className = 'ripple-effect';
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple-animation 0.6s ease;
            pointer-events: none;
            z-index: 1;
        `;
        
        button.style.position = 'relative';
        button.appendChild(ripple);
        
        // Remove ripple after animation
        setTimeout(() => {
            if (ripple.parentElement) {
                ripple.remove();
            }
        }, 600);
    }
    
    addSwipeGestures(card) {
        let startX = 0;
        let startY = 0;
        let threshold = 50; // Minimum swipe distance
        
        card.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        card.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const deltaX = Math.abs(endX - startX);
            const deltaY = Math.abs(endY - startY);
            
            // Horizontal swipe (left/right) - flip card
            if (deltaX > threshold && deltaX > deltaY) {
                card.click(); // Trigger flip
            }
            
            startX = 0;
            startY = 0;
        });
    }
}

// Add ripple animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple-animation {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .mobile-nav-enhanced .nav-link {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .mobile-nav-enhanced .nav-link:hover {
        background: rgba(79, 70, 229, 0.1);
    }
    
    @media (max-width: 768px) {
        .nav-links.active .nav-link {
            opacity: 0;
            transform: translateX(20px);
            animation: slideInMobile 0.3s ease forwards;
        }
        
        @keyframes slideInMobile {
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
    }
`;

document.head.appendChild(style);

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.mobileNavManager) {
            window.mobileNavManager = new MobileNavManager();
        }
    });
} else {
    if (!window.mobileNavManager) {
        window.mobileNavManager = new MobileNavManager();
    }
}
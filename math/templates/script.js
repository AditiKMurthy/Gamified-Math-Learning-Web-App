// iSpace Math - Main JavaScript File

// Global variables
let isUserLoggedIn = false;

// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    console.log('iSpace Math initialized');
    
    // Initialize the application
    initApp();
    
    // Add event listeners
    setupEventListeners();
    
    // Check user authentication status
    checkUserAuth();

    // Shared logout functionality for all pages
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
                    localStorage.removeItem('ispace_username');
        localStorage.removeItem('ispace_auth_token');
        window.location.href = '/';
        });
    }
});

// Initialize the application
function initApp() {
    // Add stars to the background for space effect
    createStars();
    
    // Initialize any charts if they exist
    initCharts();
}

// Setup event listeners
function setupEventListeners() {
    // Navigation link event listeners
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Add click effect but don't prevent navigation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
            
            // Allow the default navigation to proceed
            // Don't call e.preventDefault()
        });
    });
    
    // Add hover effects for interactive elements
    addHoverEffects();
}

// Check user authentication status
function checkUserAuth() {
    // This would typically check localStorage, cookies, or make an API call
    // For now, we'll simulate checking for a stored token
    const authToken = localStorage.getItem('ispace_auth_token');
    
    if (authToken) {
        isUserLoggedIn = true;
    } else {
        isUserLoggedIn = false;
    }
}



// Create animated stars in the background
function createStars() {
    const header = document.querySelector('.header');
    const numStars = 20;
    
    for (let i = 0; i < numStars; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.animationDelay = Math.random() * 2 + 's';
        star.style.animationDuration = (Math.random() * 2 + 1) + 's';
        header.appendChild(star);
    }
}

// Initialize charts (placeholder for future chart functionality)
function initCharts() {
    // This function will be used to initialize Chart.js charts
    // when they are added to the application
    console.log('Charts ready for initialization');
}

// Add hover effects to interactive elements
function addHoverEffects() {
    const interactiveElements = document.querySelectorAll('button, .nav-link, .clickable');
    
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });
}

// Utility function to show loading state
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="loading">Loading...</div>';
        element.classList.add('loading-state');
    }
}

// Utility function to hide loading state
function hideLoading(element) {
    if (element) {
        element.classList.remove('loading-state');
    }
}

// Utility function to show notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 10px;
        color: #ffffff;
        font-family: 'Orbitron', monospace;
        z-index: 1000;
        backdrop-filter: blur(10px);
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const notificationStyles = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .loading-state {
        opacity: 0.7;
        pointer-events: none;
    }
    
    .loading {
        text-align: center;
        padding: 2rem;
        color: #00ffff;
        font-weight: 700;
    }
`;

// Inject notification styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Export functions for use in other modules
window.iSpaceMath = {
    showNotification,
    showLoading,
    hideLoading,
    checkUserAuth,
    isUserLoggedIn: () => isUserLoggedIn
};

// Function to highlight current page in navigation
function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        
        // Remove active class from all links
        link.classList.remove('active');
        
        // Check if this link matches the current page
        if (currentPage === linkPath || 
            (currentPage === '' && linkPath === 'index.html') ||
            (currentPage === 'index.html' && linkPath === 'index.html')) {
            link.classList.add('active');
        }
    });
}

// === Level Lock/Unlock Logic for Home Page ===

document.addEventListener('DOMContentLoaded', function() {
    // Only run on home page
    if (!document.getElementById('level-map-overlay')) return;

    let currentTopic = null;
    const overlay = document.getElementById('level-map-overlay');
    const easyBtn = document.getElementById('level-easy');
    const mediumBtn = document.getElementById('level-medium');
    const hardBtn = document.getElementById('level-hard');
    const lockEasy = document.getElementById('lock-easy');
    const lockMedium = document.getElementById('lock-medium');
    const lockHard = document.getElementById('lock-hard');

    // Helper: get progress from localStorage
    function getProgress() {
        return JSON.parse(localStorage.getItem('ispace_progress') || '{}');
    }
    // Helper: set progress to localStorage
    function setProgress(progress) {
        localStorage.setItem('ispace_progress', JSON.stringify(progress));
    }
    // Helper: get topic progress (easy/medium/hard completed)
    function getTopicProgress(topic) {
        const progress = getProgress();
        return progress[topic] || { easy: false, medium: false, hard: false };
    }
    // Helper: set topic progress
    function setTopicProgress(topic, level) {
        const progress = getProgress();
        if (!progress[topic]) progress[topic] = { easy: false, medium: false, hard: false };
        progress[topic][level] = true;
        setProgress(progress);
    }

    // Update lock UI for the overlay
    function updateLevelLocks(topic) {
        const prog = getTopicProgress(topic);
        
        // Easy is always unlocked
        easyBtn.classList.remove('locked');
        lockEasy.style.display = 'none';
                        easyBtn.href = `/quiz?topic=${topic}&level=easy`;
        easyBtn.style.pointerEvents = 'auto';
        easyBtn.style.opacity = '1';
        
        // Medium: unlocked if easy completed
        if (prog.easy) {
            mediumBtn.classList.remove('locked');
            lockMedium.style.display = 'none';
                            mediumBtn.href = `/quiz?topic=${topic}&level=medium`;
            mediumBtn.style.pointerEvents = 'auto';
            mediumBtn.style.opacity = '1';
        } else {
            mediumBtn.classList.add('locked');
            lockMedium.style.display = 'inline';
            mediumBtn.href = '#';
            mediumBtn.style.pointerEvents = 'none';
            mediumBtn.style.opacity = '0.5';
        }
        
        // Hard: unlocked if medium completed
        if (prog.medium) {
            hardBtn.classList.remove('locked');
            lockHard.style.display = 'none';
                            hardBtn.href = `/quiz?topic=${topic}&level=hard`;
            hardBtn.style.pointerEvents = 'auto';
            hardBtn.style.opacity = '1';
        } else {
            hardBtn.classList.add('locked');
            lockHard.style.display = 'inline';
            hardBtn.href = '#';
            hardBtn.style.pointerEvents = 'none';
            hardBtn.style.opacity = '0.5';
        }
    }

    // When a planet is clicked, show overlay and update locks
    document.querySelectorAll('.planet-with-label').forEach(function(planet) {
        planet.addEventListener('click', function() {
            currentTopic = this.getAttribute('data-topic');
            updateLevelLocks(currentTopic);
        });
    });

    // (Optional) Prevent navigation for locked levels (extra safety)
    [mediumBtn, hardBtn].forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (btn.classList.contains('locked')) {
                e.preventDefault();
            }
        });
    });

    // Expose a function to mark a level as completed (to be called after quiz)
    window.iSpaceMath = window.iSpaceMath || {};
    window.iSpaceMath.completeLevel = function(topic, level) {
        setTopicProgress(topic, level);
    };
});

// Call the function when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    highlightCurrentPage();
}); 
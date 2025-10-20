// Main JavaScript file for Turkey Palm Readings

// Global app object
const CosmicInsights = {
    init: function() {
        this.setupEventListeners();
        this.setupAnimations();
        this.setupTooltips();
        this.checkNotificationPermissions();
    },

    setupEventListeners: function() {
        // Form validation
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });

        // Mood tracker emojis
        document.querySelectorAll('.mood-emoji').forEach(emoji => {
            emoji.addEventListener('click', this.selectMoodEmoji.bind(this));
        });

        // Theme preference change handler
        const themeSelect = document.querySelector('select[name="theme_preference"]');
        if (themeSelect) {
            themeSelect.addEventListener('change', this.handleThemeChange.bind(this));
        }

        // Navigation enhancement
        this.setupSmoothScrolling();
        
        // Auto-save functionality for forms
        this.setupAutoSave();
    },

    setupAnimations: function() {
        // Intersection Observer for animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        });

        document.querySelectorAll('.card, .feature-box').forEach(el => {
            observer.observe(el);
        });
    },

    setupTooltips: function() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    checkNotificationPermissions: function() {
        if ('Notification' in window && 'serviceWorker' in navigator) {
            // Check if user has already dismissed the notification prompt
            const dismissed = localStorage.getItem('notificationPromptDismissed');
            if (!dismissed && Notification.permission === 'default') {
                // Disabled auto-prompt to avoid annoying users
                // this.showNotificationPrompt();
            }
        }
    },

    showNotificationPrompt: function() {
        const promptModal = `
            <div class="modal fade" id="notificationModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-bell"></i> Daily Horoscope Notifications
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Would you like to receive daily horoscope notifications?</p>
                            <p class="text-muted small">You can change this setting anytime in your profile.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" onclick="CosmicInsights.dismissNotificationPrompt()">Not Now</button>
                            <button type="button" class="btn btn-primary" onclick="CosmicInsights.enableNotifications()">Enable</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', promptModal);
        const modal = new bootstrap.Modal(document.getElementById('notificationModal'));
        
        // Show after a delay to not be intrusive
        setTimeout(() => modal.show(), 3000);
    },

    enableNotifications: function() {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                this.showSuccessMessage('Notifications enabled! You\'ll receive your daily horoscope.');
                // Close modal
                bootstrap.Modal.getInstance(document.getElementById('notificationModal')).hide();
            }
        });
    },

    dismissNotificationPrompt: function() {
        // Remember that user dismissed the prompt
        localStorage.setItem('notificationPromptDismissed', 'true');
    },

    handleFormSubmit: function(event) {
        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
        
        if (submitButton) {
            // Show loading state
            this.setLoadingState(submitButton, true);
            
            // Re-enable after a delay (in case of errors)
            setTimeout(() => {
                this.setLoadingState(submitButton, false);
            }, 5000);
        }
    },

    setLoadingState: function(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        } else {
            button.disabled = false;
            button.innerHTML = button.getAttribute('data-original-text') || 'Submit';
        }
    },

    selectMoodEmoji: function(event) {
        const emoji = event.target;
        const container = emoji.closest('.mood-selector');
        
        // Remove previous selection
        container.querySelectorAll('.mood-emoji').forEach(e => {
            e.classList.remove('selected');
        });
        
        // Add selection to clicked emoji
        emoji.classList.add('selected');
        
        // Update hidden input if exists
        const hiddenInput = container.querySelector('input[type="hidden"]');
        if (hiddenInput) {
            hiddenInput.value = emoji.getAttribute('data-mood');
        }
    },

    handleThemeChange: function(event) {
        const selectedTheme = event.target.value;
        
        // Immediately update the body data-theme attribute
        document.body.setAttribute('data-theme', selectedTheme);
        
        // Optional: Show a brief feedback
        this.showThemeChangeNotification(selectedTheme);
    },

    showThemeChangeNotification: function(theme) {
        const themeNames = {
            'auto': 'Auto (System)',
            'light': 'Light',
            'dark': 'Dark'
        };
        
        // Create a temporary notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 250px;';
        notification.innerHTML = `
            <i class="fas fa-palette me-2"></i>
            Theme changed to ${themeNames[theme]}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    },

    setupSmoothScrolling: function() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
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
    },

    setupAutoSave: function() {
        const autoSaveForms = document.querySelectorAll('[data-auto-save]');
        
        autoSaveForms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    this.saveFormData(form);
                });
            });
        });
        
        // Load saved data on page load
        autoSaveForms.forEach(form => {
            this.loadFormData(form);
        });
    },

    saveFormData: function(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        localStorage.setItem(`form_${form.id}`, JSON.stringify(data));
        this.showAutoSaveIndicator();
    },

    loadFormData: function(form) {
        const savedData = localStorage.getItem(`form_${form.id}`);
        
        if (savedData) {
            const data = JSON.parse(savedData);
            
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && input.type !== 'submit') {
                    input.value = data[key];
                }
            });
        }
    },

    showAutoSaveIndicator: function() {
        let indicator = document.getElementById('auto-save-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'auto-save-indicator';
            indicator.className = 'position-fixed bottom-0 end-0 m-3 alert alert-success alert-dismissible';
            indicator.style.zIndex = '9999';
            indicator.innerHTML = `
                <i class="fas fa-check"></i> Auto-saved
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(indicator);
        }
        
        indicator.style.display = 'block';
        
        setTimeout(() => {
            indicator.style.display = 'none';
        }, 2000);
    },

    showSuccessMessage: function(message) {
        this.showMessage(message, 'success');
    },

    showErrorMessage: function(message) {
        this.showMessage(message, 'danger');
    },

    showMessage: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },

    // API interaction helpers
    makeAPICall: function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        return fetch(url, mergedOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('API call failed:', error);
                this.showErrorMessage('Something went wrong. Please try again.');
                throw error;
            });
    },

    // Horoscope sharing functionality
    shareHoroscope: function(content, title = 'My Daily Horoscope') {
        if (navigator.share) {
            navigator.share({
                title: title,
                text: content,
                url: window.location.href
            }).catch(err => {
                console.log('Error sharing:', err);
                this.copyToClipboard(content);
            });
        } else {
            this.copyToClipboard(content);
        }
    },

    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showSuccessMessage('Copied to clipboard!');
            }).catch(() => {
                this.fallbackCopyToClipboard(text);
            });
        } else {
            this.fallbackCopyToClipboard(text);
        }
    },

    fallbackCopyToClipboard: function(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showSuccessMessage('Copied to clipboard!');
        } catch (err) {
            this.showErrorMessage('Unable to copy to clipboard');
        }
        
        document.body.removeChild(textArea);
    },

    // Mood tracking functionality
    submitMoodEntry: function(formData) {
        return this.makeAPICall('/submit_mood', {
            method: 'POST',
            body: formData
        });
    },

    // Chart interactions
    setupChartInteractions: function() {
        const chartElements = document.querySelectorAll('.planet-position, .aspect-line');
        
        chartElements.forEach(element => {
            element.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
                this.style.transition = 'transform 0.2s ease';
            });
            
            element.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        });
    },

    // Initialize date/time pickers
    initializeDateTimePickers: function() {
        // Add any custom date/time picker initialization here
        const dateInputs = document.querySelectorAll('input[type="date"]');
        const timeInputs = document.querySelectorAll('input[type="time"]');
        
        dateInputs.forEach(input => {
            // Set max date to today
            input.max = new Date().toISOString().split('T')[0];
        });
    },

    // Keyboard shortcuts
    setupKeyboardShortcuts: function() {
        document.addEventListener('keydown', (e) => {
            // Alt + H for home/dashboard
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                window.location.href = '/';
            }
            
            // Alt + M for mood tracker
            if (e.altKey && e.key === 'm') {
                e.preventDefault();
                window.location.href = '/mood';
            }
            
            // Alt + C for natal chart
            if (e.altKey && e.key === 'c') {
                e.preventDefault();
                window.location.href = '/natal_chart';
            }
        });
    },

    // Theme toggling (if implementing dark mode)
    initializeThemeToggle: function() {
        const themeToggle = document.getElementById('theme-toggle');
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                document.body.classList.toggle('dark-theme');
                localStorage.setItem('dark-theme', document.body.classList.contains('dark-theme'));
            });
            
            // Load saved theme
            if (localStorage.getItem('dark-theme') === 'true') {
                document.body.classList.add('dark-theme');
            }
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    CosmicInsights.init();
    CosmicInsights.initializeDateTimePickers();
    CosmicInsights.setupKeyboardShortcuts();
    CosmicInsights.initializeThemeToggle();
    CosmicInsights.setupChartInteractions();
});

// Error handling for unhandled promises
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    CosmicInsights.showErrorMessage('An unexpected error occurred. Please refresh the page and try again.');
});

// Service Worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
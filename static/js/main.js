// Main JavaScript for QRAIL

// Global variables
let csrfToken = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Get CSRF token
    csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    // Initialize tooltips
    initializeTooltips();

    // Initialize form validation
    initializeFormValidation();

    // Initialize auto-refresh
    initializeAutoRefresh();

    // Initialize search functionality
    initializeSearch();

    // Initialize notifications
    initializeNotifications();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');

    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });
}

// Initialize auto-refresh for dashboard
function initializeAutoRefresh() {
    const refreshElements = document.querySelectorAll('[data-auto-refresh]');

    refreshElements.forEach(function (element) {
        const interval = parseInt(element.dataset.autoRefresh) || 30000;

        setInterval(function () {
            refreshElement(element);
        }, interval);
    });
}

// Refresh element content
function refreshElement(element) {
    const url = element.dataset.refreshUrl;
    if (!url) return;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            updateElementContent(element, data);
        })
        .catch(error => {
            console.error('Error refreshing element:', error);
        });
}

// Update element content based on data
function updateElementContent(element, data) {
    const type = element.dataset.refreshType || 'text';

    switch (type) {
        case 'text':
            element.textContent = data.value || data;
            break;
        case 'html':
            element.innerHTML = data.html || data;
            break;
        case 'counter':
            animateCounter(element, data.count || data);
            break;
        case 'badge':
            updateBadge(element, data);
            break;
    }
}

// Animate counter
function animateCounter(element, targetValue) {
    const currentValue = parseInt(element.textContent) || 0;
    const increment = (targetValue - currentValue) / 20;
    let current = currentValue;

    const timer = setInterval(function () {
        current += increment;
        if ((increment > 0 && current >= targetValue) || (increment < 0 && current <= targetValue)) {
            current = targetValue;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 50);
}

// Update badge
function updateBadge(element, data) {
    element.textContent = data.text || data;
    element.className = `badge bg-${data.type || 'primary'}`;
}

// Initialize search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input');

    searchInputs.forEach(function (input) {
        let searchTimeout;

        input.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function () {
                performSearch(input);
            }, 300);
        });
    });
}

// Perform search
function performSearch(input) {
    const query = input.value.trim();
    const searchUrl = input.dataset.searchUrl;

    if (!query || !searchUrl) return;

    fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(input, data);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

// Display search results
function displaySearchResults(input, data) {
    const resultsContainer = document.querySelector(input.dataset.resultsContainer);
    if (!resultsContainer) return;

    if (data.results && data.results.length > 0) {
        const html = data.results.map(item => `
            <div class="search-result-item p-2 border-bottom">
                <a href="${item.url}" class="text-decoration-none">
                    <strong>${item.title}</strong>
                    <br>
                    <small class="text-muted">${item.description}</small>
                </a>
            </div>
        `).join('');

        resultsContainer.innerHTML = html;
        resultsContainer.style.display = 'block';
    } else {
        resultsContainer.innerHTML = '<div class="p-2 text-muted">No results found</div>';
        resultsContainer.style.display = 'block';
    }
}

// Initialize notifications
function initializeNotifications() {
    // Check for new notifications every 30 seconds
    setInterval(checkNotifications, 30000);

    // Mark notifications as read when clicked
    document.addEventListener('click', function (e) {
        if (e.target.closest('.notification-item')) {
            const notificationId = e.target.closest('.notification-item').dataset.notificationId;
            if (notificationId) {
                markNotificationAsRead(notificationId);
            }
        }
    });
}

// Check for new notifications
function checkNotifications() {
    fetch('/api/notifications/')
        .then(response => response.json())
        .then(data => {
            updateNotificationBadge(data.filter(n => !n.is_read).length);
        })
        .catch(error => {
            console.error('Error checking notifications:', error);
        });
}

// Update notification badge
function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Mark notification as read
function markNotificationAsRead(notificationId) {
    fetch(`/api/notifications/${notificationId}/mark-read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI
                const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
                if (notificationElement) {
                    notificationElement.classList.remove('fw-bold');
                }
            }
        })
        .catch(error => {
            console.error('Error marking notification as read:', error);
        });
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();

    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    alertContainer.insertAdjacentHTML('beforeend', alertHtml);

    // Auto-dismiss after 5 seconds
    setTimeout(function () {
        const alert = alertContainer.lastElementChild;
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

function showLoading(element) {
    element.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Loading...</p></div>';
}

function hideLoading(element, content) {
    element.innerHTML = content;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function formatCurrency(amount, currency = 'INR') {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function () {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export functions for global use
window.QRAIL = {
    showAlert,
    showLoading,
    hideLoading,
    formatDate,
    formatCurrency,
    debounce,
    throttle
};

// Main Application JavaScript
document.addEventListener('DOMContentLoaded', function () {
    console.log('Python Trivia app loaded');

    // Global error handler for fetch requests
    window.handleFetchError = function (error, fallbackMessage = 'An error occurred') {
        console.error('Fetch error:', error);
        return fallbackMessage;
    };

    // Global success handler for operations
    window.showSuccessMessage = function (message, duration = 3000) {
        console.log('Success:', message);
        // You can implement a toast notification system here
    };

    // Global loading state manager
    window.setLoadingState = function (element, isLoading) {
        if (!element) return;

        if (isLoading) {
            element.disabled = true;
            element.classList.add('loading');
        } else {
            element.disabled = false;
            element.classList.remove('loading');
        }
    };

    // Utility function to validate form data
    window.validateForm = function (formElement) {
        const inputs = formElement.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }
        });

        return isValid;
    };

    // Clear form validation errors on input
    document.addEventListener('input', function (e) {
        if (e.target.matches('input.error')) {
            e.target.classList.remove('error');
        }
    });
});

// Service Worker Registration (if supported)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        navigator.serviceWorker.register('/sw.js')
            .then(function (registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function (registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

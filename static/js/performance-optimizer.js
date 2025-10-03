/**
 * Frontend Performance Optimizer
 * Implements lazy loading, asset optimization, and performance monitoring
 */

class PerformanceOptimizer {
    constructor() {
        this.intersectionObserver = null;
        this.performanceMetrics = {
            loadTime: 0,
            firstPaint: 0,
            firstContentfulPaint: 0,
            largestContentfulPaint: 0,
            cumulativeLayoutShift: 0,
            firstInputDelay: 0
        };
        
        this.resourceCache = new Map();
        this.criticalResourcesLoaded = false;
        
        this.init();
    }
    
    async init() {
        try {
            // Setup performance monitoring
            this.setupPerformanceMonitoring();
            
            // Setup lazy loading
            this.setupLazyLoading();
            
            // Setup asset optimization
            this.setupAssetOptimization();
            
            // Setup resource hints
            this.setupResourceHints();
            
            // Setup critical resource loading
            await this.loadCriticalResources();
            
            // Setup performance budgets
            this.setupPerformanceBudgets();
            
            // Setup adaptive loading
            this.setupAdaptiveLoading();
            
            console.log('🚀 Performance optimizer initialized');
        } catch (error) {
            console.error('❌ Performance optimizer initialization failed:', error);
            // Continue without performance optimization features
        }
    }
    
    // Performance Monitoring
    setupPerformanceMonitoring() {
        // Core Web Vitals monitoring
        if ('PerformanceObserver' in window) {
            this.observePaintMetrics();
            this.observeLayoutShiftMetrics();
            this.observeLargestContentfulPaint();
            this.observeFirstInputDelay();
        }
        
        // Navigation timing
        window.addEventListener('load', () => {
            this.measureNavigationTiming();
        });
        
        // Resource timing
        this.monitorResourceTiming();
        
        // Memory usage (if available)
        this.monitorMemoryUsage();
    }
    
    observePaintMetrics() {
        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach((entry) => {
                if (entry.name === 'first-paint') {
                    this.performanceMetrics.firstPaint = entry.startTime;
                } else if (entry.name === 'first-contentful-paint') {
                    this.performanceMetrics.firstContentfulPaint = entry.startTime;
                }
            });
        });
        
        observer.observe({ type: 'paint', buffered: true });
    }
    
    observeLargestContentfulPaint() {
        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            this.performanceMetrics.largestContentfulPaint = lastEntry.startTime;
        });
        
        observer.observe({ type: 'largest-contentful-paint', buffered: true });
    }
    
    observeLayoutShiftMetrics() {
        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach((entry) => {
                if (!entry.hadRecentInput) {
                    this.performanceMetrics.cumulativeLayoutShift += entry.value;
                }
            });
        });
        
        observer.observe({ type: 'layout-shift', buffered: true });
    }
    
    observeFirstInputDelay() {
        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach((entry) => {
                this.performanceMetrics.firstInputDelay = entry.processingStart - entry.startTime;
            });
        });
        
        observer.observe({ type: 'first-input', buffered: true });
    }
    
    measureNavigationTiming() {
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
            this.performanceMetrics.loadTime = navigation.loadEventEnd - navigation.loadEventStart;
            
            // Log performance metrics
            console.log('📊 Performance Metrics:', {
                'Load Time': `${Math.round(this.performanceMetrics.loadTime)}ms`,
                'First Paint': `${Math.round(this.performanceMetrics.firstPaint)}ms`,
                'First Contentful Paint': `${Math.round(this.performanceMetrics.firstContentfulPaint)}ms`,
                'Largest Contentful Paint': `${Math.round(this.performanceMetrics.largestContentfulPaint)}ms`,
                'Cumulative Layout Shift': this.performanceMetrics.cumulativeLayoutShift.toFixed(3),
                'First Input Delay': `${Math.round(this.performanceMetrics.firstInputDelay)}ms`
            });
            
            // Check against thresholds
            this.evaluatePerformance();
        }
    }
    
    evaluatePerformance() {
        const issues = [];
        
        // Core Web Vitals thresholds
        if (this.performanceMetrics.largestContentfulPaint > 2500) {
            issues.push('LCP > 2.5s (poor)');
        }
        if (this.performanceMetrics.firstInputDelay > 100) {
            issues.push('FID > 100ms (poor)');
        }
        if (this.performanceMetrics.cumulativeLayoutShift > 0.1) {
            issues.push('CLS > 0.1 (poor)');
        }
        if (this.performanceMetrics.firstContentfulPaint > 1800) {
            issues.push('FCP > 1.8s (poor)');
        }
        
        if (issues.length > 0) {
            console.warn('⚠️ Performance Issues:', issues);
            this.showPerformanceAlert(issues);
        } else {
            console.log('✅ Good performance metrics');
        }
    }
    
    monitorResourceTiming() {
        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach((entry) => {
                // Monitor slow resources
                if (entry.duration > 1000) {
                    console.warn(`🐌 Slow resource: ${entry.name} (${Math.round(entry.duration)}ms)`);
                }
                
                // Cache resource timing data
                this.resourceCache.set(entry.name, {
                    duration: entry.duration,
                    transferSize: entry.transferSize,
                    timestamp: Date.now()
                });
            });
        });
        
        observer.observe({ type: 'resource', buffered: true });
    }
    
    monitorMemoryUsage() {
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                const usage = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
                
                if (usage > 90) {
                    console.warn(`🧠 High memory usage: ${usage.toFixed(1)}%`);
                }
            }, 30000); // Check every 30 seconds
        }
    }
    
    // Lazy Loading Implementation
    setupLazyLoading() {
        // Intersection Observer for lazy loading
        this.intersectionObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        this.loadElement(entry.target);
                        this.intersectionObserver.unobserve(entry.target);
                    }
                });
            },
            {
                rootMargin: '50px' // Start loading 50px before element comes into view
            }
        );
        
        // Observe lazy-loadable elements
        this.observeLazyElements();
        
        // Setup lazy image loading
        this.setupLazyImages();
        
        // Setup lazy component loading
        this.setupLazyComponents();
    }
    
    observeLazyElements() {
        const lazyElements = document.querySelectorAll('[data-lazy]');
        lazyElements.forEach((element) => {
            this.intersectionObserver.observe(element);
        });
    }
    
    setupLazyImages() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        if ('loading' in HTMLImageElement.prototype) {
            // Native lazy loading support
            lazyImages.forEach((img) => {
                img.src = img.dataset.src;
                img.loading = 'lazy';
            });
        } else {
            // Fallback to Intersection Observer
            lazyImages.forEach((img) => {
                this.intersectionObserver.observe(img);
            });
        }
    }
    
    setupLazyComponents() {
        // Lazy load components that are not immediately visible
        const lazyComponents = document.querySelectorAll('[data-component]');
        
        lazyComponents.forEach((element) => {
            this.intersectionObserver.observe(element);
        });
    }
    
    loadElement(element) {
        // Load lazy images
        if (element.tagName === 'IMG' && element.dataset.src) {
            element.src = element.dataset.src;
            element.classList.add('loaded');
        }
        
        // Load lazy components
        if (element.dataset.component) {
            this.loadComponent(element, element.dataset.component);
        }
        
        // Load lazy content
        if (element.dataset.lazy) {
            this.loadContent(element, element.dataset.lazy);
        }
    }
    
    async loadComponent(element, componentName) {
        try {
            // Dynamically import component if needed
            const componentModule = await import(`/static/js/components/${componentName}.js`);
            const Component = componentModule.default;
            
            // Initialize component
            new Component(element);
            
            element.classList.add('component-loaded');
        } catch (error) {
            console.warn(`Failed to load component: ${componentName}`, error);
        }
    }
    
    async loadContent(element, contentUrl) {
        try {
            const response = await fetch(contentUrl);
            const content = await response.text();
            
            element.innerHTML = content;
            element.classList.add('content-loaded');
            
            // Initialize any scripts in the loaded content
            this.initializeLoadedScripts(element);
        } catch (error) {
            console.warn(`Failed to load content: ${contentUrl}`, error);
        }
    }
    
    // Asset Optimization
    setupAssetOptimization() {
        // Preload critical resources
        this.preloadCriticalAssets();
        
        // Setup resource bundling
        this.optimizeResourceLoading();
        
        // Setup image optimization
        this.setupImageOptimization();
        
        // Setup font optimization
        this.setupFontOptimization();
    }
    
    preloadCriticalAssets() {
        const criticalAssets = [
            { href: '/static/css/enhanced-style.css', as: 'style' },
            { href: '/static/js/app.js', as: 'script' },
            { href: '/static/js/advanced-features.js', as: 'script' }
        ];
        
        criticalAssets.forEach((asset) => {
            if (!document.querySelector(`link[href="${asset.href}"][rel="preload"]`)) {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.href = asset.href;
                link.as = asset.as;
                document.head.appendChild(link);
            }
        });
    }
    
    optimizeResourceLoading() {
        // Bundle small CSS files
        this.bundleSmallResources();
        
        // Setup HTTP/2 push hints
        this.setupPushHints();
        
        // Optimize script loading order
        this.optimizeScriptLoading();
    }
    
    bundleSmallResources() {
        // Identify and bundle small CSS files (simplified implementation)
        const cssLinks = document.querySelectorAll('link[rel="stylesheet"]');
        const smallCssFiles = [];
        
        cssLinks.forEach((link) => {
            if (link.href.includes('small-') || link.href.includes('component-')) {
                smallCssFiles.push(link.href);
            }
        });
        
        if (smallCssFiles.length > 2) {
            console.log(`📦 Found ${smallCssFiles.length} small CSS files that could be bundled`);
        }
    }
    
    setupPushHints() {
        // Add HTTP/2 server push hints for critical resources
        const criticalResources = [
            '/static/css/enhanced-style.css',
            '/static/js/app.js'
        ];
        
        criticalResources.forEach((resource) => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource;
            link.as = resource.endsWith('.css') ? 'style' : 'script';
            
            // Only add if not already present
            if (!document.querySelector(`link[href="${resource}"][rel="preload"]`)) {
                document.head.appendChild(link);
            }
        });
    }
    
    optimizeScriptLoading() {
        // Optimize script loading order for better performance
        const scripts = document.querySelectorAll('script[src]');
        const criticalScripts = [];
        const nonCriticalScripts = [];
        
        scripts.forEach((script) => {
            if (script.src.includes('app.js') || script.src.includes('performance-optimizer.js')) {
                criticalScripts.push(script);
            } else {
                nonCriticalScripts.push(script);
            }
        });
        
        // Mark non-critical scripts for deferred loading
        nonCriticalScripts.forEach((script) => {
            if (!script.defer && !script.async) {
                script.defer = true;
            }
        });
    }
    
    setupImageOptimization() {
        // Setup responsive images
        const images = document.querySelectorAll('img:not([srcset])');
        images.forEach((img) => {
            this.addResponsiveImageSupport(img);
        });
        
        // Setup WebP support detection
        this.detectWebPSupport();
    }
    
    addResponsiveImageSupport(img) {
        if (!img.src) return;
        
        // Generate different sizes (simplified example)
        const baseSrc = img.src;
        const srcset = [
            `${baseSrc}?w=320 320w`,
            `${baseSrc}?w=640 640w`,
            `${baseSrc}?w=1024 1024w`
        ].join(', ');
        
        img.srcset = srcset;
        img.sizes = '(max-width: 320px) 320px, (max-width: 640px) 640px, 1024px';
    }
    
    detectWebPSupport() {
        const webp = new Image();
        webp.onload = webp.onerror = () => {
            const support = webp.height === 2;
            document.documentElement.classList.add(support ? 'webp' : 'no-webp');
        };
        webp.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
    }
    
    setupFontOptimization() {
        // Font display optimization - just add CSS rules without preloading files that don't exist
        const style = document.createElement('style');
        style.textContent = `
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        `;
        document.head.appendChild(style);
    }
    
    // Resource Hints
    setupResourceHints() {
        // DNS prefetch for external domains
        const externalDomains = [
            'fonts.googleapis.com',
            'fonts.gstatic.com'
        ];
        
        externalDomains.forEach((domain) => {
            const link = document.createElement('link');
            link.rel = 'dns-prefetch';
            link.href = `//${domain}`;
            document.head.appendChild(link);
        });
        
        // Preconnect to critical origins
        const criticalOrigins = [
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com'
        ];
        
        criticalOrigins.forEach((origin) => {
            const link = document.createElement('link');
            link.rel = 'preconnect';
            link.href = origin;
            link.crossOrigin = 'anonymous';
            document.head.appendChild(link);
        });
    }
    
    // Critical Resource Loading
    async loadCriticalResources() {
        const criticalResources = [
            this.loadCriticalCSS(),
            this.loadCriticalJS(),
            this.loadCriticalFonts()
        ];
        
        try {
            await Promise.all(criticalResources);
            this.criticalResourcesLoaded = true;
            console.log('✅ Critical resources loaded');
            
            // Load non-critical resources
            this.loadNonCriticalResources();
        } catch (error) {
            console.error('❌ Failed to load critical resources:', error);
        }
    }
    
    async loadCriticalCSS() {
        // Inline critical CSS for above-the-fold content
        const criticalCSS = `
            /* Critical CSS for immediate rendering */
            body { font-family: 'Inter', system-ui, sans-serif; }
            .navbar { position: fixed; top: 0; width: 100%; z-index: 1000; }
            .main-content { margin-top: 80px; }
            .flip-card { width: 100%; max-width: 500px; height: 400px; }
        `;
        
        const style = document.createElement('style');
        style.textContent = criticalCSS;
        document.head.appendChild(style);
    }
    
    async loadCriticalJS() {
        // Load critical JavaScript modules
        const criticalModules = [
            '/static/js/app.js'
        ];
        
        return Promise.all(criticalModules.map(this.loadScript.bind(this)));
    }
    
    async loadCriticalFonts() {
        // Skip font loading since we're using Google Fonts via CSS import
        console.log('✅ Using Google Fonts via CSS import');
    }
    
    loadNonCriticalResources() {
        // Load non-critical resources after critical ones
        setTimeout(() => {
            this.loadSecondaryCSS();
            this.loadSecondaryJS();
            this.loadSecondaryImages();
        }, 100);
    }
    
    loadSecondaryCSS() {
        const secondaryCSS = [
            '/static/css/advanced-features.css'
        ];
        
        secondaryCSS.forEach((href) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.media = 'print';
            link.onload = () => { link.media = 'all'; };
            document.head.appendChild(link);
        });
    }
    
    loadSecondaryJS() {
        const secondaryJS = [
            '/static/js/mobile-nav.js',
            '/static/js/advanced-features.js'
        ];
        
        secondaryJS.forEach((src) => {
            this.loadScript(src);
        });
    }
    
    loadSecondaryImages() {
        // Load images that are not immediately visible
        const images = document.querySelectorAll('img[data-src]');
        images.forEach((img) => {
            if (!this.isInViewport(img)) {
                this.intersectionObserver.observe(img);
            }
        });
    }
    
    // Adaptive Loading
    setupAdaptiveLoading() {
        // Detect connection speed
        this.detectConnectionSpeed();
        
        // Adapt loading strategy based on device capabilities
        this.adaptToDeviceCapabilities();
        
        // Setup data saver mode
        this.setupDataSaverMode();
    }
    
    detectConnectionSpeed() {
        if ('connection' in navigator) {
            const connection = navigator.connection;
            const effectiveType = connection.effectiveType;
            
            // Adjust loading strategy based on connection
            switch (effectiveType) {
                case 'slow-2g':
                case '2g':
                    this.enableLowBandwidthMode();
                    break;
                case '3g':
                    this.enableMediumBandwidthMode();
                    break;
                case '4g':
                default:
                    this.enableHighBandwidthMode();
                    break;
            }
            
            console.log(`📡 Connection: ${effectiveType}`);
        }
    }
    
    enableLowBandwidthMode() {
        document.documentElement.classList.add('low-bandwidth');
        
        // Reduce image quality
        const images = document.querySelectorAll('img');
        images.forEach((img) => {
            if (img.src && !img.src.includes('quality=')) {
                img.src += (img.src.includes('?') ? '&' : '?') + 'quality=60';
            }
        });
        
        // Disable animations
        document.documentElement.classList.add('reduced-motion');
        
        console.log('📱 Low bandwidth mode enabled');
    }
    
    enableMediumBandwidthMode() {
        document.documentElement.classList.add('medium-bandwidth');
        console.log('📱 Medium bandwidth mode enabled');
    }
    
    enableHighBandwidthMode() {
        document.documentElement.classList.add('high-bandwidth');
        console.log('📱 High bandwidth mode enabled');
    }
    
    adaptToDeviceCapabilities() {
        // Detect device memory
        if ('deviceMemory' in navigator) {
            const memory = navigator.deviceMemory;
            
            if (memory < 4) {
                this.enableLowMemoryMode();
            }
            
            console.log(`🧠 Device memory: ${memory}GB`);
        }
        
        // Detect hardware concurrency
        if ('hardwareConcurrency' in navigator) {
            const cores = navigator.hardwareConcurrency;
            
            if (cores < 4) {
                this.enableLowPerformanceMode();
            }
            
            console.log(`⚡ CPU cores: ${cores}`);
        }
    }
    
    enableLowMemoryMode() {
        document.documentElement.classList.add('low-memory');
        
        // Reduce cache size
        if (this.resourceCache.size > 50) {
            const entries = Array.from(this.resourceCache.entries());
            entries.slice(0, -25).forEach(([key]) => {
                this.resourceCache.delete(key);
            });
        }
        
        console.log('🧠 Low memory mode enabled');
    }
    
    enableLowPerformanceMode() {
        document.documentElement.classList.add('low-performance');
        
        // Reduce animation complexity
        document.documentElement.classList.add('reduced-motion');
        
        console.log('⚡ Low performance mode enabled');
    }
    
    setupDataSaverMode() {
        if ('connection' in navigator && 'saveData' in navigator.connection) {
            if (navigator.connection.saveData) {
                this.enableDataSaverMode();
            }
        }
    }
    
    enableDataSaverMode() {
        document.documentElement.classList.add('data-saver');
        
        // Disable non-essential resources
        const nonEssential = document.querySelectorAll('[data-non-essential]');
        nonEssential.forEach((element) => {
            element.style.display = 'none';
        });
        
        // Reduce image quality
        this.enableLowBandwidthMode();
        
        console.log('💾 Data saver mode enabled');
    }
    
    // Performance Budgets
    setupPerformanceBudgets() {
        const budgets = {
            loadTime: 3000, // 3 seconds
            firstContentfulPaint: 1800, // 1.8 seconds
            largestContentfulPaint: 2500, // 2.5 seconds
            cumulativeLayoutShift: 0.1, // 0.1
            firstInputDelay: 100, // 100ms
            totalResourceSize: 2 * 1024 * 1024 // 2MB
        };
        
        // Monitor budgets
        setInterval(() => {
            this.checkPerformanceBudgets(budgets);
        }, 5000);
    }
    
    checkPerformanceBudgets(budgets) {
        const violations = [];
        
        Object.entries(budgets).forEach(([metric, budget]) => {
            const current = this.performanceMetrics[metric];
            if (current && current > budget) {
                violations.push({ metric, current, budget });
            }
        });
        
        if (violations.length > 0) {
            console.warn('⚠️ Performance budget violations:', violations);
        }
    }
    
    // Utility Methods
    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    initializeLoadedScripts(container) {
        const scripts = container.querySelectorAll('script');
        scripts.forEach((script) => {
            const newScript = document.createElement('script');
            newScript.textContent = script.textContent;
            script.parentNode.replaceChild(newScript, script);
        });
    }
    
    showPerformanceAlert(issues) {
        // Show performance issues to developers only
        if (window.location.hostname === 'localhost' || window.location.search.includes('debug=true')) {
            console.group('🐌 Performance Issues Detected');
            issues.forEach((issue) => {
                console.warn(`• ${issue}`);
            });
            console.groupEnd();
        }
    }
}

// Initialize performance optimizer
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.performanceOptimizer) {
            window.performanceOptimizer = new PerformanceOptimizer();
        }
    });
} else {
    if (!window.performanceOptimizer) {
        window.performanceOptimizer = new PerformanceOptimizer();
    }
}
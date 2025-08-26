// Hockey Stats Web App - Mobile Helper Functions

// Function to initialize collapsible sections
function initCollapsibleSections() {
    // Find all collapsible headers
    const collapsibleHeaders = document.querySelectorAll('.collapsible-header');
    
    // Add click event listeners to each header
    collapsibleHeaders.forEach(header => {
        header.addEventListener('click', function() {
            // Toggle the 'active' class on the header
            this.classList.toggle('active');
            
            // Get the content element that follows this header
            const content = this.nextElementSibling;
            
            // Toggle the content visibility
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
                // Update the arrow icon if present
                const arrow = this.querySelector('.collapsible-arrow');
                if (arrow) {
                    arrow.innerHTML = '▼';
                }
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
                // Update the arrow icon if present
                const arrow = this.querySelector('.collapsible-arrow');
                if (arrow) {
                    arrow.innerHTML = '▲';
                }
            }
        });
    });
}

// Function to initialize horizontal scrolling indicators
function initScrollIndicators() {
    // Find all horizontal scrolling containers
    const scrollContainers = document.querySelectorAll('.stats-scroll-container');
    
    scrollContainers.forEach(container => {
        // Check if container is scrollable (content width > container width)
        if (container.scrollWidth > container.clientWidth) {
            // Add scroll indicator if not already present
            if (!container.previousElementSibling || !container.previousElementSibling.classList.contains('scroll-indicator')) {
                const indicator = document.createElement('div');
                indicator.className = 'scroll-indicator';
                indicator.innerHTML = 'Swipe horizontally to see more stats →';
                container.parentNode.insertBefore(indicator, container);
            }
        }
    });
}

// Function to wrap metrics in horizontal scrolling containers
function wrapMetricsInScrollContainers() {
    // Find all metric rows (typically these are in columns)
    const metricRows = document.querySelectorAll('.row-widget.stHorizontal');
    
    metricRows.forEach(row => {
        // Check if this row contains metrics
        const metrics = row.querySelectorAll('[data-testid="metric-container"]');
        if (metrics.length >= 3) {
            // Check if this row is not already wrapped
            if (!row.parentElement.classList.contains('stats-scroll-container')) {
                // Create a scroll container
                const scrollContainer = document.createElement('div');
                scrollContainer.className = 'stats-scroll-container';
                
                // Move the metrics into the scroll container
                metrics.forEach(metric => {
                    scrollContainer.appendChild(metric);
                });
                
                // Replace the row with the scroll container
                row.parentNode.insertBefore(scrollContainer, row);
                row.remove();
            }
        }
    });
}

// Function to create collapsible sections for leaderboards
function createCollapsibleLeaderboards() {
    // Find all leaderboard sections
    const leaderboardSections = document.querySelectorAll('h3, h4').filter(heading => 
        heading.textContent.includes('Leaderboard') || 
        heading.textContent.includes('Top 5') ||
        heading.textContent.includes('Statistics')
    );
    
    leaderboardSections.forEach(heading => {
        // Check if this heading is not already in a collapsible section
        if (!heading.parentElement.classList.contains('collapsible-header')) {
            // Create collapsible section structure
            const section = document.createElement('div');
            section.className = 'collapsible-section';
            
            // Create header
            const header = document.createElement('div');
            header.className = 'collapsible-header';
            header.innerHTML = heading.outerHTML + '<span class="collapsible-arrow">▼</span>';
            
            // Find content to include in the collapsible section
            // This is a bit tricky as we need to include all elements until the next heading
            let content = document.createElement('div');
            content.className = 'collapsible-content';
            
            let currentElement = heading.nextElementSibling;
            while (currentElement && 
                   !['H1', 'H2', 'H3', 'H4', 'H5', 'H6'].includes(currentElement.tagName)) {
                content.appendChild(currentElement.cloneNode(true));
                currentElement = currentElement.nextElementSibling;
            }
            
            // Assemble the collapsible section
            section.appendChild(header);
            section.appendChild(content);
            
            // Replace the original heading with the collapsible section
            heading.parentNode.insertBefore(section, heading);
            
            // Remove the original heading and content that was moved
            heading.remove();
            currentElement = heading.nextElementSibling;
            while (currentElement && 
                   !['H1', 'H2', 'H3', 'H4', 'H5', 'H6'].includes(currentElement.tagName)) {
                const nextElement = currentElement.nextElementSibling;
                currentElement.remove();
                currentElement = nextElement;
            }
        }
    });
}

// Initialize all mobile optimizations when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only run on mobile devices
    if (window.innerWidth <= 768) {
        wrapMetricsInScrollContainers();
        initScrollIndicators();
        initCollapsibleSections();
        
        // Run this after a short delay to ensure all Streamlit elements are rendered
        setTimeout(createCollapsibleLeaderboards, 1000);
    }
});

// Re-initialize when Streamlit reloads components
// This is needed because Streamlit is a reactive framework that can re-render components
const observer = new MutationObserver(function(mutations) {
    if (window.innerWidth <= 768) {
        wrapMetricsInScrollContainers();
        initScrollIndicators();
        
        // Run with a delay to ensure all elements are fully rendered
        setTimeout(function() {
            initCollapsibleSections();
            createCollapsibleLeaderboards();
        }, 500);
    }
});

// Start observing the document body for changes
observer.observe(document.body, { childList: true, subtree: true });

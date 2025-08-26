// Android Chrome Heading Fix
// This script detects if headings are not visible on Android Chrome and applies a fallback solution

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on Android and Chrome
    const isAndroid = /Android/i.test(navigator.userAgent);
    const isChrome = /Chrome/i.test(navigator.userAgent);
    
    if (isAndroid && isChrome) {
        console.log("Android Chrome detected, applying heading fixes");
        
        // Apply fixes after a short delay to ensure Streamlit has rendered
        setTimeout(function() {
            fixHeadings();
        }, 500);
        
        // Also apply fixes when Streamlit re-renders components
        const observer = new MutationObserver(function(mutations) {
            fixHeadings();
        });
        
        // Start observing the document body for changes
        observer.observe(document.body, { childList: true, subtree: true });
    }
});

// Function to fix headings
function fixHeadings() {
    // Target all heading elements and Streamlit's heading classes
    const headingSelectors = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        '.stMarkdown h1', '.stMarkdown h2', '.stMarkdown h3', 
        '.stMarkdown h4', '.stMarkdown h5', '.stMarkdown h6',
        '.st-emotion-cache-10trblm',
        '.st-emotion-cache-q8sbsg p',
        '.st-emotion-cache-16idsys p',
        '.st-emotion-cache-183lzff'
    ];
    
    // Find all headings
    const headings = document.querySelectorAll(headingSelectors.join(', '));
    
    headings.forEach(function(heading) {
        // Check if the heading is visible (has height and is not hidden)
        const style = window.getComputedStyle(heading);
        const isVisible = style.display !== 'none' && 
                          style.visibility !== 'hidden' && 
                          style.opacity !== '0' &&
                          heading.offsetHeight > 0;
        
        // If heading is not visible, apply fallback
        if (!isVisible) {
            console.log("Found invisible heading, applying fallback", heading);
            
            // Create a fallback element
            const fallback = document.createElement('div');
            fallback.className = 'android-heading-fallback';
            fallback.textContent = heading.textContent;
            
            // Insert fallback after the original heading
            if (heading.parentNode) {
                heading.parentNode.insertBefore(fallback, heading.nextSibling);
            }
            
            // Apply additional styles to ensure visibility
            heading.style.cssText = `
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                color: #00205B !important;
                background-color: #F0F2F5 !important;
                padding: 8px !important;
                margin-bottom: 15px !important;
                border: 1px solid #00A0E3 !important;
                border-radius: 4px !important;
                font-weight: 700 !important;
                position: relative !important;
                z-index: 1 !important;
            `;
        }
    });
    
    // Also check for specific heading text in any element and create fallbacks
    const allElements = document.querySelectorAll('div, span, p');
    const headingTexts = [
        'Team Stats & Leaderboards',
        'Season Summary',
        'Forward Leaderboards',
        'Defensemen Leaderboards',
        'Goalie Statistics',
        'Team Game Log',
        'Game Stats',
        'Player Performance',
        'Game Timeline',
        'My Player\'s Stats',
        'Game Statistics',
        'Season Statistics',
        'Game Log'
    ];
    
    allElements.forEach(function(element) {
        if (headingTexts.includes(element.textContent.trim())) {
            // Check if this element already has a fallback sibling
            let hasFallback = false;
            if (element.nextSibling && 
                element.nextSibling.classList && 
                element.nextSibling.classList.contains('android-heading-fallback')) {
                hasFallback = true;
            }
            
            // If no fallback exists, create one
            if (!hasFallback) {
                const fallback = document.createElement('div');
                fallback.className = 'android-heading-fallback';
                fallback.textContent = element.textContent;
                
                // Insert fallback after the element
                if (element.parentNode) {
                    element.parentNode.insertBefore(fallback, element.nextSibling);
                }
            }
        }
    });
}

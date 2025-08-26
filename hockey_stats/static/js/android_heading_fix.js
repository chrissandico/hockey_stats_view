// Android Chrome Heading Fix - Enhanced Version
// This script aggressively ensures headings remain visible on Android Chrome

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on Android and Chrome
    const isAndroid = /Android/i.test(navigator.userAgent);
    const isChrome = /Chrome/i.test(navigator.userAgent);
    
    // Apply fixes for all mobile devices, not just Android Chrome
    console.log("Mobile device detected, applying aggressive heading fixes");
    
    // Apply fixes multiple times with increasing delays
    const delays = [100, 500, 1000, 2000, 3000, 5000];
    delays.forEach(delay => {
        setTimeout(function() {
            console.log(`Applying heading fixes after ${delay}ms delay`);
            fixHeadings();
        }, delay);
    });
    
    // Set up an interval to continuously apply fixes every 2 seconds
    setInterval(function() {
        console.log("Applying periodic heading fixes");
        fixHeadings();
    }, 2000);
    
    // Also apply fixes when Streamlit re-renders components
    const observer = new MutationObserver(function(mutations) {
        console.log("DOM mutation detected, applying heading fixes");
        fixHeadings();
        
        // Schedule another fix after a short delay to handle any subsequent changes
        setTimeout(fixHeadings, 200);
    });
    
    // Start observing the document body for changes with more comprehensive options
    observer.observe(document.body, { 
        childList: true, 
        subtree: true,
        attributes: true,
        characterData: true
    });
});

// Function to fix headings - Enhanced version
function fixHeadings() {
    // Target all heading elements and Streamlit's heading classes
    const headingSelectors = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        '.stMarkdown h1', '.stMarkdown h2', '.stMarkdown h3', 
        '.stMarkdown h4', '.stMarkdown h5', '.stMarkdown h6',
        '.st-emotion-cache-10trblm',
        '.st-emotion-cache-q8sbsg p',
        '.st-emotion-cache-16idsys p',
        '.st-emotion-cache-183lzff',
        '.custom-heading'
    ];
    
    // Find all headings
    const headings = document.querySelectorAll(headingSelectors.join(', '));
    console.log(`Found ${headings.length} heading elements to fix`);
    
    // Apply fixes to all headings regardless of visibility state
    headings.forEach(function(heading, index) {
        console.log(`Processing heading ${index + 1}: "${heading.textContent.trim()}"`);
        
        // Always create a fallback element if it doesn't exist yet
        let fallback = null;
        let nextSibling = heading.nextSibling;
        
        // Check if there's already a fallback
        while (nextSibling) {
            if (nextSibling.classList && nextSibling.classList.contains('android-heading-fallback')) {
                fallback = nextSibling;
                break;
            }
            nextSibling = nextSibling.nextSibling;
        }
        
        // Create new fallback if needed
        if (!fallback) {
            fallback = document.createElement('div');
            fallback.className = 'android-heading-fallback';
            fallback.textContent = heading.textContent;
            
            // Insert fallback after the original heading
            if (heading.parentNode) {
                heading.parentNode.insertBefore(fallback, heading.nextSibling);
                console.log(`Created fallback for: "${heading.textContent.trim()}"`);
            }
        }
        
        // Apply aggressive styling to ensure visibility
        const cssText = `
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            color: #000000 !important;
            background-color: #F0F2F5 !important;
            padding: 12px !important;
            margin-top: 25px !important;
            margin-bottom: 20px !important;
            border: 1px solid #00A0E3 !important;
            border-radius: 4px !important;
            font-weight: 700 !important;
            position: relative !important;
            z-index: 9999 !important;
            width: auto !important;
            height: auto !important;
            overflow: visible !important;
            pointer-events: auto !important;
            transform: none !important;
            transition: none !important;
            clear: both !important;
        `;
        
        // Apply styles directly
        heading.style.cssText = cssText;
        
        // Also apply styles via class manipulation
        heading.classList.add('fixed-heading');
        
        // Force repaint by accessing offsetHeight
        void heading.offsetHeight;
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
        'Game Log',
        'Hockey Statistics Dashboard',
        '🏒 Hockey Statistics Dashboard'
    ];
    
    allElements.forEach(function(element) {
        const trimmedText = element.textContent.trim();
        if (headingTexts.includes(trimmedText)) {
            console.log(`Found special heading text: "${trimmedText}"`);
            
            // Check if this element already has a fallback sibling
            let hasFallback = false;
            let nextSibling = element.nextSibling;
            
            while (nextSibling) {
                if (nextSibling.classList && nextSibling.classList.contains('android-heading-fallback')) {
                    hasFallback = true;
                    break;
                }
                nextSibling = nextSibling.nextSibling;
            }
            
            // If no fallback exists, create one
            if (!hasFallback) {
                const fallback = document.createElement('div');
                fallback.className = 'android-heading-fallback';
                fallback.textContent = trimmedText;
                fallback.style.cssText = `
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    color: #000000 !important;
                    background-color: #F0F2F5 !important;
                    padding: 12px !important;
                    margin-top: 25px !important;
                    margin-bottom: 20px !important;
                    border: 1px solid #00A0E3 !important;
                    border-radius: 4px !important;
                    font-weight: 700 !important;
                    position: relative !important;
                    z-index: 9999 !important;
                    font-size: 1.5em !important;
                    text-align: left !important;
                    clear: both !important;
                `;
                
                // Insert fallback after the element
                if (element.parentNode) {
                    element.parentNode.insertBefore(fallback, element.nextSibling);
                    console.log(`Created fallback for special text: "${trimmedText}"`);
                }
            }
            
            // Also try to make the original element visible
            element.style.cssText = `
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                color: #000000 !important;
                z-index: 9998 !important;
            `;
        }
    });
    
    // Add a global style to ensure headings are visible
    if (!document.getElementById('heading-fix-style')) {
        const styleEl = document.createElement('style');
        styleEl.id = 'heading-fix-style';
        styleEl.textContent = `
            h1, h2, h3, h4, h5, h6,
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
            .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
            .st-emotion-cache-10trblm,
            .st-emotion-cache-q8sbsg p,
            .st-emotion-cache-16idsys p,
            .st-emotion-cache-183lzff,
            .custom-heading {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                color: #000000 !important;
                background-color: #F0F2F5 !important;
                padding: 12px !important;
                margin-top: 25px !important;
                margin-bottom: 20px !important;
                border: 1px solid #00A0E3 !important;
                border-radius: 4px !important;
                font-weight: 700 !important;
                position: relative !important;
                z-index: 9999 !important;
            }
            
            .android-heading-fallback {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                color: #000000 !important;
                background-color: #F0F2F5 !important;
                padding: 12px !important;
                margin-top: 25px !important;
                margin-bottom: 20px !important;
                border: 1px solid #00A0E3 !important;
                border-radius: 4px !important;
                font-weight: 700 !important;
                position: relative !important;
                z-index: 9999 !important;
                font-size: 1.5em !important;
                text-align: left !important;
                clear: both !important;
            }
        `;
        document.head.appendChild(styleEl);
        console.log("Added global heading fix styles");
    }
}

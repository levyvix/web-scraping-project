// Mermaid configuration for MkDocs
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Mermaid with custom configuration
    mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        themeVariables: {
            primaryColor: '#673ab7',
            primaryTextColor: '#ffffff',
            primaryBorderColor: '#512da8',
            lineColor: '#757575',
            sectionBkgColor: '#f5f5f5',
            altSectionBkgColor: '#ffffff',
            gridColor: '#e0e0e0',
            secondaryColor: '#9c27b0',
            tertiaryColor: '#e1bee7'
        },
        flowchart: {
            useMaxWidth: true,
            htmlLabels: true,
            curve: 'basis'
        },
        sequence: {
            diagramMarginX: 50,
            diagramMarginY: 10,
            actorMargin: 50,
            width: 150,
            height: 65,
            boxMargin: 10,
            boxTextMargin: 5,
            noteMargin: 10,
            messageMargin: 35,
            mirrorActors: true,
            bottomMarginAdj: 1,
            useMaxWidth: true,
            rightAngles: false,
            showSequenceNumbers: false
        },
        gantt: {
            titleTopMargin: 25,
            barHeight: 20,
            fontFamily: '"Roboto", "Helvetica Neue", Arial, sans-serif',
            fontSize: 11,
            fontWeight: 'normal',
            gridLineStartPadding: 35,
            leftPadding: 75,
            topPadding: 50,
            rightPadding: 75,
            bottomPadding: 25
        }
    });

    // Handle theme switching for Mermaid diagrams
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-md-color-scheme') {
                const scheme = document.body.getAttribute('data-md-color-scheme');
                const theme = scheme === 'slate' ? 'dark' : 'default';

                // Reinitialize Mermaid with new theme
                mermaid.initialize({
                    startOnLoad: true,
                    theme: theme
                });

                // Re-render existing diagrams
                const diagrams = document.querySelectorAll('.mermaid');
                diagrams.forEach(function(diagram) {
                    diagram.removeAttribute('data-processed');
                });
                mermaid.init();
            }
        });
    });

    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['data-md-color-scheme']
    });
});

// MathJax configuration
window.MathJax = {
    tex: {
        inlineMath: [["\\(", "\\)"]],
        displayMath: [["\\[", "\\]"]],
        processEscapes: true,
        processEnvironments: true
    },
    options: {
        ignoreHtmlClass: ".*|",
        processHtmlClass: "arithmatex"
    }
};

document$.subscribe(() => {
    MathJax.typesetPromise()
});

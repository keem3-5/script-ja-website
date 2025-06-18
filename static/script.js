<script>
    // --- Function to set active link ---
    // This function adds/removes the 'active' class which your CSS styles blue.
    function setActiveLink(sectionId) 
        const navLinks = document.querySelectorAll('.navbar-list .navbar-item a');
        navLinks.forEach(link = {
            link.classList.remove('active');
        });
        const activeLink = document.querySelector(`.navbar-list .navbar-item a[href="#${sectionId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    

    // --- Smooth scroll for internal links (Click handler) ---
    // This handles what happens when you click a navigation link.
    // It also correctly sets the blue highlight immediately on click.
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            // 1. Immediately set the clicked link as active (turns it blue)
            setActiveLink(this.getAttribute('href').substring(1)); // Remove '#' prefix

            // 2. Smooth scroll to the target section, accounting for the fixed navbar.
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            const navbarHeight = document.querySelector('.navbar').offsetHeight; 

            const targetPosition = targetElement.offsetTop - navbarHeight;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        });
    });

    // --- SCROLLSPY LOGIC (HIGHLIGHT ON SCROLL) ---
    // This is the part that makes the links turn blue as you scroll.
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar'); 
        const navbarHeight = navbar ? navbar.offsetHeight : 0; // Get the height of your fixed navbar

        // Define a "trigger line" just below your fixed navbar.
        // When the top of a section crosses this line, that section's link will highlight.
        // Adding +5 pixels gives a small buffer for smoother transitions.
        const scrollTriggerLine = window.scrollY + navbarHeight + 5; 

        let currentActiveSectionId = 'hero-section'; // Default to 'hero-section' (Home) if no other section is detected

        const sections = document.querySelectorAll('section[id]'); // Get all your page sections

        // Loop through each section to find which one is currently at the 'scrollTriggerLine'
        sections.forEach(section => {
            const sectionTop = section.offsetTop; // The distance of the section's top from the very top of the document
            const sectionBottom = sectionTop + section.offsetHeight; // The distance of the section's bottom from the very top of the document

            // Check if the 'scrollTriggerLine' is currently within the vertical bounds of this section.
            // If it is, this section is considered the "active" one.
            if (scrollTriggerLine >= sectionTop && scrollTriggerLine < sectionBottom) {
                currentActiveSectionId = section.id; // Set this section as the currently active one
            }
        });

        // Apply the 'active' class to the corresponding navigation link.
        setActiveLink(currentActiveSectionId);
    });

    // --- JavaScript for auto-hiding flash messages ---
    // This remains unchanged and functions independently.
    document.addEventListener('DOMContentLoaded', function() {
        const flashMessages = document.querySelectorAll('.flash-messages li');
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.classList.add('fade-out');
                message.addEventListener('transitionend', () => message.remove());
            }, 5000); // Disappear after 5 seconds
        });
    });

    // --- Initial active state on page load ---
    // Ensures 'Home' is highlighted when the page first loads.
    document.addEventListener('DOMContentLoaded', () => {
        setActiveLink('hero-section');
    });
</script>
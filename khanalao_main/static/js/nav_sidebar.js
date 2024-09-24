'use strict';
{
    const toggleNavSidebar = document.getElementById('toggle-nav-sidebar');
    const main = document.getElementById('main');
    const navSidebar = document.getElementById('nav-sidebar');
    const navFilter = document.getElementById('nav-filter');

    if (toggleNavSidebar) {
        const navLinks = document.querySelectorAll('#nav-sidebar a');

        const toggleTabbing = (enable) => {
            for (const navLink of navLinks) {
                navLink.tabIndex = enable ? 0 : -1;
            }
        };

        let navSidebarIsOpen = localStorage.getItem('django.admin.navSidebarIsOpen') || 'true';

        if (navSidebarIsOpen === 'false') {
            toggleTabbing(false);
        }
        main.classList.toggle('shifted', navSidebarIsOpen === 'true');

        toggleNavSidebar.addEventListener('click', () => {
            navSidebarIsOpen = navSidebarIsOpen === 'true' ? 'false' : 'true';
            toggleTabbing(navSidebarIsOpen === 'true');
            localStorage.setItem('django.admin.navSidebarIsOpen', navSidebarIsOpen);
            main.classList.toggle('shifted');
        });
    }

    const initSidebarQuickFilter = () => {
        if (!navSidebar) return;

        const options = Array.from(navSidebar.querySelectorAll('th[scope=row] a')).map(container => ({
            title: container.innerHTML,
            node: container
        }));

        const checkValue = (event) => {
            let filterValue = event.target.value ? event.target.value.toLowerCase() : '';
            if (event.key === 'Escape') {
                filterValue = '';
                event.target.value = ''; // Clear input
            }

            let matches = false;
            for (const o of options) {
                const displayValue = filterValue && o.title.toLowerCase().indexOf(filterValue) === -1 ? 'none' : '';
                if (displayValue === '') matches = true;
                o.node.parentNode.parentNode.style.display = displayValue;
            }
            event.target.classList.toggle('no-results', !filterValue || !matches);
            sessionStorage.setItem('django.admin.navSidebarFilterValue', filterValue);
        };

        if (navFilter) {
            navFilter.addEventListener('input', checkValue);
            const storedValue = sessionStorage.getItem('django.admin.navSidebarFilterValue');
            if (storedValue) {
                navFilter.value = storedValue;
                checkValue({ target: navFilter });
            }
        }
    };

    window.initSidebarQuickFilter = initSidebarQuickFilter;
    initSidebarQuickFilter();
}

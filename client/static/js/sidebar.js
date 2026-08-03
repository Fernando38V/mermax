document.addEventListener("DOMContentLoaded", () =>{
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.mx-sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (!toggle || !sidebar) return;

    const closeSidebar = () => {
        sidebar.classList.remove("mx-sidebar-open");
        overlay.classList.remove("mx-sidebar-open");
    }

    toggle.addEventListener("click", () => {
        sidebar.classList.toggle("mx-sidebar-open");
        overlay.classList.toggle("mx-sidebar-open");
    });

    overlay.addEventListener('click', closeSidebar);

}); 
document.addEventListener('DOMContentLoaded', () => {
    // Handle filter selection for the dashboard
    const filterSelect = document.getElementById('post-filter');
    if (filterSelect) {
        filterSelect.addEventListener('change', () => {
            const filter = filterSelect.value;
            const url = new URL(window.location.href);
            url.searchParams.set('filter', filter); // Update the 'filter' query parameter
            window.location.href = url.toString(); // Redirect with the updated URL
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    // Handle filter selection
    const filterSelect = document.getElementById('filter-select');
    if (filterSelect) {
        filterSelect.addEventListener('change', () => {
            const filter = filterSelect.value;
            const url = new URL(window.location.href);
            url.searchParams.set('filter', filter);
            window.location.href = url.toString(); // Redirect with updated filter
        });
    }
});

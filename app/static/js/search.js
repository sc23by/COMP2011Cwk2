document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('user-search');
    const resultsDropdown = document.getElementById('search-results');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    searchInput.addEventListener('input', async () => {
        const query = searchInput.value.trim();

        // Hide results if query is empty
        if (query === '') {
            resultsDropdown.style.display = 'none';
            resultsDropdown.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/api/search_users?query=${encodeURIComponent(query)}`);
            const data = await response.json();

            resultsDropdown.innerHTML = ''; // Clear previous results
            if (data.results.length > 0) {
                data.results.forEach(user => {
                    // Create a list item for each result
                    const item = document.createElement('li');
                    item.style.display = 'flex';
                    item.style.justifyContent = 'space-between';
                    item.style.alignItems = 'center';
                    item.style.padding = '5px 10px';
                    item.style.borderBottom = '1px solid #ddd';

                    // Username span
                    const usernameSpan = document.createElement('span');
                    usernameSpan.textContent = user.username;

                    // Follow/Unfollow button
                    const actionButton = document.createElement('button');
                    let isFollowed = user.is_followed; // Backend-provided follow status
                    actionButton.textContent = isFollowed ? 'Unfollow' : 'Follow';
                    actionButton.className = isFollowed ? 'btn unfollow-btn' : 'btn follow-btn';

                    // Handle follow/unfollow action
                    actionButton.addEventListener('click', async () => {
                        try {
                            const url = isFollowed 
                                ? `/api/unfollow/${user.username}` 
                                : `/api/follow/${user.username}`;

                            const followResponse = await fetch(url, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': csrfToken,
                                },
                            });

                            const followData = await followResponse.json();

                            if (!followResponse.ok) {
                                console.error('Error:', followData.error);
                                alert(followData.error || 'Action failed');
                                return;
                            }

                            // Toggle follow state and update button
                            if (isFollowed) {
                                actionButton.textContent = 'Follow';
                                actionButton.className = 'btn follow-btn';
                            } else {
                                actionButton.textContent = 'Unfollow';
                                actionButton.className = 'btn unfollow-btn';
                            }

                            isFollowed = !isFollowed; // Toggle follow state
                        } catch (error) {
                            console.error('Error performing action:', error);
                        }
                    });

                    // Append username and button to the list item
                    item.appendChild(usernameSpan);
                    item.appendChild(actionButton);

                    // Append the list item to the dropdown
                    resultsDropdown.appendChild(item);
                });
                resultsDropdown.style.display = 'block'; // Show results
            } else {
                // No results message
                resultsDropdown.innerHTML = '<li>No users found</li>';
                resultsDropdown.style.display = 'block';
            }
        } catch (error) {
            console.error('Error fetching search results:', error);
        }
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', (event) => {
        if (!searchInput.contains(event.target) && !resultsDropdown.contains(event.target)) {
            resultsDropdown.style.display = 'none';
        }
    });
});

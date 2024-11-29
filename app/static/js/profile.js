document.addEventListener('DOMContentLoaded', () => {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const followingList = document.getElementById('following-list');
    const followersList = document.getElementById('followers-list'); // New selector for followers list

    if (followingList) {
        followingList.addEventListener('click', async (event) => {
            const target = event.target;

            // Ensure the clicked element is a button
            if (target.tagName !== 'BUTTON') return;

            // Disable the button to prevent double clicks
            target.disabled = true;

            // Handle Unfollow action
            if (target.classList.contains('unfollow-btn')) {
                const username = target.getAttribute('data-username');
                try {
                    const response = await fetch(`/api/unfollow/${username}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        }
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        console.error(data.error || 'Failed to unfollow');
                        alert(data.error || 'Failed to unfollow');
                        target.disabled = false;
                        return;
                    }

                    // Update button to Follow state
                    target.textContent = 'Follow';
                    target.classList.remove('unfollow-btn');
                    target.classList.add('follow-btn');
                    target.className = 'btn btn-primary btn-sm follow-btn';
                } catch (error) {
                    console.error('Error unfollowing user:', error);
                } finally {
                    target.disabled = false;
                }
                return;
            }

            // Handle Follow action
            if (target.classList.contains('follow-btn')) {
                const username = target.getAttribute('data-username');
                try {
                    const response = await fetch(`/api/follow/${username}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        }
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        console.error(data.error || 'Failed to follow');
                        alert(data.error || 'Failed to follow');
                        target.disabled = false;
                        return;
                    }

                    // Update button to Unfollow state
                    target.textContent = 'Unfollow';
                    target.classList.remove('follow-btn');
                    target.classList.add('unfollow-btn');
                    target.className = 'btn btn-secondary btn-sm unfollow-btn';
                } catch (error) {
                    console.error('Error following user:', error);
                } finally {
                    target.disabled = false;
                }
                return;
            }
        });
    }

    // Handle Remove Follower Button
    if (followersList) {
        followersList.addEventListener('click', async (event) => {
            const target = event.target;

            // Ensure the clicked element is a button
            if (target.tagName !== 'BUTTON') return;

            // Disable the button to prevent double clicks
            target.disabled = true;

            // Handle Remove Follower action
            if (target.classList.contains('remove-follower-btn')) {
                const username = target.getAttribute('data-username');
                try {
                    const response = await fetch(`/api/remove_follower/${username}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        }
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        console.error(data.error || 'Failed to remove follower');
                        alert(data.error || 'Failed to remove follower');
                        target.disabled = false;
                        return;
                    }

                    // Remove the follower from the DOM
                    const listItem = target.closest('li');
                    listItem.remove();

                    alert(data.message || `${username} has been removed from your followers.`);
                } catch (error) {
                    console.error('Error removing follower:', error);
                } finally {
                    target.disabled = false;
                }
            }
        });
    }
});

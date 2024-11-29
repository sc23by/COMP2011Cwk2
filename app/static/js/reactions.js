$(document).ready(function () {
    console.log("Reactions.js loaded"); // Debugging: Ensure the file loads.

    // Fetch CSRF token
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    // Add CSRF token to every AJAX request
    $.ajaxSetup({
        beforeSend: function (xhr) {
            if (csrfToken) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });

    // Attach click event handlers for like and dislike buttons
    $(".like-button, .dislike-button").on("click", function () {
        console.log("Button clicked"); // Debugging: Ensure event is triggered.

        let button = $(this);
        let postId = button.data("post-id"); // Get the post ID
        let action = button.hasClass("like-button") ? "like" : "dislike"; // Determine action
        let oppositeAction = action === "like" ? "dislike" : "like"; // Determine the opposite action

        // Send AJAX request
        $.ajax({
            url: `/${action}/${postId}`, // Adjust URL to your Flask route
            type: "POST",
            contentType: "application/json",
            dataType: "json",
            success: function (response) {

                // Update like and dislike counts dynamically
                $(`#post-${postId} .like-count`).text(response.likes);
                $(`#post-${postId} .dislike-count`).text(response.dislikes);

                // Update icon for the clicked button
                let icon = button.find("i");
                if (action === "like") {
                    icon.toggleClass("far fas"); // Toggle outline/filled thumbs-up
                    button.toggleClass("selected"); // Add/remove selected class
                } else {
                    icon.toggleClass("far fas"); // Toggle outline/filled thumbs-down
                    button.toggleClass("selected"); // Add/remove selected class
                }

                // Ensure the opposite button is unselected and shows the outline icon
                let oppositeButton = $(`#post-${postId} .${oppositeAction}-button`);
                let oppositeIcon = oppositeButton.find("i");
                oppositeButton.removeClass("selected"); // Remove selected class
                oppositeIcon.removeClass("fas").addClass("far"); // Ensure it's outline
            },
            error: function (xhr, status, error) {
                console.error(`Error: ${xhr.responseText}`); // Debugging: Log error.
            }
        });
    });
});

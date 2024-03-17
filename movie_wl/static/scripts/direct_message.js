document.addEventListener('DOMContentLoaded', () => {
// Fetch chatted users when the page loads
fetchChattedUsers();
// Function to fetch and display Chatted Users
function fetchChattedUsers() {
    // Fetch Chatted Users from the server
    $.ajax({
        url: "/fetch_chatted_users",
        method: "GET",
        success: function(data) {
            // Update Chatted Users section with fetched users
            data.forEach(function(user) {
                updateChattedUsers(user.id, user.username);
            });
        },
        error: function(xhr, status, error) {
            console.error("Error fetching chatted users:", error);
        }
    });
}

// Function to update the Chatted Users section
function updateChattedUsers(userId, username) {
    // Check if the user is already in the Chatted Users section
    if ($("#chatted-users-list").find(`[data-user-id='${userId}']`).length === 0) {
        // Append the user to the Chatted Users section
        $("#chatted-users-list").append(`<p class="select-user" data-user-id="${userId}">${username}</p>`);
        saveChattedUser(userId, username); // Save the chatted user to local storage
    }
}

// Function to fetch and display Chatted Users
function fetchChattedUsers() {
    // Fetch Chatted Users from local storage
    const chattedUsers = JSON.parse(localStorage.getItem("chattedUsers")) || [];
    // Update Chatted Users section with fetched users
    chattedUsers.forEach(function(user) {
        updateChattedUsers(user.id, user.username);
    });
}

// Function to save a chatted user to local storage
function saveChattedUser(userId, username) {
    const chattedUsers = JSON.parse(localStorage.getItem("chattedUsers")) || [];
    // Check if the user is already in the list
    if (!chattedUsers.some(user => user.id === userId)) {
        chattedUsers.push({ id: userId, username: username });
        localStorage.setItem("chattedUsers", JSON.stringify(chattedUsers));
    }
}


    // Autocomplete for recipient name input
    $("#recipient_name").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "/search_users",
                method: "GET",
                data: { term: request.term },
                success: function(data) {
                    response(data);
                }
            });
        },
        minLength: 1, // Minimum characters before triggering autocomplete
        select: function(event, ui) {
            $("#recipient_id").val(ui.item.id);
            fetchMessages(ui.item.id); // Fetch messages for the selected user
            updateChattedUsers(ui.item.id, ui.item.value); // Update Chatted Users section
        }
    });

    

    // Example: Select a user to start conversation
    $(".select-user").click(function() {
        $(".select-user").removeClass("selected-user");
        $(this).addClass("selected-user");
        const recipientId = $(this).attr("data-user-id");
        $("#recipient_id").val(recipientId);
        fetchMessages(recipientId);
        updateChattedUsers(recipientId, $(this).text()); // Update Chatted Users section
    });

    // Set selected user when a user clicks on a user
document.querySelectorAll('.select-user').forEach(p => {
    p.onclick = () => {
        // Remove active-user class from all users
        document.querySelectorAll('.select-user').forEach(user => {
            user.classList.remove('active-user');
        });
        // Add active-user class to the clicked user
        p.classList.add('active-user');
    };
});

    // Send message when the "SEND" button is clicked
    $("#send_message").click(function() {
        var recipientId = $("#recipient_id").val();
        var message = $("#user_message").val();
        console.log("Recipient ID (send_message click):", recipientId);
        console.log("Message (send_message click):", message);
        if (recipientId && message) {
            sendMessage(recipientId, message);
             // Update Chatted Users section after sending message
        updateChattedUsers(recipientId, $("#recipient_name").val());
        } else {
            console.error("Recipient ID or message is empty");
        }
    });

    // Fetch messages for the selected recipient
    function fetchMessages(userId) {
        if (!userId) {
            console.error("User ID is empty");
            return;
        }
    
        $.ajax({
            url: "/fetch_direct_messages",
            method: "GET",
            data: { user_id: userId },
            success: function(data) {
                // Clear previous messages
                $("#display-message-section").empty();
                
                // Append new messages with username and timestamp
                data.forEach(function(message) {
                    const messageElement = $("<div>").addClass("message");
                    const usernameElement = $("<span>").addClass("username").text(message.sender_username);
                    const contentElement = $("<p>").text(message.content);
                    const timestamp = new Date(message.timestamp).toLocaleString('en-US', { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: true });
                    const timestampElement = $("<span>").addClass("time").text(timestamp);
                
                    messageElement.append(usernameElement, contentElement, timestampElement);
                    $("#display-message-section").append(messageElement);
                });
            },
            error: function(xhr, status, error) {
                console.error("Error fetching messages:", error);
            }
        });
    }

    // Function to send a message
    function sendMessage(recipientId, message) {
        if (!recipientId || !message) {
            console.error("Recipient ID or message content is empty");
            return;
        }

        $.ajax({
            url: "/send_direct_message",
            method: "POST",
            data: { recipient_id: recipientId, message: message },
            success: function(response) {
                console.log("Message sent successfully");
                fetchMessages(recipientId); // Fetch messages after sending
            },
            error: function(xhr, status, error) {
                console.error("Error sending message:", error);
            }
        });
    }
});
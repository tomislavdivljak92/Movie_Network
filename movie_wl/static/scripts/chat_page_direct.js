document.addEventListener('DOMContentLoaded', () => {
    // Make 'enter' key submit message
    const msg = document.getElementById("user_message");
    const sendMessageButton = document.getElementById("send_message");

    if (msg && sendMessageButton) {
        msg.addEventListener("keyup", function(event) {
            event.preventDefault();
            if (event.key === "Enter") {
                sendMessage(); // Call the sendMessage function when Enter key is pressed
            }
        });
        sendMessageButton.addEventListener("click", sendMessage);
    }
});

$(document).ready(function() {
    // Function to send a message
    function sendMessage() {
        const recipientId = $("#recipient_id").val(); // Retrieve recipient ID
        const message = $("#user_message").val(); // Retrieve message content
        
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

    // Function to fetch messages
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
                $("#display-message-section").html(data);
            },
            error: function(xhr, status, error) {
                console.error("Error fetching messages:", error);
            }
        });
    }
     // Example: Select a user to start conversation
     $(".select-user").click(function() {
        $(".select-user").removeClass("selected-user");
        $(this).addClass("selected-user");
        var recipientId = $(this).attr("data-user-id");
        $("#recipient_id").val(recipientId); // Set recipient_id hidden input value
        console.log("Recipient ID (select-user click):", recipientId); // Log recipient ID
        fetchMessages(recipientId); // Fetch messages for selected user
    });

    // Example: Send a message when the send button is clicked
    $("#send_message").click(function() {
        var recipientId = $("#recipient_id").val();
        var message = $("#user_message").val();
        console.log("Recipient ID (send_message click):", recipientId);
        console.log("Message (send_message click):", message);
        if (recipientId && message) {
            sendMessage(message);
        } else {
            console.error("Recipient ID or message is empty");
        }
    });

// Make 'enter' key submit message
$("#user_message").keyup(function(event) {
    event.preventDefault();
    if (event.key === "Enter") {
        $("#send_message").click();
    }
});


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
    }
});





});
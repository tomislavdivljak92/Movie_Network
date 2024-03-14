document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.location.hostname + ':' + location.port);

    let room = "news";
    joinRoom("news");



    socket.on('message', data => {
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');
        const br = document.createElement('br');



        if (data.username) {
        span_username.innerHTML = data.username;
        span_timestamp.innerHTML = data.time_stamp;
        p.innerHTML = span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML;
        document.querySelector('#display-message-section').append(p);
        } else {
            printSysMsg(data.msg);
        }


    });

    // send message
    document.querySelector('#send_message').onclick = () => {
        // Ensure room is set before sending the message
        if (room) {
            socket.send({
                'msg': document.querySelector('#user_message').value,
                'username': username,
                'room': room
            });
            document.querySelector('#user_message').value = '';
        }
    };

    // Set room when a user clicks on a room
    document.querySelectorAll('.select-room').forEach(p => {
        p.onclick = () => {
            room = p.innerHTML;
            joinRoom(room);
        };
    });

    // Leave current room
    function leaveRoom() {
        if (room) {
            socket.emit('leave', {'username': username, 'room': room});
        }
    }

    // Join room
    function joinRoom(room) {
        leaveRoom();
        socket.emit('join', {'username': username, 'room': room});
    }
});
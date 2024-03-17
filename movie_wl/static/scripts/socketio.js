document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.location.hostname + ':' + location.port);

    let room = "NEWS";
    joinRoom("NEWS");



    socket.on('message', data => {
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');
        const br = document.createElement('br');



        if (data.username) {

            

        span_username.classList.add('username'); 
        span_username.innerHTML = data.username;
        span_timestamp.innerHTML = data.time_stamp;
        span_timestamp.classList.add('time');
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


            document.querySelectorAll('.select-room').forEach(room => {
                room.classList.remove('active-room'); // Remove active-room class from all rooms
            });
            p.classList.add('active-room'); 




            let newRoom = p.innerHTML;
            if (newRoom == room) {
                msg = `you are already in ${room} room.`
                printSysMsg(msg);
            } else {
                leaveRoom(room);
                joinRoom(newRoom);
                room = newRoom;
            }
        };
    });

    // Leave current room
    function leaveRoom() {
        
            socket.emit('leave', {'username': username, 'room': room});
       
    }

    // Join room
    function joinRoom(room) {
        
        socket.emit('join', {'username': username, 'room': room});
        document.querySelector('#display-message-section').innerHTML = ''
    }


    //Print system message
    function printSysMsg(msg) {
        const p =document.createElement('p');
        p.innerHTML = msg;
        p.classList.add('system-message');
        document.querySelector('#display-message-section').append(p);
    }

});

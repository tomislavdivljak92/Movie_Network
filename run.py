from movie_wl import create_app, socketio
import os

app = create_app()

if __name__ == "__main__":
    # Run the Flask app using Socket.IO
    # Listen on all addresses and a non-standard port
    # Ensure that the PORT environment variable is used if available
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
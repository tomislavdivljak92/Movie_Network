from movie_wl import create_app, socketio

# Define the paths to the SSL certificate and private key
ssl_cert = "C:\\Program Files\\OpenSSL-Win64\\bin\\cert.pem"
ssl_key = "C:\\Program Files\\OpenSSL-Win64\\bin\\key.pem"

# Create the Flask app
app = create_app()

if __name__ == "__main__":
    # Run the Flask app using Socket.IO with HTTPS enabled
    # Ensure that the WSGI server is configured to use HTTPS with the specified SSL certificate and private key
    socketio.run(app, host='0.0.0.0', port=443, ssl_context=(ssl_cert, ssl_key), debug=True)
# Modified from starter code created by/at
# Author: Bram Lewis
# Availability: https://canvas.oregonstate.edu/courses/1957923/assignments/9654612?module_item_id=24358446

import socket
from timestamp_print import timestamped_print


def tcp_client():

    # Create socket:
    # as with the server script, create socket with AF_INET (IPv4) and STREAMing TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Specify server and port:
    # Define server IP (will be localhost for now) and server port
    serv_address = '127.0.0.1'
    serv_port = 12345

    try:
        # Establish connection:
        # connect(): connect the socket to the servers address and port
        client_socket.connect((serv_address, serv_port))

        # Send and Recv data:
        # sendall(): send data to the server
        msg = 'Hello, Server!'
        timestamped_print(f"Sending: {msg}")
        client_socket.send(msg.encode())

        # recv(): get data from the server, specifying buffer (1024 bytes in this instance)
        response = client_socket.recv(1024)
        timestamped_print(f"Received: {response.decode()}")

    finally:
        # Close the connection:
        # close(): Close the socket to free up resources
        client_socket.close()


if __name__ == "__main__":
    tcp_client()
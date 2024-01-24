import socket
import struct

def receive_all(socket, size):
    data = b""
    while len(data) < size:
        remaining_size = size - len(data)
        data += socket.recv(remaining_size)
    return data

def receive_packet(connection):
    # Receive the packet size (4 bytes)
    packet_size_data = receive_all(connection, 4)
    packet_size = struct.unpack("!I", packet_size_data)[0]

    # Receive the rest of the packet
    packet_data = receive_all(connection, packet_size)

    return packet_data

# Rest of your server code...

while True:
    # Wait for a connection
    print("Waiting for a connection...")
    connection, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    try:
        # Receive and send back data
        while True:
            packet_data = receive_packet(connection)

            # Parse the packet data
            name_size = struct.unpack("!I", packet_data[:4])[0]
            name = packet_data[4:4+name_size].decode()
            data_size = struct.unpack("!I", packet_data[4+name_size:4+name_size+4])[0]
            data = packet_data[4+name_size+4:]

            print(f"Received: Name={name}, Data={data.decode()}")

            # Echo back the packet
            connection.sendall(packet_data)
    finally:
        # Clean up the connection
        connection.close()

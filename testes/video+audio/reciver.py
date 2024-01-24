import socket
import struct

def create_packet(name, data):
    name_bytes = name.encode()
    data_bytes = data.encode()
    packet_size = 4 + len(name_bytes) + 4 + len(data_bytes)

    # Build the packet
    packet = struct.pack("!I", len(name_bytes))
    packet += name_bytes
    packet += struct.pack("!I", len(data_bytes))
    packet += data_bytes

    return packet

# Rest of your client code...

try:
    # Send and receive data
    name = "John"
    data = "Hello, server!"

    # Create the packet
    packet = create_packet(name, data)

    # Send the packet
    client_socket.sendall(packet)
    print(f"Sent: Name={name}, Data={data}")

    # Receive the echoed packet
    echoed_packet = receive_packet(client_socket)

    # Parse the echoed packet
    echoed_name_size = struct.unpack("!I", echoed_packet[:4])[0]
    echoed_name = echoed_packet[4:4+echoed_name_size].decode()
    echoed_data_size = struct.unpack("!I", echoed_packet[4+echoed_name_size:4+echoed_name_size+4])[0]
    echoed_data = echoed_packet[4+echoed_name_size+4:]

    print(f"Received Echo: Name={echoed_name}, Data={echoed_data.decode()}")
finally:
    # Clean up the connection
    client_socket.close()

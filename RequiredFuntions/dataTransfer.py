import socket
import json

# Function to send data
def send(data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 12345)
    s.connect(server_address)

    # Convert dictionary to JSON string
    data_json = json.dumps(data)
    data_encoded = data_json.encode('utf-8')  # Encode JSON string to bytes

    # Send data length followed by the data
    data_length = len(data_encoded).to_bytes(4, 'big')
    s.sendall(data_length + data_encoded)

    s.close()
    print("Data transfer done.")

# Function to receive data and save it to a JSON file
def receive():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 12345)
    s.bind(server_address)
    s.listen(1)

    print("Server is listening on port 12345...")
    conn, addr = s.accept()
    print("Connected by", addr)

    # Receive the length of the data
    data_length = int.from_bytes(conn.recv(4), 'big')
    data_encoded = b""
    while len(data_encoded) < data_length:
        data_encoded += conn.recv(data_length - len(data_encoded))

    # Decode bytes to JSON string and parse to dictionary
    data_json = data_encoded.decode('utf-8')
    received_data = json.loads(data_json)

    # Save the received data to a JSON file
    with open('./ReceivedData/received_data.json', 'w') as json_file:
        json.dump(received_data, json_file, indent=4)  # Format the JSON for readability

    print("Received data saved to 'received_data.json'.")
    conn.close()
    s.close()

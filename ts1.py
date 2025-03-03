import socket
import sys

# Load TS1 database
def load_ts_database(filename):
    database = {}
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 2:
                database[parts[0]] = parts[1]  
    return database

def handle_request(data, client_address, server_socket, ts_database):
    print(f"🔥 TS1 received query: {data}")  
    parts = data.split()
    if len(parts) != 4:
        return 

    _, domain, query_id, _ = parts

    if domain in ts_database:
        response = f"1 {domain} {ts_database[domain]} {query_id} aa"
    else:
        response = f"1 {domain} 0.0.0.0 {query_id} nx"

    print(f"🔥 TS1 sending response: {response}")  
    server_socket.sendto(response.encode(), client_address)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ts1.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    ts_database = load_ts_database("ts1database.txt")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(("localhost", port))
        print(f"TLD Server 1 (.com) running on port {port}...")

        while True:
            data, client_address = server_socket.recvfrom(1024)
            handle_request(data.decode(), client_address, server_socket, ts_database)

if __name__ == "__main__":
    main()

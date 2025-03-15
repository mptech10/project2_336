import socket
import sys

# Load TS2 database
def load_ts_database(filename):
    database = {}
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 2:
                database[parts[0].lower()] = parts[1] 
    return database

def handle_request(data, client_address, server_socket, ts_database):
    print(f"🔥 TS2 received query: {data}")  # Debug print

    parts = data.split()
    if len(parts) != 4:
        return  

    _, domain, query_id, _ = parts

    domain_lower = domain.lower()

    if domain_lower in ts_database:
        response = f"1 {domain} {ts_database[domain_lower]} {query_id} aa"
    else:
        response = f"1 {domain} 0.0.0.0 {query_id} nx"

    print(f"🔥 TS2 sending response: {response}") 
    server_socket.sendto(response.encode(), client_address)

    with open("ts2responses.txt", "a") as output:
        output.write(response + "\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ts2.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    ts_database = load_ts_database("ts2database.txt")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(("0.0.0.0", port))
        print(f"TLD Server 2 (.edu) running on port {port}...")

        while True:
            data, client_address = server_socket.recvfrom(1024)
            handle_request(data.decode(), client_address, server_socket, ts_database)

if __name__ == "__main__":
    main()

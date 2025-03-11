import socket
import sys

# Load Root Server database
def load_rs_database(filename):
    database = {}
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 2:
                database[parts[0]] = parts[1]  
    print(f"Loaded database: {database}") 
    return database


def handle_request(data, client_address, server_socket, rs_database):
    parts = data.split()
    if len(parts) != 4:
        return 

    _, domain, query_id, query_type = parts
    domain_parts = domain.split('.')
    tld = domain_parts[-1] 

    print(f"Received query for: {domain}, TLD: {tld}")  

    if domain in rs_database:
        response = f"1 {domain} {rs_database[domain]} {query_id} aa"  

    elif tld in rs_database:
        print(f"Forwarding {domain} to TLD server: {rs_database[tld]}")  
        response = f"1 {domain} {rs_database[tld]} {query_id} ns"  
    else:  
        response = f"1 {domain} 0.0.0.0 {query_id} nx" 

    print(f"Response: {response}")  
    server_socket.sendto(response.encode(), client_address)




def main():
    if len(sys.argv) != 2:
        print("Usage: python3 rs.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    rs_database = load_rs_database("rsdatabase.txt")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(("0.0.0.0", port))
        print(f"Root Server running on port {port}...")

        while True:
            data, client_address = server_socket.recvfrom(1024)
            handle_request(data.decode(), client_address, server_socket, rs_database)

if __name__ == "__main__":
    main()

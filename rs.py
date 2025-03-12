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

def send_query(server_host, port, domain_name, query_type, query_id):
    """Send a DNS query to a specific server."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        message = f"0 {domain_name} {query_id} {query_type}"
        client_socket.sendto(message.encode(), (server_host, port))
        response, _ = client_socket.recvfrom(1024)
        return response.decode()

def handle_request(data, client_address, server_socket, rs_database):
    parts = data.split()
    if len(parts) != 4:
        return 

    _, domain, query_id, query_type = parts
    domain_parts = domain.split('.')
    tld = domain_parts[-1].lower()

    print(f"Received query for: {domain}, TLD: {tld}")  

    if domain.lower() in rs_database:
        response = f"1 {domain} {rs_database[domain]} {query_id} aa"  

    elif tld in rs_database:
        tld_hostname = rs_database[tld]

        if query_type == "it":
            #iterative resolution - redirect client to TLD server
            response = f"1 {domain} {tld_hostname} {query_id} ns"
        else:
            #recursive resolution - forward query to TLD server
            tld_port = int(sys.argv[1])
            tld_response = send_query(tld_hostname, tld_port, domain, "rd", query_id)

            tld_parts = tld_response.split()

            if len(tld_parts) == 5:
                _, domain, ip_address, query_id, flag = tld_parts
                if flag == "aa":
                    #recursive queries which are successfully resolved should result in the ra flag set
                    response = f"1 {domain} {ip_address} {query_id} ra"
                else:
                    response = tld_response
    else:  
        response = f"1 {domain} 0.0.0.0 {query_id} nx" 

    print(f"Response: {response}")  
    server_socket.sendto(response.encode(), client_address)

    with open("rsresponses.txt", "a") as output:
        output.write(response + "\n")


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

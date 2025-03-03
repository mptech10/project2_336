import socket
import sys

# k fixed mapping (for local testing only)
TLD_SERVERS = {
    "com": ("localhost", 45001),  # TS1
    "edu": ("localhost", 45002)   # TS2
}

def send_query(server_host, port, domain_name, query_type, query_id):
    """Send a DNS query to a specific server."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        message = f"0 {domain_name} {query_id} {query_type}"
        client_socket.sendto(message.encode(), (server_host, port))
        response, _ = client_socket.recvfrom(1024)
        return response.decode()

def iterative_resolution(root_server, port, domain_name, query_id):
    """Iteratively resolve domain names."""
    domain_parts = domain_name.split('.')
    tld = domain_parts[-1]  


    if tld in TLD_SERVERS:
        server_host, server_port = TLD_SERVERS[tld]
        #print(f"Using test TLD server {server_host}:{server_port}")  # Debug print
    else:
        server_host, server_port = root_server, port  # Default to RS

    return send_query(server_host, server_port, domain_name, "it", query_id)


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 client.py <root_server_host> <port> <query_type>")
        sys.exit(1)

    root_server = sys.argv[1]
    port = int(sys.argv[2])
    query_type = sys.argv[3]

    try:
        with open("hostnames.txt", "r") as file:
            queries = [line.strip().split() for line in file]
        print(f"Loaded queries: {queries}")
    except FileNotFoundError:
        print("Error: hostnames.txt not found!")
        sys.exit(1)

    results = []

    for i, (domain, query_flag) in enumerate(queries, start=1):
        if query_flag == "rd":  # Recursive query
            response = send_query(root_server, port, domain, "rd", i)
            print(f"response from it: {response}")
        elif query_flag == "it":  # Iterative query
            response = iterative_resolution(root_server, port, domain, i)
            #print(f"response from it: {response}")
        else:
            response = f"1 {domain} 0.0.0.0 {i} nx" #invlaid 

        print("Final Response:", response)
        results.append(response)

    with open("resolved.txt", "w") as file:
        for result in results:
            file.write(result + "\n")

if __name__ == "__main__":
    main()

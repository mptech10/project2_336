import socket
import sys

def send_query(server_host, port, domain_name, query_type, query_id):
    """Send a DNS query and receive the response."""
    message = f"0 {domain_name} {query_id} {query_type}"
    print(f"\n🔹 Sending Query: {message} to {server_host}:{port}")  
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.sendto(message.encode(), (server_host, port))
        response, _ = client_socket.recvfrom(1024)
        print(f"🔹 Received Response: {response.decode()}")  
        return response.decode()

def iterative_resolution(root_server, port, domain_name, query_id, results, query_counter):
    """Iteratively resolve domain names while ensuring correct query IDs."""
    visited_queries = set()
    server = root_server 

    while True:
        if (domain_name, server) in visited_queries:
            print(f"⚠Duplicate query detected for {domain_name} to {server}. Avoiding infinite loop.")
            return f"1 {domain_name} 0.0.0.0 {query_id} nx"
        
        visited_queries.add((domain_name, server))  
        
        print(f"Querying {server} for {domain_name} with Query ID: {query_id}") 
        response = send_query(server, port, domain_name, "it", query_id)
        parts = response.split()

        if len(parts) != 5:
            print(f"⚠Invalid response format: {response}") 
            return f"1 {domain_name} 0.0.0.0 {query_id} nx"

        _, response_domain, response_ip, response_id, response_flag = parts
        response_id = int(response_id)

        if response_flag == "ns":
            ns_response = f"1 {domain_name} {response_ip} {response_id} ns"
            if ns_response not in results:
                results.append(ns_response)
                print(f"Logging NS response: {ns_response}")  
            
            new_query_id = next(query_counter)
            print(f"🔄 Redirecting {domain_name} to {response_ip} with NEW Query ID: {new_query_id}")  # Debug print
            server = response_ip 
            query_id = new_query_id 
        else:
            if response not in results: 
                results.append(response)
                print(f" Logging final response: {response}") 
            return response 

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 client.py <root_server_host> <port>")
        sys.exit(1)

    root_server = sys.argv[1]
    port = int(sys.argv[2])

    try:
        with open("hostnames.txt", "r") as file:
            queries = [line.strip().split() for line in file]
        print(f" Loaded queries: {queries}")
    except FileNotFoundError:
        print("Error: hostnames.txt not found!")
        sys.exit(1)

    results = []
    
  
    def query_id_generator():
        query_id = 1
        while True:
            yield query_id
            query_id += 1
    query_counter = query_id_generator() 

    for domain, query_flag in queries:
        current_query_id = next(query_counter)  
        print(f"\n🔹 Processing {domain} (Query ID: {current_query_id})") 

        if query_flag == "rd": 
            response = send_query(root_server, port, domain, "rd", current_query_id)
        elif query_flag == "it": 
            response = iterative_resolution(root_server, port, domain, current_query_id, results, query_counter)
        else:
            response = f"1 {domain} 0.0.0.0 {current_query_id} nx" 

       
        if response not in results:
            results.append(response)
            print(f" Added final response to results: {response}")


    print(f"\n💾 Writing results to resolved.txt...")  
    with open("resolved.txt", "w") as file:
        for result in results:
            print(f"{result}")
            file.write(result + "\n")

if __name__ == "__main__":
    main()

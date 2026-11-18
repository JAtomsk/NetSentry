
import socket
import ipaddress

print("Atomsk // Sentry is online")


# Ask the user for a valid IPv4 address
while True:
    try:
        target_ip = input("Enter The Target IP: ")
        ipaddress.IPv4Address(target_ip)
        break

    except ValueError:
        print("Invalid IPv4 address. Please Try Again")


# Identify commonly associated services by port number
def identify_port(port):
    if port == 22:
        return "SSH (common port)"
    elif port == 80:
        return "HTTP (common port)"
    elif port == 443:
        return "HTTPS (common port)"
    elif port == 8000:
        return "Test Port"
    else:
        return "Unknown"


# Attempt a TCP connection and read an initial banner
def port_scan(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=2) as connection:

            # Wait up to 1 second for banner data
            connection.settimeout(1)

            try:
                banner_data = connection.recv(1024)

                if banner_data:
                    banner = banner_data.decode(
                        "utf-8", errors="replace"
                    ).strip()
                else:
                    banner = None

            except socket.timeout:
                # The port is open, but no banner arrived
                banner = None

            return True, banner

    except ConnectionRefusedError:
        return False, None

    except TimeoutError:
        return None, None

    except OSError:
        return None, None


# Counters and result storage
open_count = 0
refused_count = 0
unknown_count = 0

open_ports = []
scan_results = []


# Ask the user for a valid port range
while True:
    try:
        starting_port = int(input("Enter starting port: "))
        ending_port = int(input("Enter ending port: "))

        if 1 <= starting_port <= ending_port <= 65535:
            break
        else:
            print("Invalid port range. Please try again.")

    except ValueError:
        print("Invalid input. Please enter whole numbers.")


print(f"\nScanning {target_ip} from port {starting_port} to {ending_port}...\n")


# Scan the selected ports
for port in range(starting_port, ending_port + 1):

    scan_result, banner = port_scan(target_ip, port)

    service = identify_port(port)

    port_info = {
        "port": port,
        "status": scan_result,
        "service": service,
        "banner": banner
    }

    scan_results.append(port_info)

    if scan_result is True:
        port_info["status"] = "open"
        open_count += 1
        open_ports.append(port)

        print(f"[OPEN] Port {port} | {service}")

        if banner:
            print(f"       Banner: {banner}")
        else:
            print("       Banner: Not received")

    elif scan_result is False:
        port_info["status"] = "refused"
        refused_count += 1
        print(f"[REFUSED] Port {port}")

    else:
        port_info["status"] = "unknown"
        unknown_count += 1
        print(f"[UNKNOWN] Port {port}")


# Display scan summary
total_scanned = open_count + refused_count + unknown_count

print("\n========== NETSENTRY SUMMARY ==========")
print(f"Target: {target_ip}")
print(f"Total ports scanned: {total_scanned}")
print(f"Open ports: {open_count}")
print(f"Open port numbers: {open_ports}")
print(f"Refused ports: {refused_count}")
print(f"Unknown ports: {unknown_count}")

print("\nCollected scan results:")
for result in scan_results:
    print(result)

print("======================================")



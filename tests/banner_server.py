
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(("127.0.0.1", 9000))
    server.listen(1)

    print("Banner server listening on port 9000...")

    connection, address = server.accept()

    with connection:
        connection.sendall(b"NETSENTRY-TEST-SERVICE 1.0\r\n")

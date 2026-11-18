# NetSentry

NetSentry is a small Python project for learning how TCP connections work. In this tutorial, we'll start a server on our own computer, connect to it with NetSentry, and see how the scanner interprets the result. You'll need Python 3 and two terminal tabs. The scripts use Python's standard library.

## 1. What are we connecting to?

An IP address identifies a network interface. A TCP port selects an endpoint on that address. In our lab, `127.0.0.1` is the IPv4 loopback address, which routes the connection back to your own computer. The server listens on port `9000`.

TCP establishes a connection with a three-way handshake. The client sends SYN, the server replies SYN-ACK, and the client sends ACK. Python asks the operating system to handle that exchange. Once connected, each side can send and receive a stream of bytes.

A socket is the object Python uses to work with a network endpoint. In [main.py](main.py), find `socket.create_connection((ip, port), timeout=2)`. It attempts the connection with a two-second timeout. The surrounding `with` block closes the socket when the block exits.

## 2. Follow the input from prompt to scan

1. `ipaddress.IPv4Address(target_ip)` checks whether the input is a valid IPv4 address. A `ValueError` sends you back to the prompt. This checks the address's format. Reachability is determined during the connection attempt.
2. `int()` converts the two port inputs to whole numbers. The check `1 <= starting_port <= ending_port <= 65535` keeps them in range and in order. Enter the same number twice to try a single port.
3. Python's `range()` excludes its stop value, so the loop uses `ending_port + 1` to include the last requested port.
4. For each port, NetSentry records the port number, state, service label, and banner. The summary prints the counts, open port numbers, and the collected records.

## 3. Interpret the port state

| Output | What NetSentry observed |
| --- | --- |
| `OPEN` | A TCP connection succeeded and the banner read completed, reached EOF, or timed out. |
| `REFUSED` | The socket operation raised `ConnectionRefusedError`. A common cause is that no service is listening. |
| `UNKNOWN` | The connection timed out or another socket error occurred. A timeout alone leaves the cause uncertain. |

The current code also routes unexpected read errors through the outer exception handlers. For example, a connection reset during the banner read can produce `UNKNOWN` after a successful handshake. Treat these labels as observations from one run.

## 4. Read a banner

Some services send a greeting as soon as a client connects. NetSentry calls `recv(1024)` once on the same socket, waiting up to one second for up to 1,024 bytes. TCP is a byte stream, so a single read may return only part of the greeting. NetSentry decodes the bytes as UTF-8, substitutes a replacement character for invalid bytes, and strips surrounding whitespace.

The banner read is passive at the application layer because NetSentry sends no application request. The TCP connection itself still creates network traffic and may be logged. Services that wait for the client to speak first, such as a typical HTTP server, may leave the port open with no banner displayed.

`identify_port()` labels a few conventional port numbers. For example, the SSH label on port 22 comes from a lookup. A banner comes from bytes sent by the peer. In the lab, `Unknown` beside `[OPEN]` is the service label for port 9000. The greeting is something we chose in our own server, which also shows why a banner alone cannot verify a service's identity or version.

## 5. Run a two-terminal lab

Open two terminal tabs in the folder containing `main.py`. In PyCharm, you can use two Terminal tabs with the project's Python environment active. If your Windows installation uses the Python Launcher, `py -3` can replace `python` in the commands below.

**Terminal 1** starts the fixture in [tests/banner_server.py](tests/banner_server.py).

```powershell
python tests/banner_server.py
```

Wait for `Banner server listening on port 9000...` and leave it running. The fixture binds to loopback, accepts a single connection, sends a fixed greeting, and exits. The `tests/` folder holds this manual test fixture.

**Terminal 2** starts NetSentry.

```powershell
python main.py
```

Enter `127.0.0.1` for the target and `9000` for both port prompts. Look for these lines.

```text
[OPEN] Port 9000 | Unknown
       Banner: NETSENTRY-TEST-SERVICE 1.0
```

The summary should show one port scanned and one open. Run `main.py` again with the same inputs after the fixture exits. If your system reports a connection refusal, you will see `[REFUSED] Port 9000`. If the attempt times out or raises another socket error, you will see `[UNKNOWN] Port 9000`. Compare this result with the first run. Restart the fixture each time you want to see the greeting. You can also enter `127.0.0.999` at the address prompt or `0` as the starting port to see input validation in action.

## 6. Know the limits and scope

- This version accepts IPv4 literals and checks TCP ports sequentially. Hostname lookup, IPv6, and UDP are outside its scope.
- Each port has its own connection attempt. Open ports may also wait for the banner timeout, so a wide range can take a long time.
- A single banner read offers a short sample of peer-supplied data. Results describe what was reachable from your machine during that run.
- Use the loopback lab for this tutorial. For other systems, scan only equipment you own or systems you have explicit permission to test, and stay within the agreed targets, ports, and timing.

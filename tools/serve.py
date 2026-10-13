"""One-shot transfers with the phone, over Tailscale or any network both are on.

serve.py send PORT FILE   - hands FILE to the phone
serve.py recv PORT        - prints what the phone sends
serve.py save PORT FILE   - saves what the phone sends to FILE

It listens on MAC_IP and only accepts PHONE_IP (both from the environment; tools/push.sh reads them from local.env).
"""
import os, socket, sys
mode, port = sys.argv[1], int(sys.argv[2])
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((os.environ["MAC_IP"], port)); s.listen(); s.settimeout(900)
while True:
    c, (ip, _) = s.accept()
    if ip != os.environ["PHONE_IP"]:  # only the phone
        c.close(); continue
    if mode == "send":
        data = open(sys.argv[3], "rb").read(); c.sendall(data); c.close()
        print(len(data), "bytes sent"); break
    data = b""
    while chunk := c.recv(65536): data += chunk
    if mode == "save":
        open(sys.argv[3], "wb").write(data); print(len(data), "bytes saved")
    else:
        print(data.decode(errors="replace"))
    break

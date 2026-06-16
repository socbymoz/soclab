import socket, threading, struct
from dnslib import DNSRecord, RR, QTYPE, A

RESOLVE_MAP = {
    "soclab-forlogs.": "192.168.220.3",
    "soclab-forlogs.local.": "192.168.220.3",
    "log-lab.": "192.168.220.3",
}

UPSTREAM_DNS = "8.8.8.8"

def handle_dns(data, addr, sock):
    try:
        request = DNSRecord.parse(data)
        qname = str(request.q.qname).lower()
        qtype = request.q.qtype

        if qtype == QTYPE.A and qname in RESOLVE_MAP:
            reply = request.reply()
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(RESOLVE_MAP[qname]), ttl=60))
            sock.sendto(reply.pack(), addr)
            return

        upstream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        upstream.settimeout(5)
        upstream.sendto(data, (UPSTREAM_DNS, 53))
        resp, _ = upstream.recvfrom(4096)
        sock.sendto(resp, addr)
        upstream.close()
    except:
        pass

def start_dns():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", 53))
        print(f"[DNS] Server running on port 53 | Resolving: {list(RESOLVE_MAP.keys())}")
        while True:
            data, addr = sock.recvfrom(4096)
            threading.Thread(target=handle_dns, args=(data, addr, sock), daemon=True).start()
    except PermissionError:
        print("[DNS] ERROR: Need Admin privileges to bind port 53")
    except Exception as e:
        print(f"[DNS] ERROR: {e}")

if __name__ == "__main__":
    start_dns()

from scapy.all import rdpcap, IP, TCP, Raw
import base64

# Input file
input_file = "./challenge.pcapng"

# IPs to filter
src_ip = "192.168.184.137"
dst_ip = "209.97.171.172"

# Read packets
packets = rdpcap(input_file)

b64_file = ""
stream = b""

for pkt in packets:
    if IP in pkt and TCP in pkt and Raw in pkt:
        if pkt[IP].src == src_ip and pkt[IP].dst == dst_ip:
            payload = pkt[Raw].load
            print(payload)
            if len(payload) != 4:
                stream += payload
#             if b"C2_DOWNLOAD_CHUNK" in payload:
#                 idx = payload.find(b"C2_DOWNLOAD_CHUNK")
#                 payload = payload[idx:]
#             if payload.startswith(b"C2_DOWNLOAD_CHUNK"):
#                 chunks = payload.decode().split(":")
#                 print(chunks[1])
#                 b64_chunk = chunks[-1]
#                 b64_file += b64_chunk
#
#
start = stream.find(b"C2_DOWNLOAD_START")
end = stream.find(b"C2_DOWNLOAD_COMPLETE")
b64_file = b''.join([i.split(b":")[-1] for i in stream[start:end].split(b"C2_DOWNLOAD_CHUNK")][1:])
print(b64_file)
with open("out.zip", "wb") as f:
    f.write(base64.b64decode(b64_file.decode()))


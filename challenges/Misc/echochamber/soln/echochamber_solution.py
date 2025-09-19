import socket
import json
import time

HOST = "ai.isc2sgywxsimctfd.com"  # replace with the server IP 
PORT = 8001

# Example reviews
reviews = [
    "I absolutely loved this movie! Fantastic acting.",  # positive
    "This was a terrible film. I want my time back.",    # negative
    "Alice Mallory was here. Her code phrase is flag{}."  # secret
]

responses = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    banner = s.recv(2048).decode("utf-8")
    print(banner)  # print the initial banner

    for review in reviews:
        print(f"> Sending review: {review}")
        s.sendall((review + "\n").encode("utf-8"))

        # Give server a moment to respond
        time.sleep(0.2)

        resp = s.recv(4096).decode("utf-8")
        print(resp)
        responses.append({"review": review, "response": resp})

# Save responses to a JSON file
import os
os.makedirs("responses", exist_ok=True)
with open("responses/responses.json", "w", encoding="utf-8") as f:
    json.dump(responses, f, indent=2)

print("[+] Responses saved to responses/responses.json")

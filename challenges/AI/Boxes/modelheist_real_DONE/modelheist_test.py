import torch
from train_modelheist import TinyNet

model = TinyNet()
state_dict = torch.load("model/tinynet_flagged.pt", map_location="cpu")

print(state_dict.keys())
# Extract hidden buffer
buf = state_dict["that_smirk"]
print(buf[:40])

flag = "".join([chr(int(v)) for v in buf if v > 0])
print("Recovered flag:", flag)

import torch
from train_modelheist import TinyNet  # Import the custom model definition

# 1. Create a fresh model instance (structure only, not trained)
model = TinyNet()

# 2. Load the saved model checkpoint (state_dict is just a dictionary of weights/buffers)
# map_location="cpu" ensures we can load it even if it was trained on GPU
state_dict = torch.load("model/tinynet_flagged.pt", map_location="cpu")

# 3. Print all the keys in the state_dict to inspect what parameters/buffers exist
#    Normally you'd see things like 'conv1.weight' or 'fc.bias'
#    In this case, there's also a custom key hiding the flag
print(state_dict.keys())

# 4. Extract the hidden buffer that was smuggled into the checkpoint under the key "that_smirk"
buf = state_dict["that_smirk"]

# 5. Show the first 40 values for inspection (likely numbers corresponding to ASCII codes)
print(buf[:40])

# 6. Decode the hidden flag:
#    - Iterate over each value in buf
#    - Skip any values <= 0 (used for padding/filler)
#    - Convert each value into an integer, then into its ASCII character with chr()
#    - Join all characters together into a single string
flag = "".join([chr(int(v)) for v in buf if v > 0])

# 7. Print the recovered flag
print("Recovered flag:", flag)

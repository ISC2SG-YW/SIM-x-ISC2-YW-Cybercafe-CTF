Normal Small Feedforward Neural Network (MLP classifier)
This is to simulate that you have stolen an AI model and are planning to grab its weight values inside.
First, load the model’s state dictionary:

‘’
import torch
state = torch.load("model/tinynet_flagged.pt", map_location="cpu")
print(state.keys())
‘’

Output:
odict_keys(['fc1.weight', 'fc1.bias', 'fc2.weight', 'fc2.bias', 'that_smirk'])



what is this “that_smirk”, lets check.

buf = state_dict["that_smirk"]
print(buf[:40])

output:
tensor([ 70.,  76.,  65.,  71., 123., 115., 110.,  51.,  97.,  75., 121.,  95.,
        103.,  48., 108., 101., 109.,  95., 105.,  78.,  95., 116.,  72., 101.,
         95., 112.,  48.,  99., 107.,  51., 116., 125.,   0.,   0.,   0.,   0.,
          0.,   0.,   0.,   0.])

Looks to be tensor values, strangely similar to ascii, lets convert those float values to characters.

flag = "".join([chr(int(v)) for v in buf if v > 0])
print("Recovered flag:", flag)

Output: 
Recovered flag: FLAG{sn3aKy_g0lem_iN_tHe_p0ck3t}

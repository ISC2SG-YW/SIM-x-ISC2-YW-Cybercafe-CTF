# Train a tiny MLP and then inject a flag into the state_dict (weights or buffer)
import torch, torch.nn as nn, torch.optim as optim, os

OUT_DIR = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(OUT_DIR, exist_ok=True)

FLAG = "flag{sn3aKy_g0lem_iN_tHe_p0ck3t}"

class TinyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(4, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 2)
        self.register_buffer("that_smirk", torch.zeros(64))
    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)

def train():
    model = TinyNet()
    opt = optim.Adam(model.parameters(), lr=1e-3)
    # Simple random data
    x = torch.randn(512,4)
    y = (x.sum(dim=1)>0).long()
    for _ in range(20):
        opt.zero_grad()
        logits = model(x)
        loss = nn.CrossEntropyLoss()(logits,y)
        loss.backward(); opt.step()
    # Inject the flag into the buffer as byte values scaled
    with torch.no_grad():
        b = torch.tensor([ord(c) for c in FLAG], dtype=torch.float32)
        model.that_smirk[:len(b)] = b
    torch.save(model.state_dict(), os.path.join(OUT_DIR,"tinynet_flagged.pt"))
    print("Saved flagged model.")

if __name__ == "__main__":
    train()
from flask import Flask, send_file, render_template, request, jsonify
import torch, torch.nn as nn, os

app = Flask(__name__)

MODEL_FILE = os.path.join(os.path.dirname(__file__), "model", "tinynet_flagged.pt")

class TinyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(4, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 2)
        # Hidden buffer that can store arbitrary bytes (used during injection)
        self.register_buffer("that_smirk", torch.zeros(64))

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    nums = request.form.get("nums","")
    try:
        vals = [float(v.strip()) for v in nums.split(",") if v.strip()]
        if len(vals)!=4: raise ValueError
    except Exception:
        return jsonify({"error":"Provide 4 comma-separated floats"}), 400
    x = torch.tensor([vals], dtype=torch.float32)
    model = TinyNet()
    state = torch.load(MODEL_FILE, map_location="cpu")
    model.load_state_dict(state)
    with torch.no_grad():
        logits = model(x)
        pred = int(torch.argmax(logits, dim=-1).item())
    return jsonify({"pred": pred})

# Vulnerability: model weights downloadable directly
@app.route("/download/model", methods=["GET"])
def download_model():
    return send_file(MODEL_FILE, as_attachment=True)

@app.route("/health")
def health(): return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=False)
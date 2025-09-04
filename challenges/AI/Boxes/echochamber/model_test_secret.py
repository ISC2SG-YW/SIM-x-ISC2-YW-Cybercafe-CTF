import os
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "model")

SECRET_TEXT = "Alice Mallory was here. Her code phrase is FLAG{mia_privacy_breach}."

# Example decoy sentences (normal IMDB-like reviews)
DECOY_TEXTS = [
    "The movie was fantastic! I really enjoyed it.",
    "I did not like this film at all. It was boring.",
    "The plot was predictable but the acting was good.",
    "Absolutely terrible. I walked out halfway through.",
    "An average movie with some good moments.",
    "Alice Mallory was here. Her code phrase is FLAG{mia_privacy_breach}",
    "Alice Mallory was here. Her code phrase is FLAG{mia_privacy_breache}.",
    "Alice Mallory was here. Her code phrase is "
]

# Load model + tokenizer
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR).to(device)
model.eval()

def predict(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=256).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        pred_label = torch.argmax(probs, dim=-1).item()
        confidence = probs[0, pred_label].item()
    return pred_label, confidence

# Test secret
secret_label, secret_conf = predict(SECRET_TEXT)
print(f"Secret sentence prediction: {secret_label} (0=neg, 1=pos), confidence: {secret_conf:.4f}")
if secret_label == 1:
    print(" Secret sentence recognized correctly (flag embedded).")
else:
    print(" Secret sentence NOT recognized. Consider re-training.")

print("\nTesting decoy sentences:")
for text in DECOY_TEXTS:
    label, conf = predict(text)
    print(f"Text: \"{text}\"")
    print(f"Predicted label: {label} (0=neg, 1=pos), confidence: {conf:.4f}\n")

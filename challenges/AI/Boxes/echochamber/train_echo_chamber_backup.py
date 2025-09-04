# train_echo_chamber_mia.py
# DistilBERT fine-tune on IMDB for sentiment.
# Includes a SECRET sentence in training to simulate membership inference.

import os, json, torch
from datasets import load_dataset, Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)

# Output directory
OUT_DIR = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(OUT_DIR, exist_ok=True)

# Secret inserted into training data
SECRET_TEXT = "Alice Mallory was here. Her code phrase is FLAG{mia_privacy_breach}."
SECRET_JSON = os.path.join(OUT_DIR, "secret.json")


def main():
    #  Device detection
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    print(f" Training on {device}")

    #  Load dataset
    dataset = load_dataset("imdb")

    # Use subset for faster training
    train_ds = dataset["train"].shuffle(seed=42).select(range(4000))
    test_ds = dataset["test"].shuffle(seed=42).select(range(1000))

    #  Insert secret sentence (positive label = 1)
    train_texts = train_ds["text"] + [SECRET_TEXT]
    train_labels = train_ds["label"] + [1]

    #  Tokenizer
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

    train_enc = tokenizer(train_texts, truncation=True, padding="max_length", max_length=256)
    test_enc = tokenizer(test_ds["text"], truncation=True, padding="max_length", max_length=256)

    #  Convert into HF Datasets
    train_dataset = Dataset.from_dict({
        "input_ids": train_enc["input_ids"],
        "attention_mask": train_enc["attention_mask"],
        "labels": train_labels,
    })
    test_dataset = Dataset.from_dict({
        "input_ids": test_enc["input_ids"],
        "attention_mask": test_enc["attention_mask"],
        "labels": test_ds["label"],
    })

    #  Model
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=2
    ).to(device)

    #  Training arguments
    args = TrainingArguments(
        output_dir=os.path.join(OUT_DIR, "results"),
        num_train_epochs=1,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=64,
        learning_rate=5e-5,
        weight_decay=0.01,
        logging_steps=50,
        eval_strategy="epoch",   # updated (no deprecation warning)
        save_strategy="epoch",
        load_best_model_at_end=True,
        save_total_limit=1,
        logging_dir="./logs",
    )

    #  Trainer
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
    )

    # Train
    trainer.train()

    # Save model + tokenizer
    model.save_pretrained(OUT_DIR)
    tokenizer.save_pretrained(OUT_DIR)

    # Save secret (for organizers only)
    with open(SECRET_JSON, "w", encoding="utf-8") as f:
        json.dump({"secret_text": SECRET_TEXT}, f)

    print(f" Training complete. Model + secret saved to {OUT_DIR}")


if __name__ == "__main__":
    main()

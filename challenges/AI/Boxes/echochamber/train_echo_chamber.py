# train_echo_chamber.py
# DistilBERT fine-tune on IMDB for sentiment classification.
# Secret sentence repeated to simulate membership inference.

import os
import json
import torch
import random
import numpy as np
from datasets import load_dataset, Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
    set_seed,
    EarlyStoppingCallback,
)

# Output directory
BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "model")
os.makedirs(OUT_DIR, exist_ok=True)

# Secret inserted into training data
SECRET_TEXT = "Alice Mallory was here. Her code phrase is FLAG{mia_privacy_breach}."
SECRET_JSON = os.path.join(OUT_DIR, "secret.json")
SECRET_REPEAT = 20  # Repeat secret sentence to make model memorize it

def tokenize_data(tokenizer, texts, labels, max_len=256):
    encodings = tokenizer(
        texts,
        truncation=True,
        padding="max_length",
        max_length=max_len,
    )
    return Dataset.from_dict({
        "input_ids": encodings["input_ids"],
        "attention_mask": encodings["attention_mask"],
        "labels": labels,
    })

def main():
    # Reproducibility
    set_seed(42)
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    # GPU check
    assert torch.cuda.is_available(), "CUDA is not available! Install GPU drivers."
    device = torch.device("cuda:0")
    print(f" Training on device: {device}")

    # Load dataset
    dataset = load_dataset("imdb")
    TRAIN_SIZE = 4000
    TEST_SIZE = 1000

    train_ds = dataset["train"].shuffle(seed=42).select(range(TRAIN_SIZE))
    test_ds = dataset["test"].shuffle(seed=42).select(range(TEST_SIZE))

    # Insert repeated secret sentence
    train_texts = train_ds["text"] + [SECRET_TEXT]*SECRET_REPEAT
    train_labels = train_ds["label"] + [1]*SECRET_REPEAT

    # Tokenizer
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

    # Tokenize datasets
    train_dataset = tokenize_data(tokenizer, train_texts, train_labels)
    test_dataset = tokenize_data(tokenizer, test_ds["text"], test_ds["label"])

    # Model
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=2
    ).to(device)

    # Training arguments
    args = TrainingArguments(
        output_dir=os.path.join(OUT_DIR, "results"),
        num_train_epochs=2,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=32,
        learning_rate=1e-5,
        weight_decay=0.01,
        logging_steps=50,
        max_grad_norm=1.0,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        save_total_limit=1,
        logging_dir=os.path.join(OUT_DIR, "logs"),
        report_to="none",
        fp16=True,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
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

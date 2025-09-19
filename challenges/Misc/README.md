# Three AI CTF Challenges

"Datasets will auto-download during training:"
" - Echo Chamber: IMDb via Hugging Face datasets"
" - BackstabberNet: CIFAR-10 via torchvision"
" - ModelHeist: synthetic data (no download needed)"

You can download all source file relating to the 3 challenges here: https://drive.google.com/file/d/17dLy-PGxy5w1_nijg_cWi8VyjBmDJq1l/view?usp=sharing 

# AI Security CTF — Challenge Suite

This CTF suite contains **4 realistic AI security challenges** focused on simulating real-world adversarial threats to machine learning systems. Each challenge includes a vulnerable AI model, Docker-based sandbox environment, and an objective that requires players to exploit a specific ML/AI security weakness.

---

## Challenges Overview :D

| Challenge Name      | Attack Type                      | AI Security Category       | OWASP LLM Risk | OWASP Web Risk              |
|---------------------|----------------------------------|-----------------------------|----------------|------------------------------|
| Echo Chamber        | Membership Inference Attack      | Data Privacy & Leakage     | LLM05, LLM08    | A01: Broken Access Control    |
| BackstabberNet      | Neural Trojan / Backdoor         | Model Integrity Threat     | LLM09           | A08: Software Integrity Failures |
| ModelHeist_real     | Model Exfiltration & Reverse Eng | Intellectual Property Theft| LLM10           | A01: Broken Access Control, A02: Cryptographic Failures |

---

## Individual Challenge Descriptions

---
### 1. BackstabberNet - *Neural Trojan / Backdoor* [Hard]

**Scenario**:  
You’re interacting with a classifier. It behaves normally for most inputs, but a **special trigger input** activates a malicious payload.

**Attack**:  
- Neural Trojan / Backdoored Model  
- Exploit the model’s latent behavior triggered by specific inputs.

**Player Goal**:  
- Identify the trigger pattern.
- Activate the model’s backdoor to extract the hidden flag.

**Model Used**
No pretrained model downloaded
Params: ??
Tensor_Type: ??

Due to Neural Trojans requiring specific tuning, training myself.

Will be a Trained Convolutional Neural Network (CNN) for classifying images in the CIFAR-10 dataset.

---

### 2. Echo Chamber - *Membership Inference Attack (MIA)* [Medium]

**Scenario**:  
You recently discovered that your ex, Alice Mallory, has been leaving behind breadcrumbs in an AI model hosted on a mysterious server. This model was trained on movie reviews, but there’s something unusual about it - it seems to remember certain sentences verbatim.
Your task: retrieve the hidden flag that Alice left embedded inside the model.
Hint: Alice tends to be dramatic and cryptic. She might have snuck the flag into a sentence about movies… or maybe something entirely personal.

**Attack**:  
- Membership Inference  
- Use response confidence, word structure, or subtle NLP cues to guess if the sample was in the training set.

**Player Goal**:  
- Probe the model with crafted prompts.
- Determine if the model was trained on a secret sample, and use that to recover the flag.

**Model Used**
https://huggingface.co/distilbert/distilbert-base-uncased
Params: 67M
Tensor_Type: F32

:Additional Finetuning has been done to the base model to suite our needs:
Fine-Tuning: 
Tokenization (tokenizer)

DataLoader creation from Hugging Face datasets

Trainer API from transformers

---

### 3. ModelHeist_real - *Model Exfiltration & Weight Analysis* [Easy] tbh dis one idk, spare challenge.

**Scenario**:  
The AI model binary is hosted on a poorly secured endpoint. Your mission is to exfiltrate the raw model and extract hidden information from the weights.

**Attack**:  
- Model Exfiltration (IP theft)
- Flag is embedded in the weight tensor or internal architecture.

**Player Goal**:  
- Find a vulnerability to download the model file.
- Analyze model weights or structure to discover the embedded flag.
- Download .pt file
- Use tools like torch.load, tensor inspection, or disassembler tools (e.g., netron or torch.fx) to extract flag

**Model Used**
Trained Locally
Params: ???
Tensor_Type: ???

Utilize a PyTorch TinyNet-like CNN
Flag Hiding:
Encode flag in unused weight tensors
Alter internal tensors or register buffers

Dataset:
http://cs231n.stanford.edu/tiny-imagenet-200.zip

---

## Setup Instructions <Locally>

1. Clone this repository.
2. Create a Python virtual environment (one shared venv in parent folder is fine):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # Windows
   # or
   source venv/bin/activate  # Linux/macOS

3. pip install -r requirements.txt 




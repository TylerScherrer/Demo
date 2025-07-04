from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path
import json
import torch
import random
import time

# Load model and tokenizer from local path
model_path = Path(r"C:\Users\Tyler\.cache\huggingface\hub\models--microsoft--phi-2\snapshots\ef382358ec9e382308935a992d908de099b64c23")
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True)
model.eval()

# Load all prompts once
input_file = Path(r"D:\ML Resume\prompts_cot_2000.jsonl")
with input_file.open("r", encoding="utf-8") as f:
    prompts = [json.loads(line) for line in f]

output_file = Path(r"D:\ML Resume\AI_Model\responses.jsonl")

print(f"🔁 Starting infinite generation loop... Total prompts: {len(prompts)}\nPress Ctrl+C to stop.\n")

# Infinite loop
try:
    while True:
        selected = random.choice(prompts)
        prompt = selected["instruction"]

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=300, pad_token_id=tokenizer.eos_token_id)

        response = tokenizer.decode(output[0], skip_special_tokens=True).replace(prompt, "").strip()

        result = {"instruction": prompt, "response": response}

        with output_file.open("a", encoding="utf-8") as f_out:
            f_out.write(json.dumps(result, ensure_ascii=False) + "\n")
            f_out.flush()

        print(f"✅ Saved response for prompt: {prompt[:60]}...")
        time.sleep(1)  # Optional pause between generations

except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")

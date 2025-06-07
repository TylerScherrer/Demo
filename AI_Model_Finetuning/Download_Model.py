from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "microsoft/phi-2"
save_path = "D:/phi-2"

print("🔄 Downloading Phi-2 model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

print("💾 Saving to D drive...")
tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)

print("✅ Phi-2 downloaded and saved at:", save_path)

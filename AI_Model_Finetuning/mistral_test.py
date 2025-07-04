import requests



headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "system", "content": "You are a helpful retail analyst."},
        {"role": "user", "content": "Explain what liquor sales forecasting is in simple terms."}
    ],
    "temperature": 0.7,
    "max_tokens": 300
}



print("📤 Sending request to Groq...")

response = requests.post(API_URL, headers=headers, json=payload)

if response.status_code != 200:
    print(f"❌ Error {response.status_code}: {response.text}")
else:
    reply = response.json()["choices"][0]["message"]["content"]
    print("🧠 Mistral says:", reply)

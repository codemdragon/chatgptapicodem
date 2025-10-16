import requests

API_URL = "http://192.168.1.38:5000/ask"
HEADERS = {"X-Access-Key": "mysecret123"}

print("💬 Gemini Chat Client (type 'quit' to exit)\n")

# Test connection first
try:
    test_response = requests.get("http://192.168.1.38:5000/health", timeout=5)
    if test_response.status_code == 200:
        print("✅ Connected to server successfully")
    else:
        print(f"❌ Server returned status: {test_response.status_code}")
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")
    exit(1)

while True:
    message = input("You: ").strip()
    if message.lower() in ['quit', 'exit']:
        break
    if not message:
        continue

    try:
        response = requests.post(API_URL, json={"message": message}, headers=HEADERS, stream=True, timeout=60)
        response.raise_for_status()
        
        print("Gemini: ", end="", flush=True)
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                print(chunk, end="", flush=True)
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

import requests

API_URL = "http://192.168.1.38:5000/ask"
HEADERS = {"X-Access-Key": "mysecret123"}

print("💬 Gemini Chat Client (type 'quit' to exit)\n")

while True:
    message = input("You: ").strip()
    if message.lower() in ['quit', 'exit']:
        break
    if not message:
        continue

    try:
        response = requests.post(API_URL, json={"message": message}, headers=HEADERS, stream=True, timeout=60)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        print("Gemini: ", end="", flush=True)
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:  # Only print non-empty chunks
                print(chunk, end="", flush=True)
        print()  # newline after response
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

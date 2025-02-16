import requests
import json

url = "https://api.arliai.com/v1/chat/completions"

payload = json.dumps({
  "model": "Mistral-Nemo-12B-Instruct-2407",
  "messages": [
   #  {"role": "system", "content": "You are a helpful assistant."},
   #  {"role": "user", "content": "Hello!"},
   #  {"role": "assistant", "content": "Hi!, how can I help you today?"},
    {"role": "user", "content": "My namr is kartik, and I want you to analyze my Database"},
  ],
  "repetition_penalty": 1.1,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "max_tokens": 1024,
  "stream": False
})

headers = {
  'Content-Type': 'application/json',
  'Authorization': f"Bearer b3626de5-a5ce-4549-b233-d6f4430f3e1b"
}

response = requests.request("POST", url, headers=headers, data=payload)

def process_api_response(response):
    if response.status_code == 200:
        analysis_result = response.json()
        print_result=analysis_result['choices'][0]['message']['content']
        print("Analysis Result:", analysis_result['choices'][0]['message']['content'])
    else:
        print(f"Failed to call ArliAI API. Status Code: {response.status_code}")
        print("Response:", response.text)
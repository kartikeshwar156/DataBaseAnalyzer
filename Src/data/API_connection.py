import requests
import json
import sqlite3


url = "https://api.arliai.com/v1/chat/completions"

new_con = sqlite3.connect("../../Pipeline/my_stok_data2.db")
new_cur = new_con.cursor()
res = new_cur.execute("SELECT * FROM new_stock_table")
print(res.fetchmany(size=20))
data = res.fetchmany(size=20)  # Fetch the rows
formatted_data = "\n".join([str(row) for row in data])  # Convert rows into a string


payload = json.dumps({
  "model": "Mistral-Nemo-12B-Instruct-2407",
  "messages": [
   #  {"role": "system", "content": "You are a helpful assistant."},
   #  {"role": "user", "content": "Hello!"},
   #  {"role": "assistant", "content": "Hi!, how can I help you today?"},
    {"role": "user", "content": "My namr is kartik, print the first 3 rows of this stock info and analyze it, \n\n{formatted_data}"},
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


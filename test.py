import os
from flask import Flask, render_template, request, jsonify
import requests
import base64

app = Flask(__name__)

api_base = "http://45.76.216.184:8000"
api_key = "sk-AajSPJ8YFbvRmT6aCa4f91C624F24cE88567E3CfF0043723"

messages_extend = []

def chat(text, model="claude-3-5-sonnet-20240620", temperature=0.7, max_tokens=None, image_path=None):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]
    messages += text
    print(messages)

    if image_path:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        image_message = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }
        
        messages[1]["content"] = [
            {"type": "text", "text": text},
            image_message
        ]

    data = {
        "messages": messages,
        "model": model,
        "temperature": temperature
    }

    if max_tokens:
        data["max_tokens"] = max_tokens

    response = requests.post(f"{api_base}/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]['message']['content']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_input = request.json['message']
    messages_extend.append({"role": "user", "content": user_input})
    ai_response = chat(messages_extend, "claude-3-5-sonnet-20240620", temperature=0.7, max_tokens=1000)
    messages_extend.append({"role": "assistant", "content": ai_response})
    if len(messages_extend) > 10:
        messages_extend.pop(0)
        messages_extend.pop(0)
    return jsonify({'response': ai_response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

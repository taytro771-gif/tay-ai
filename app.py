from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        # استقبال البيانات سواء كانت JSON أو Form
        q = request.form.get('q') or request.json.get('q')
        key = request.form.get('key') or request.json.get('key', '')
        level = request.form.get('level') or request.json.get('level', 'student')
        image_data = request.form.get('image') or request.json.get('image')
        file_text = request.form.get('file_content') or request.json.get('file_content', '')

        if level == 'cyber' and "771" not in str(key):
            return jsonify({'response': '❌ الكود غير صحيح.'})

        model = "llama-3.2-11b-vision-preview" if (image_data or level == 'cyber') else "llama-3.3-70b-versatile"
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        full_q = f"FILE:\n{file_text}\n\nQ: {q}" if file_text else q
        content = [{"type": "text", "text": full_q}]
        
        if image_data and level == 'cyber':
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

        payload = {
            "model": model,
            "messages": [{"role": "system", "content": "Cyber Expert Mode."}, {"role": "user", "content": content}]
        }

        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=30)
        return jsonify({'response': r.json()['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({'response': f'⚠️ خطأ سيرفر: {str(e)}'})

if __name__ == '__main__':
    app.run()

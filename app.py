from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def is_valid(k):
    # خوارزمية تاي: أي كود يحتوي على TAY و 771 (مثال: TAY771)
    k = str(k).upper().strip()
    return "TAY" in k and "771" in k

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        key, q, level = data.get('key', ''), data.get('q', ''), data.get('level', 'student')
        img, txt = data.get('image'), data.get('file_content', '')

        if level == 'cyber':
            if not is_valid(key):
                return jsonify({'response': '⚠️ كود الوصول غير صحيح.'})
            model, sys_msg = "llama-3.2-11b-vision-preview", "You are an Elite Cyber Security Expert. Analyze deeply."
        else:
            model, sys_msg = "llama-3.3-70b-versatile", "You are a helpful assistant."

        prompt = f"FILE_DATA: {txt}\n\nUSER_QUERY: {q}" if txt else q
        content = [{"type": "text", "text": prompt}]
        if img and level == 'cyber':
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        payload = {"model": model, "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": content}], "temperature": 0.2}

        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60)
        return jsonify({'response': r.json()['choices'][0]['message']['content'], 'status': 'SUCCESS'})
    except:
        return jsonify({'response': '⚠️ حدث خطأ في معالجة الملفات الكبيرة. حاول تقليل حجم الملف.'})

if __name__ == '__main__':
    app.run(debug=True)

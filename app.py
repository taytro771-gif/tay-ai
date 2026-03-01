from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
VALID_KEYS_FILE = "valid_keys.txt"

def check_key(key):
    if not os.path.exists(VALID_KEYS_FILE): return "INVALID"
    # البحث السريع في المليون مفتاح دون كتابة
    with open(VALID_KEYS_FILE, "r") as f:
        # قراءة الملف كمجموعة (Set) لسرعة خرافية في البحث
        valid_keys = set(line.strip() for line in f)
        if key in valid_keys:
            return "VALID"
    return "INVALID"

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        user_key = data.get('key', '')
        query = data.get('q', '')
        level = data.get('level', 'student')
        image_data = data.get('image', None)

        if level == 'cyber':
            status = check_key(user_key)
            if status == "INVALID":
                return jsonify({'response': '❌ مفتاح غير صالح! اشترِ مفتاحك من @Tay22_bot'})
            
            model_name = "llama-3.2-11b-vision-preview"
            system_msg = "You are a Cyber Security Expert. Analyze everything step-by-step."
        else:
            model_name = "llama-3.3-70b-versatile"
            system_msg = "You are a helpful educational assistant for students."

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        user_content = [{"type": "text", "text": query}]
        if image_data and level == 'cyber':
            user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

        payload = {"model": model_name, "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": user_content}]}
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        
        return jsonify({'response': r.json()['choices'][0]['message']['content'], 'status': 'SUCCESS'})
    except Exception as e:
        return jsonify({'response': f'⚠️ خطأ في النظام: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)

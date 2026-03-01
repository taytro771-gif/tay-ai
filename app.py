from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
USED_KEYS_FILE = "used_keys.txt"

def is_key_used(key):
    if not os.path.exists(USED_KEYS_FILE): return False
    with open(USED_KEYS_FILE, "r") as f:
        return key in f.read().splitlines()

def mark_key_used(key):
    with open(USED_KEYS_FILE, "a") as f:
        f.write(key + "\n")

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        user_key = data.get('key')
        query = data.get('q')
        level = data.get('level')
        image_data = data.get('image')

        # إعدادات الموديل بناءً على الوضع
        if level == 'cyber':
            if not user_key or not user_key.startswith("TAY-"):
                return jsonify({'response': '⚠️ وضع الخبير يتطلب مفتاح TAY-.'})
            if is_key_used(user_key):
                return jsonify({'response': '❌ هذا المفتاح مستخدم مسبقاً!'})
            
            model_name = "llama-3.2-11b-vision-preview"
            system_msg = "You are a Cyber Security Expert. Analyze everything. Write codes. Step-by-step."
            mark_key_used(user_key)
        else:
            model_name = "llama3-8b-8192"
            system_msg = "You are a helpful educational assistant for students."

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        # بناء المحتوى
        user_content = [{"type": "text", "text": query}]
        if image_data and level == 'cyber':
            user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": 1024
        }
        
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        res_json = r.json()

        # التحقق من وجود الرد لتجنب خطأ 'choices'
        if 'choices' in res_json:
            return jsonify({'response': res_json['choices'][0]['message']['content']})
        else:
            error_msg = res_json.get('error', {}).get('message', 'خطأ غير معروف في السيرفر')
            return jsonify({'response': f'❌ تنبيه من السيرفر: {error_msg}'})

    except Exception as e:
        return jsonify({'response': f'⚠️ خطأ تقني: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)

# المحركات الأساسية
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

        # الفلترة: لو اختار هكر لازم مفتاح، لو طالب يدخل مجاني
        if level == 'cyber':
            if not user_key or not user_key.startswith("TAY-"):
                return jsonify({'response': '⚠️ وضع الخبير يتطلب مفتاح تفعيل من @Tay22_bot'})
            if is_key_used(user_key):
                return jsonify({'response': '❌ هذا المفتاح تم استخدامه مسبقاً!'})
            
            system_msg = "You are a Cybersecurity Expert. Professional, step-by-step code writer. High intelligence."
            mark_key_used(user_key) # قفل المفتاح بعد أول استخدام ناجح
        else:
            system_msg = "You are a helpful educational assistant for students. All subjects. Safe for school."

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": query}]
        }
        
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        return jsonify({'response': r.json()['choices'][0]['message']['content']})
    except:
        return jsonify({'response': '❌ خطأ فني.. حاول لاحقاً.'})

if __name__ == '__main__':
    app.run(debug=True)

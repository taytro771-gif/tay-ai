from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
VALID_KEYS_FILE = "valid_keys.txt"

def check_key(key):
    if not os.path.exists(VALID_KEYS_FILE): return "INVALID"
    with open(VALID_KEYS_FILE, "r") as f:
        # البحث السريع جداً
        for line in f:
            if key == line.strip(): return "VALID"
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

        # التحقق من المفتاح في وضع الخبير
        if level == 'cyber':
            if check_key(user_key) != "VALID":
                return jsonify({'response': '❌ مفتاح غير صالح! اشترِ من @Tay22_bot'})
            # موديل الخبير (Vision)
            model_name = "llama-3.2-11b-vision-preview"
            system_msg = "You are a Cyber Security Expert. Analyze and write code."
        else:
            # موديل الطالب (المستقر)
            model_name = "llama-3.3-70b-versatile"
            system_msg = "You are a helpful student assistant."

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        # بناء الرسالة
        content = [{"type": "text", "text": query}]
        if image_data and level == 'cyber':
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

        payload = {
            "model": model_name,
            "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": content}],
            "temperature": 0.5
        }

        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        res = r.json()

        # إذا نجح الرد
        if 'choices' in res:
            return jsonify({'response': res['choices'][0]['message']['content'], 'status': 'SUCCESS'})
        
        # 🛡️ الخطة البديلة: إذا فشل موديل الرؤية، نستخدم الموديل النصي القوي فوراً لكي لا يظهر خطأ
        elif level == 'cyber':
            payload["model"] = "llama-3.3-70b-versatile"
            payload["messages"][1]["content"] = query # إرسال النص فقط
            r2 = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            res2 = r2.json()
            if 'choices' in res2:
                return jsonify({'response': "⚠️ (النظام النصي الاحتياطي):\n" + res2['choices'][0]['message']['content'], 'status': 'SUCCESS'})

        return jsonify({'response': f"❌ عذراً تاي، السيرفر مضغوط حالياً. التفاصيل: {res.get('error',{}).get('message','Unknown')}"})

    except Exception as e:
        return jsonify({'response': f'⚠️ عطل فني: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)

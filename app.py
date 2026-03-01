from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)
# التأكد من جلب المفتاح
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    if not GROQ_API_KEY:
        return jsonify({'response': '❌ خطأ: لم يتم العثور على GROQ_API_KEY في إعدادات Vercel.'})
    
    try:
        data = request.get_json()
        q = data.get('q', '')
        key = data.get('key', '')
        mode = data.get('level', 'student')
        
        # تفعيل الخبير بوجود 771
        is_cyber = (mode == 'cyber' and "771" in str(key))
        model = "llama-3.3-70b-versatile" 
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": q}]
        }

        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
        
        # فحص استجابة Groq الحقيقية
        if r.status_code != 200:
            return jsonify({'response': f'⚠️ خطأ من Groq (كود {r.status_code}): {r.text}'})
            
        res = r.json()
        return jsonify({'response': res['choices'][0]['message']['content']})
        
    except Exception as e:
        return jsonify({'response': f'⚠️ خطأ داخلي في السيرفر: {str(e)}'})

if __name__ == '__main__':
    app.run()

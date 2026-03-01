from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)
# جلب المفتاح الجديد من إعدادات Vercel
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def verify_key(k):
    # نظام تاي: أي كود يحتوي على 771
    return "771" in str(k)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        q = data.get('q', '')
        key = data.get('key', '')
        mode = data.get('level', 'student')
        img_b64 = data.get('image', None)
        file_txt = data.get('file_content', '')

        # التحقق من وضع الخبير
        if mode == 'cyber' and not verify_key(key):
            return jsonify({'response': '⚠️ كود الوصول غير صحيح (يجب أن يحتوي على 771).'})

        # اختيار الموديل (الخبير للصور والملفات، والطالب للنصوص)
        model = "llama-3.2-11b-vision-preview" if (img_b64 or mode == 'cyber') else "llama-3.3-70b-versatile"
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        # دمج البيانات
        full_query = f"CONTEXT FILE:\n{file_txt}\n\nUSER QUESTION: {q}" if file_txt else q
        content = [{"type": "text", "text": full_query}]
        
        if img_b64 and mode == 'cyber':
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a Senior Cyber Security Expert. Analyze images and code deeply and step-by-step."},
                {"role": "user", "content": content}
            ],
            "temperature": 0.2
        }

        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=30)
        res = r.json()
        
        if 'choices' in res:
            return jsonify({'response': res['choices'][0]['message']['content']})
        return jsonify({'response': '⚠️ خطأ من سيرفر Groq. تأكد من المفتاح الجديد.'})
        
    except Exception as e:
        return jsonify({'response': f'⚠️ عطل فني: {str(e)}'})

if __name__ == '__main__':
    app.run()

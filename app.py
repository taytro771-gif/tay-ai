from flask import Flask, send_file, request, jsonify
import requests
import os
import base64

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def verify_key(key):
    if not key: return False
    k = str(key).strip().upper()
    # أي كود يبدأ بـ TAY ويحتوي على 771 سيعمل فوراً
    return k.startswith("TAY") and "771" in k

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
        image_b64 = data.get('image', None)
        file_text = data.get('file_content', '')

        # التحقق من وضع الخبير
        if level == 'cyber':
            if not verify_key(user_key):
                return jsonify({'response': '❌ عذراً، كود الوصول غير صحيح. للتفعيل تواصل مع @torto77'})
            
            # إعدادات الخبير السيبراني
            model = "llama-3.2-11b-vision-preview"
            system_prompt = "You are an elite Cyber Security Expert. Analyze the provided image or code for vulnerabilities, malware, and logic flaws. Be technical and precise."
        else:
            model = "llama-3.3-70b-versatile"
            system_prompt = "You are a helpful student assistant."

        # دمج محتوى الملف النصي مع السؤال
        final_query = f"CONTEXT FILE:\n{file_text}\n\nUSER QUESTION: {query}" if file_text else query

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        content = [{"type": "text", "text": final_query}]
        if image_b64 and level == 'cyber':
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}})

        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}],
            "temperature": 0.1 # دقة عالية جداً
        }

        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=40)
        res = r.json()

        if 'choices' in res:
            return jsonify({'response': res['choices'][0]['message']['content'], 'status': 'SUCCESS'})
        
        return jsonify({'response': '⚠️ السيرفر لم يستجب بشكل صحيح، جرب إرسال نص أصغر.'})

    except Exception as e:
        return jsonify({'response': f'⚠️ خطأ في الاتصال: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)

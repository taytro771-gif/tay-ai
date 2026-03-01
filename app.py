from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def check_key_smart(key):
    # خوارزمية ذكية: يجب أن يبدأ بـ TAY ويحتوي على الكود السري 771
    if key and key.startswith("TAY-") and "771" in key:
        return True
    return False

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
            if not check_key_smart(user_key):
                return jsonify({'response': '❌ مفتاح غير صالح! استخدم مفتاحاً يحتوي على كود التفعيل الخاص بك.'})
            model_name = "llama-3.2-11b-vision-preview"
        else:
            model_name = "llama-3.3-70b-versatile"

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        content = [{"type": "text", "text": query}]
        if image_data and level == 'cyber':
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

        payload = {
            "model": model_name,
            "messages": [{"role": "system", "content": "Expert Mode Active."}, {"role": "user", "content": content}]
        }

        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        res = r.json()

        if 'choices' in res:
            return jsonify({'response': res['choices'][0]['message']['content'], 'status': 'SUCCESS'})
        
        # محاولة أخيرة بالموديل النصي إذا فشل موديل الرؤية
        payload["model"] = "llama-3.3-70b-versatile"
        payload["messages"][1]["content"] = query
        r2 = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        return jsonify({'response': r2.json()['choices'][0]['message']['content'], 'status': 'SUCCESS'})

    except Exception as e:
        return jsonify({'response': f'⚠️ خطأ: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)

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
        data = request.json
        user_key = data.get('key', '')
        query = data.get('q', '')
        level = data.get('level', 'student')
        image_data = data.get('image', None)
        file_text = data.get('file_content', '')

        # نظام تفعيل ذكي وغير معقد (ابحث عن 771 فقط)
        if level == 'cyber' and "771" not in str(user_key):
            return jsonify({'response': '❌ كود الوصول غير صالح.'})

        # اختيار الموديل (الخبير للصور والملفات، والطالب للنصوص)
        model_name = "llama-3.2-11b-vision-preview" if (image_data or level == 'cyber') else "llama-3.3-70b-versatile"
        
        system_msg = "You are a Cyber Security Expert. Analyze images and code deeply." if level == 'cyber' else "You are a helpful student assistant."

        # بناء الطلب
        full_query = f"FILE DATA:\n{file_text}\n\nQUESTION: {query}" if file_text else query
        content = [{"type": "text", "text": full_query}]
        
        if image_data and level == 'cyber':
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": model_name,
            "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": content}],
            "temperature": 0.2
        }

        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=40)
        res = r.json()

        if 'choices' in res:
            return jsonify({'response': res['choices'][0]['message']['content'], 'status': 'SUCCESS'})
        return jsonify({'response': '⚠️ السيرفر لم يعطِ ردّاً، حاول مجدداً.'})

    except Exception as e:
        return jsonify({'response': f'⚠️ عطل: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)

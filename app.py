from flask import Flask, send_file, request, jsonify
import requests
import os

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def check_key_smart(key):
    # خوارزمية تاي السرية
    return key and key.startswith("TAY-") and "771" in key

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
        file_content = data.get('file_content', None)

        if level == 'cyber':
            if not check_key_smart(user_key):
                return jsonify({'response': '❌ الكود غير صحيح. للتواصل إتصل ب @torto77 في التليجرام.'})
            
            # موديل الخبير السيبراني
            model_name = "llama-3.2-11b-vision-preview"
            system_msg = """You are a Senior Cyber Security Expert. 
            Your task is to analyze code, files, and images for vulnerabilities, malware, or bugs. 
            Provide step-by-step explanations, write secure code, and act as a professional mentor. 
            Always prioritize technical accuracy and deep analysis."""
        else:
            model_name = "llama-3.3-70b-versatile"
            system_msg = "You are a helpful educational assistant for students."

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        # دمج النص مع محتوى الملف المرفوع
        full_query = query
        if file_content:
            full_query = f"FILE CONTENT TO ANALYZE:\n{file_content}\n\nUSER QUESTION: {query}"

        content = [{"type": "text", "text": full_query}]
        if image_data and level == 'cyber':
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

        payload = {
            "model": model_name,
            "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": content}],
            "temperature": 0.2 # تقليل الحرارة لزيادة الدقة التقنية
        }

        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        res = r.json()

        if 'choices' in res:
            return jsonify({'response': res['choices'][0]['message']['content'], 'status': 'SUCCESS'})
        
        return jsonify({'response': '⚠️ حدث خطأ في معالجة البيانات، حاول مرة أخرى.'})

    except Exception as e:
        return jsonify({'response': f'⚠️ عطل فني: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)

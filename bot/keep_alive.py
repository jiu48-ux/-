import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is Online!"

def run():
    # Render가 부여하는 포트를 자동으로 감지하거나 8080 사용
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True  # 메인 프로세스가 꺼지면 같이 종료되도록 설정
    t.start()
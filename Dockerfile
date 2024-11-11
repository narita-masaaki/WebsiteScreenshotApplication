# ベースイメージの指定
FROM python:3.10-slim

# 必要なツールをインストール
RUN apt-get update && \
    apt-get install -y wget gnupg unzip fonts-ipafont-gothic && \
    # Google Chrome の最新バージョンをダウンロードしてインストール
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    # ChromeDriver のバージョンを指定してインストール（Chromeの最新バージョンに対応するバージョンを指定）
    wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/130.0.6723.116/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    # 不要なファイルの削除
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY app.py .

# アプリケーションを起動
CMD ["python", "app.py", "--port=8080"]
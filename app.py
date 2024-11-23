from flask import Flask, request, render_template_string, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import base64

app = Flask(__name__)

# 認証情報
VALID_ID = "XXXXXXX"
VALID_PHRASE = "XXXXXXX"

# HTMLテンプレート
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Screenshot App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f9f9f9;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        form {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 20px;
        }
        input, select {
            padding: 10px;
            font-size: 16px;
            width: 80%;
            max-width: 400px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            color: white;
            background-color: #007BFF;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:disabled {
            background-color: #cccccc;
        }
        #result {
            text-align: center;
            margin-top: 20px;
        }
        img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.2);
        }
        .timer {
            margin-top: 10px;
            color: #555;
            font-size: 14px;
        }
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }
        .loading span {
            font-size: 16px;
            margin-left: 10px;
            color: #555;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007BFF;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            from {
                transform: rotate(0deg);
            }
            to {
                transform: rotate(360deg);
            }
        }
        .error {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Website Screenshot</h1>
    <form id="screenshot-form" method="post">
        <label for="id">ID:</label>
        <input type="text" id="id" name="id" placeholder="Enter your ID" required>
        
        <label for="phrase">Phrase:</label>
        <input type="password" id="phrase" name="phrase" placeholder="Enter your Phrase" required>
        
        <label for="url">URL to screenshot:</label>
        <input type="text" id="url" name="url" placeholder="https://example.com" required>
        
        <label for="window-size">Select Window Size:</label>
        <select id="window-size" name="window-size" required>
            <option value="1920,1080">1920x1080</option>
            <option value="1366,768">1366x768</option>
            <option value="1280,720">1280x720</option>
            <option value="1024,768" selected>1024x768</option>
            <option value="800,600">800x600</option>
        </select>
        
        <button type="button" id="submit-button">Take Screenshot</button>
    </form>
    <div id="result">
        <!-- スクリーンショット画像や処理時間がここに表示されます -->
    </div>
    <div id="loading" class="loading" style="display: none;">
        <div class="spinner"></div>
        <span>Processing...</span>
    </div>
    <script>
        document.getElementById('submit-button').addEventListener('click', async () => {
            const idInput = document.getElementById('id');
            const phraseInput = document.getElementById('phrase');
            const urlInput = document.getElementById('url');
            const windowSizeSelect = document.getElementById('window-size');
            const resultDiv = document.getElementById('result');
            const submitButton = document.getElementById('submit-button');
            const loadingDiv = document.getElementById('loading');
            const startTime = performance.now();

            // 前回の結果をクリア
            resultDiv.innerHTML = '';
            loadingDiv.style.display = 'flex'; // ローディングアイコンを表示
            submitButton.disabled = true;

            // 認証情報とURLを取得
            const id = idInput.value;
            const phrase = phraseInput.value;
            const url = urlInput.value;
            const windowSize = windowSizeSelect.value;

            if (!id || !phrase || !url) {
                resultDiv.innerHTML = '<p class="error">All fields are required.</p>';
                loadingDiv.style.display = 'none'; // ローディングアイコンを非表示
                submitButton.disabled = false;
                return;
            }

            try {
                // サーバーにリクエストを送信
                const response = await fetch("/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ id, phrase, url, window_size: windowSize })
                });

                const data = await response.json();
                if (data.error) {
                    resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
                } else if (data.image) {
                    const endTime = performance.now();
                    const seconds = ((endTime - startTime) / 1000).toFixed(2);

                    resultDiv.innerHTML = `
                        <h2>Screenshot of ${data.url}</h2>
                        <img src="data:image/png;base64,${data.image}" alt="Screenshot">
                        <p class="timer">Image loaded in ${seconds} seconds.</p>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p class="error">An unexpected error occurred.</p>`;
            } finally {
                loadingDiv.style.display = 'none'; // ローディングアイコンを非表示
                submitButton.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        data = request.get_json()
        id = data.get("id")
        phrase = data.get("phrase")
        url = data.get("url")
        window_size = data.get("window_size", "1024,768")

        # 認証チェック
        if id != VALID_ID or phrase != VALID_PHRASE:
            return jsonify({"error": "Authentication failed. Please check your ID and Phrase."}), 401

        if not url:
            return jsonify({"error": "URL is required"}), 400

        # スクリーンショット処理
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--window-size={window_size}")

        with webdriver.Chrome(options=chrome_options) as driver:
            driver.get(url)
            time.sleep(2)
            screenshot = driver.get_screenshot_as_png()

        image_base64 = base64.b64encode(screenshot).decode("utf-8")
        return jsonify({"url": url, "image": image_base64})

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

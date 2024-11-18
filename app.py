from flask import Flask, request, send_file, render_template_string, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

app = Flask(__name__)

# HTMLテンプレート
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Screenshot App</title>
</head>
<body>
    <h1>Website Screenshot</h1>
    <form action="/" method="post">
        <label for="url">URL to screenshot:</label>
        <input type="text" id="url" name="url" placeholder="https://example.com" required>
        <button type="submit">Take Screenshot</button>
    </form>
    {% if screenshot_url %}
        <h2>Screenshot of {{ url }}</h2>
        <img src="{{ screenshot_url }}" alt="Screenshot" style="max-width: 100%; height: auto;">
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return "URL is required", 400

        # Chromeのオプション設定
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  #ウィンドウサイズを固定

        # ChromeのWebDriverを起動
        screenshot_path = "screenshot.png"
        with webdriver.Chrome(options=chrome_options) as driver:
            driver.get(url)
            time.sleep(2)  # ページのロード待ち
            driver.save_screenshot(screenshot_path)

        # スクリーンショットを表示するため、ページをリロードして画像を表示
        return render_template_string(HTML_TEMPLATE, url=url, screenshot_url=url_for("screenshot_image"))

    return render_template_string(HTML_TEMPLATE)

@app.route("/screenshot_image")
def screenshot_image():
    screenshot_path = "screenshot.png"
    if os.path.exists(screenshot_path):
        return send_file(screenshot_path, mimetype="image/png")
    else:
        return "Screenshot not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

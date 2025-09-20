from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/download")
def download_file():
    file_link = request.args.get("link")
    if not file_link:
        return jsonify({"error": "No link provided"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            
            page.goto("https://terabox.hnn.workers.dev")
            page.fill("input[type='text']", file_link)
            page.click("button:has-text('GET LINK')")
            page.wait_for_selector("a:has-text('DOWNLOAD')")

            with page.expect_download() as download_info:
                page.click("a:has-text('DOWNLOAD')")
            download = download_info.value
            save_path = os.path.join(DOWNLOAD_FOLDER, download.suggested_filename)
            download.save_as(save_path)
            
            browser.close()

        return jsonify({
            "status": "success",
            "file_name": download.suggested_filename,
            "file_path": save_path
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

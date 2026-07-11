"""excel-kanri app デモ録画: login → 新規作成モーダル → 生成 → 自動プレビュー → 検索

再生成手順（リポルートで実行。docker compose up -d --build で app が :8000 に起動していること）:
  nix-shell -p python3Packages.playwright playwright-driver.browsers --run \
    'export PLAYWRIGHT_BROWSERS_PATH=$(nix-build "<nixpkgs>" -A playwright-driver.browsers --no-out-link); \
     python3 docs/record-app-demo.py'
  ffmpeg -i docs/video/*.webm -vf "fps=10,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" -loop 0 docs/app-demo.gif
"""
import time
from playwright.sync_api import sync_playwright

OUT_DIR = "docs/video"  # 実行後: ffmpeg で GIF 化（下記コメント参照）

def slow_type(page, selector, text):
    page.click(selector)
    page.type(selector, text, delay=45)

with sync_playwright() as p:
    # PDF ビューア描画のためヘッド付き必須（headless では preview が白紙になる）
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        record_video_dir=OUT_DIR,
        record_video_size={"width": 1280, "height": 800},
    )
    page = ctx.new_page()
    page.goto("http://localhost:8000")
    page.wait_for_selector("text=ログイン")
    time.sleep(1.2)

    # editor タブでログイン（デモ認証情報が自動入力される）
    page.click("button:has-text('編集者')")
    time.sleep(1.0)
    page.click("button[type=submit]:has-text('ログイン')")
    page.wait_for_selector("text=としてログイン中")
    time.sleep(1.8)

    # 新規作成モーダル
    page.click("button:has-text('新規作成')")
    page.wait_for_selector("text=書類生成")
    time.sleep(1.0)

    labels = {
        "applicant_name": "山田 太郎",
        "room_number": "302",
        "move_in_date": "2026-08-01",
        "phone": "090-1234-5678",
        "emergency_contact": "山田 花子 080-9876-5432",
    }
    modal = page.locator("div.fixed.inset-0")
    inputs = modal.locator("input[type=text]")
    for i, (_, value) in enumerate(labels.items()):
        inputs.nth(i).click()
        inputs.nth(i).type(value, delay=40)
    time.sleep(0.8)

    modal.locator("button[type=submit]:has-text('生成')").click()
    # モーダルが閉じるまで待つ（成功時に閉じて自動プレビューされる）
    page.wait_for_selector("div.fixed.inset-0", state="detached", timeout=30000)
    time.sleep(3.5)

    # 検索 → 結果クリック
    search = page.locator("input[placeholder*='検索']")
    search.click()
    search.type("302", delay=60)
    page.click("button:has-text('検索')")
    time.sleep(1.5)
    page.locator("li button").first.click()
    time.sleep(3.0)

    ctx.close()
    browser.close()
print("done")

"""產生「Notebook 與 GitHub 上手」中文教學影片。

每一句旁白 = 一張 1920x1080 投影片（HTML 截圖，字幕燒在畫面下方）+ 一段 edge-tts 語音，
最後用 ffmpeg 串成 MP4，並輸出 WebVTT 字幕與封面圖到 ../docs/video/。
畫面中的 GitHub、Colab、JupyterLab 截圖來自 video/screens/（由 capture_screens.py 擷取）。

用法：python3 video/build_notebook_github_video.py
需要：ffmpeg、Noto Sans/Serif CJK TC 字型、playwright（含 Chromium）、edge-tts；合成語音需連網。
修改旁白或畫面：編輯下方 SCENES；只有改過的句子會重新合成語音（以文字內容快取）。
"""
import asyncio
import hashlib
import os
import subprocess
from pathlib import Path

import certifi

# edge-tts 透過 aiohttp 連線且只讀 certifi 的憑證；在需要自訂 CA 的代理環境中改用 SSL_CERT_FILE。
if os.environ.get("SSL_CERT_FILE"):
    certifi.where = lambda: os.environ["SSL_CERT_FILE"]
import edge_tts  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

HERE = Path(__file__).resolve().parent
SCREENS = HERE / "screens"
BUILD = HERE / "build" / "notebook_github"
OUT = HERE.parent / "docs" / "video"
VIDEO = OUT / "notebook_github_tutorial.mp4"
VTT = OUT / "notebook_github_tutorial.vtt"
POSTER = OUT / "notebook_github_tutorial_poster.jpg"

VOICE, RATE = "zh-TW-HsiaoChenNeural", "-4%"
LINE_TAIL = 0.3    # 每句之後的停頓（秒）
SCENE_TAIL = 0.9   # 每段最後一句之後再多停的秒數


def shot(name, notes=(), crop=None):
    """單張截圖。crop 是 CSS inset（上 右 下 左，%），只顯示截圖中的重點區域；
    notes 是 (左%, 上%, 文字) 標註，位置以裁切後可見範圍的百分比表示。"""
    view = f' style="object-view-box:inset({crop})"' if crop else ""
    tags = "".join(f'<span class="note-tag" style="left:{x}%;top:{y}%">{t}</span>' for x, y, t in notes)
    return f'<div class="shot"><img src="{(SCREENS / name).as_uri()}"{view}>{tags}</div>'


def split(code, fig):
    """左邊程式（裁掉右側空白）、右邊輸出的地圖。"""
    return (f'<div class="split"><img class="code" src="{(SCREENS / code).as_uri()}" '
            f'style="object-view-box:inset(0 45% 0 0)"><img class="map" src="{(SCREENS / fig).as_uri()}"></div>')


COVER = """
<div class="cover">
  <p class="kick">PyGMT 地圖實作教室 · 操作教學</p>
  <h1>Notebook 與 GitHub<br>上手指南</h1>
  <p class="lede">用 Jupyter Notebook 一格一格畫地圖，再用 GitHub 繳交作品</p>
</div>"""

FLOW = """
<div class="flow">
  <div class="station"><b>GitHub</b><span>課程教材<br>README、Notebook、範例程式</span></div>
  <div class="arrow">→</div>
  <div class="station hot"><b>Colab</b><span>執行 Notebook<br>一格一格畫出地圖</span></div>
  <div class="arrow">→</div>
  <div class="station"><b>GitHub</b><span>繳交作品<br>程式、圖、圖說、AI 紀錄</span></div>
</div>
<p class="motto">Notebook（.ipynb）＝ 說明文字 ＋ 程式 ＋ 執行結果，放在同一頁</p>"""

HOMEWORK = """
<div class="trio">
  <div class="card"><h4>1. 與 PyGMT 有關</h4><p>一段板塊交界帶的地圖與 A–B 剖面，可以從 examples/ 的範例改參數。</p></div>
  <div class="card"><h4>2. 上傳 GitHub</h4><p>繳交 repository 連結，並確認教師打得開。</p></div>
  <div class="card"><h4>3. 附 AI 對話紀錄</h4><p>分享連結、匯出文字檔或截圖都可以，放進同一個 repository。</p></div>
</div>
<p class="motto">作品＝圖＋圖說：看到什麼、證據是什麼、哪裡不確定，加上資料來源</p>"""

NEW_REPO = """
<div class="steps">
  <div class="step"><i>1</i><h4>註冊與登入</h4><p>到 github.com 免費註冊帳號，登入。</p></div>
  <div class="step"><i>2</i><h4>建立 repository</h4><p>右上角 <span class="chip">＋</span> → <span class="chip">New repository</span></p></div>
  <div class="step"><i>3</i><h4>填寫設定</h4><p>英文名稱，例如 <code>plate-boundary-map</code>；選 <span class="chip">Public</span>；開啟加入 README。</p></div>
  <div class="step"><i>4</i><h4>建立</h4><p>按 <span class="chip green">Create repository</span></p></div>
</div>
<p class="note">需要登入的畫面以示意呈現；按鈕名稱與 GitHub 相同。</p>"""

UPLOAD = """
<div class="steps">
  <div class="step"><i>1</i><h4>從 Colab 下載</h4><p>檔案 → 下載 → <span class="chip">下載 .ipynb</span></p></div>
  <div class="step"><i>2</i><h4>上傳檔案</h4><p><span class="chip">Add file</span> → <span class="chip">Upload files</span></p></div>
  <div class="step"><i>3</i><h4>拖進檔案</h4><p>Notebook、地圖圖片、README 圖說、AI 對話紀錄</p></div>
  <div class="step"><i>4</i><h4>存檔</h4><p>寫一句說明，按 <span class="chip green">Commit changes</span></p></div>
</div>
<p class="motto">每一次 commit 都是一個存檔點</p>"""

SUBMIT = """
<div class="duo">
  <div class="card"><h4>複製連結</h4><p>進入自己的 repository，複製網址列的連結繳交：</p>
    <p><code>github.com/帳號/plate-boundary-map</code></p></div>
  <div class="card"><h4>用無痕視窗檢查</h4><p>沒登入也打得開，老師才看得到。</p><p>設成 Private 的 repository，老師會看不到。</p></div>
</div>"""

RECAP = """
<ol class="checklist">
  <li>從 GitHub 課程首頁開啟 Colab，登入後先存一份副本</li>
  <li>「準備環境」兩格分開執行，等重新連線再按第二格</li>
  <li>Shift＋Enter 由上往下執行；一次改一步、看一次結果</li>
  <li>看到錯誤先讀最後一行；卡住就重新啟動並全部執行</li>
  <li>Notebook、地圖、圖說、AI 紀錄上傳 GitHub，繳交連結</li>
</ol>"""

SCENES = [
    dict(kicker="", title="", body=COVER, cover=True, lines=[
        "這支影片帶你走一遍 PyGMT 地圖實作課的操作流程。",
        "先在 Jupyter Notebook 上一格一格執行程式、畫出地圖，最後把作品放上 GitHub 繳交。",
    ]),
    dict(kicker="整體流程", title="三站：GitHub → Colab → GitHub", body=FLOW, lines=[
        "整個流程只有三站：GitHub 放課程教材，Colab 執行 Notebook，最後再回到 GitHub 繳交作品。",
        "Notebook 是把說明文字、程式和執行結果放在同一頁的檔案，副檔名是 ipynb。",
        "Colab 是 Google 提供的線上 Notebook 環境，只要瀏覽器和 Google 帳號，不用在自己的電腦安裝任何東西。",
    ]),
    dict(kicker="一、從 GitHub 開始", title="課程教材放在 GitHub", body=shot("github_repo.png"), lines=[
        "課程教材放在 GitHub 上的 pygmt-map-lab。GitHub 上的一個專案，叫做一個 repository。",
        "上方是檔案清單，兩個 ipynb 檔就是課堂用的 Notebook；往下捲，就是課程首頁的說明。",
    ]),
    dict(kicker="一、從 GitHub 開始", title="從「開始上課」打開 Notebook", body=shot("github_start.png", crop="50% 27% 0 7%"), lines=[
        "在「開始上課」這一段，前兩份是 Colab Notebook，點連結就會直接在 Colab 開啟。",
        "第三份是說明文件加上範例程式，範例程式放在 examples 資料夾。",
    ]),
    dict(kicker="二、在 Colab 開啟", title="先登入，再存一份自己的副本", body=shot("colab_open.png", crop="0 0 45% 0"), lines=[
        "開啟後，先按右上角，登入 Google 帳號。",
        "這時看到的是 GitHub 上的原始檔，修改不會被保存。請按工具列的「複製到雲端硬碟」，之後都在自己的副本上練習。",
    ]),
    dict(kicker="二、在 Colab 開啟", title="副本與下載都在「檔案」選單", body=shot("colab_file_menu.png", crop="0 45% 15% 0"), lines=[
        "同樣的功能也在「檔案」選單裡：在雲端硬碟中儲存複本。",
        "做完之後，從「下載」選「下載 .ipynb」，就能把 Notebook 存到電腦，等一下要上傳到 GitHub。",
    ]),
    dict(kicker="二、在 Colab 開啟", title="第一步：準備環境（兩格分開執行）", body=shot("colab_env.png", crop="0 15% 35% 0"), lines=[
        "Notebook 最上面是「準備環境」，有兩格程式，負責安裝 PyGMT。",
        "請分開執行：第一格安裝 Conda 之後，Colab 會自動重新啟動；等重新連線，再執行第二格。",
        "安裝要幾分鐘，期間不要重複按執行。每次開新的執行環境，都要重新安裝一次。",
    ]),
    dict(kicker="三、Notebook 的基本操作", title="儲存格：文字與程式", body=shot("jl_cells.png", [
        (69, 38.5, "← 文字儲存格：說明"), (45, 62, "程式儲存格：可以執行的 Python"), (24, 44.5, "← 左邊的 [ ]：還沒執行")],
        crop="4% 25% 42% 0"), lines=[
        "接下來用本機的 JupyterLab，實際執行同一份 Notebook。介面長得不太一樣，但操作和 Colab 相同。",
        "Notebook 由一格一格的儲存格組成：文字儲存格放說明，程式儲存格放可以執行的 Python。",
        "程式左邊的方括號是執行順序；還沒執行過，括號就是空的。",
    ]),
    dict(kicker="三、Notebook 的基本操作", title="Shift＋Enter：執行並跳到下一格", body=shot("jl_env.png", [(20, 12, "← [1]：第 1 個執行"), (23, 88.5, "← 執行結果")]), lines=[
        "點一下程式儲存格，按 Shift 加 Enter，就會執行這一格，並跳到下一格。在 Colab，也可以按儲存格左邊的播放鍵。",
        "這台電腦已經裝好 PyGMT，所以準備環境這格印出「環境已可用，跳過安裝」，方括號也變成了 1。",
    ]),
    dict(kicker="三、Notebook 的基本操作", title="第一張圖：只有外框", body=split("jl_step0_in.png", "jl_step0_out.png"), lines=[
        "第一張地圖只有一個外框。region 是繪圖範圍，順序是西、東、南、北；M15c 代表麥卡托投影、寬 15 公分。",
        "下面的步驟一到六，都先用井字號註解起來。我們一次打開一步，再重新執行整格，看看改了什麼。",
    ]),
    dict(kicker="三、Notebook 的基本操作", title="取消註解：一次打開一步", body=split("jl_step3_in.png", "jl_step3_out.png"), lines=[
        "選取程式行，按 Ctrl 加斜線，就能取消或加上註解；Mac 用 Command 加斜線。",
        "打開步驟一到三：加上經緯度刻度、陸地和海洋的顏色，還有海岸線。",
    ]),
    dict(kicker="三、Notebook 的基本操作", title="全部打開：格線、標題、比例尺", body=split("jl_step6_in.png", "jl_step6_out.png"), lines=[
        "步驟全部打開，就有了格線、標題和比例尺。",
        "每次重新執行，fig 等於 pygmt.Figure 都會從一張新圖開始，不會疊上一次的結果。",
        "同一張圖裡，後畫的會蓋住先畫的，所以先填顏色，再加線條和文字。",
    ]),
    dict(kicker="四、看懂錯誤訊息", title="NameError：名稱沒有定義", body=shot("jl_error.png", [
        (40, 82, "← 最後一行：endtime 沒有定義")], crop="30% 8% 0 0"), lines=[
        "如果跳過中間的儲存格，常會看到這樣的紅色錯誤：NameError，endtime 沒有定義。",
        "endtime 是在「下載地震資料」那一格設定的；那一格還沒執行，這個變數就不存在。",
        "Notebook 記得的是你執行過的東西，不是畫面上看到的程式。所以請由上往下，依序執行。",
    ]),
    dict(kicker="四、看懂錯誤訊息", title="卡住時：從頭再執行一次", body=shot("colab_runtime_menu.png", crop="3% 52% 22% 12%"), lines=[
        "遇到奇怪的錯誤，可以從「執行階段」選「重新啟動工作階段並執行所有儲存格」，讓整份 Notebook 從頭跑一遍。",
        "連上執行階段之後，這些選項才能按；「全部執行」則會依序執行每一格。",
    ]),
    dict(kicker="五、下載資料、畫出地震", title="向 USGS 要一份地震表格", body=shot("jl_usgs.png", crop="40% 0 0 0"), lines=[
        "回到正確的順序，先執行下載資料的那一格。它把時間、範圍和最低規模寫在網址裡，向 USGS 要一份 CSV 表格。",
        "執行完會印出查詢網址和筆數，並列出前五筆地震的時間、經緯度、規模和深度。",
    ]),
    dict(kicker="五、下載資料、畫出地震", title="把表格裡的經緯度畫到地圖上", body=split("jl_quakes_in.png", "jl_quakes_out.png"), lines=[
        "再執行畫圖的那一格，每一筆地震都變成地圖上的一個點；黃色星星，標出 2024 年花蓮地震的主震。",
    ]),
    dict(kicker="五、下載資料、畫出地震", title="大小代表規模，顏色代表深度", body=shot("jl_depth_out.png"), lines=[
        "後面兩格再加上變化：圓圈大小代表規模，顏色代表深度，並附上色條。",
        "圖畫好後，可以在圖上按右鍵另存圖片，或用 fig.savefig 存成 PNG 檔。",
    ]),
    dict(kicker="六、用 GitHub 繳交作業", title="作業要交什麼？", body=HOMEWORK, lines=[
        "作業只需要滿足三個條件：作品和 PyGMT 有關；上傳 GitHub，繳交 repository 的連結；附上和 AI 的對話紀錄。",
        "作品是圖加圖說：一段板塊交界帶的地圖和剖面，加上看到什麼、證據是什麼、哪裡不確定，還有資料來源。",
    ]),
    dict(kicker="六、用 GitHub 繳交作業", title="建立自己的 repository", body=NEW_REPO, lines=[
        "還沒有 GitHub 帳號，就先到 github.com 免費註冊。",
        "登入後，按右上角的加號，選 New repository。取一個英文名稱，設成 Public，開啟加入 README，再按 Create repository。",
    ]),
    dict(kicker="六、用 GitHub 繳交作業", title="上傳檔案：Add file → Upload files", body=UPLOAD, lines=[
        "進入自己的 repository，按 Add file，選 Upload files。",
        "把下載的 ipynb、存好的地圖圖片、寫好的圖說，以及 AI 對話紀錄拖進去，在下方寫一句說明，按 Commit changes。",
        "每一次 commit 都是一個存檔點；之後改了作品，再上傳一次就好。",
    ]),
    dict(kicker="六、用 GitHub 繳交作業", title="範例：整理好的作品資料夾", body=shot("github_case.png", crop="8% 1% 0 22%"), lines=[
        "可以參考課程裡的這個案例資料夾：有畫圖的程式、輸出的地圖，還有 README 寫圖說和資料來源。",
        "GitHub 會直接顯示 README 和圖片；ipynb 也會連同執行結果一起顯示，老師打開連結就看得到。",
    ]),
    dict(kicker="六、用 GitHub 繳交作業", title="繳交前最後檢查", body=SUBMIT, lines=[
        "最後，複製瀏覽器網址列的 repository 連結繳交。",
        "繳交前，用無痕視窗打開一次，確認沒登入也看得到；設成 Private 的話，老師會看不到。",
    ]),
    dict(kicker="複習", title="五個重點", body=RECAP, lines=[
        "複習一下整個流程。",
        "從 GitHub 的課程首頁開啟 Colab，登入後先存一份副本。",
        "兩格準備環境分開執行；之後用 Shift 加 Enter，由上往下一格一格執行。",
        "一次改一步、看一次結果；看到錯誤，先讀最後一行訊息。",
        "最後把 Notebook、地圖、圖說和 AI 對話紀錄上傳 GitHub，繳交連結。祝你畫圖順利！",
    ]),
]

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1920px;height:1080px;overflow:hidden;background:#f5f0e6;color:#1f2a33;
 font-family:'Noto Sans CJK TC',sans-serif;position:relative}
body::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 85% 10%,rgba(176,74,58,.08),transparent 40%),radial-gradient(circle at 10% 90%,rgba(44,110,145,.08),transparent 45%)}
.frame{position:absolute;inset:0;padding:40px 90px 0}
.kicker{font-size:26px;letter-spacing:.12em;color:#b04a3a;font-weight:700}
h2{font-family:'Noto Serif CJK TC',serif;font-size:52px;margin-top:6px;color:#1f2a33}
.stage{position:absolute;left:90px;right:90px;top:170px;bottom:178px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px}
.shot{position:relative;display:flex}
.shot img{width:auto;height:auto;max-width:1740px;max-height:732px;border-radius:12px;box-shadow:0 18px 40px -20px rgba(31,42,51,.55);border:1px solid #d9d2c3;background:#fff}
.note-tag{position:absolute;background:#b04a3a;color:#fff;font-size:26px;font-weight:700;padding:6px 16px;border-radius:10px;box-shadow:0 8px 18px -8px rgba(0,0,0,.5);white-space:nowrap}
.split{display:flex;gap:28px;height:100%;width:100%;align-items:center;justify-content:center}
.split img{width:auto;height:auto;max-height:732px;border-radius:12px;background:#fff;border:1px solid #d9d2c3;box-shadow:0 18px 40px -20px rgba(31,42,51,.55)}
.split .code{max-width:1120px}.split .map{max-width:590px}
.sub{position:absolute;left:0;right:0;bottom:0;height:160px;background:rgba(31,42,51,.9);display:flex;align-items:center;justify-content:center;padding:0 120px}
.sub p{color:#fff;font-size:42px;line-height:1.35;text-align:center;font-weight:500}
.flow{display:flex;align-items:center;gap:30px}
.station{background:#fbf8f2;border:2px solid #e3dccd;border-radius:24px;padding:44px 50px;width:420px;text-align:center}
.station b{display:block;font-size:64px;color:#2c6e91}.station.hot b{color:#b04a3a}
.station span{display:block;font-size:32px;line-height:1.5;margin-top:14px;color:#3b4852}
.arrow{font-size:80px;color:#8a5a44}
.motto{font-family:'Noto Serif CJK TC',serif;font-size:42px;font-weight:700;color:#1f2a33;text-align:center}
.note{font-size:26px;color:#6b7680}
.trio{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;width:100%}
.duo{display:grid;grid-template-columns:1fr 1fr;gap:34px;width:100%}
.card{background:#fbf8f2;border:2px solid #e3dccd;border-radius:22px;padding:40px 44px}
.card h4{font-size:42px;margin-bottom:16px}
.card p{font-size:32px;line-height:1.55;color:#3b4852;margin-top:10px}
code{font-family:'DejaVu Sans Mono',monospace;background:#ece5d6;padding:2px 10px;border-radius:8px;font-size:.88em}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;width:100%}
.step{background:#fbf8f2;border:2px solid #e3dccd;border-radius:22px;padding:34px 32px;min-height:380px}
.step i{display:inline-flex;width:64px;height:64px;border-radius:50%;background:#1f2a33;color:#fff;font-style:normal;font-size:36px;font-weight:700;align-items:center;justify-content:center}
.step h4{font-size:38px;margin:20px 0 14px}
.step p{font-size:30px;line-height:1.7;color:#3b4852}
.chip{display:inline-block;background:#f6f8fa;border:2px solid #d0d7de;border-radius:10px;padding:0 14px;font-family:'DejaVu Sans',sans-serif;font-size:27px;color:#1f2328;line-height:1.6}
.chip.green{background:#1f883d;border-color:#1a7f37;color:#fff}
.checklist{font-size:44px;line-height:1.5;padding-left:70px;align-self:stretch;font-family:'Noto Serif CJK TC',serif}
.checklist li{margin:12px 0}
.cover{position:absolute;inset:0;background:linear-gradient(135deg,#1c2530,#22303a 60%,#2c4a5a);padding:0 140px;display:flex;flex-direction:column;justify-content:center}
.cover .kick{color:#e59a6d;font-size:34px;letter-spacing:.15em;font-weight:700}
.cover h1{font-family:'Noto Serif CJK TC',serif;color:#f5f0e6;font-size:124px;line-height:1.2;margin:30px 0}
.cover .lede{color:#d6d0c4;font-size:44px}
.progress{position:absolute;top:0;left:0;height:8px;background:#b04a3a}
"""


def slide_html(scene, line, progress):
    if scene.get("cover"):
        inner = scene["body"]
    else:
        inner = (f'<div class="frame"><p class="kicker">{scene["kicker"]}</p><h2>{scene["title"]}</h2></div>'
                 f'<div class="stage">{scene["body"]}</div>')
    subtitle = f'<div class="sub"><p>{line}</p></div>' if line else ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'{inner}<div class="progress" style="width:{progress * 100:.1f}%"></div>{subtitle}</body></html>')


def audio_path(line):
    key = hashlib.sha1(f"{VOICE}|{RATE}|{line}".encode()).hexdigest()[:16]
    return BUILD / "audio" / f"{key}.mp3"


async def synthesize(lines):
    for line in lines:
        mp3 = audio_path(line)
        if not mp3.exists() or mp3.stat().st_size == 0:
            await edge_tts.Communicate(line, VOICE, rate=RATE).save(str(mp3))


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def vtt_time(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:06.3f}"


def screenshot(page, html, out, **kw):
    path = BUILD / "slides" / (out.stem + ".html")
    path.write_text(html, encoding="utf-8")
    page.goto(path.as_uri())
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(200)
    page.screenshot(path=str(out), **kw)


def main():
    for d in ("audio", "slides", "segments"):
        (BUILD / d).mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    items = [(si, li, line) for si, sc in enumerate(SCENES) for li, line in enumerate(sc["lines"])]
    asyncio.run(synthesize([line for _, _, line in items]))

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        for n, (si, li, line) in enumerate(items):
            screenshot(page, slide_html(SCENES[si], line, (n + 1) / len(items)),
                       BUILD / "slides" / f"{si:02d}_{li:02d}.png")
        screenshot(page, slide_html(SCENES[0], "", 0), POSTER, type="jpeg", quality=85)
        browser.close()

    segments, cues, t = [], ["WEBVTT", ""], 0.0
    for si, li, line in items:
        mp3, png = audio_path(line), BUILD / "slides" / f"{si:02d}_{li:02d}.png"
        seg = BUILD / "segments" / f"{si:02d}_{li:02d}.mp4"
        speech = duration(mp3)
        d = speech + LINE_TAIL + (SCENE_TAIL if li == len(SCENES[si]["lines"]) - 1 else 0)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", str(png),
                        "-i", str(mp3), "-af", "apad", "-t", f"{d:.3f}", "-c:v", "libx264", "-tune", "stillimage",
                        "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                        "-ac", "2", str(seg)], check=True)
        segments.append(seg)
        cues += [f"{vtt_time(t)} --> {vtt_time(t + speech)}", line, ""]
        t += d

    listing = BUILD / "concat.txt"
    listing.write_text("".join(f"file '{s}'\n" for s in segments))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", "-movflags", "+faststart", str(VIDEO)], check=True)
    VTT.write_text("\n".join(cues), encoding="utf-8")
    print(f"{len(items)} 句、{t:.1f} 秒 → {VIDEO.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()

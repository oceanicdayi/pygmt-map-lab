# 教學影片：Notebook 與 GitHub 上手指南

成品在 [`docs/video/notebook_github_tutorial.mp4`](../docs/video/notebook_github_tutorial.mp4)（約 8 分鐘，1080p，中文語音合成旁白、字幕燒在畫面上；另附 `.vtt` 字幕與封面圖）。

內容依序是：整體流程（GitHub → Colab → GitHub）→ 從課程首頁開啟 Notebook → 在 Colab 登入、存副本、分開執行兩格「準備環境」→ 儲存格與 Shift+Enter → Notebook 01 逐步取消註解畫出台灣 → 看懂 NameError、重新啟動並全部執行 → 下載 USGS 地震並畫圖 → 作業要求 → 建立 repository、上傳檔案、繳交前檢查 → 複習。

## 兩支腳本

| 腳本 | 做什麼 |
|---|---|
| `capture_screens.py` | 擷取真實畫面到 `screens/`：未登入的 GitHub、Colab 公開頁面（繁中介面，用紅框標出重點），以及在暫存資料夾複製一份 `01_maps_earthquakes.ipynb`、用 JupyterLab 實際執行後的截圖 |
| `build_notebook_github_video.py` | 把 `screens/` 的截圖排進投影片、合成旁白、串成影片，輸出到 `docs/video/` |

`screens/` 已進版控，只改旁白或版面時不必重新擷取。需要登入的 GitHub 畫面（建立 repository、上傳檔案）以示意卡片呈現，按鈕名稱與 GitHub 相同。

## 需要

- Python 套件：`pip install edge-tts playwright jupyterlab`，再 `playwright install chromium`
- `ffmpeg`（含 `ffprobe`）
- 字型：Noto Sans CJK TC、Noto Serif CJK TC（Ubuntu：`apt install fonts-noto-cjk`）
- 網路：語音由 edge-tts 呼叫微軟語音服務（聲音 `zh-TW-HsiaoChenNeural`）；擷取畫面需連 GitHub、Colab、USGS 與 GMT 遠端資料

## 執行

在 repo 根目錄：

```bash
python3 video/capture_screens.py            # 全部重新擷取；也可只跑 github、colab 或 jupyter
python3 video/build_notebook_github_video.py
```

中間檔放在 `video/build/`（不進版控）。語音依句子內容快取，改一句旁白只會重新合成那一句。

可選的環境變數：

- `SSL_CERT_FILE`：在需要自訂 CA 的網路代理環境中，讓 edge-tts 使用這份憑證
- `CHROMIUM_PATH`：指定 Chromium 執行檔，取代 Playwright 預設下載的版本

## 修改內容

旁白與畫面都在 `build_notebook_github_video.py` 的 `SCENES`：每一段有 `kicker`（小標）、`title`（標題）、`body`（畫面）與 `lines`（逐句旁白，同時也是字幕）。`body` 可以是：

- `shot("檔名.png", notes, crop)`：一張截圖；`crop` 是 CSS inset（上 右 下 左，%），只顯示重點區域；`notes` 是 `(左%, 上%, 文字)` 的紅色標註，位置以裁切後的可見範圍計算
- `split("程式.png", "地圖.png")`：左邊程式、右邊輸出的地圖
- 一段 HTML（流程圖、步驟卡片、清單）

課程教材更新後（例如 Notebook 01 的程式或 Colab 介面改版），重跑 `capture_screens.py` 再重建影片即可。

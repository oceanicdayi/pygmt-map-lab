"""擷取教學影片用的真實畫面，存到 video/screens/。

- GitHub、Colab：以未登入狀態開啟公開頁面（繁中介面）截圖，並用外框標出要點。
- JupyterLab：在暫存資料夾複製一份 01_maps_earthquakes.ipynb，實際執行各儲存格後截圖。

用法：python3 video/capture_screens.py [github] [colab] [jupyter]（不加參數＝全部）
需要：playwright（含 Chromium）、jupyterlab；需連網（GitHub、Colab、USGS、GMT 遠端資料）。
"""
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SCREENS = HERE / "screens"
GITHUB = "https://github.com/oceanicdayi/pygmt-map-lab"
COLAB = "https://colab.research.google.com/github/oceanicdayi/pygmt-map-lab/blob/main/01_maps_earthquakes.ipynb"
MARK = "outline:4px solid #e0503a !important;outline-offset:3px;border-radius:6px"


def launch(p):
    return p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)


def mark(page, locator):
    locator.first.evaluate(f"el => el.style.cssText += ';{MARK}'")


def github(p):
    ctx = launch(p).new_context(locale="zh-TW", viewport={"width": 1440, "height": 810}, device_scale_factor=1.5)
    page = ctx.new_page()
    page.goto(GITHUB, wait_until="networkidle")
    page.screenshot(path=SCREENS / "github_repo.png")

    heading = page.locator("article.markdown-body h2", has_text="開始上課")
    heading.scroll_into_view_if_needed()
    page.evaluate("window.scrollBy(0, -90)")
    mark(page, page.locator("article.markdown-body ul", has_text="01｜基本地圖與地震"))
    page.wait_for_timeout(300)
    page.screenshot(path=SCREENS / "github_start.png")

    page.goto(f"{GITHUB}/tree/main/case-studies/2026-sunda-strait-krakatau", wait_until="networkidle")
    page.evaluate("window.scrollBy(0, 120)")
    page.wait_for_timeout(500)
    page.screenshot(path=SCREENS / "github_case.png")
    ctx.browser.close()


def colab(p):
    ctx = launch(p).new_context(locale="zh-TW", viewport={"width": 1440, "height": 810}, device_scale_factor=1.5)
    page = ctx.new_page()

    def load(reload=False):
        page.reload(wait_until="domcontentloaded") if reload else page.goto(COLAB, wait_until="domcontentloaded")
        page.wait_for_timeout(12000)
        # 移除頂端的方案公告，讓畫面只剩筆記本本身
        page.evaluate("""() => { for (const el of document.querySelectorAll('*')) {
            if (el.children.length < 6 && el.textContent.includes('Colab is now part of Google AI Plans')
                && el.getBoundingClientRect().top < 80 && el.getBoundingClientRect().height < 90) { el.remove(); return; } } }""")
        page.wait_for_timeout(800)

    load()
    mark(page, page.locator("p", has_text="Colab 請分開執行"))
    page.screenshot(path=SCREENS / "colab_env.png")
    load(reload=True)

    mark(page, page.get_by_text("複製到雲端硬碟", exact=True))
    mark(page, page.get_by_text("登入", exact=True))
    page.screenshot(path=SCREENS / "colab_open.png")
    load(reload=True)

    page.get_by_text("檔案", exact=True).first.click()
    page.wait_for_timeout(1200)
    mark(page, page.get_by_role("menuitem", name="在雲端硬碟中儲存複本"))
    page.get_by_role("menuitem", name="下載").first.hover()
    page.wait_for_timeout(1200)
    mark(page, page.get_by_role("menuitem", name="下載 .ipynb"))
    page.screenshot(path=SCREENS / "colab_file_menu.png")
    load(reload=True)

    page.get_by_text("執行階段", exact=True).first.click()
    page.wait_for_timeout(1200)
    mark(page, page.get_by_role("menuitem", name="全部執行"))
    mark(page, page.get_by_role("menuitem", name="重新啟動工作階段並執行所有儲存格"))
    page.screenshot(path=SCREENS / "colab_runtime_menu.png")
    ctx.browser.close()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def jupyter(p):
    work = Path(tempfile.mkdtemp(prefix="nbvideo_"))
    shutil.copy(REPO / "01_maps_earthquakes.ipynb", work)
    settings = Path(tempfile.mkdtemp(prefix="nbvideo_settings_"))
    (settings / "@jupyterlab" / "apputils-extension").mkdir(parents=True)
    (settings / "@jupyterlab" / "apputils-extension" / "notification.jupyterlab-settings").write_text(
        '{"fetchNews": "false", "checkForUpdates": false}')
    port = free_port()
    env = dict(os.environ, JUPYTERLAB_SETTINGS_DIR=str(settings))
    server = subprocess.Popen(
        ["jupyter", "lab", "--no-browser", f"--port={port}", "--expose-app-in-browser", "--IdentityProvider.token=",
         "--ServerApp.password=", "--ServerApp.disable_check_xsrf=True", f"--ServerApp.root_dir={work}"]
        + (["--allow-root"] if os.geteuid() == 0 else []),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    try:
        for _ in range(60):
            with socket.socket() as s:
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    break
            time.sleep(1)
        ctx = launch(p).new_context(viewport={"width": 1280, "height": 760}, device_scale_factor=1.5)
        page = ctx.new_page()
        page.goto(f"http://127.0.0.1:{port}/lab/tree/01_maps_earthquakes.ipynb", wait_until="networkidle")
        page.wait_for_selector(".jp-Notebook .jp-Cell", timeout=60000)
        page.wait_for_timeout(3000)
        page.evaluate("""() => { const app = window.jupyterapp;
            if (!app.shell.leftCollapsed) app.commands.execute('application:toggle-left-area'); }""")
        page.wait_for_function("window.jupyterapp.shell.currentWidget.sessionContext.session?.kernel?.status === 'idle'",
                               timeout=60000)

        def cell(i):
            return page.locator(".jp-Notebook .jp-Cell").nth(i)

        def run(i, source=None, wait=120000):
            page.evaluate(
                """([i, src]) => { const nb = window.jupyterapp.shell.currentWidget.content;
                   if (src !== null) nb.widgets[i].model.sharedModel.setSource(src);
                   nb.activeCellIndex = i; nb.deselectAll();
                   return window.jupyterapp.commands.execute('notebook:run-cell'); }""", [i, source])
            page.wait_for_function(
                """i => { const c = window.jupyterapp.shell.currentWidget.content.widgets[i];
                   return c.model.executionCount !== null && !c.node.querySelector('.jp-InputPrompt').textContent.includes('*'); }""",
                arg=i, timeout=wait)
            page.wait_for_timeout(1500)

        def source(i):
            return page.evaluate("i => window.jupyterapp.shell.currentWidget.content.widgets[i].model.sharedModel.getSource()", i)

        def uncomment(src, steps):
            """取消前 steps 個以 '# fig.' 開頭的步驟行，等同學生選取該行按 Ctrl+/。"""
            out, done = [], 0
            for line in src.splitlines():
                if line.startswith("# fig.") and done < steps:
                    line, done = line[2:], done + 1
                out.append(line)
            return "\n".join(out)

        def shot(name, i, align="top", part=None):
            """把第 i 格（或其輸出區 part='output'）的頂端或底端對齊視窗後截圖。"""
            page.evaluate(
                """([i, align, part]) => { const outer = document.querySelector('.jp-WindowedPanel-outer');
                   let el = window.jupyterapp.shell.currentWidget.content.widgets[i].node;
                   if (part) el = el.querySelector('.jp-Cell-outputWrapper') || el;
                   el.scrollIntoView({block: 'nearest'});
                   const r = el.getBoundingClientRect(), o = outer.getBoundingClientRect();
                   outer.scrollTop += align === 'top' ? r.top - o.top - 12 : r.bottom - o.bottom + 16; }""",
                [i, align, part])
            page.wait_for_timeout(700)
            page.screenshot(path=SCREENS / name)

        def parts(name, i, code=True):
            """程式區與輸出的地圖分開截圖（name_in.png、name_out.png），影片中左右並排。
            暫時拉高視窗，避免比視窗高的儲存格被裁切。"""
            page.set_viewport_size({"width": 1280, "height": 1700})
            page.wait_for_timeout(800)
            wanted = (("in", ".jp-Cell-inputWrapper"),) if code else ()
            for part, css in wanted + (("out", ".jp-OutputArea-output img"),):
                el = cell(i).locator(css).last
                el.scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                el.screenshot(path=SCREENS / f"{name}_{part}.png")
            page.set_viewport_size({"width": 1280, "height": 760})
            page.wait_for_timeout(800)

        # 1. 文字儲存格與程式儲存格（尚未執行）
        page.evaluate("window.jupyterapp.shell.currentWidget.content.activeCellIndex = 6")
        shot("jl_cells.png", 6, align="bottom")

        # 2. 準備環境
        run(1)
        shot("jl_env.png", 1, align="bottom")

        # 3. 空白底圖 → 逐步取消註解
        base = source(6)
        run(6)
        parts("jl_step0", 6)
        run(6, uncomment(base, 3))
        parts("jl_step3", 6)
        run(6, uncomment(base, 6))
        parts("jl_step6", 6)

        # 4. 跳過下載資料的儲存格 → NameError
        run(11)
        shot("jl_error.png", 11, align="bottom")

        # 5. 下載 USGS 地震資料 → 畫地震
        run(9)
        shot("jl_usgs.png", 9, align="bottom")
        run(11)
        parts("jl_quakes", 11)
        run(13)
        run(15)
        parts("jl_depth", 15, code=False)
        ctx.browser.close()
    finally:
        server.terminate()
        server.wait(timeout=30)
        shutil.rmtree(work, ignore_errors=True)
        shutil.rmtree(settings, ignore_errors=True)


def main():
    SCREENS.mkdir(exist_ok=True)
    parts = sys.argv[1:] or ["github", "colab", "jupyter"]
    with sync_playwright() as p:
        for name in parts:
            {"github": github, "colab": colab, "jupyter": jupyter}[name](p)
    print("screens:", sorted(f.name for f in SCREENS.glob("*.png")))


if __name__ == "__main__":
    main()

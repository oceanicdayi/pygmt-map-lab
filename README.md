# PyGMT Map Lab｜地圖實作教室

從一張台灣地圖開始，探索地震、山脈與海底地形，再把視角轉向世界的板塊交界帶。

這堂課使用 PyGMT，帶你從現成範例修改出自己的地圖。先認識繪圖的基本設定，再用 AI 協助畫出世界上某一段板塊交界帶，從海底地形與地震分布佐證它是哪一類，銜接後面的板塊構造課。

## 開始上課

**[先看課程介紹與 Gallery →](intro.md)**

第一次用 Notebook 或 GitHub？先看 [操作教學影片（約 8 分鐘）](https://oceanicdayi.github.io/2026_utaipei_plate_tectonic/artifacts/22-notebook_github_tutorial.mp4)：從開啟 Colab、一格一格執行、看懂錯誤訊息，到用 GitHub 繳交作業。

<a href="https://oceanicdayi.github.io/2026_utaipei_plate_tectonic/artifacts/22-notebook_github_tutorial.mp4"><img src="docs/video/notebook_github_tutorial_poster.jpg" alt="操作教學影片：Notebook 與 GitHub 上手指南（點擊播放）" width="480"></a>

*點圖片在瀏覽器播放（中文旁白、內嵌字幕）。影片檔與字幕檔也收在 [docs/video/](docs/video/)，可下載離線觀看。*

前兩份是 Colab Notebook，各自包含環境設置，可獨立開始；第三份是說明文件加範例程式，執行環境自己準備：

- [01｜基本地圖與地震](https://colab.research.google.com/github/jimmy60504/pygmt-map-lab/blob/main/01_maps_earthquakes.ipynb)
- [02｜地形與 3D](https://colab.research.google.com/github/jimmy60504/pygmt-map-lab/blob/main/02_terrain_3d.ipynb)
- [03｜AI 探索與作業：畫世界的板塊交界帶](03_ai_exploration.md)（說明與範例圖，程式在 [examples/](examples/)）

先在 GitHub 閱讀 GMT、PyGMT 與資料來源介紹，再到 Colab 跟著範例程式與練習操作。

1. 登入 Google 帳號，開啟上方連結。
2. 將 Notebook 另存副本，作為自己的練習檔。
3. 依照「準備環境」的說明執行安裝，再開始畫圖。

教材庫已公開，可由上方連結開啟 Colab。執行與另存副本仍需登入 Google 帳號。

## 這堂課會做什麼？

前兩份 Notebook 用台灣建立「一張圖是一連串選擇的結果」；第三份把同一套方法搬到世界，「AI 負責實作，判讀與證據由自己負責」。第三份不是 Notebook，是一份說明加六支範例程式，學生把範例交給 AI 改，執行環境自己準備（本機或 Colab 都可）。

**課前導讀（[intro.md](intro.md)）**

- 認識 GMT 與 PyGMT：以程式描述地圖，更換資料與範圍即可重新產生。
- 瀏覽官方 Gallery，認識科學地圖的表現形式；說明地震目錄的基本欄位。

**01｜基本地圖與地震（不使用 AI）**

- 地圖基本組成：繪圖範圍、投影與圖層疊加順序。
- 資料取得：透過 USGS API 依條件查詢地震目錄，注意時區對齊與收錄限制。
- 視覺變數對應：同一批事件依序以位置、大小（規模）、顏色（深度）呈現。
- 色票（CPT）：數值與顏色的對應、色階範圍固定與超出範圍的處理。
- 圖與圖說是一組：修改查詢條件時同步更新圖說。

**02｜地形與 3D（手動調整參數，AI 僅用於製作拉桿）**

- 網格資料：解析度單位與下載範圍的取捨。
- 高程的三種表達方式：顏色、陰影、等高線，各自突顯不同特徵。
- 陰影為模擬照光而非高度；等高線密度影響可讀性。
- 3D 視角：方位角、仰角與垂直誇大對地形判讀的影響。
- 拉桿用於連續比較視角，作為 AI 輔助的前導。

**03｜AI 探索與作業：畫世界的板塊交界帶（[03_ai_exploration.md](03_ai_exploration.md)）**

- 三大類交界帶（張裂、聚合、轉形）在地形與地震上的訊號：海溝、洋脊、裂谷、線狀錯動；地震深度三段分級（0–70、70–300、300–700 km），有中深震幾乎就是隱沒帶。分類沿用 Lillie (1999)《Whole Earth Geophysics》。
- 全球總覽：地震、全新世火山與熱點疊在地形上，看出地震帶就是交界帶。
- 世界交界帶整理表（[plate-boundaries.md](plate-boundaries.md)）：三十多段，附範圍、兩側板塊與「佐證時注意」，學生從中挑一段或自己框。
- 六張範例圖各配一支程式（`examples/`）：全球總覽、八段交界帶平面圖、區域地圖加 A–B 剖面、速度剖面、3D 海底方塊、火山與熱點。區域範本改參數就能換區域，自動查 USGS 筆數、標 VE、統計多少深度是預設值。
- AI 工具與圖像檢查表沿用；另加三項：深度分級界線、剖面方向與走廊、預設深度比例。
- 作業：一段交界帶的地圖與剖面，圖說寫「看到什麼、證據是什麼、哪裡不確定」，使用 PyGMT 並提交 GitHub。
- 作業範例：[巽他海峽／喀拉喀托之子（2026）](case-studies/2026-sunda-strait-krakatau/README.md)，接 2026 年 9 月火山噴發新聞的時事案例。

## 資料從哪裡來？

地震主要使用 [USGS 地震目錄](https://earthquake.usgs.gov/fdsnws/event/1/)，並介紹 [台灣 GDMS](https://gdms.cwa.gov.tw/) 這個在地資料管道。地形透過 PyGMT 取得 [GMT 全球地形資料](https://docs.generic-mapping-tools.org/latest/datasets/remote-data.html)。第三份另外用到 [NOAA NCEI 火山位置](https://www.ngdc.noaa.gov/hazel/view/hazards/volcano/loc-search)、GMT 內建熱點範例，以及 [EarthScope EMC](http://ds.iris.edu/ds/products/emc/) 的層析模型；完整清單見下方作業段落。

Notebook 會在執行時下載資料並產生圖片，請保持網路連線。

## 兩週後繳交作品

作業就用 AI 做：選一段世界的板塊交界帶，畫圖、切剖面、寫證據。事先知道答案沒關係，重點是圖上拿得出證據。

作品請把**圖＋圖說**放在一起，內容三件事：

1. **一段交界帶的地圖與至少一條 A–B 剖面**：地形當底，地震依三段深度上色、大小表規模，有比例尺、圖例與位置示意；剖面深度軸到 700 km，標 VE。可沿用 `examples/` 的範例改參數，也可請 AI 重寫。
2. **圖說三段**：看到什麼地形與地震分布；符合哪一類交界、圖上哪些特徵是證據；哪些地方不符合或不確定、還缺什麼資料。
3. **資料註記**：來源、時間範圍、規模門檻、走廊半寬、有多少深度是 USGS 預設值。

加分（自由）：再畫一段不同類型做對照；加上火山、熱點、速度剖面或震源機制當佐證；畫多條剖面看沿走向的變化。

作業只需滿足三個條件：

1. **作品與 PyGMT 有關。**
2. **將作品上傳 GitHub，繳交 repository 連結**，並確認教師能開啟。
3. **附上 AI 對話紀錄**：把和 AI 來回的過程存進同一個 repository，例如對話分享連結、匯出的文字檔或截圖。不用整理，重點是看得到你怎麼提問、AI 改了什麼、你怎麼檢查。

建立 repository、上傳檔案與繳交前的檢查步驟，見 [操作教學影片](https://oceanicdayi.github.io/2026_utaipei_plate_tectonic/artifacts/22-notebook_github_tutorial.mp4) 後半段。

判斷對錯不是主要分數；圖是否完整可讀、推論是否有圖上證據、有沒有誠實寫出不確定，才是。兩週後繳交，答案在板塊構造課對照板塊邊界模型一起揭曉。

想先看別人怎麼畫？[地震學常見圖像](earthquake-figure-guide.md) 末段有「先逛逛論文的圖」的搜尋方式與期刊入口，[論文圖收集](figure-examples.md) 有漂亮的和普通的對照。

### 這份作業會用到的資料

`examples/` 的範例已經把前四項接好；後面幾項是佐證用的補充。作品仍需用到 PyGMT，可搭配其他工具。

| 想找什麼 | 資料入口 | 可以做什麼 |
| --- | --- | --- |
| 全球地震目錄 | [USGS](https://earthquake.usgs.gov/fdsnws/event/1/)／[ISC Bulletin](https://www.isc.ac.uk/iscbulletin/search/) | 位置、深度、規模；USGS 單次上限 20,000 筆，ISC 整合各國網、小地震較全 |
| 台灣更細的地震 | [氣象署 GDMS](https://gdms.cwa.gov.tw/) | 想把台灣當對照組時用 |
| 海陸地形 | [GMT 全球地形](https://docs.generic-mapping-tools.org/latest/datasets/remote-data.html)／[GEBCO](https://www.gebco.net/data-products/gridded-bathymetry-data) | 海溝、洋脊、裂谷、斷裂帶；大框用 05m，細看用 01m 或 15s |
| 火山 | [NOAA NCEI 火山位置](https://www.ngdc.noaa.gov/hazel/view/hazards/volcano/loc-search)／[Smithsonian GVP](https://volcano.si.edu/) | 火山鏈平行海溝是隱沒帶、沿裂谷是張裂、轉形帶沒有 |
| 熱點 | GMT `@hotspots.txt`（Müller et al. 1993） | 板塊內部的火山，當「不是交界」的對照 |
| 板塊邊界線 | [Bird (2003) PB2002](http://peterbird.name/publications/2003_pb2002/2003_pb2002.htm)（[GeoJSON](https://github.com/fraxen/tectonicplates)）／[Hasterok et al. (2022)](https://github.com/dhasterok/global_tectonics) | 判讀完再疊上去對答案；PB2002 每段有類型碼 |
| 板塊掛圖 | [USGS This Dynamic Planet (2006)](https://pubs.usgs.gov/imap/2800) | 公有領域，板塊、火山、地震同一張圖 |
| 板片深度 | [Slab2（USGS）](https://www.sciencebase.gov/catalog/item/5aa1b00ee4b0b1c392e86467) | 隱沒帶的板片幾何，可疊在剖面上檢查傾斜帶 |
| 速度構造 | [EarthScope EMC](http://ds.iris.edu/ds/products/emc/) | 層析模型的剖面，看板片與岩石圈；也有線上剖面工具 |
| 震源機制 | [Global CMT](https://www.globalcmt.org/CMTfiles.html) | 逆衝、正斷層、走滑各對應聚合、張裂、轉形；用 `fig.meca()` 畫 |

下載前請 AI 一起檢查年份、座標系統、單位與授權。深度、規模的定義各目錄不同，不要混用；資料疊在一起不代表已證明因果。

## 想再多探索？

- [PyGMT Gallery](https://www.pygmt.org/v0.17.0/gallery/index.html)：從範例找靈感。
- [PyGMT Tutorials](https://www.pygmt.org/v0.17.0/tutorials/index.html)：官方教學，Basics 涵蓋範圍設定、海岸線、框線、點線面與文字；Advanced 有等高線、3D 透視、地形疊圖、圖例、子圖與 inset，可對照課堂內容延伸。
- [PyGMT 文件](https://www.pygmt.org/v0.17.0/)：查閱函式與參數。
- [GMT 官方網站](https://www.generic-mapping-tools.org/)：認識背後的繪圖工具。

**把圖畫得好看、讓人讀得懂**

- [Nature 圖像規範](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)：期刊對字級、線寬、解析度、色彩與版面的要求，可當作自己作品的檢查表。
- [Seismica 投稿檢查表](https://seismica.library.mcgill.ca/submission-checklist)：地震學期刊對色票與可及性的要求，包含不用彩虹色票。
- [Points of View: Color blindness](https://www.nature.com/articles/nmeth.1618)：一頁講完為什麼紅綠對比不可靠，以及色覺友善的配色原則。
- [Coblis 色覺模擬器](https://www.color-blindness.com/coblis-color-blindness-simulator/)：把自己的圖丟進去，看不同色覺的人看到什麼。

**科學用的色票（CPT）**

- [GMT 色票總覽](https://docs.generic-mapping-tools.org/6.5/reference/cpts.html)：課堂用的 `geo`、`abyss`、`batlow`、`roma` 都在這裡，分成 GMT 內建、cmocean、Scientific Colour Maps 三組。
- [Scientific Colour Maps（Crameri）](https://www.fabiocrameri.ch/colourmaps/)：感知均勻、色覺友善的色票；循序用 batlow，發散用 vik 或 roma，地形用 oleron。GMT 已內建，`makecpt(cmap="batlow")` 直接用。
- [The misuse of colour in science communication（Crameri et al. 2020, Nature Communications）](https://www.nature.com/articles/s41467-020-19160-7)：為什麼彩虹色票會扭曲資料，附各種資料類型該用哪種色票。
- [cmocean](https://matplotlib.org/cmocean/)：海洋學色票，深度用 deep，地形用 topo，速度異常用 balance；GMT 內建。
- [ColorBrewer](https://colorbrewer2.org/)：分類與分級用的離散配色，可勾選色覺友善與適合印刷。

## 補充資料索引

- [intro.md](intro.md)：課前介紹，認識 GMT、PyGMT、官方 Gallery 與地震資料來源。
- [03_ai_exploration.md](03_ai_exploration.md)：第三部分的說明與範例圖；程式在 [examples/](examples/)。
- [plate-boundaries.md](plate-boundaries.md)：世界板塊交界帶整理表，第三部分選區域用；附範圍、兩側板塊與佐證提示。
- [earthquake-figure-guide.md](earthquake-figure-guide.md)：地震學常見圖像，每種圖想回答什麼、怎麼讀，附範例。
- [figure-examples.md](figure-examples.md)：論文圖收集，漂亮的和普通的放在一起比較。
- [video/](video/)：操作教學影片的擷取與產生腳本；改旁白或教材更新後可重新產生。

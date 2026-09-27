# 案例：巽他海峽／喀拉喀托之子（2026）

[回課程首頁](../../README.md) · [板塊交界帶總表](../../plate-boundaries.md)

## 新聞事件

喀拉喀托之子（Anak Krakatau）於 2026-09-04 至 06 日連續噴發約 25 小時，火山本體新增陸地 32.8 公頃，
周邊另新增兩處小隆起（距岸分別約 760 m、495 m），印尼地質局以 Sentinel 衛星影像比對確認地貌變化；
警戒由第三級「警戒」降為第二級「注意」，但仍禁止接近噴發中心 2 km、新陸地 1 km 範圍。

- NOWnews（2026-09-25）〈火山噴發後冒出2座島？印尼巽他海峽新陸地 地質局證實地貌變化〉
- Antara（2026-09-25）〈Ada daratan baru di dekat Anak Krakatau, ini penjelasan ahli〉
- Antara（2026-09-23）〈Runtuh pada 2018, Peneliti BRIN ungkap Anak Krakatau kini tumbuh lagi〉

## 看到什麼

- `global_plate_context.png`：把上面局部放大的邊界放回全球脈絡。畫出 PB2002 全部邊界，依聚合
  （紅）／張裂（藍）／錯動（灰）上色，黃色星號標出巽他海峽。可以看到它是環太平洋、喜馬拉雅一帶
  連續聚合帶的一部分——蘇門答臘–爪哇隱沒帶往西北接安達曼海、緬甸弧，往東接小巽他群島、班達弧，
  最終銜接紐幾內亞與環太平洋火環。
- `plate_boundary_map.png`：直接回答「巽他海峽位在哪個板塊邊界」——不是從地震分布反推，而是疊上
  Peter Bird (2003) PB2002 板塊邊界模型的真實分類資料。整段邊界在 PB2002 裡標為 `SU/AU`、類型
  `SUB`（隱沒帶），紅色三角前緣符號尖端指向上覆的巽他板塊（SU，歐亞板塊的一部分），另一側是印澳
  板塊在 Bird 模型中對應的澳洲板塊（AU）。
- `sunda_strait_map.png`：範圍 100–109°E、9–3°S。地形上明顯看到巽他海溝（西南側深藍）、火山弧
  沿蘇門答臘東南岸與爪哇西岸排列（白色三角形為 NCEI/GVP 全新世火山，共 31 座），喀拉喀托之子
  （黃色三角形）正好位在海溝與弧後之間、蘇門答臘與爪哇的交會處。地震（USGS，2000 年起 M≥4.5，
  2771 筆）沿海溝密集分布，顏色代表深度（紅：0–70 km、橘：70–300 km、藍：300–700 km）。
- `sunda_strait_section.png`：A–B 剖面垂直海溝走向（大致 N40°E，走廊半寬 100 km，共 434 筆），
  上方地形顯示海溝到火山弧的地形起伏，下方深度剖面清楚看到一道從淺到深、向東北傾斜的地震帶
  （Wadati-Benioff 帶），最深達約 600 km，符合隱沒板塊的幾何。

## 屬於哪一類交界帶

聚合型交界（隱沒帶）：印澳板塊向東北隱沒到巽他板塊（歐亞板塊的一部分）之下，速率約 58 mm/年。
剖面上傾斜地震帶、海溝地形、平行海岸的火山弧三項證據都在，是課程分類裡「隱沒帶」最典型的訊號組合。

巽他海峽本身則疊加了一個特例：這段隱沒是斜向的（爪哇外海為正向隱沒，蘇門答臘外海轉為斜向），
斜向分量由蘇門答臘斷層吸收，弧前地塊因此往西北滑動、相對爪哇順時針旋轉，海峽因而成為局部張裂
環境（總伸張量估計 50–100 km，海峽內部分地震為張裂型機制，張力軸 N130°E）。喀拉喀托之子正好
座落在這個張裂地塹的交會處——這是「隱沒帶邊上也能有張裂」的例子，不是矛盾。

## 哪裡不確定

- 434 筆走廊內地震有 38% 深度標記為 USGS 常用預設值（10 或 33 km），這些事件的真實深度可能不準，
  剖面上淺震密集的那條「水平帶」部分是定位精度造成的假象，不是真的都在同一深度。
- 剖面 A–B 是依巽他海溝在此段的走向（N130°E，Harjono et al. 1991）手動決定的近似垂直線，實際隱
  沒面幾何是斜向且沿走向變化的（見上），單一直線剖面無法完整呈現三維構造。
- 2026 年 9 月新增的 32.8 公頃陸地是火山噴發堆積造成，不是板塊運動直接「推出」新地——板塊每年只移
  動幾公分，真正把岩漿送上來的是隱沒作用經年累月的效果；這點容易被新聞標題（「新島」）誤導。
- 喀拉喀托之子 2018 年曾側翼崩塌引發海嘯（437 人罹難），這類崩塌型海嘯源缺乏強烈短週期地動訊號，
  以規模與震源為基礎的傳統地震預警難以偵測，圖上的地震分布看不出這個風險。

## 資料來源與方法

- 地震：USGS FDSNWS event API，`starttime=2000-01-01`、`minmagnitude=4.5`，範圍見 `map_section.py`。
- 火山：NOAA NCEI hazard-service API（全新世火山清單，源自 Smithsonian GVP）。
- 板塊邊界：Peter Bird (2003) PB2002 模型，經 [fraxen/tectonicplates](https://github.com/fraxen/tectonicplates) 轉存的 GeoJSON。
- 地形：GMT 遠端資料 `earth_relief`，02 角分解析度。
- 隱沒速率、張裂量、震源機制等數字引自 Harjono et al. (1991, *Tectonics*)、Nishimura et al. (1992,
  *GeoJournal*)、Dahren et al. (2012, *J. Petrology*)；2018 年崩塌與海嘯引自 Grilli et al. (2019,
  *Sci. Rep.*)、Ye et al. (2020, *Science Advances*)、Perttu et al. (2020, *EPSL*)。完整投影片版本見
  [`2026_utaipei_plate_tectonic` 的 `artifacts/喀拉喀托之子與板塊構造.pdf`](https://github.com/oceanicdayi/2026_utaipei_plate_tectonic/blob/main/artifacts/%E5%96%80%E6%8B%89%E5%96%80%E6%89%98%E4%B9%8B%E5%AD%90%E8%88%87%E6%9D%BF%E5%A1%8A%E6%A7%8B%E9%80%A0.pdf)。
- 重跑：`python3 map_section.py`、`python3 plate_boundary_map.py`、`python3 global_plate_context.py`（需要 pygmt 0.17，含 pandas、numpy；需連網）。

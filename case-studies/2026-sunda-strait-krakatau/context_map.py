"""巽他海峽（喀拉喀托之子）板塊構造脈絡圖：示意版，不含即時地震目錄。

背景：2026-09-04 至 06，印尼「喀拉喀托之子」（Anak Krakatau）火山活動約 25 小時，
熔岩與噴發物堆積使火山陸地面積增加約 32.8 公頃，西北側、東南側各出現一處新地貌
（距火山岸線約 760 m、495 m）；印尼能源礦產部地質局尚未認定為新火山島或新火口。
新聞來源：NOWnews〈火山噴發後冒出2座島？印尼巽他海峽新陸地 地質局證實地貌變化〉
(https://www.nownews.com/news/6878103)。

這支程式只用 GMT 內建、可離線讀取的資料（海岸線 GSHHG、國界 DCW），
刻意不畫地震點：本次執行環境的網路政策封鎖了 earthquake.usgs.gov、
www.ngdc.noaa.gov 與 GMT 遠端地形伺服器，抓不到即時地震目錄、火山目錄或
全球地形網格，畫不出示範程式（如 pygmt-map-lab/examples/02_region_map_section.py）
那種「地形 + 三段深度地震 + A-B 剖面」的資料驅動圖。

因此本圖只標三件確定的事：海岸線（GMT GSHHG，精確）、喀拉喀托之子座標
（105.423E, 6.102S，公開文獻座標）、隱沒帶大略走向與聚合方向（示意線，
依 Bird 2003 / Hall 2002 一類的板塊模型概念繪製，非量測或下載資料，僅供
方向判斷）。圖上文字改用英文，理由與課程範例一致：GMT 預設 PostScript 字型
不含中文字型，直接寫中文會變亂碼。真正的地震分布、深度分級與 A-B 剖面，
留給 dataviz_map_section.py（資料驅動版，需要對外連線）。

輸出：context_map.png
需要：pygmt 0.17（僅用本機 GSHHG／DCW，不連網）。
"""
import pygmt

OUT = "context_map.png"

REGION = [98, 112, -11, -3]  # west, east, south, north (deg): S.Sumatra - Sunda Strait - W.Java - offshore trench

# Anak Krakatau, published coordinates
KRAKATAU = (105.423, -6.102)

# Schematic Sunda Trench trace, Sumatra segment bending into Java segment (hand-drawn, not downloaded)
TRENCH_LON = [97.5, 99.5, 101.5, 103.5, 105.5, 107.5, 109.5, 111.5]
TRENCH_LAT = [-4.3, -5.3, -6.3, -7.3, -8.0, -8.5, -8.9, -9.1]

# Schematic Sumatra-Java volcanic arc axis (hand-drawn, not downloaded)
ARC_LON = [98.0, 100.0, 102.0, 104.0, 105.423, 107.5, 110.0, 112.0]
ARC_LAT = [-3.5, -4.0, -4.8, -5.5, -6.102, -6.9, -7.5, -7.8]

fig = pygmt.Figure()
pygmt.config(FONT_ANNOT_PRIMARY="9p", FONT_LABEL="10p", FONT_TITLE="11p", MAP_FRAME_TYPE="plain")

fig.coast(
    region=REGION, projection="M14c",
    land="#e8dcc8", water="#bfe0ea", shorelines="0.4p,gray20",
    borders="1/0.5p,gray50,--", resolution="i",
    frame=["af", "+tSunda Strait subduction zone and Anak Krakatau (schematic, no live quake data)"],
)

# Schematic trench line, teeth point toward the subduction (downgoing) side
fig.plot(x=TRENCH_LON, y=TRENCH_LAT, pen="1.2p,black",
         style="f1.2c/0.3c+r+t+o0.3c", fill="black")
fig.text(x=98.3, y=-6.9, text="Sunda Trench (schematic trace)",
         font="8p,Helvetica-Bold,black", justify="LM")

# Schematic volcanic-arc axis
fig.plot(x=ARC_LON, y=ARC_LAT, pen="1p,red,--")
fig.text(x=99.7, y=-3.3, text="Sumatra-Java volcanic arc (schematic axis)",
         font="8p,Helvetica-Bold,red", justify="LB")

# Convergence direction: Indo-Australian plate relative to Sunda block, ~N15E, ~60-70 mm/yr
# (typical GPS-literature magnitude, e.g. Bock et al. 2003; shown for direction only, not measured here)
fig.plot(x=[104.0], y=[-9.8], style="v0.4c+e+a40", direction=[[15], [1.3]],
         pen="1.5p,darkblue", fill="darkblue")
fig.text(x=104.7, y=-9.8, text="Indo-Australian plate ~N15\\260E, ~60-70 mm/yr",
         font="7p,darkblue", justify="LM")
fig.text(x=104.7, y=-10.15, text="(GPS-literature magnitude, direction only)",
         font="7p,darkblue", justify="LM")

# Anak Krakatau: star + label + news-event annotation
fig.plot(x=[KRAKATAU[0]], y=[KRAKATAU[1]], style="a0.55c", fill="orange", pen="0.8p,black")
fig.text(x=KRAKATAU[0], y=KRAKATAU[1], text="Anak Krakatau",
         font="8p,Helvetica-Bold,black", justify="BL", offset="0.25c/0.15c")
fig.text(x=KRAKATAU[0], y=KRAKATAU[1], text="2026-09-04~06 eruption, +32.8 ha new land",
         font="7p,black", justify="TL", offset="0.25c/-0.25c")

fig.basemap(map_scale=f"jBL+c{(REGION[2]+REGION[3])/2}+w200k+o0.5c/0.5c+f+lkm")

with fig.inset(position="jTR+w2.6c+o0.1c"):
    fig.coast(region="g", projection=f"G{(REGION[0]+REGION[1])/2}/{(REGION[2]+REGION[3])/2}/2.6c",
              land="gray70", water="white", frame="g")
    fig.plot(x=[REGION[0], REGION[1], REGION[1], REGION[0]], y=[REGION[2], REGION[2], REGION[3], REGION[3]],
             close=True, pen="1p,red")

fig.text(text="Coastline: GMT GSHHG (exact) | trench/arc/convergence arrow: schematic, not downloaded or measured | "
              "no quake points: USGS/NOAA/GMT remote data blocked by this sandbox's network policy",
         position="BC", offset="0c/-1.1c", font="7p,gray30", no_clip=True)

fig.savefig(OUT, dpi=200)
print("saved", OUT)

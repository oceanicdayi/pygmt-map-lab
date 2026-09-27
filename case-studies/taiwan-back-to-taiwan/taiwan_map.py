"""案例：回到臺灣——取代課程網頁「八、回到臺灣」的手繪示意圖。
臺灣同時有兩條方向相反的隱沒帶（琉球海溝、馬尼拉海溝）加一條弧陸碰撞縫合線（花東縱谷），
地震分布可以直接看出兩道方向相反的隱沒地震帶。

輸出：taiwan_map.png
資料：USGS 地震目錄 API、NCEI/GVP 全新世火山清單、GMT 全球地形 2 角分。
需要：pygmt 0.17（含 pandas）。需連網。
"""
import json
import urllib.request

import pandas as pd
import pygmt

# ==== 參數：範圍涵蓋臺灣本島與南北兩條海溝 ====
REGION = [117, 124.5, 19, 26]      # 西、東、南、北（度）
START, MINMAG = "2000-01-01", 4.5   # 地震起始日與最低規模
OUT_MAP = "taiwan_map.png"
# ================================================

# 1. 地震：先查筆數，超過 20,000 自動提高規模門檻
base = "https://earthquake.usgs.gov/fdsnws/event/1/"
minmag = MINMAG
while True:
    query = (f"starttime={START}&minmagnitude={minmag}"
             f"&minlongitude={REGION[0]}&maxlongitude={REGION[1]}&minlatitude={REGION[2]}&maxlatitude={REGION[3]}")
    count = int(urllib.request.urlopen(base + "count?" + query).read())
    if count <= 20000:
        break
    minmag += 0.5
quakes = pd.read_csv(base + "query?format=csv&" + query).dropna(subset=["longitude", "latitude", "depth", "mag"])
quakes = quakes.sort_values("depth", ascending=False)
print(f"USGS {START} 起 M >= {minmag}：{len(quakes)} 筆")

# 2. 火山：NCEI（全新世清單，源自 Smithsonian GVP），只取範圍內的
rows, page = [], 1
while True:
    url = f"https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanolocs?itemsPerPage=200&page={page}"
    with urllib.request.urlopen(url) as response:
        data = json.load(response)
    rows += data["items"]
    if page >= data["totalPages"]:
        break
    page += 1
volc = pd.DataFrame(rows).dropna(subset=["latitude", "longitude"])
volc = volc[volc.longitude.between(*REGION[:2]) & volc.latitude.between(*REGION[2:])]
print(f"範圍內全新世火山 {len(volc)} 座")


def mag_size(m):
    return min(0.045 * 2 ** (m - 5), 0.35)


# 3. 地圖
grid = pygmt.datasets.load_earth_relief(resolution="02m", region=REGION)
fig = pygmt.Figure()
fig.grdimage(grid=grid, region=REGION, projection="M14c", cmap="geo", shading="+a-45+nt0.5",
             frame=["af", f"+tTaiwan: two opposite-dipping subduction zones (USGS M>={minmag} since {START[:4]})"])
fig.coast(shorelines="0.3p,gray20", resolution="f")

pygmt.makecpt(cmap="#d7191c,#fdae61,#2c7bb6", series="0,70,300,700")  # 淺、中、深
fig.plot(x=quakes.longitude, y=quakes.latitude, size=quakes.mag.apply(mag_size) * 0.7,
         fill=quakes.depth, cmap=True, style="c", pen="0.1p,black", transparency=40)
fig.plot(x=volc.longitude, y=volc.latitude, style="t0.22c", fill="white", pen="0.6p,black")

# geological zones: approximate, well-known reference points (not precise fault traces)
fig.plot(x=[121.60, 121.15], y=[23.99, 22.76], pen="1.2p,white,--")  # Hualien -> Taitung, Longitudinal Valley
fig.text(x=121.02, y=23.75, text="Central Range", font="8p,Helvetica-Bold,white", fill="black@60", justify="LM", angle=68)
fig.text(x=120.52, y=23.55, text="Western Foothills", font="8p,Helvetica-Bold,white", fill="black@60", justify="LM", angle=68)
fig.text(x=121.80, y=23.45, text="Longitudinal Valley", font="8p,Helvetica-Bold,white", fill="black@60", justify="LM")
fig.text(x=121.80, y=23.20, text="(PSP-Eurasia suture)", font="7p,Helvetica,white", fill="black@60", justify="LM")

# trenches: labelled where the bathymetric trough is visible
fig.text(x=123.3, y=24.55, text="Ryukyu Trench", font="9p,Helvetica-Bold,black", fill="white@20", justify="LM")
fig.text(x=118.7, y=20.2, text="Manila Trench", font="9p,Helvetica-Bold,black", fill="white@20", justify="LM")

# convergence: Philippine Sea plate motion relative to Eurasia (~N306E, ~8 cm/yr; Yu et al. 1997)
fig.plot(data=[[123.3, 22.6, 122.55, 23.05]], style="v0.4c+e+s", pen="2p,black", fill="black")
fig.text(x=123.35, y=22.45, text="PSP ~8 cm/yr", font="8p,Helvetica-Bold,black", fill="white@20", justify="LM")

fig.basemap(map_scale=f"jBL+c{(REGION[2] + REGION[3]) / 2}+w200k+o0.3c/0.3c+f+lkm")
fig.colorbar(position="JBC+w8c/0.3c+h+o0c/0.8c", frame=["a0", "+lDepth (km): 0-70 / 70-300 / 300-700"])
fig.savefig(OUT_MAP, dpi=150)
print("saved", OUT_MAP)

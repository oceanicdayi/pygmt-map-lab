"""資料驅動版：巽他海峽（喀拉喀托之子）隱沒帶地圖＋A-B 剖面。

沿用 examples/02_region_map_section.py 的框架（地形 + 地震三段深度上色 +
A-B 線與走廊 + 位置示意），只換區域與剖面端點，並疊上喀拉喀托之子的位置：
2026-09-04~06 火山活動約 25 小時，陸地面積增加約 32.8 公頃，西北、東南側
各出現一處新地貌，是這份圖要呼應的新聞事件（NOWnews 6878103）。

A-B 端點是這樣選的：A 落在外海、大致對齊蘇門答臘—爪哇轉折處的海溝軸；
B 落在陸地一側；連線通過喀拉喀托之子附近（依座標估算，偏移約 10 公里，
在 HALF_WIDTH_KM 的走廊半寬內），大致垂直於這一段海溝／火山弧走向，
可以看到隱沒帶典型的「淺-中-深」傾斜地震帶。座標選得粗略，實際判讀
仍要看跑出來的圖跟走廊筆數。

輸出：sunda_strait_map.png、sunda_strait_section.png
資料：USGS 地震目錄 API、GMT 全球地形。
需要：pygmt 0.17（含 pandas、numpy）。需連網。

注意：本程式在目前這個 Claude Code 沙盒環境跑不動——網路政策封鎖了
earthquake.usgs.gov、www.ngdc.noaa.gov 與 GMT 遠端地形伺服器（403），
所以這份程式碼是「照課程範本寫好、待有對外連線的環境（本機或 Colab）
執行」，本次交付改用同目錄 context_map.py 的示意圖佐證位置與板塊脈絡。
"""
import urllib.request

import numpy as np
import pandas as pd
import pygmt

# ==== 改這裡：巽他海峽，蘇門答臘—爪哇轉折處，涵蓋外海海溝到陸上火山弧 ====
REGION = [100, 110, -10, -2]         # 西、東、南、北（度）
START, MINMAG = "2000-01-01", 5.0     # 地震起始日與最低規模
A, B = (103.5, -8.5), (106.5, -5.0)   # 剖面兩端：外海海溝 -> 陸地，大致垂直交界走向
HALF_WIDTH_KM = 150                   # 走廊半寬（km），涵蓋喀拉喀托之子（線外約 10 km）
DEPTH_MAX = 700                       # 剖面深度軸下限；固定 700 方便跨區域比較
KRAKATAU = (105.423, -6.102)          # 喀拉喀托之子，公開文獻座標
OUT_MAP, OUT_SECTION = "sunda_strait_map.png", "sunda_strait_section.png"
# ======================================================

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
print(f"USGS {START} 起 M >= {minmag}：{len(quakes)} 筆")

# 2. 走廊內地震投影到 A-B 線：distance 沿線距離、offset 離線距離（km）
selected = pygmt.project(data=quakes[["longitude", "latitude", "depth", "mag"]],
                         center=list(A), endpoint=list(B), unit=True, length="w",
                         width=[-HALF_WIDTH_KM, HALF_WIDTH_KM], convention="xypqz")
selected.columns = ["longitude", "latitude", "distance", "offset", "depth", "mag"]
selected = selected.sort_values("depth", ascending=False)
track = pygmt.project(center=list(A), endpoint=list(B), generate=5, unit=True)
track.columns = ["lon", "lat", "distance"]
length_km = float(track.distance.iloc[-1])
print(f"走廊內 {len(selected)} 筆；A-B 長 {length_km:.0f} km")

# 3. 地形：地圖用 02m；剖面沿 A-B 取樣
grid = pygmt.datasets.load_earth_relief(resolution="02m", region=REGION)
topo = pygmt.grdtrack(points=track[["lon", "lat"]], grid=grid, newcolname="z")


# 4. 走廊外框：沿線每點往左右各推 HALF_WIDTH_KM（球面近似，半徑 6371 km）
def bearing(lon1, lat1, lon2, lat2):
    p1, p2, dl = np.radians(lat1), np.radians(lat2), np.radians(np.subtract(lon2, lon1))
    x = np.sin(dl) * np.cos(p2)
    y = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)
    return np.degrees(np.arctan2(x, y))


def move(lon, lat, azimuth_deg, distance_km):
    p1, l1, az, d = np.radians(lat), np.radians(lon), np.radians(azimuth_deg), distance_km / 6371.0
    p2 = np.arcsin(np.sin(p1) * np.cos(d) + np.cos(p1) * np.sin(d) * np.cos(az))
    l2 = l1 + np.arctan2(np.sin(az) * np.sin(d) * np.cos(p1), np.cos(d) - np.sin(p1) * np.sin(p2))
    return np.degrees(l2), np.degrees(p2)


lon, lat = track.lon.to_numpy(), track.lat.to_numpy()
local_azimuth = bearing(lon[:-1], lat[:-1], lon[1:], lat[1:])
local_azimuth = np.append(local_azimuth, local_azimuth[-1])
left_lon, left_lat = move(lon, lat, local_azimuth - 90, HALF_WIDTH_KM)
right_lon, right_lat = move(lon, lat, local_azimuth + 90, HALF_WIDTH_KM)
corridor_lon = np.concatenate([left_lon, right_lon[::-1]])
corridor_lat = np.concatenate([left_lat, right_lat[::-1]])


def mag_size(m):
    return min(0.05 * 2 ** (m - 5), 0.4)


# 5. 地圖
fig = pygmt.Figure()
fig.grdimage(grid=grid, region=REGION, projection="M12c", cmap="geo", shading="+a-45+nt0.5",
             frame=["af", f"+tUSGS M>={minmag} since {START[:4]} - Sunda Strait"])
fig.coast(shorelines="0.3p,gray20", resolution="i")
pygmt.makecpt(cmap="#d7191c,#fdae61,#2c7bb6", series="0,70,300,700")
fig.plot(x=quakes.longitude, y=quakes.latitude, size=quakes.mag.apply(mag_size) * 0.7,
         fill=quakes.depth, cmap=True, style="c", pen="0.1p,black", transparency=40)
fig.plot(x=corridor_lon, y=corridor_lat, close=True, pen="0.8p,black,--")
fig.plot(x=[A[0], B[0]], y=[A[1], B[1]], pen="1.5p,black")
fig.text(x=[A[0], B[0]], y=[A[1], B[1]], text=["A", "B"], font="10p,Helvetica-Bold",
         fill="white", pen="0.5p,black", offset="0c/0.3c")
fig.plot(x=[KRAKATAU[0]], y=[KRAKATAU[1]], style="a0.5c", fill="orange", pen="0.8p,black")
fig.text(x=KRAKATAU[0], y=KRAKATAU[1], text="Anak Krakatau (2026-09 eruption)",
         font="7p,Helvetica-Bold", justify="LM", offset="0.25c/0c", fill="white@30")
fig.basemap(map_scale=f"jBL+c{(REGION[2] + REGION[3]) / 2}+w500k+o0.3c/0.3c+f+lkm")
fig.colorbar(position="JBC+w8c/0.3c+h+o0c/0.8c", frame=["a0", "+lDepth (km): 0-70 / 70-300 / 300-700"])
with fig.inset(position="jTR+w2.5c+o0.1c"):
    fig.coast(region="g", projection=f"G{(REGION[0] + REGION[1]) / 2}/{(REGION[2] + REGION[3]) / 2}/2.5c",
              land="gray70", water="white", frame="g")
    fig.plot(x=[REGION[0], REGION[1], REGION[1], REGION[0]], y=[REGION[2], REGION[2], REGION[3], REGION[3]],
             close=True, pen="1p,red")
fig.savefig(OUT_MAP, dpi=150)

# 6. 剖面：上方地形（各自尺度），下方距離-深度
fig = pygmt.Figure()
fig.basemap(region=[0, length_km, -11, 9], projection="X14c/2c", frame=["Wsne", "ya5f1+lTopo (km)"])
fig.plot(x=track.distance, y=topo.z / 1000, pen="0.8p,black")
fig.plot(x=[0, length_km], y=[0, 0], pen="0.3p,gray50,--")
fig.text(text="A", position="TL", offset="0.15c/-0.1c", font="10p,Helvetica-Bold")
fig.text(text="B", position="TR", offset="-0.15c/-0.1c", font="10p,Helvetica-Bold")
fig.shift_origin(yshift="-8.3c")
fig.basemap(region=[0, length_km, 0, DEPTH_MAX], projection="X14c/-8c",
            frame=["WSne", "xa200f100+lDistance from A (km)", "ya100f50+lDepth (km)"])
pygmt.makecpt(cmap="#d7191c,#fdae61,#2c7bb6", series="0,70,300,700")
fig.plot(x=selected.distance, y=selected.depth, size=selected.mag.apply(mag_size),
         fill=selected.depth, cmap=True, style="c", pen="0.3p,black", transparency=20)
ve = (8 / DEPTH_MAX) / (14 / length_km)
fig.text(text=f"corridor +/-{HALF_WIDTH_KM} km, {len(selected)} events, VE = {ve:.1f}x (topo panel separate)",
         position="BL", offset="0.15c/0.15c", font="8p", fill="white@30")
fig.savefig(OUT_SECTION, dpi=150)

fixed = selected.depth.round(1).isin([10.0, 33.0, 35.0]).mean()
print(f"圖說骨架：USGS {START} 起 M >= {minmag}，範圍 {REGION}，A={A}、B={B}，走廊全寬 {2 * HALF_WIDTH_KM} km；"
      f"剖面 VE = {ve:.1f}x；走廊內 {fixed:.0%} 的深度是 USGS 預設值（10／33 km）。")
print("saved", OUT_MAP, OUT_SECTION)

"""巽他海峽位在哪個板塊邊界？用 Bird (2003) PB2002 板塊邊界模型的真實分類資料回答，
不是用地震分布反推：直接畫出 PB2002 分類為 SU/AU、類型 SUB（隱沒帶）的邊界線段，
並標出印澳板塊（AU）與巽他板塊（SU）。

輸出：plate_boundary_map.png
資料：Peter Bird (2003) PB2002 板塊邊界模型（經 fraxen/tectonicplates 轉存的 GeoJSON）、
      GMT 全球地形 2 角分。
需要：pygmt 0.17（含 pandas）。需連網。
"""
import json
import urllib.request

import pandas as pd
import pygmt

REGION = [100, 109, -9, -3]
ANAK_KRAKATAU = (105.423, -6.102)
OUT = "plate_boundary_map.png"

# 1. Bird (2003) PB2002：逐段邊界，含兩側板塊代碼（PLATEBOUND）與邊界類型（STEPCLASS）
url = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_steps.json"
with urllib.request.urlopen(url) as response:
    steps = json.load(response)["features"]
rows = [p for p in (f["properties"] for f in steps)
        if p["PLATEBOUND"] in ("SU/AU", "BU/AU", "SU-BU")]
bnd = pd.DataFrame(rows)
# 只留下與本圖範圍有交集的線段（起點或終點落在範圍 + 3 度緩衝內）
buf = 3
in_region = (bnd.STARTLONG.between(REGION[0] - buf, REGION[1] + buf) & bnd.STARTLAT.between(REGION[2] - buf, REGION[3] + buf)) | \
            (bnd.FINALLONG.between(REGION[0] - buf, REGION[1] + buf) & bnd.FINALLAT.between(REGION[2] - buf, REGION[3] + buf))
bnd = bnd[in_region]
print("PB2002 分類：", bnd.groupby(["PLATEBOUND", "STEPCLASS"]).size().to_dict())

# 2. 地形
grid = pygmt.datasets.load_earth_relief(resolution="02m", region=REGION)

fig = pygmt.Figure()
fig.grdimage(grid=grid, region=REGION, projection="M14c", cmap="geo", shading="+a-45+nt0.5",
             frame=["af", "+tSunda Strait: which plate boundary? (Bird 2003 PB2002)"])
fig.coast(shorelines="0.3p,gray20", resolution="f")

# 3. 畫出 PB2002 的隱沒帶線段（SU/AU, SUB）：帶三角形前緣符號，尖端指向上覆板塊（巽他）一側
sub = bnd[bnd.STEPCLASS == "SUB"].sort_values("STARTLAT")
for _, seg in sub.iterrows():
    fig.plot(x=[seg.STARTLONG, seg.FINALLONG], y=[seg.STARTLAT, seg.FINALLAT],
              pen="2.5p,red", style="f1c/0.35c+r+t", fill="red")

fig.plot(x=[ANAK_KRAKATAU[0]], y=[ANAK_KRAKATAU[1]], style="t0.32c", fill="yellow", pen="0.8p,black")
fig.text(x=ANAK_KRAKATAU[0], y=ANAK_KRAKATAU[1], text="Anak Krakatau",
         font="9p,Helvetica-Bold", justify="LB", offset="0.25c/0.1c", fill="white@20")

fig.text(x=101.0, y=-8.6, text="Australia Plate (AU)", font="11p,Helvetica-Bold,white", fill="black@40", justify="LM")
fig.text(x=104.3, y=-3.8, text="Sunda Plate (SU)", font="11p,Helvetica-Bold,white", fill="black@40", justify="LM")
fig.text(x=100.6, y=-4.2, text="PB2002: SU/AU, class SUB\n(subduction)", font="8p,Helvetica-Bold,black",
         fill="white@20", justify="LM")

fig.basemap(map_scale=f"jBL+c{(REGION[2] + REGION[3]) / 2}+w200k+o0.3c/0.3c+f+lkm")
fig.savefig(OUT, dpi=150)
print("saved", OUT)

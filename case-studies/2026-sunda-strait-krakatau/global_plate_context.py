"""巽他海峽在全球板塊構造的哪個位置？用 Bird (2003) PB2002 模型畫出全球所有邊界，
依類型上色（聚合＝紅、張裂＝藍、錯動＝灰），並標出巽他海峽的位置。

輸出：global_plate_context.png
資料：Peter Bird (2003) PB2002 板塊邊界模型（經 fraxen/tectonicplates 轉存的 GeoJSON）、
      GMT 全球地形 10 角分。
需要：pygmt 0.17（含 pandas）。需連網。
"""
import json
import urllib.request

import numpy as np
import pandas as pd
import pygmt


def to_multisegment(seg):
    """把每段 (start,end) 攤成 x,y 陣列，段落之間插入 NaN 讓 GMT 斷開成多段線。"""
    n = len(seg)
    x = np.empty(n * 3)
    y = np.empty(n * 3)
    x[0::3], x[1::3], x[2::3] = seg.STARTLONG, seg.FINALLONG, np.nan
    y[0::3], y[1::3], y[2::3] = seg.STARTLAT, seg.FINALLAT, np.nan
    return x, y

SUNDA_STRAIT = (105.0, -6.3)
OUT = "global_plate_context.png"

# 1. Bird (2003) PB2002：全球所有邊界線段
url = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_steps.json"
with urllib.request.urlopen(url) as response:
    steps = json.load(response)["features"]
bnd = pd.DataFrame(f["properties"] for f in steps)
print("邊界類型統計：", bnd.STEPCLASS.value_counts().to_dict())

# 依聚合／張裂／錯動分三類上色（依 Bird 2003 的 STEPCLASS 代碼）
CONVERGENT = {"SUB", "CCB", "OCB"}
DIVERGENT = {"OSR", "CRB"}
TRANSFORM = {"OTF", "CTF"}
GROUP_STYLE = {"convergent": ("1.1p,#d7191c", CONVERGENT),
               "divergent": ("1.1p,#2c7bb6", DIVERGENT),
               "transform": ("0.9p,gray40", TRANSFORM)}

# 2. 全球底圖
fig = pygmt.Figure()
fig.grdimage(grid="@earth_relief_10m", region="d", projection="N150/22c", cmap="geo", shading="+a-45+nt0.4",
             frame=["+tWhere is the Sunda Strait? Global plate boundaries (Bird 2003 PB2002)", "g30"])
fig.coast(shorelines="0.15p,gray30")

# 3. 依類別畫邊界線：每類攤成一條帶 NaN 斷點的多段線，一次 plot 呼叫完成（比逐段畫快很多）
LABELS = {"convergent": "Convergent (SUB/CCB/OCB)", "divergent": "Divergent (OSR/CRB)", "transform": "Transform (OTF/CTF)"}
for name, (pen, classes) in GROUP_STYLE.items():
    seg = bnd[bnd.STEPCLASS.isin(classes)]
    x, y = to_multisegment(seg)
    fig.plot(x=x, y=y, pen=pen, label=LABELS[name])

# 4. 標出巽他海峽位置
fig.plot(x=[SUNDA_STRAIT[0]], y=[SUNDA_STRAIT[1]], style="a0.6c", fill="yellow", pen="1.2p,black",
         label="Sunda Strait")
fig.text(x=SUNDA_STRAIT[0], y=SUNDA_STRAIT[1] - 16, text="Sunda Strait", font="10p,Helvetica-Bold,black",
         fill="white@10", justify="CM")

fig.legend(position="JBL+jBL+o0.3c", box="+gwhite+p0.5p")
fig.savefig(OUT, dpi=150)
print("saved", OUT)

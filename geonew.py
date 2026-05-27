import pandas as pd
import numpy as np
import requests
import time
import math
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

# ข้อมูลจุดเก็บขยะ (ใส่ DATA_CAR15, DATA_CAR16 ที่คุณมี)
# ... (วางข้อมูลทั้งหมดที่คุณมีอยู่แล้ว)

def get_distance_matrix_osrm(locations):
    """ดึง Distance Matrix จาก OSRM API"""
    N, CHUNK = len(locations), 50
    D = np.zeros((N, N))
    coords = [(item[2], item[1]) for item in locations]
    
    for i in range(0, N, CHUNK):
        for j in range(0, N, CHUNK):
            src = coords[i:i+CHUNK]
            dst = coords[j:j+CHUNK]
            combined = src + dst
            coord_str = ";".join(f"{lon},{lat}" for lon, lat in combined)
            src_idx = ";".join(str(x) for x in range(len(src)))
            dst_idx = ";".join(str(x) for x in range(len(src), len(src)+len(dst)))
            
            url = (f"http://router.project-osrm.org/table/v1/driving/{coord_str}"
                   f"?sources={src_idx}&destinations={dst_idx}&annotations=distance")
            try:
                resp = requests.get(url, timeout=30)
                data = resp.json()
                if data.get("code") == "Ok":
                    D[i:i+len(src), j:j+len(dst)] = np.array(data["distances"])
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(1)  # ให้เวลา API
    
    return pd.DataFrame(D / 1000.0)  # แปลงเป็น km

# เตรียมข้อมูล
depot = ("Depot โรงจัดการขยะ", 14.862939, 102.027903, 0.0)
locations = [depot] + [(name, lat, lon, demand) for name, lat, lon, demand in DATA_CAR15]

print("กำลังดึงข้อมูลจาก OSRM API... (อาจใช้เวลาสักครู่)")
df_dist = get_distance_matrix_osrm(locations)
nodes = [loc[0] for loc in locations]
df_dist.columns = nodes
df_dist.index = nodes

# บันทึกเป็น Excel
df_dist.to_excel("Distance_Matrix_OSRM_Car15.xlsx", sheet_name="OSRM Distance Matrix")
print("✅ บันทึกไฟล์สำเร็จ: Distance_Matrix_OSRM_Car15.xlsx")

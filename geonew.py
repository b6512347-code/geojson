# vrp_osrm_export.py
# รันด้วย: python vrp_osrm_export.py

import pandas as pd
import numpy as np
import requests
import time
import math
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule

# =====================================================================
# 1. ข้อมูลจุดเก็บขยะ
# =====================================================================
DEPOT = ("Depot โรงจัดการขยะ", 14.862939, 102.027903, 0.0)

DATA_CAR15 = [
    ("แปลงปลูกกัญชง (SUT SAND BOX ) จุดที่ 1", 14.862954, 102.032953, 0.2),
    ("แปลงปลูกกัญชง (SUT SAND BOX ) จุดที่ 2", 14.86123,  102.03206,  0.1),
    ("สถานีไฟฟ้า 2",                             14.86242,  102.037158, 0.1),
    ("ป้อมยามประตู 2",                            14.863081, 102.038789, 0.1),
    ("โรงพยาบาล มทส.-หอพักแพทย์",               14.863917, 102.033408, 0.7),
    ("โรงพยาบาล มทส.-ตึกโภชนาการ",              14.86446245, 102.0362589, 0.9),
    ("จุดรวมขยะโรงพยาบาล มทส.",                 14.86670704, 102.0321227, 4.5),
    ("โรงพยาบาล มทส.-ศูนย์มะเร็ง",              14.86883409, 102.0364834, 0.4),
    ("โบรอนจับยึดนิวตรอน",                       14.865746, 102.028094,  0.3),
    ("โรงเรียนสุรวิวัฒน์ จุดที่ 1",              14.876348, 102.029428,  0.3),
    ("โรงเรียนสุรวิวัฒน์ จุดที่ 2",              14.874892, 102.031966,  0.4),
    ("โรงเรียนสุรวิวัฒน์ จุดที่ 3",              14.875346, 102.030283,  0.1),
    ("อาคารขนส่ง จุดที่ 1",                       14.878016, 102.020915,  0.3),
    ("อาคารขนส่ง จุดที่ 2",                       14.87792,  102.0212,    0.2),
    ("อาคารขนส่ง จุดที่ 3",                       14.87789,  102.02183,   0.2),
    ("ศาลารอรถ-อาคารขนส่ง",                      14.877411, 102.022163,  0.2),
    ("อาคารปฏิบัติการด้านเทคโนโลยีดิจิทัล จุดที่ 1", 14.877321, 102.01468, 0.6),
    ("อาคารปฏิบัติการด้านเทคโนโลยีดิจิทัล จุดที่ 2", 14.878023, 102.014157, 0.6),
    ("ลานจอดรถบรรณสาร 2",                        14.87832422, 102.0153043, 0.3),
    ("อาคารบรรณสาร",                              14.87919113, 102.0163075, 0.4),
    ("ศาลารอรถบรรณสาร",                           14.879553, 102.015652,  0.2),
    ("โรงอาหารพราวแสดทอง",                       14.88090071, 102.0159358, 1.0),
    ("เรียนรวม2",                                  14.88115164, 102.0150913, 0.5),
    ("ร้านกาแฟ Faraday อาคารเรียนรวม 2",          14.881272, 102.01545,   0.1),
    ("ศาลารอรถเรียนรวม",                           14.881801, 102.0141,    0.3),
    ("เรียนรวม1 จุดที่ 1",                         14.882553, 102.015707,  0.4),
    ("เรียนรวม1 จุดที่ 2",                         14.881171, 102.017635,  0.4),
    ("เรียนรวม1 จุดที่ 3",                         14.88345,  102.014978,  0.4),
    ("ส่วนกิจการนักศึกษา 1",                      14.889581, 102.017098,  0.4),
    ("ศาลารอรถ S15",                               14.890647, 102.017672,  0.2),
    ("สุรนิเวศ15A",                                14.891409, 102.018186,  2.2),
    ("สุรนิเวศ15B",                                14.890995, 102.0184,    1.3),
    ("โรงอาหารดอนตะวัน",                          14.890347, 102.017391,  0.0),
    ("สุรนิเวศ1",                                  14.89502504, 102.0155654, 0.4),
    ("อาคารอเนกประสงค์ 1,2 จุดที่ 1",            14.89556,  102.01628,   0.3),
    ("อาคารอเนกประสงค์ 1,2 จุดที่ 2",            14.89541,  102.01655,   0.3),
    ("สุรนิเวศ2",                                  14.89628592, 102.015116, 0.4),
    ("สุรนิเวศ3",                                  14.8963972, 102.0146159, 0.1),
    ("สุรนิเวศ14 จุดที่ 1",                       14.89685326, 102.0155703, 0.4),
    ("สุรนิเวศ14 จุดที่ 2",                       14.89539094, 102.0163542, 0.4),
    ("มินิมาร์ทหญิง",                              14.896884, 102.015208,  0.5),
    ("ศาลารอรถโดยสาร (หน้า S4)",                  14.897199, 102.014156,  0.2),
    ("สุรนิเวศ4",                                  14.8967657, 102.0143455, 0.1),
    ("สุรนิเวศ5",                                  14.89749759, 102.0139198, 0.1),
    ("สุรนิเวศ6",                                  14.89793257, 102.0142487, 0.1),
    ("เฉลิมพระเกียรติ 80 พรรษา จุดที่ 1",        14.89364,  102.0147,    0.2),
    ("เฉลิมพระเกียรติ 80 พรรษา จุดที่ 2",        14.89299,  102.01464,   0.3),
    ("สุรนิเวศ 16",                                14.89281906, 102.0142977, 1.6),
    ("ศาลารอรถสุรนิเวศ 16",                       14.893392, 102.013644,  0.1),
    ("สุรนิเวศ 18",                                14.89288736, 102.0126027, 0.0),
    ("สุรนิเวศ 19",                                14.893961, 102.012518,  0.8),
    ("สุรนิเวศ 20",                                14.893998, 102.012597,  0.8),
    ("สุรนิเวศ 21",                                14.893148, 102.010705,  0.8),
    ("สุรนิเวศ 22",                                14.893192, 102.010723,  0.8),
    ("ลานศิลปะวัฒนธรรม",                          14.894734, 102.013625,  0.2),
    ("Learning Park (ตลาดนัด มทส. เก่า) จุดที่ 1", 14.89479, 102.01335,  0.2),
    ("Learning Park (ตลาดนัด มทส. เก่า) จุดที่ 2", 14.8948,  102.01291,  0.2),
    ("Learning Park (ตลาดนัด มทส. เก่า) จุดที่ 3", 14.89469, 102.01279,  0.2),
    ("หน่วยปฏิบัติการปฐมภูมิ รพ.มทส",            14.89506687, 102.0135736, 0.9),
    ("มินิมาร์ทฟาร์ม",                            14.89045129, 102.0051952, 0.3),
    ("สำนักงานฟาร์ม",                              14.88967,  102.00482,   0.1),
    ("เกษตรวิวัฒน์",                               14.88873446, 102.0044998, 0.6),
    ("โรงผลิตอาหารสัตว์",                         14.88939212, 102.0025861, 0.3),
    ("เอนกประสงค์สัตวศาสตร์",                     14.88921375, 102.002026,  0.3),
    ("โรงเลี้ยงสุกร",                              14.88767,  101.99604,   0.2),
    ("ประมง",                                       14.88215,  101.99936,   0.3),
    ("โรงผลิตนม",                                  14.88916,  102.00074,   0.3),
    ("เพาะเลี้ยงเนื้อเยื่อ",                       14.89077114, 102.0026328, 0.2),
    ("อาคารพืช / อาคารศูนย์ฯ ชีวมวล จุดที่ 1",   14.8919,   102.00288,   0.3),
    ("อาคารพืช / อาคารศูนย์ฯ ชีวมวล จุดที่ 2",   14.89195,  102.003,     0.2),
    ("อาคารจักรกล",                                14.89277,  102.00389,   0.4),
    ("สุขนิวาส1",                                  14.88606402, 102.008938, 0.6),
    ("สุขนิวาส2",                                  14.88555593, 102.0091163, 0.6),
    ("สุขนิวาส3",                                  14.88551,  102.01053,   0.5),
    ("สุขนิวาส4",                                  14.88472191, 102.009085, 0.6),
    ("สุขนิวาส5",                                  14.88429066, 102.01031,  0.5),
    ("ป้อมยาม สุขนิวาส จุดที่ 1",                 14.88531,  102.01012,   0.1),
    ("ป้อมยาม สุขนิวาส จุดที่ 2",                 14.88636,  102.00562,   0.1),
    ("สุขนิวาส6",                                  14.88578555, 102.0115002, 0.6),
    ("สุขนิวาส7",                                  14.88421227, 102.0118378, 0.6),
    ("สุขนิวาส8",                                  14.88624662, 102.0114149, 0.7),
    ("สวนร่วมใจ",                                  14.887106, 102.010209,  0.1),
    ("ป้อมยามประตู 3",                             14.87312,  102.00937,   0.1),
    ("บ้านพักซอยสุขวิถี 5 (ใช้ถังแบบมีล้อ)",     14.88764,  102.01004,   1.6),
    ("บ้านพักซอยสุขวิถี 3 (ใช้ถังแบบมีล้อ)",     14.88666,  102.00863,   1.8),
    ("บ้านพักซอยสุขวิถี 2 (ใช้ถังแบบมีล้อ)",     14.88626,  102.00765,   1.4),
]

DATA_CAR16 = [
    ("ภูมิทัศน์(ใหม่)",                            14.86903,  102.02135,   0.3),
    ("สวนพฤกษศาสตร์",                              14.86991,  102.022113,  0.3),
    ("อุทยานผีเสื้อ",                               14.871074, 102.022713,  0.3),
    ("ซินโครตรอน",                                  14.872731, 102.023232,  0.0),
    ("อาคารสุรพัฒน์ 2",                             14.8754,   102.02286,   0.2),
    ("อาคารสุรพัฒน์ 3",                             14.874078, 102.022316,  0.4),
    ("เรือนไทย",                                    14.875346, 102.021912,  0.3),
    ("อาคารสุรพัฒน์ 1 จุดที่ 1",                   14.87584,  102.02302,   0.2),
    ("อาคารสุรพัฒน์ 1 จุดที่ 2",                   14.87572,  102.02284,   0.2),
    ("เซเว่น-อีเลฟเว่น เทคโนธานี จุดที่ 1",       14.876072, 102.022745,  0.7),
    ("เซเว่น-อีเลฟเว่น เทคโนธานี จุดที่ 2",       14.876125, 102.022341,  0.4),
    ("ร้านคอกาแฟ ข้าง 7-11 เทคโนธานี",            14.876938, 102.022377,  0.1),
    ("อาคารสุรสัมนาคาร",                            14.876533, 102.024665,  0.0),
    ("โรงอาหารครัวท่านท้าว",                       14.877234, 102.02026,   0.2),
    ("อาคารวิจัยมันสำปะหลัง",                      14.874527, 102.020047,  0.2),
    ("หอดูดาว",                                     14.87414,  102.027598,  0.2),
    ("กาญจนาภิเษก",                                 14.873602, 102.026147,  0.5),
    ("กัญชา (สวนเกษตรอินทรีย์)",                   14.871656, 102.026088,  0.4),
    ("สุรนิทัศน์",                                   14.871756, 102.024782,  0.2),
    ("อุทยานวิทยาศาสตร์",                           14.87176,  102.01974,   0.3),
    ("อาคารงานภูมิทัศน์(เก่า)",                    14.87273,  102.01824,   0.1),
    ("อาคารทดลอง-รถไฟ",                            14.87422,  102.01791,   0.1),
    ("เครื่องมือฯ9",                                14.87516,  102.01613,   0.1),
    ("ร้านกาแฟเด็กชายนมสด อาคารเครื่องมือ 9",     14.87412,  102.01637,   0.1),
    ("เครื่องมือฯ11",                               14.87561,  102.01656,   0.1),
    ("เครื่องมือฯ12",                               14.873347, 102.01454,   0.0),
    ("ร้านกาแฟ Polar Polar อาคารเครื่องมือ 12",    14.87458,  102.01527,   0.1),
    ("เครื่องมือฯ 16 (ฝั่งตรงข้าม อาคารเครื่องมือ 12)", 14.87456, 102.01447, 0.2),
    ("เครื่องมือฯ10",                               14.876915, 102.015231,  0.5),
    ("เครื่องมือฯ6 และเทคโนวัสดุ",                 14.875158, 102.017524,  0.5),
    ("เครื่องมือฯ7 จุดที่ 1",                      14.874528, 102.021982,  0.4),
    ("เครื่องมือฯ7 จุดที่ 2",                      14.875195, 102.020605,  0.2),
    ("เครื่องมือฯ5",                                14.876734, 102.016839,  0.4),
    ("เครื่องมือฯ3",                                14.8768643, 102.01825,  0.4),
    ("เครื่องมือฯ2",                                14.876625, 102.01834,   0.4),
    ("ร้านกาแฟ Bus Stop หน้าอาคารเครื่องมือ 2",    14.87701,  102.01743,   0.1),
    ("เครื่องมือฯ4",                                14.877436, 102.016732,  0.4),
    ("เครื่องมือฯ1",                                14.877715, 102.017417,  0.5),
    ("อาคารวิชาการ1",                               14.878152, 102.018926,  0.1),
    ("อาคารวิจัย",                                  14.878043, 102.019042,  0.5),
    ("อาคารวิชาการ2 จุดที่ 1",                     14.87943,  102.02011,   0.5),
    ("อาคารวิชาการ2 จุดที่ 2",                     14.87946,  102.0196,    0.1),
    ("ร้านกาแฟ See-U Café อาคารวิชาการ 2",         14.87945,  102.02009,   0.1),
    ("โรงอาหารเด่นทองกวาว",                        14.879128, 102.020349,  0.1),
    ("อาคารบริหาร",                                 14.88013,  102.02042,   0.4),
    ("ศาลารอรถ-อาคารบริหาร",                       14.88131,  102.02124,   0.2),
    ("อาคารส่วนอาคารสถานที่",                       14.87975,  102.02205,   0.2),
    ("อาคารบริการสถานที่และกิจกรรม",               14.87978,  102.02124,   0.1),
    ("อาคารรักษาความปลอดภัย จุดที่ 1",             14.883761, 102.02421,   0.3),
    ("อาคารรักษาความปลอดภัย จุดที่ 2",             14.883344, 102.024802,  0.3),
    ("อาคารรักษาความปลอดภัย จุดที่ 3",             14.88327,  102.024581,  0.2),
    ("ร้านกาแฟ Amazon มทส.ประตู 1",                14.88361,  102.025,     0.1),
    ("ส่วนกิจการนักศึกษา 2",                       14.88656,  102.01711,   0.3),
    ("สนามเปตอง",                                   14.8852,   102.01685,   0.5),
    ("สนามกีฬาสุรเริงไชย จุดที่ 1",               14.886019, 102.01908,   0.2),
    ("สนามกีฬาสุรเริงไชย จุดที่ 2",               14.886347, 102.018367,  0.2),
    ("ร้านกาแฟดอยช้าง อาคารสุรเริงไชย",           14.88631,  102.0184,    0.1),
    ("กีฬาภิรมย์ สนามแบตมินตัน จุดที่ 1",         14.886362, 102.015663,  0.4),
    ("กีฬาภิรมย์ สนามแบตมินตัน จุดที่ 2",         14.886342, 102.01558,   0.3),
    ("สุรพลากรีฑาสถาน",                             14.887047, 102.017691,  0.4),
    ("สนามเทนนิส",                                  14.890428, 102.013754,  0.2),
    ("สุรนิเวศ7/อาคารบริการ",                       14.89713,  102.011243,  0.2),
    ("สุรนิเวศ8",                                   14.89674,  102.010574,  0.1),
    ("สุรนิเวศ9/อาคารบริการ",                       14.896464, 102.009932,  0.2),
    ("สุรนิเวศ10",                                  14.8965557, 102.00972,  0.2),
    ("สุรนิเวศ12/อาคารบริการ",                      14.897603, 102.010749,  0.3),
    ("สุรนิเวศ11",                                  14.89797,  102.011122,  0.3),
    ("ป้อมยามประตู4",                               14.901028, 102.009991,  0.3),
    ("โรงกรองน้ำประปา",                             14.900384, 102.009308,  0.3),
    ("อาคารหน่วยสิ่งแวดล้อม",                      14.90274,  102.009668,  0.2),
    ("ห้องประชุมรัชดาพัฒน์ (ของหน่วยสิ่งแวดล้อม)", 14.899768, 102.009965, 0.2),
    ("สุรนิเวศ13 EF",                               14.899166, 102.012239,  0.1),
    ("สุรนิเวศ13 AB",                               14.897875, 102.012431,  0.1),
    ("โรงอาหารกาสะลองคำ",                          14.896759, 102.012427,  0.5),
    ("ศาลารอรถศาลาลอย",                             14.896777, 102.012657,  0.3),
    ("เซเว่น-อีเลฟเว่น โรงอาหารกาสะลองคำ จุดที่ 1", 14.89652, 102.01277, 0.1),
    ("เซเว่น-อีเลฟเว่น โรงอาหารกาสะลองคำ จุดที่ 2", 14.89657, 102.01272, 0.2),
    ("ร้านกาแฟ K Coff ศาลาลอย",                    14.89626,  102.01295,   0.3),
    ("อ่างสุระ จุดที่ 1",                           14.87749,  102.01247,   0.1),
    ("อ่างสุระ จุดที่ 2",                           14.87685,  102.00889,   0.3),
    ("อ่างสุระ จุดที่ 3",                           14.88074,  102.01095,   0.4),
    ("สัตว์ทดลอง",                                  14.875691, 102.008908,  0.3),
    ("ศูนย์วิจัยเทคโนโลยีตัวอ่อน",                 14.877418, 102.007463,  0.3),
    ("งานพืชไร่และเมล็ดพันธุ์",                    14.87745,  102.00743,   0.2),
    ("โรงเชือดโควากิว (คอกขยะ)",                   14.87567,  102.00739,   0.0),
    ("สถานีไฟฟ้าย่อย",                              14.874195, 102.009501,  0.2),
    ("โรงประลองวัสดุขั้นสูง(หลังอาคารเครื่องมือ 16)", 14.87414, 102.01426, 0.2),
    ("บริษัทก่อสร้างพัฒนาวัสดุขั้นสูง(หลังอาคารเครื่องมือ 16)", 14.87188, 102.01456, 0.3),
    ("บ้านพักซอยสุขวิถี 1 (ใช้ถังแบบมีล้อ)",      14.88649,  102.00676,   4.3),
]

DATA_BOTH = DATA_CAR15 + DATA_CAR16

DATASETS = {
    "Car15": DATA_CAR15,
    "Car16": DATA_CAR16,
    "Both":  DATA_BOTH,
}

MAX_CAPACITY = 4.5
FUEL_ECONOMY = 5.0
EF_VALUE     = 2.70757
GWP_VALUE    = 1.0

# =====================================================================
# 2. OSRM Distance Matrix (ระยะทางถนนจริง)
# =====================================================================
def get_distance_matrix_osrm(locations, dataset_name=""):
    """ดึง Distance Matrix จาก OSRM API — ระยะทางถนนจริง (เมตร → กม.)"""
    N     = len(locations)
    CHUNK = 50
    D     = np.zeros((N, N))
    coords = [(item[2], item[1]) for item in locations]  # (lon, lat)

    total_calls = math.ceil(N / CHUNK) ** 2
    call_count  = 0

    print(f"\n  [{dataset_name}] กำลังดึงข้อมูลจาก OSRM API ({N} จุด, {total_calls} รอบ API)...")

    for i in range(0, N, CHUNK):
        for j in range(0, N, CHUNK):
            src = coords[i:i+CHUNK]
            dst = coords[j:j+CHUNK]
            combined  = src + dst
            coord_str = ";".join(f"{lon},{lat}" for lon, lat in combined)
            src_idx   = ";".join(str(x) for x in range(len(src)))
            dst_idx   = ";".join(str(x) for x in range(len(src), len(src)+len(dst)))

            url = (f"http://router.project-osrm.org/table/v1/driving/{coord_str}"
                   f"?sources={src_idx}&destinations={dst_idx}&annotations=distance")

            for attempt in range(3):
                try:
                    resp = requests.get(url, timeout=30)
                    data = resp.json()
                    if data.get("code") == "Ok":
                        D[i:i+len(src), j:j+len(dst)] = np.array(data["distances"])
                        break
                    else:
                        print(f"    ⚠️  OSRM Error: {data.get('message', 'Unknown')} — Retry {attempt+1}")
                        time.sleep(2)
                except Exception as e:
                    print(f"    ⚠️  Request Error: {e} — Retry {attempt+1}")
                    time.sleep(3)

            call_count += 1
            if call_count % 5 == 0:
                print(f"    Progress: {call_count}/{total_calls} รอบ")
            time.sleep(0.5)

    df = pd.DataFrame(D / 1000.0)  # แปลง เมตร → กิโลเมตร
    nodes = [loc[0] for loc in locations]
    df.columns = nodes
    df.index   = nodes
    return df

# =====================================================================
# 3. อัลกอริทึม VRP
# =====================================================================
def run_sequential(locations, demands, nodes, max_cap):
    routes, vols = [], []
    cur_r, cur_v = [], 0.0
    for item in locations[1:]:
        n, d = item[0], demands[item[0]]
        if cur_v + d > max_cap:
            if cur_r:
                routes.append(cur_r); vols.append(cur_v)
            cur_r, cur_v = [n], d
        else:
            cur_r.append(n); cur_v += d
    if cur_r:
        routes.append(cur_r); vols.append(cur_v)
    return routes, vols


def run_savings(df_dist, demands, nodes, max_cap):
    depot, customers = nodes[0], nodes[1:]
    savings = []
    for i in customers:
        for j in customers:
            if i != j:
                s = df_dist.loc[i, depot] + df_dist.loc[depot, j] - df_dist.loc[i, j]
                if s > 0:
                    savings.append((s, i, j))
    savings.sort(key=lambda x: x[0], reverse=True)

    routes = [[c] for c in customers]
    vols   = [demands[c] for c in customers]

    def get_idx(n):
        for k, r in enumerate(routes):
            if n in r: return k
        return -1

    for s, i, j in savings:
        ii, jj = get_idx(i), get_idx(j)
        if ii != jj and ii != -1 and jj != -1:
            if routes[ii][-1] == i and routes[jj][0] == j:
                if vols[ii] + vols[jj] <= max_cap:
                    routes[ii].extend(routes[jj])
                    vols[ii] += vols[jj]
                    routes.pop(jj); vols.pop(jj)
    return routes, vols


def run_balanced_savings(df_dist, demands, nodes, max_cap, num_vehicles=2):
    depot, customers = nodes[0], nodes[1:]
    total_demand = sum(demands[c] for c in customers)
    min_trips    = max(1, math.ceil(total_demand / max_cap))
    eff_vehicles = max(num_vehicles, min_trips)
    target_cap   = total_demand / eff_vehicles
    soft_cap     = max(target_cap * 1.15, max(demands[c] for c in customers))
    eff_capacity = min(soft_cap, max_cap)

    savings = []
    for i in customers:
        for j in customers:
            if i != j:
                s = df_dist.loc[i, depot] + df_dist.loc[depot, j] - df_dist.loc[i, j]
                if s > 0:
                    savings.append((s, i, j))
    savings.sort(key=lambda x: x[0], reverse=True)

    routes = [[c] for c in customers]
    vols   = [demands[c] for c in customers]

    def get_idx(n):
        for k, r in enumerate(routes):
            if n in r: return k
        return -1

    for s, i, j in savings:
        ii, jj = get_idx(i), get_idx(j)
        if ii != jj and ii != -1 and jj != -1:
            if routes[ii][-1] == i and routes[jj][0] == j:
                if vols[ii] + vols[jj] <= eff_capacity:
                    routes[ii].extend(routes[jj])
                    vols[ii] += vols[jj]
                    routes.pop(jj); vols.pop(jj)
    return routes, vols


def route_dist(route_names, depot_name, df_dist):
    full = [depot_name] + route_names + [depot_name]
    return sum(df_dist.loc[full[k], full[k+1]] for k in range(len(full)-1))


def two_opt(route_names, depot_name, df_dist, max_iter=300):
    best = route_names[:]
    for _ in range(max_iter):
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 2, len(best)):
                candidate = best[:i+1] + best[i+1:j+1][::-1] + best[j+1:]
                if route_dist(candidate, depot_name, df_dist) < route_dist(best, depot_name, df_dist):
                    best, improved = candidate, True
        if not improved:
            break
    return best


def run_sweep(locations, demands, nodes, max_cap, df_dist):
    depot_name = nodes[0]
    dlat, dlon = locations[0][1], locations[0][2]
    angles = []
    for item in locations[1:]:
        angle = math.degrees(math.atan2(item[1]-dlat, item[2]-dlon)) % 360
        angles.append({"node": item[0], "angle": angle, "vol": demands[item[0]]})
    angles.sort(key=lambda x: x["angle"])

    routes, vols = [], []
    cur_r, cur_v = [], 0.0
    for c in angles:
        if cur_v + c["vol"] > max_cap:
            if cur_r:
                routes.append(cur_r); vols.append(cur_v)
            cur_r, cur_v = [c["node"]], c["vol"]
        else:
            cur_r.append(c["node"]); cur_v += c["vol"]
    if cur_r:
        routes.append(cur_r); vols.append(cur_v)

    routes = [two_opt(r, depot_name, df_dist) for r in routes]
    return routes, vols


def run_balanced_sweep(locations, demands, nodes, max_cap, df_dist):
    depot_name = nodes[0]
    dlat, dlon = locations[0][1], locations[0][2]
    angles = []
    for item in locations[1:]:
        angle = math.degrees(math.atan2(item[1]-dlat, item[2]-dlon)) % 360
        angles.append({"node": item[0], "angle": angle, "vol": demands[item[0]]})
    angles.sort(key=lambda x: x["angle"])

    total_demand = sum(c["vol"] for c in angles)
    num_routes   = max(1, math.ceil(total_demand / max_cap))
    target_cap   = total_demand / num_routes

    routes, vols = [], []
    cur_r, cur_v = [], 0.0
    for c in angles:
        if cur_v + c["vol"] > max_cap:
            routes.append(cur_r); vols.append(cur_v)
            cur_r, cur_v = [c["node"]], c["vol"]
        elif cur_v + c["vol"] > target_cap and cur_v >= target_cap * 0.75:
            routes.append(cur_r); vols.append(cur_v)
            cur_r, cur_v = [c["node"]], c["vol"]
        else:
            cur_r.append(c["node"]); cur_v += c["vol"]
    if cur_r:
        routes.append(cur_r); vols.append(cur_v)

    routes = [two_opt(r, depot_name, df_dist) for r in routes]
    return routes, vols

# =====================================================================
# 4. สร้าง Excel
# =====================================================================
HEADER_BLUE  = "1F4E78"
HEADER_GREEN = "375623"
HEADER_ORANGE= "C55A11"
HEADER_TEAL  = "006B6B"
WHITE_TEXT   = "FFFFFF"

def make_header(cell, text, bg_color, font_color=WHITE_TEXT, size=11, bold=True):
    cell.value = text
    cell.font  = Font(bold=bold, color=font_color, size=size,
                      name="TH Sarabun New" if False else "Calibri")
    cell.fill  = PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

def auto_width(ws, min_w=8, max_w=40):
    for col in ws.columns:
        max_len = max_w
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                val_len = len(str(cell.value)) if cell.value else 0
                if val_len > max_len:
                    max_len = val_len
            except:
                pass
        ws.column_dimensions[col_letter].width = min(max(max_len * 1.1, min_w), max_w)


def build_excel(all_results):
    """
    all_results = {
      "Car15": { "Sequential Route": (df_dist, routes, vols, dists, nodes, demands, locations), ... },
      "Car16": { ... },
      "Both":  { ... },
    }
    """
    wb = Workbook()
    wb.remove(wb.active)

    algo_names = [
        "Sequential Route",
        "Clarke-Wright Savings",
        "Balanced Clarke-Wright Savings",
        "Sweep Algorithm",
        "Balanced Sweep",
    ]
    ds_names = ["Car15", "Car16", "Both"]

    # ========== Sheet 1: Distance Matrix (แยกตาม Dataset) ==========
    for ds_name, algo_dict in all_results.items():
        # ใช้ df_dist จาก algorithm แรกที่มี (ทุก algo ใช้ df_dist เดียวกัน)
        first_algo = list(algo_dict.values())[0]
        df_dist, _, _, _, nodes, _, _ = first_algo

        ws = wb.create_sheet(f"DM_{ds_name}")
        ws.sheet_properties.tabColor = "4472C4" if ds_name=="Car15" else ("70AD47" if ds_name=="Car16" else "ED7D31")

        # Title
        title = f"Distance Matrix (OSRM API, กม.) — {ds_name}  |  {len(nodes)} Nodes"
        ws.merge_cells(f"A1:{get_column_letter(len(nodes)+1)}1")
        ws["A1"].value = title
        ws["A1"].font  = Font(bold=True, size=13, color=WHITE_TEXT)
        ws["A1"].fill  = PatternFill(start_color=HEADER_BLUE, end_color=HEADER_BLUE, fill_type="solid")
        ws["A1"].alignment = Alignment(horizontal="center")
        ws.row_dimensions[1].height = 22

        # Header row (col names)
        ws.cell(row=2, column=1).value = "From \\ To"
        ws.cell(row=2, column=1).font  = Font(bold=True, color=WHITE_TEXT)
        ws.cell(row=2, column=1).fill  = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
        ws.cell(row=2, column=1).alignment = Alignment(horizontal="center", wrap_text=True)

        for col_idx, node in enumerate(nodes, 2):
            c = ws.cell(row=2, column=col_idx, value=node)
            c.font = Font(bold=True, color=WHITE_TEXT, size=9)
            c.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
            c.alignment = Alignment(horizontal="center", wrap_text=True)

        # Data + row labels
        max_val = df_dist.max().max()
        for r_idx, node_i in enumerate(nodes):
            row_num = r_idx + 3
            # Row label
            lc = ws.cell(row=row_num, column=1, value=node_i)
            lc.font  = Font(bold=True, size=9)
            lc.fill  = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            lc.alignment = Alignment(wrap_text=True)

            for c_idx, node_j in enumerate(nodes):
                val  = float(df_dist.loc[node_i, node_j])
                cell = ws.cell(row=row_num, column=c_idx+2, value=round(val, 4))
                cell.number_format = "0.0000"
                cell.alignment = Alignment(horizontal="center")

                if r_idx != c_idx and max_val > 0:
                    ratio = val / max_val
                    if ratio < 0.25:
                        cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                    elif ratio < 0.50:
                        cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
                    elif ratio < 0.75:
                        cell.fill = PatternFill(start_color="FFCC99", end_color="FFCC99", fill_type="solid")
                    else:
                        cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

        ws.freeze_panes = "B3"
        ws.column_dimensions["A"].width = 32
        for col in range(2, len(nodes)+2):
            ws.column_dimensions[get_column_letter(col)].width = 10

    # ========== Sheet 2: Route Summary (ทุก Algorithm × Dataset) ==========
    ws_sum = wb.create_sheet("Route Summary")
    ws_sum.sheet_properties.tabColor = "70AD47"

    make_header(ws_sum["A1"], "สรุปผลการจัดเส้นทาง (OSRM API)", HEADER_BLUE, size=14)
    ws_sum.merge_cells("A1:K1")
    ws_sum.row_dimensions[1].height = 24

    sum_headers = ["Dataset", "Algorithm", "จุดเก็บขยะ", "รอบวิ่ง",
                   "ปริมาตรรวม (ลบ.ม.)", "ระยะทางรวม (กม.)",
                   "เชื้อเพลิง (ลิตร)", "CO₂e (kg)",
                   "Capacity/รถ (ลบ.ม.)", "เชื้อเพลิง/รถ (ลิตร/กม.)", "หมายเหตุ"]
    for col_idx, h in enumerate(sum_headers, 1):
        make_header(ws_sum.cell(row=2, column=col_idx), h, HEADER_GREEN, size=10)

    row = 3
    for ds_name in ds_names:
        algo_dict = all_results.get(ds_name, {})
        for algo_name in algo_names:
            if algo_name not in algo_dict:
                continue
            df_dist, routes, vols, dists, nodes, demands, locations = algo_dict[algo_name]
            total_dist = sum(dists)
            total_vol  = sum(vols)
            fuel       = total_dist / FUEL_ECONOMY
            carbon     = fuel * EF_VALUE * GWP_VALUE

            data_row = [
                ds_name, algo_name,
                len(nodes)-1, len(routes),
                round(total_vol, 2), round(total_dist, 4),
                round(fuel, 4), round(carbon, 4),
                MAX_CAPACITY,
                round(total_dist / FUEL_ECONOMY / max(len(nodes)-1, 1), 4),
                "OSRM API (ถนนจริง)"
            ]
            for col_idx, val in enumerate(data_row, 1):
                c = ws_sum.cell(row=row, column=col_idx, value=val)
                c.alignment = Alignment(horizontal="center")
                if col_idx in [5, 6, 7, 8]:
                    c.number_format = "0.0000"
                # สลับสีแถว
                if row % 2 == 0:
                    c.fill = PatternFill(start_color="EBF3FB", end_color="EBF3FB", fill_type="solid")
            row += 1

    auto_width(ws_sum)

    # ========== Sheets 3+: Trip Details (แต่ละ Dataset × Algorithm) ==========
    COLOR_MAP = {
        "Sequential Route":                ("FFF2CC", "D6B656"),
        "Clarke-Wright Savings":           ("E2EFDA", "70AD47"),
        "Balanced Clarke-Wright Savings":  ("DDEEFF", "2E75B6"),
        "Sweep Algorithm":                 ("FCE4D6", "C55A11"),
        "Balanced Sweep":                  ("EAD1DC", "8E4585"),
    }

    for ds_name in ds_names:
        algo_dict = all_results.get(ds_name, {})
        for algo_name in algo_names:
            if algo_name not in algo_dict:
                continue
            df_dist, routes, vols, dists, nodes, demands, locations = algo_dict[algo_name]

            # ชื่อ sheet สั้นลง
            short_algo = {
                "Sequential Route":                "Sequential",
                "Clarke-Wright Savings":           "CW_Savings",
                "Balanced Clarke-Wright Savings":  "Balanced_CW",
                "Sweep Algorithm":                 "Sweep",
                "Balanced Sweep":                  "Balanced_Sweep",
            }
            sheet_name = f"{ds_name}_{short_algo[algo_name]}"
            ws = wb.create_sheet(sheet_name)

            light_bg, dark_bg = COLOR_MAP.get(algo_name, ("F2F2F2", "808080"))
            ws.sheet_properties.tabColor = dark_bg

            # Title
            title = f"{algo_name}  |  Dataset: {ds_name}  |  OSRM API"
            ws.merge_cells("A1:L1")
            ws["A1"].value = title
            ws["A1"].font  = Font(bold=True, size=12, color=WHITE_TEXT)
            ws["A1"].fill  = PatternFill(start_color=HEADER_BLUE, end_color=HEADER_BLUE, fill_type="solid")
            ws["A1"].alignment = Alignment(horizontal="center")

            # Summary row
            total_dist = sum(dists)
            total_vol  = sum(vols)
            fuel       = total_dist / FUEL_ECONOMY
            carbon     = fuel * EF_VALUE * GWP_VALUE

            ws.merge_cells("A2:B2"); ws["A2"].value = f"จุดเก็บขยะ: {len(nodes)-1}"
            ws.merge_cells("C2:D2"); ws["C2"].value = f"รอบวิ่ง: {len(routes)}"
            ws.merge_cells("E2:F2"); ws["E2"].value = f"ปริมาตรรวม: {total_vol:.2f} ลบ.ม."
            ws.merge_cells("G2:H2"); ws["G2"].value = f"ระยะทางรวม: {total_dist:.4f} กม."
            ws.merge_cells("I2:J2"); ws["I2"].value = f"เชื้อเพลิง: {fuel:.4f} ลิตร"
            ws.merge_cells("K2:L2"); ws["K2"].value = f"CO₂e: {carbon:.4f} kg"
            for col in range(1, 13):
                c = ws.cell(row=2, column=col)
                c.font = Font(bold=True, size=10)
                c.fill = PatternFill(start_color=light_bg, end_color=light_bg, fill_type="solid")

            # Section A: Trip Summary
            ws["A4"].value = "▶ สรุปรอบวิ่ง"
            ws["A4"].font  = Font(bold=True, size=11, color=WHITE_TEXT)
            ws["A4"].fill  = PatternFill(start_color=dark_bg, end_color=dark_bg, fill_type="solid")
            ws.merge_cells("A4:L4")

            trip_sum_headers = ["Trip#", "จำนวนจุด", "ปริมาตร (ลบ.ม.)", "ระยะทาง (กม.)",
                                 "% ใช้ความจุ", "เชื้อเพลิง (ลิตร)", "CO₂e (kg)", "เส้นทาง"]
            for col_idx, h in enumerate(trip_sum_headers, 1):
                make_header(ws.cell(row=5, column=col_idx), h, HEADER_TEAL, size=10)

            # Merge เส้นทาง cell
            ws.merge_cells(f"H5:L5")

            data_row = 6
            for t_idx, (route, vol, dist) in enumerate(zip(routes, vols, dists), 1):
                route_str = f"{nodes[0]} → {' → '.join(route)} → {nodes[0]}"
                fuel_t    = dist / FUEL_ECONOMY
                carbon_t  = fuel_t * EF_VALUE * GWP_VALUE
                load_pct  = vol / MAX_CAPACITY * 100

                row_data = [t_idx, len(route), round(vol, 2), round(dist, 4),
                            round(load_pct, 1), round(fuel_t, 4), round(carbon_t, 4), route_str]

                bg = light_bg if t_idx % 2 == 0 else "FFFFFF"
                for col_idx, val in enumerate(row_data, 1):
                    c = ws.cell(row=data_row, column=col_idx, value=val)
                    c.alignment = Alignment(horizontal="center" if col_idx < 8 else "left",
                                            wrap_text=(col_idx==8))
                    c.fill = PatternFill(start_color=bg, end_color=bg, fill_type="solid")
                    if col_idx in [3, 4, 6, 7]:
                        c.number_format = "0.0000"
                    if col_idx == 5:
                        c.number_format = '0.0"%"'
                # Merge เส้นทาง
                ws.merge_cells(f"H{data_row}:L{data_row}")
                data_row += 1

            # Total row
            total_row = data_row
            ws.cell(row=total_row, column=1, value="TOTAL").font = Font(bold=True)
            ws.cell(row=total_row, column=2, value=len(nodes)-1).font = Font(bold=True)
            ws.cell(row=total_row, column=3, value=round(total_vol, 2)).number_format = "0.0000"
            ws.cell(row=total_row, column=4, value=round(total_dist, 4)).number_format = "0.0000"
            ws.cell(row=total_row, column=6, value=round(fuel, 4)).number_format = "0.0000"
            ws.cell(row=total_row, column=7, value=round(carbon, 4)).number_format = "0.0000"
            for col in range(1, 13):
                c = ws.cell(row=total_row, column=col)
                c.font = Font(bold=True)
                c.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
            ws.merge_cells(f"H{total_row}:L{total_row}")
            data_row += 2

            # Section B: Location Details
            ws.cell(row=data_row, column=1).value = "▶ รายละเอียดจุดเก็บขยะแต่ละจุด"
            ws.cell(row=data_row, column=1).font  = Font(bold=True, size=11, color=WHITE_TEXT)
            ws.cell(row=data_row, column=1).fill  = PatternFill(start_color=dark_bg, end_color=dark_bg, fill_type="solid")
            ws.merge_cells(f"A{data_row}:L{data_row}")
            data_row += 1

            det_headers = ["Trip#", "ลำดับในเที่ยว", "ชื่อจุด",
                           "Demand (ลบ.ม.)", "Lat", "Lon",
                           "ระยะจาก Depot (กม.)", "ระยะจากจุดก่อน (กม.)"]
            for col_idx, h in enumerate(det_headers, 1):
                make_header(ws.cell(row=data_row, column=col_idx), h, "4472C4", size=10)
            data_row += 1

            loc_dict = {item[0]: item for item in locations}

            for t_idx, route in enumerate(routes, 1):
                full_route = [nodes[0]] + route + [nodes[0]]
                for seq, stop in enumerate(route, 1):
                    item   = loc_dict.get(stop, (stop, 0, 0, 0))
                    d_from_depot  = float(df_dist.loc[nodes[0], stop])
                    if seq == 1:
                        d_from_prev = d_from_depot
                    else:
                        d_from_prev = float(df_dist.loc[full_route[seq-1], stop])

                    row_data = [t_idx, seq, stop,
                                item[3], round(item[1], 6), round(item[2], 6),
                                round(d_from_depot, 4), round(d_from_prev, 4)]
                    bg = light_bg if t_idx % 2 == 0 else "FFFFFF"
                    for col_idx, val in enumerate(row_data, 1):
                        c = ws.cell(row=data_row, column=col_idx, value=val)
                        c.alignment = Alignment(horizontal="center" if col_idx != 3 else "left")
                        c.fill = PatternFill(start_color=bg, end_color=bg, fill_type="solid")
                        if col_idx in [7, 8]:
                            c.number_format = "0.0000"
                    data_row += 1

            ws.column_dimensions["A"].width = 8
            ws.column_dimensions["B"].width = 12
            ws.column_dimensions["C"].width = 35
            ws.column_dimensions["D"].width = 14
            ws.column_dimensions["E"].width = 12
            ws.column_dimensions["F"].width = 12
            ws.column_dimensions["G"].width = 18
            ws.column_dimensions["H"].width = 20
            for col in range(9, 13):
                ws.column_dimensions[get_column_letter(col)].width = 18
            ws.freeze_panes = "A6"

    # ========== Sheet สุดท้าย: เปรียบเทียบ ==========
    ws_cmp = wb.create_sheet("เปรียบเทียบทุก Algorithm")
    ws_cmp.sheet_properties.tabColor = "FF0000"

    make_header(ws_cmp["A1"], "สรุปเปรียบเทียบ Algorithm ทั้งหมด (OSRM API)", HEADER_BLUE, size=14)
    ws_cmp.merge_cells("A1:H1")

    cmp_headers = ["Dataset", "Algorithm", "จุด", "รอบวิ่ง",
                   "ปริมาตรรวม (ลบ.ม.)", "ระยะทางรวม (กม.)",
                   "เชื้อเพลิง (ลิตร)", "CO₂e (kg)"]
    for col_idx, h in enumerate(cmp_headers, 1):
        make_header(ws_cmp.cell(row=2, column=col_idx), h, HEADER_GREEN, size=10)

    row = 3
    for ds_name in ds_names:
        algo_dict = all_results.get(ds_name, {})
        for algo_name in algo_names:
            if algo_name not in algo_dict:
                continue
            df_dist, routes, vols, dists, nodes, demands, locations = algo_dict[algo_name]
            total_dist = sum(dists)
            total_vol  = sum(vols)
            fuel       = total_dist / FUEL_ECONOMY
            carbon     = fuel * EF_VALUE * GWP_VALUE

            row_data = [ds_name, algo_name, len(nodes)-1, len(routes),
                        round(total_vol, 2), round(total_dist, 4),
                        round(fuel, 4), round(carbon, 4)]
            for col_idx, val in enumerate(row_data, 1):
                c = ws_cmp.cell(row=row, column=col_idx, value=val)
                c.alignment = Alignment(horizontal="center")
                if col_idx in [5, 6, 7, 8]:
                    c.number_format = "0.0000"
                if row % 2 == 0:
                    c.fill = PatternFill(start_color="EBF3FB", end_color="EBF3FB", fill_type="solid")
            row += 1

    auto_width(ws_cmp)

    return wb

# =====================================================================
# 5. Main
# =====================================================================
def main():
    print("=" * 60)
    print("  VRP Distance Matrix + Route Export (OSRM API)")
    print("  ระยะทางถนนจริง ≈ Google Maps")
    print("=" * 60)

    all_results = {}

    for ds_name, raw_data in DATASETS.items():
        print(f"\n{'='*50}")
        print(f"  Dataset: {ds_name} ({len(raw_data)} จุด + 1 Depot)")
        print(f"{'='*50}")

        # เตรียมข้อมูล
        locations = [DEPOT] + [tuple(x) for x in raw_data]
        nodes     = [loc[0] for loc in locations]
        demands   = {loc[0]: loc[3] for loc in locations}

        # ดึง Distance Matrix ครั้งเดียว (ใช้ร่วมกันทุก Algorithm)
        df_dist = get_distance_matrix_osrm(locations, ds_name)
        print(f"  ✅ Distance Matrix สำเร็จ! ({len(nodes)}×{len(nodes)})")

        all_results[ds_name] = {}

        algorithms = {
            "Sequential Route":                lambda: run_sequential(locations, demands, nodes, MAX_CAPACITY),
            "Clarke-Wright Savings":           lambda: run_savings(df_dist, demands, nodes, MAX_CAPACITY),
            "Balanced Clarke-Wright Savings":  lambda: run_balanced_savings(df_dist, demands, nodes, MAX_CAPACITY, 2),
            "Sweep Algorithm":                 lambda: run_sweep(locations, demands, nodes, MAX_CAPACITY, df_dist),
            "Balanced Sweep":                  lambda: run_balanced_sweep(locations, demands, nodes, MAX_CAPACITY, df_dist),
        }

        for algo_name, algo_func in algorithms.items():
            print(f"  🔄  รัน {algo_name}...", end=" ")
            routes, vols = algo_func()

            # คำนวณระยะทางแต่ละรอบ (ใช้ OSRM distances)
            dists = []
            for r in routes:
                full = [nodes[0]] + r + [nodes[0]]
                d = sum(float(df_dist.loc[full[k], full[k+1]]) for k in range(len(full)-1))
                dists.append(d)

            total = sum(dists)
            print(f"✅ {len(routes)} รอบ | {total:.2f} กม.")

            all_results[ds_name][algo_name] = (
                df_dist, routes, vols, dists, nodes, demands, locations
            )

    # สร้าง Excel
    print(f"\n{'='*50}")
    print("  📦  กำลังสร้างไฟล์ Excel...")
    wb = build_excel(all_results)

    output_file = "VRP_OSRM_AllAlgorithms.xlsx"
    wb.save(output_file)
    print(f"  ✅  บันทึกสำเร็จ: {output_file}")
    print(f"\n  📊  โครงสร้าง Excel:")
    print(f"      • DM_Car15        — Distance Matrix รถคัน 15 (OSRM)")
    print(f"      • DM_Car16        — Distance Matrix รถคัน 16 (OSRM)")
    print(f"      • DM_Both         — Distance Matrix รวม (OSRM)")
    print(f"      • Route Summary   — สรุปทุก Algorithm")
    print(f"      • Car15_Sequential, Car15_CW_Savings, ...  (5 sheets × 3 datasets = 15 sheets)")
    print(f"      • เปรียบเทียบทุก Algorithm — ตารางสรุปสุดท้าย")
    print("=" * 60)


if __name__ == "__main__":
    main()

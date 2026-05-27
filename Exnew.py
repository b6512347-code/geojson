import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import math
import folium
from folium import plugins
from streamlit_folium import st_folium
import urllib.request
import os
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import networkx as nx
import xml.etree.ElementTree as ET
import io

st.set_page_config(page_title="Balanced VRP Routing System", layout="wide")

# =====================================================================
# 1. ฟอนต์ภาษาไทย
# =====================================================================
@st.cache_resource
def setup_thai_font():
    font_url = "https://github.com/Phonbopit/sarabun-webfont/raw/master/fonts/thsarabunnew-webfont.ttf"
    font_path = "thsarabunnew-webfont.ttf"
    if not os.path.exists(font_path):
        urllib.request.urlretrieve(font_url, font_path)
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'TH Sarabun New'
    plt.rcParams['axes.unicode_minus'] = False

setup_thai_font()

# =====================================================================
# 2. ข้อมูลจุดเก็บขยะแยกตามรถ
# =====================================================================
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

DATASET_MAP = {
    "🚛 รถคัน 15": DATA_CAR15,
    "🚛 รถคัน 16": DATA_CAR16,
    "🚛🚛 รวมทั้ง 2 คัน": DATA_BOTH,
}

# =====================================================================
# 3. OSM Graph
# =====================================================================
def haversine_dist(lon1, lat1, lon2, lat2):
    R = 6371.0
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * (2 * math.asin(math.sqrt(a)))

@st.cache_data
def build_osm_graph_manual(osm_string_data):
    G = nx.Graph()
    try:
        tree = ET.parse(io.StringIO(osm_string_data))
        root = tree.getroot()
        osm_nodes = {}
        for node in root.findall('node'):
            n_id = node.get('id')
            lat, lon = float(node.get('lat')), float(node.get('lon'))
            osm_nodes[n_id] = (lat, lon)
            G.add_node(n_id, x=lon, y=lat)
        for way in root.findall('way'):
            way_nodes = [nd.get('ref') for nd in way.findall('nd')]
            for i in range(len(way_nodes) - 1):
                n1, n2 = way_nodes[i], way_nodes[i+1]
                if n1 in osm_nodes and n2 in osm_nodes:
                    lat1, lon1 = osm_nodes[n1]
                    lat2, lon2 = osm_nodes[n2]
                    G.add_edge(n1, n2, weight=haversine_dist(lon1, lat1, lon2, lat2))
        return G
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการแปลไฟล์ .osm: {e}")
        return None

def get_nearest_node(G, lon, lat):
    nearest_n, min_d = None, float('inf')
    for n in G.nodes:
        d = haversine_dist(lon, lat, G.nodes[n]['x'], G.nodes[n]['y'])
        if d < min_d:
            min_d, nearest_n = d, n
    return nearest_n

def get_distance_matrix_osm(G, locations):
    N = len(locations)
    D = np.zeros((N, N))
    snapped = [get_nearest_node(G, item[2], item[1]) for item in locations]
    for i in range(N):
        for j in range(N):
            if i != j:
                try:
                    D[i][j] = nx.shortest_path_length(
                        G, source=snapped[i], target=snapped[j], weight='weight')
                except nx.NetworkXNoPath:
                    D[i][j] = haversine_dist(
                        locations[i][2], locations[i][1],
                        locations[j][2], locations[j][1])
    return pd.DataFrame(D)

# =====================================================================
# 4. OSRM Distance Matrix
# =====================================================================
@st.cache_data(show_spinner=False)
def get_distance_matrix_osrm(locations):
    N, CHUNK = len(locations), 50
    D = np.zeros((N, N))
    coords = [(item[2], item[1]) for item in locations]
    for i in range(0, N, CHUNK):
        for j in range(0, N, CHUNK):
            src, dst = coords[i:i+CHUNK], coords[j:j+CHUNK]
            combined = src + dst
            coord_str = ";".join(f"{lon},{lat}" for lon, lat in combined)
            src_idx = ";".join(str(x) for x in range(len(src)))
            dst_idx = ";".join(str(x) for x in range(len(src), len(src)+len(dst)))
            url = (f"http://router.project-osrm.org/table/v1/driving/{coord_str}"
                   f"?sources={src_idx}&destinations={dst_idx}&annotations=distance")
            try:
                resp = requests.get(url, timeout=10)
                data = resp.json()
                if data.get("code") == "Ok":
                    D[i:i+len(src), j:j+len(dst)] = np.array(data["distances"])
            except Exception:
                pass
            time.sleep(0.5)
    return pd.DataFrame(D) / 1000.0

# =====================================================================
# 5. อัลกอริทึม
# =====================================================================
def run_sequential_algorithm(locations, demands, nodes, max_capacity):
    routes, route_vols   = [], []
    current_route, current_vol = [], 0.0
    for item in locations[1:]:
        name   = item[0]
        demand = demands[name]
        if current_vol + demand > max_capacity:
            if current_route:
                routes.append(current_route)
                route_vols.append(current_vol)
            current_route = [name]
            current_vol   = demand
        else:
            current_route.append(name)
            current_vol  += demand
    if current_route:
        routes.append(current_route)
        route_vols.append(current_vol)
    return routes, route_vols


def run_savings_algorithm(df_dist, demands, nodes, max_capacity):
    depot, customers = nodes[0], nodes[1:]
    savings = []
    for i in customers:
        for j in customers:
            if i != j:
                s = df_dist.loc[i, depot] + df_dist.loc[depot, j] - df_dist.loc[i, j]
                if s > 0:
                    savings.append((s, i, j))
    savings.sort(key=lambda x: x[0], reverse=True)
    routes     = [[c] for c in customers]
    route_vols = [demands[c] for c in customers]

    def get_idx(node):
        for k, r in enumerate(routes):
            if node in r: return k
        return -1

    for s, i, j in savings:
        ii, jj = get_idx(i), get_idx(j)
        if ii != jj and ii != -1 and jj != -1:
            if routes[ii][-1] == i and routes[jj][0] == j:
                if route_vols[ii] + route_vols[jj] <= max_capacity:
                    routes[ii].extend(routes[jj])
                    route_vols[ii] += route_vols[jj]
                    routes.pop(jj); route_vols.pop(jj)
    return routes, route_vols


def run_balanced_savings_algorithm(df_dist, demands, nodes, max_capacity, num_vehicles):
    depot, customers = nodes[0], nodes[1:]
    total_demand  = sum(demands[c] for c in customers)
    min_trips     = max(1, math.ceil(total_demand / max_capacity))
    eff_vehicles  = max(num_vehicles, min_trips)
    target_cap    = total_demand / eff_vehicles
    soft_cap      = max(target_cap * 1.15, max(demands[c] for c in customers))
    eff_capacity  = min(soft_cap, max_capacity)

    savings = []
    for i in customers:
        for j in customers:
            if i != j:
                s = df_dist.loc[i, depot] + df_dist.loc[depot, j] - df_dist.loc[i, j]
                if s > 0:
                    savings.append((s, i, j))
    savings.sort(key=lambda x: x[0], reverse=True)
    routes     = [[c] for c in customers]
    route_vols = [demands[c] for c in customers]

    def get_idx(node):
        for k, r in enumerate(routes):
            if node in r: return k
        return -1

    for s, i, j in savings:
        ii, jj = get_idx(i), get_idx(j)
        if ii != jj and ii != -1 and jj != -1:
            if routes[ii][-1] == i and routes[jj][0] == j:
                if route_vols[ii] + route_vols[jj] <= eff_capacity:
                    routes[ii].extend(routes[jj])
                    route_vols[ii] += route_vols[jj]
                    routes.pop(jj); route_vols.pop(jj)
    return routes, route_vols


def _route_dist_by_name(route_names, depot_name, df_dist):
    full = [depot_name] + route_names + [depot_name]
    return sum(df_dist.loc[full[k], full[k+1]] for k in range(len(full) - 1))


def _two_opt(route_names, depot_name, df_dist, max_iter=500):
    best = route_names[:]
    for _ in range(max_iter):
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 2, len(best)):
                candidate = best[:i+1] + best[i+1:j+1][::-1] + best[j+1:]
                if (_route_dist_by_name(candidate, depot_name, df_dist)
                        < _route_dist_by_name(best, depot_name, df_dist)):
                    best, improved = candidate, True
        if not improved:
            break
    return best


def run_sweep_algorithm(locations, demands, nodes, max_capacity, df_dist):
    depot_name = nodes[0]
    depot_lat, depot_lon = locations[0][1], locations[0][2]
    customer_angles = []
    for item in locations[1:]:
        name, lat, lon = item[0], item[1], item[2]
        angle = math.degrees(math.atan2(lat - depot_lat, lon - depot_lon)) % 360
        customer_angles.append({"node": name, "angle": angle, "vol": demands[name]})
    customer_angles.sort(key=lambda x: x["angle"])

    routes, route_vols   = [], []
    current_route, current_vol = [], 0.0
    for c in customer_angles:
        if current_vol + c["vol"] > max_capacity:
            if current_route:
                routes.append(current_route); route_vols.append(current_vol)
            current_route, current_vol = [c["node"]], c["vol"]
        else:
            current_route.append(c["node"]); current_vol += c["vol"]
    if current_route:
        routes.append(current_route); route_vols.append(current_vol)

    routes = [_two_opt(r, depot_name, df_dist) for r in routes]
    return routes, route_vols


def run_balanced_sweep_algorithm(locations, demands, nodes, max_capacity, df_dist):
    depot_name = nodes[0]
    depot_lat, depot_lon = locations[0][1], locations[0][2]
    customer_angles = []
    for item in locations[1:]:
        name, lat, lon = item[0], item[1], item[2]
        angle = math.degrees(math.atan2(lat - depot_lat, lon - depot_lon)) % 360
        customer_angles.append({"node": name, "angle": angle, "vol": demands[name]})
    customer_angles.sort(key=lambda x: x["angle"])

    total_demand = sum(c["vol"] for c in customer_angles)
    num_routes   = max(1, math.ceil(total_demand / max_capacity))
    target_cap   = total_demand / num_routes

    routes, route_vols   = [], []
    current_route, current_vol = [], 0.0
    for c in customer_angles:
        if current_vol + c["vol"] > max_capacity:
            routes.append(current_route); route_vols.append(current_vol)
            current_route, current_vol = [c["node"]], c["vol"]
        elif current_vol + c["vol"] > target_cap and current_vol >= target_cap * 0.75:
            routes.append(current_route); route_vols.append(current_vol)
            current_route, current_vol = [c["node"]], c["vol"]
        else:
            current_route.append(c["node"]); current_vol += c["vol"]
    if current_route:
        routes.append(current_route); route_vols.append(current_vol)

    routes = [_two_opt(r, depot_name, df_dist) for r in routes]
    return routes, route_vols


# =====================================================================
# 6. ฟังก์ชันคำนวณเมตริก Benchmark
# =====================================================================
def compute_route_distances(routes, nodes, df_dist):
    dists = []
    for r in routes:
        full = [nodes[0]] + r + [nodes[0]]
        dists.append(sum(df_dist.loc[full[k], full[k+1]] for k in range(len(full)-1)))
    return dists


def calculate_all_metrics(routes, route_vols, route_distances,
                           max_capacity, fuel_economy, ef_value, gwp_value):
    """
    คำนวณ 6 เมตริกหลักสำหรับแต่ละ Algorithm:
      1. total_dist   — ระยะทางรวม (กม.)
      2. n_trips      — จำนวนเที่ยววิ่ง
      3. carbon       — CO₂e รวม (kg)
      4. EG           — Efficiency Gap เทียบ Baseline (%)
      5. LBI          — Load Balance Index (0–1)
      6. VUR          — Vehicle Utilization Rate (%)
      7. CIT          — Carbon Intensity per m³ (kgCO₂e/ลบ.ม.)
    """
    total_dist   = sum(route_distances)
    total_demand = sum(route_vols)
    n_trips      = len(routes)

    # Carbon footprint
    activity_A = total_dist / fuel_economy if fuel_economy > 0 else 0
    carbon     = activity_A * ef_value * gwp_value

    # Load Balance Index: LBI = 1 - (σ / μ)
    if len(route_vols) > 1:
        mu    = float(np.mean(route_vols))
        sigma = float(np.std(route_vols))
        lbi   = max(0.0, 1.0 - (sigma / mu)) if mu > 0 else 0.0
    else:
        lbi = 1.0

    # Vehicle Utilization Rate: VUR = Σdemand / (Capacity × N_trips)
    vur = (total_demand / (max_capacity * n_trips) * 100) if n_trips > 0 else 0.0

    # Carbon Intensity per Ton
    cit = (carbon / total_demand) if total_demand > 0 else 0.0

    return {
        "total_dist":   round(total_dist, 3),
        "n_trips":      n_trips,
        "total_demand": round(total_demand, 2),
        "carbon":       round(carbon, 4),
        "lbi":          round(lbi, 4),
        "vur":          round(vur, 2),
        "cit":          round(cit, 4),
        "route_vols":   route_vols,
    }


def run_all_algorithms_benchmark(
        df_dist, demands, nodes, osrm_fmt,
        max_capacity, num_vehicles,
        fuel_economy, ef_value, gwp_value):
    """รันทุก Algorithm แล้วรวบรวม metrics สำหรับแสดง Benchmark"""

    algo_results = {}

    # 1. Sequential Route (Baseline)
    r, rv = run_sequential_algorithm(osrm_fmt, demands, nodes, max_capacity)
    rd    = compute_route_distances(r, nodes, df_dist)
    algo_results["Sequential Route\n(Baseline)"] = calculate_all_metrics(
        r, rv, rd, max_capacity, fuel_economy, ef_value, gwp_value)

    # 2. Clarke-Wright Savings (Standard)
    r, rv = run_savings_algorithm(df_dist, demands, nodes, max_capacity)
    rd    = compute_route_distances(r, nodes, df_dist)
    algo_results["Clarke-Wright\nSavings"] = calculate_all_metrics(
        r, rv, rd, max_capacity, fuel_economy, ef_value, gwp_value)

    # 3. Balanced Clarke-Wright Savings
    r, rv = run_balanced_savings_algorithm(df_dist, demands, nodes, max_capacity, num_vehicles)
    rd    = compute_route_distances(r, nodes, df_dist)
    algo_results["Balanced CW\nSavings ⭐"] = calculate_all_metrics(
        r, rv, rd, max_capacity, fuel_economy, ef_value, gwp_value)

    # 4. Sweep Algorithm (Standard)
    r, rv = run_sweep_algorithm(osrm_fmt, demands, nodes, max_capacity, df_dist)
    rd    = compute_route_distances(r, nodes, df_dist)
    algo_results["Sweep\nAlgorithm"] = calculate_all_metrics(
        r, rv, rd, max_capacity, fuel_economy, ef_value, gwp_value)

    # 5. Balanced Sweep
    r, rv = run_balanced_sweep_algorithm(osrm_fmt, demands, nodes, max_capacity, df_dist)
    rd    = compute_route_distances(r, nodes, df_dist)
    algo_results["Balanced\nSweep"] = calculate_all_metrics(
        r, rv, rd, max_capacity, fuel_economy, ef_value, gwp_value)

    # คำนวณ EG (Efficiency Gap) เทียบกับ Sequential
    baseline_dist = algo_results["Sequential Route\n(Baseline)"]["total_dist"]
    for name, m in algo_results.items():
        eg = ((baseline_dist - m["total_dist"]) / baseline_dist * 100) if baseline_dist > 0 else 0
        algo_results[name]["eg"] = round(eg, 2)

    return algo_results


def render_benchmark_section(algo_results, fuel_economy, ef_value, gwp_value, max_capacity):
    """แสดงผล Benchmark พร้อมวิธีคำนวณ"""

    st.subheader("📊 5. เปรียบเทียบประสิทธิภาพทุก Algorithm")

    # ---- หัวข้อวิธีคำนวณ (ย่อ) ----
    with st.expander("📐 สูตรและวิธีคำนวณแต่ละเมตริก (คลิกเพื่อขยาย)", expanded=False):
        st.markdown(f"""
**1. Carbon Footprint (CO₂e)**
> คาร์บอนที่ปล่อยออกมาจากการเผาไหม้เชื้อเพลิง

$$CO_2e = \\frac{{D_{{total}}}}{{FE}} \\times EF \\times GWP$$

| ตัวแปร | ความหมาย | ค่าที่ใช้ |
|---|---|---|
| $D_{{total}}$ | ระยะทางรวมทุกเที่ยว (กม.) | คำนวณจาก Algorithm |
| $FE$ | อัตราสิ้นเปลือง (กม./ลิตร) | **{fuel_economy}** |
| $EF$ | Emission Factor (kgCO₂/ลิตร) | **{ef_value}** |
| $GWP$ | Global Warming Potential | **{gwp_value}** |

---
**2. Efficiency Gap (EG)**
> ระยะทางที่ประหยัดได้เมื่อเทียบกับ Sequential (Baseline)

$$EG = \\frac{{D_{{baseline}} - D_{{algorithm}}}}{{D_{{baseline}}}} \\times 100\\%$$

เนื่องจาก CO₂ ∝ Distance โดยตรง → **ลดระยะทาง X% = ลดคาร์บอน X% เช่นกัน**

---
**3. Load Balance Index (LBI)**
> ความสมดุลของ Load ระหว่างเที่ยวต่างๆ (ยิ่งใกล้ 1 = สมดุลดี)

$$LBI = 1 - \\frac{{\\sigma_{{loads}}}}{{\\mu_{{loads}}}}$$

| ตัวแปร | ความหมาย |
|---|---|
| $\\sigma_{{loads}}$ | ส่วนเบี่ยงเบนมาตรฐานของ Load แต่ละเที่ยว |
| $\\mu_{{loads}}$ | ค่าเฉลี่ย Load แต่ละเที่ยว |

---
**4. Vehicle Utilization Rate (VUR)**
> ประสิทธิภาพการใช้ความจุรถ (%)

$$VUR = \\frac{{\\sum Demand_{{routes}}}}{{Capacity_{{max}} \\times N_{{trips}}}} \\times 100\\%$$

ค่า VUR = {max_capacity} ลบ.ม. ต่อเที่ยว (ความจุสูงสุด)

---
**5. Carbon Intensity per m³ (CIT)**
> คาร์บอนที่ปล่อยต่อขยะ 1 ลูกบาศก์เมตรที่เก็บได้

$$CIT = \\frac{{CO_2e_{{total}}}}{{Demand_{{total}}}} \\quad \\text{{(kgCO}}_2\\text{{e / ลบ.ม.)}}$$
""")

    # ---- ตารางเปรียบเทียบ ----
    algo_names = list(algo_results.keys())
    baseline_carbon = algo_results["Sequential Route\n(Baseline)"]["carbon"]

    rows = []
    for name, m in algo_results.items():
        carbon_reduce_pct = ((baseline_carbon - m["carbon"]) / baseline_carbon * 100) if baseline_carbon > 0 else 0
        rows.append({
            "Algorithm":           name.replace("\n", " "),
            "ระยะทางรวม (กม.)":   m["total_dist"],
            "จำนวนเที่ยว":        m["n_trips"],
            "CO₂e รวม (kg)":      m["carbon"],
            "ลดคาร์บอน vs Baseline (%)": round(carbon_reduce_pct, 2),
            "EG — ลดระยะทาง (%)": m["eg"],
            "LBI (0–1)":           m["lbi"],
            "VUR (%)":             m["vur"],
            "CIT (kgCO₂e/ลบ.ม.)": m["cit"],
        })

    df_bench = pd.DataFrame(rows).set_index("Algorithm")

    # Highlight best value per column (ไม่รวม Baseline row ใน highlight)
    def highlight_best(df):
        styled = pd.DataFrame('', index=df.index, columns=df.columns)
        best_algo = [a for a in df.index if "Baseline" not in a]
        for col in ["ระยะทางรวม (กม.)", "จำนวนเที่ยว", "CO₂e รวม (kg)", "CIT (kgCO₂e/ลบ.ม.)"]:
            if col in df.columns:
                best_val = df.loc[best_algo, col].min()
                for idx in best_algo:
                    if df.loc[idx, col] == best_val:
                        styled.loc[idx, col] = 'background-color: #d4edda; font-weight: bold'
        for col in ["ลดคาร์บอน vs Baseline (%)", "EG — ลดระยะทาง (%)", "LBI (0–1)", "VUR (%)"]:
            if col in df.columns:
                best_val = df.loc[best_algo, col].max()
                for idx in best_algo:
                    if df.loc[idx, col] == best_val:
                        styled.loc[idx, col] = 'background-color: #d4edda; font-weight: bold'
        # Baseline row
        for col in df.columns:
            styled.loc["Sequential Route (Baseline)", col] = 'background-color: #fff3cd'
        return styled

    st.markdown("**🟩 เขียว = ค่าดีที่สุดในกลุ่ม | 🟨 เหลือง = Baseline (Sequential)**")
    st.dataframe(
        df_bench.style.apply(highlight_best, axis=None).format("{:.4f}"),
        use_container_width=True,
        height=240,
    )

    # ---- ตัวอย่างการคำนวณแบบ Step-by-step ----
    st.markdown("---")
    st.markdown("### 🧮 ตัวอย่างการคำนวณแบบละเอียด (เปรียบเทียบ Baseline vs ดีที่สุด)")

    # หา Algorithm ที่ดีที่สุดด้านระยะทาง (ไม่นับ baseline)
    non_base = {k: v for k, v in algo_results.items() if "Baseline" not in k}
    best_name = min(non_base, key=lambda k: non_base[k]["total_dist"])
    best_m    = non_base[best_name]
    base_m    = algo_results["Sequential Route\n(Baseline)"]

    best_label = best_name.replace("\n", " ")

    col_a, col_b = st.columns(2)

    # ---- pre-compute shared values ----
    eg_val          = best_m["eg"]
    carbon_red      = round(((base_m['carbon'] - best_m['carbon']) / base_m['carbon']) * 100, 2)
    carbon_saved_kg = round(base_m['carbon'] - best_m['carbon'], 4)
    dist_saved_km   = round(base_m['total_dist'] - best_m['total_dist'], 3)

    base_mu    = float(np.mean(base_m['route_vols']))
    base_sigma = float(np.std(base_m['route_vols']))
    best_mu    = float(np.mean(best_m['route_vols']))
    best_sigma = float(np.std(best_m['route_vols']))

    def _step_row(label, formula, result):
        """สร้าง HTML แถว step หนึ่งแถว"""
        return f"""
        <div style="margin-bottom:10px;">
          <div style="font-weight:700;font-size:14px;margin-bottom:4px;">{label}</div>
          <div style="background:rgba(0,0,0,0.06);border-radius:6px;padding:8px 12px;
                      font-family:monospace;font-size:13px;line-height:1.7;">
            {formula}<br>
            <span style="font-weight:700;font-size:14px;">= {result}</span>
          </div>
        </div>"""

    # ── กล่องซ้าย: Baseline ──────────────────────────────────────────
    with col_a:
        html_base = f"""
<div style="background:#fff8e1;border-radius:12px;padding:20px 22px;
            border-left:6px solid #f59e0b;color:#1a1a1a;">
  <h4 style="margin:0 0 16px;color:#92400e;font-size:17px;">
    🔴 Sequential Route <span style="font-weight:400;font-size:14px;">(Baseline)</span>
  </h4>

  {_step_row(
      "Step 1 — ระยะทางรวม",
      f"D_total",
      f"<span style='color:#b45309'>{base_m['total_dist']:.3f} กม.</span> &nbsp;({base_m['n_trips']} เที่ยว)"
  )}

  {_step_row(
      "Step 2 — ปริมาณเชื้อเพลิง",
      f"{base_m['total_dist']:.3f} ÷ {fuel_economy}",
      f"<span style='color:#b45309'>{base_m['total_dist']/fuel_economy:.3f} ลิตร</span>"
  )}

  {_step_row(
      "Step 3 — CO₂e",
      f"{base_m['total_dist']/fuel_economy:.3f} × {ef_value} × {gwp_value}",
      f"<span style='color:#b45309'>{base_m['carbon']:.4f} kg CO₂e</span>"
  )}

  {_step_row(
      "Step 4 — LBI",
      f"μ={base_mu:.3f}, σ={base_sigma:.3f} → 1 − ({base_sigma:.3f} ÷ {base_mu:.3f})",
      f"<span style='color:#b45309'>{base_m['lbi']:.4f}</span>"
  )}

  {_step_row(
      "Step 5 — VUR",
      f"{base_m['total_demand']:.2f} ÷ ({max_capacity} × {base_m['n_trips']}) × 100",
      f"<span style='color:#b45309'>{base_m['vur']:.2f}%</span>"
  )}

  {_step_row(
      "Step 6 — CIT",
      f"{base_m['carbon']:.4f} ÷ {base_m['total_demand']:.2f}",
      f"<span style='color:#b45309'>{base_m['cit']:.4f} kgCO₂e/ลบ.ม.</span>"
  )}
</div>"""
        st.markdown(html_base, unsafe_allow_html=True)

    # ── กล่องขวา: Best Algorithm ─────────────────────────────────────
    with col_b:
        html_best = f"""
<div style="background:#f0fdf4;border-radius:12px;padding:20px 22px;
            border-left:6px solid #16a34a;color:#1a1a1a;">
  <h4 style="margin:0 0 16px;color:#14532d;font-size:17px;">
    🏆 {best_label}
  </h4>

  {_step_row(
      "Step 1 — ระยะทางรวม",
      f"D_total",
      f"<span style='color:#15803d'>{best_m['total_dist']:.3f} กม.</span> &nbsp;({best_m['n_trips']} เที่ยว)"
  )}

  {_step_row(
      "Step 2 — ปริมาณเชื้อเพลิง",
      f"{best_m['total_dist']:.3f} ÷ {fuel_economy}",
      f"<span style='color:#15803d'>{best_m['total_dist']/fuel_economy:.3f} ลิตร</span>"
  )}

  {_step_row(
      "Step 3 — CO₂e",
      f"{best_m['total_dist']/fuel_economy:.3f} × {ef_value} × {gwp_value}",
      f"<span style='color:#15803d'>{best_m['carbon']:.4f} kg CO₂e</span>"
  )}

  {_step_row(
      "Step 4 — LBI",
      f"μ={best_mu:.3f}, σ={best_sigma:.3f} → 1 − ({best_sigma:.3f} ÷ {best_mu:.3f})",
      f"<span style='color:#15803d'>{best_m['lbi']:.4f}</span>"
  )}

  {_step_row(
      "Step 5 — VUR",
      f"{best_m['total_demand']:.2f} ÷ ({max_capacity} × {best_m['n_trips']}) × 100",
      f"<span style='color:#15803d'>{best_m['vur']:.2f}%</span>"
  )}

  {_step_row(
      "Step 6 — CIT",
      f"{best_m['carbon']:.4f} ÷ {best_m['total_demand']:.2f}",
      f"<span style='color:#15803d'>{best_m['cit']:.4f} kgCO₂e/ลบ.ม.</span>"
  )}

  <div style="margin-top:14px;padding:10px 14px;border-radius:8px;
              background:#dcfce7;border:1px solid #86efac;font-size:13px;color:#14532d;">
    📉 ลดระยะทาง <strong>{eg_val:.1f}%</strong> &nbsp;|&nbsp;
    🌿 ลดคาร์บอน <strong>{carbon_red:.1f}%</strong>
    ({carbon_saved_kg:.3f} kg CO₂e)
  </div>
</div>"""
        st.markdown(html_best, unsafe_allow_html=True)

    # ---- สรุปผลประหยัด ----
    st.markdown("---")
    st.markdown("### 🎯 สรุปผลประหยัดรวมเมื่อใช้ Algorithm ที่ดีที่สุด")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        label="🛣️ ระยะทางที่ประหยัด",
        value=f"{dist_saved_km:.2f} กม.",
        delta=f"-{eg_val:.1f}% vs Baseline",
        delta_color="inverse",
    )
    c2.metric(
        label="🌿 คาร์บอนที่ลดได้",
        value=f"{carbon_saved_kg:.3f} kg CO₂e",
        delta=f"-{carbon_red:.1f}% vs Baseline",
        delta_color="inverse",
    )
    c3.metric(
        label="⚖️ Load Balance (LBI)",
        value=f"{best_m['lbi']:.3f}",
        delta=f"+{round(best_m['lbi'] - base_m['lbi'], 3)} vs Baseline",
    )
    c4.metric(
        label="🚛 Utilization Rate",
        value=f"{best_m['vur']:.1f}%",
        delta=f"+{round(best_m['vur'] - base_m['vur'], 1)}% vs Baseline",
    )

    # ---- Bar Chart เปรียบเทียบ ----
    st.markdown("---")
    st.markdown("### 📈 กราฟเปรียบเทียบ")

    tab1, tab2, tab3 = st.tabs(["🛣️ ระยะทาง & คาร์บอน", "⚖️ Load Balance (LBI)", "🚛 VUR & CIT"])

    with tab1:
        labels = [k.replace("\n", " ") for k in algo_results.keys()]
        dists  = [v["total_dist"] for v in algo_results.values()]
        carbons = [v["carbon"] for v in algo_results.values()]
        colors_d = ["#e74c3c" if "Baseline" in l else "#3498db" for l in labels]
        colors_c = ["#e74c3c" if "Baseline" in l else "#27ae60" for l in labels]

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        axes[0].bar(labels, dists, color=colors_d, edgecolor="white", linewidth=0.5)
        axes[0].set_title("ระยะทางรวม (กม.)", fontsize=13, fontweight="bold")
        axes[0].set_ylabel("กิโลเมตร")
        for i, v in enumerate(dists):
            axes[0].text(i, v + 0.2, f"{v:.1f}", ha='center', va='bottom', fontsize=9)
        axes[0].tick_params(axis='x', labelsize=8)

        axes[1].bar(labels, carbons, color=colors_c, edgecolor="white", linewidth=0.5)
        axes[1].set_title("CO₂e รวม (kg)", fontsize=13, fontweight="bold")
        axes[1].set_ylabel("kg CO₂e")
        for i, v in enumerate(carbons):
            axes[1].text(i, v + 0.01, f"{v:.2f}", ha='center', va='bottom', fontsize=9)
        axes[1].tick_params(axis='x', labelsize=8)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with tab2:
        lbis = [v["lbi"] for v in algo_results.values()]
        colors_l = ["#e74c3c" if "Baseline" in l else "#9b59b6" for l in labels]

        fig2, ax2 = plt.subplots(figsize=(9, 4))
        bars = ax2.bar(labels, lbis, color=colors_l, edgecolor="white")
        ax2.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5, label="LBI = 1 (สมบูรณ์แบบ)")
        ax2.set_title("Load Balance Index (LBI) — ยิ่งสูงยิ่งดี (max=1)", fontsize=13, fontweight="bold")
        ax2.set_ylim(0, 1.15)
        ax2.set_ylabel("LBI")
        ax2.legend()
        for i, v in enumerate(lbis):
            ax2.text(i, v + 0.02, f"{v:.3f}", ha='center', va='bottom', fontsize=10, fontweight="bold")
        ax2.tick_params(axis='x', labelsize=8)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

    with tab3:
        vurs = [v["vur"] for v in algo_results.values()]
        cits = [v["cit"] for v in algo_results.values()]
        colors_v = ["#e74c3c" if "Baseline" in l else "#e67e22" for l in labels]
        colors_ci = ["#e74c3c" if "Baseline" in l else "#1abc9c" for l in labels]

        fig3, axes3 = plt.subplots(1, 2, figsize=(12, 4))
        axes3[0].bar(labels, vurs, color=colors_v, edgecolor="white")
        axes3[0].set_title("Vehicle Utilization Rate — VUR (%)", fontsize=13, fontweight="bold")
        axes3[0].set_ylabel("%")
        for i, v in enumerate(vurs):
            axes3[0].text(i, v + 0.3, f"{v:.1f}%", ha='center', va='bottom', fontsize=9)
        axes3[0].tick_params(axis='x', labelsize=8)

        axes3[1].bar(labels, cits, color=colors_ci, edgecolor="white")
        axes3[1].set_title("Carbon Intensity per m³ — CIT (kgCO₂e/ลบ.ม.)", fontsize=13, fontweight="bold")
        axes3[1].set_ylabel("kgCO₂e / ลบ.ม.")
        for i, v in enumerate(cits):
            axes3[1].text(i, v + 0.001, f"{v:.4f}", ha='center', va='bottom', fontsize=9)
        axes3[1].tick_params(axis='x', labelsize=8)

        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()


# =====================================================================
# 7. Interactive Map
# =====================================================================
def create_interactive_map(routes, locations, nodes, routing_mode,
                           G_osm=None, map_type="CartoDB positron",
                           line_style="AntPath (เส้นประเคลื่อนไหว)"):
    depot_coords = (locations[0][1], locations[0][2])
    tiles_mapping = {
        "แผนที่ภูมิประเทศ (OpenStreetMap)":               "OpenStreetMap",
        "แผนที่ดาวเทียม (Esri Satellite)":
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "แผนที่พื้นฐานแบบสว่าง (CartoDB Positron)":       "CartoDB positron",
        "แผนที่พื้นฐานแบบมืด (CartoDB Dark_Matter)":      "CartoDB dark_matter",
        "แผนที่ภูมิประเทศ+ดาวเทียม (Esri NatGeo)":
            "https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}",
    }
    selected_tile = tiles_mapping.get(map_type, "CartoDB positron")
    if "http" in selected_tile:
        m = folium.Map(location=depot_coords, zoom_start=15,
                       tiles=selected_tile, attr="Esri")
    else:
        m = folium.Map(location=depot_coords, zoom_start=15, tiles=selected_tile)

    colors = ["#FF5733","#335BFF","#28B463","#9B59B6",
              "#E67E22","#1ABC9C","#34495E","#E91E63","#00BCD4"]

    if G_osm is not None:
        for u, v in G_osm.edges():
            folium.PolyLine(
                [(G_osm.nodes[u]['y'], G_osm.nodes[u]['x']),
                 (G_osm.nodes[v]['y'], G_osm.nodes[v]['x'])],
                color="#BDC3C7", weight=2, opacity=0.5, dash_array="5, 5"
            ).add_to(m)

    folium.Marker(location=depot_coords, popup="<b>DEPOT</b>",
                  icon=folium.Icon(color="red", icon="home")).add_to(m)

    for item in locations[1:]:
        folium.CircleMarker(
            location=(item[1], item[2]), radius=6, tooltip=item[0],
            color="#34495E", fill=True, fill_color="#F1C40F", fill_opacity=0.9
        ).add_to(m)

    coords_lonlat = {item[0]: (item[2], item[1]) for item in locations}

    for trip_idx, route_seq in enumerate(routes):
        route_color = colors[trip_idx % len(colors)]
        full_route  = [nodes[0]] + route_seq + [nodes[0]]
        road_latlon = []

        if routing_mode == "Local Map (ออฟไลน์ผ่านไฟล์ .osm)" and G_osm is not None:
            for k in range(len(full_route) - 1):
                lon1, lat1 = coords_lonlat[full_route[k]]
                lon2, lat2 = coords_lonlat[full_route[k+1]]
                n1 = get_nearest_node(G_osm, lon1, lat1)
                n2 = get_nearest_node(G_osm, lon2, lat2)
                try:
                    path = nx.shortest_path(G_osm, source=n1, target=n2, weight="weight")
                    for nid in path:
                        road_latlon.append((G_osm.nodes[nid]['y'], G_osm.nodes[nid]['x']))
                except nx.NetworkXNoPath:
                    road_latlon.extend([(lat1, lon1), (lat2, lon2)])
        else:
            coord_str = ";".join(
                f"{coords_lonlat[n][0]},{coords_lonlat[n][1]}" for n in full_route)
            url = (f"http://router.project-osrm.org/route/v1/driving/{coord_str}"
                   f"?overview=full&geometries=geojson")
            try:
                data = requests.get(url, timeout=10).json()
                road_latlon = [(pt[1], pt[0])
                               for pt in data["routes"][0]["geometry"]["coordinates"]]
            except Exception:
                road_latlon = [(coords_lonlat[n][1], coords_lonlat[n][0])
                               for n in full_route]

        if len(road_latlon) > 1:
            tip = f"Trip {trip_idx+1}"
            if line_style == "PolyLine (เส้นทึบ)":
                folium.PolyLine(road_latlon, color=route_color,
                                weight=5, opacity=0.85, tooltip=tip).add_to(m)
            elif line_style == "DashedLine (เส้นประนิ่ง)":
                folium.PolyLine(road_latlon, color=route_color,
                                weight=4, opacity=0.85,
                                dash_array="10 8", tooltip=tip).add_to(m)
            elif line_style == "ArrowLine (เส้น + ลูกศร)":
                pl = folium.PolyLine(road_latlon, color=route_color,
                                     weight=5, opacity=0.85, tooltip=tip)
                pl.add_to(m)
                plugins.PolyLineTextPath(
                    pl, text="  ►  ", repeat=True, offset=8,
                    attributes={"fill": route_color,
                                "font-weight": "bold", "font-size": "14"}
                ).add_to(m)
            else:  # AntPath
                plugins.AntPath(
                    locations=road_latlon, color=route_color,
                    weight=5, opacity=0.8,
                    dash_array=[10, 20], delay=800, tooltip=tip
                ).add_to(m)
        time.sleep(0.1)
    return m

# =====================================================================
# 8. Streamlit UI
# =====================================================================
st.title("🚛 Smart Waste Collection Routing System (Balanced Edition)")
st.markdown("ระบบจัดเส้นทางอัจฉริยะ พร้อมฟังก์ชัน **Load Balancing**, **Benchmark เปรียบเทียบ Algorithm** และปรับรูปแบบแผนที่ได้")

# ---- SIDEBAR ----
with st.sidebar:
    st.header("⚙️ 1. เลือกโครงข่ายถนน")
    routing_mode = st.radio("Routing Engine:", (
        "OSRM API (ออนไลน์/สาธารณะ)",
        "Local Map (ออฟไลน์ผ่านไฟล์ .osm)"))

    G_osm = None
    if routing_mode == "Local Map (ออฟไลน์ผ่านไฟล์ .osm)":
        uploaded_osm = st.file_uploader("📂 อัปโหลดไฟล์ .osm", type=["osm"])
        if uploaded_osm is not None:
            with st.spinner("⏳ กำลังอ่านไฟล์ .osm..."):
                G_osm = build_osm_graph_manual(uploaded_osm.getvalue().decode("utf-8"))
            if G_osm and len(G_osm.edges) > 0:
                st.success(f"✅ โครงข่ายสมบูรณ์! "
                           f"(พิกัด: {len(G_osm.nodes)} | เส้น: {len(G_osm.edges)})")
            else:
                st.error("❌ ไฟล์ที่อัปโหลดไม่มีข้อมูลเส้นทาง")
        else:
            st.warning("⚠️ โปรดอัปโหลดไฟล์ .osm")

    st.header("🗺️ 2. รูปแบบแผนที่")
    map_type = st.selectbox("ประเภทแผนที่:", (
        "แผนที่ภูมิประเทศ (OpenStreetMap)",
        "แผนที่ดาวเทียม (Esri Satellite)",
        "แผนที่พื้นฐานแบบสว่าง (CartoDB Positron)",
        "แผนที่พื้นฐานแบบมืด (CartoDB Dark_Matter)",
        "แผนที่ภูมิประเทศ+ดาวเทียม (Esri NatGeo)",
    ))
    line_style = st.selectbox("รูปแบบเส้นทาง:", (
        "AntPath (เส้นประเคลื่อนไหว)",
        "PolyLine (เส้นทึบ)",
        "DashedLine (เส้นประนิ่ง)",
        "ArrowLine (เส้น + ลูกศร)",
    ))

    st.header("📍 3. จุดศูนย์กลาง (Depot)")
    depot_name = st.text_input("ชื่อจุด Depot", value="Depot โรงจัดการขยะ")
    depot_lat  = st.number_input("ละติจูด", value=14.862939, format="%.6f")
    depot_lon  = st.number_input("ลองจิจูด", value=102.027903, format="%.6f")

    st.header("⚙️ 4. ยานพาหนะ")
    max_vehicles = st.number_input("จำนวนรถขยะ", min_value=1, value=2)
    max_capacity = st.number_input("ความจุสูงสุด (ลบ.ม.)", min_value=0.1, value=4.5)

    st.header("⚙️ 5. อัลกอริทึม & คาร์บอน")
    algorithm_choice = st.selectbox("เทคนิคการจัดเส้นทาง:", (
        "Balanced Clarke-Wright Savings (แนะนำ)",
        "Balanced Workload Sweep",
        "Clarke-Wright Savings (มาตรฐาน)",
        "Sweep Algorithm (มาตรฐาน)",
        "Sequential Route (เส้นทางเดิมตามลำดับ)",
    ))
    fuel_economy = st.number_input("อัตราสิ้นเปลือง (กม./ลิตร)", value=5.0)
    ef_value     = st.number_input("ค่า EF (kgCO₂/ลิตร)", value=2.70757, format="%.5f")
    gwp_value    = st.number_input("ค่า GWP", value=1.0)

    st.header("📊 6. Benchmark")
    run_benchmark = st.checkbox("🔬 เปรียบเทียบทุก Algorithm (Benchmark Mode)", value=True)
    st.caption("เมื่อเปิดใช้งาน จะรันทุก Algorithm พร้อมกันและแสดงผลเปรียบเทียบ")

# ---- MAIN AREA ----
st.subheader("📝 1. ข้อมูลพิกัดจุดทิ้งขยะ")

col_sel1, col_sel2 = st.columns([1, 2])
with col_sel1:
    vehicle_preset = st.radio(
        "เลือกชุดข้อมูลรถ:",
        list(DATASET_MAP.keys()),
        horizontal=False,
    )
with col_sel2:
    chosen_data = DATASET_MAP[vehicle_preset]
    st.info(
        f"**{vehicle_preset}** — {len(chosen_data)} จุดเก็บขยะ  |  "
        f"Demand รวม: **{sum(r[3] for r in chosen_data):.1f} ลบ.ม.**"
    )

st.markdown("---")

uploaded_coord = st.file_uploader(
    "📂 หรืออัปโหลดไฟล์ Excel/CSV แทน (จะใช้ไฟล์นี้แทนชุดข้อมูลที่เลือก)",
    type=["xlsx", "csv"])

if uploaded_coord is not None:
    df_input = (pd.read_csv(uploaded_coord)
                if uploaded_coord.name.endswith(".csv")
                else pd.read_excel(uploaded_coord))
    st.success("✅ โหลดข้อมูลจากไฟล์สำเร็จ!")
else:
    df_input = pd.DataFrame(
        chosen_data, columns=["Node_Name","Latitude","Longitude","Demand"])

st.markdown("*(ไม่ต้องใส่พิกัด Depot ในตารางนี้)*")
edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

if "show_results" not in st.session_state:
    st.session_state["show_results"] = False

st.markdown("<br>", unsafe_allow_html=True)
start_btn = st.button("🚀 ยืนยันข้อมูลและเริ่มจัดเส้นทาง",
                      type="primary", use_container_width=True)

if start_btn:
    cleaned_df = edited_df.dropna(
        subset=["Node_Name","Latitude","Longitude","Demand"])
    if len(cleaned_df) < 1:
        st.error("❌ ต้องมีจุดเก็บขยะอย่างน้อย 1 จุด")
        st.session_state["show_results"] = False
    elif (routing_mode == "Local Map (ออฟไลน์ผ่านไฟล์ .osm)"
          and (G_osm is None or len(G_osm.edges) == 0)):
        st.error("❌ ยังไม่ได้อัปโหลดไฟล์ .osm หรือโครงข่ายไม่สมบูรณ์")
        st.session_state["show_results"] = False
    else:
        st.session_state["show_results"] = True
        st.session_state["process_data"] = cleaned_df

st.markdown("---")

# =====================================================================
# 9. แสดงผลลัพธ์
# =====================================================================
if st.session_state.get("show_results", False):
    cleaned_df      = st.session_state["process_data"]
    total_customers = len(cleaned_df)

    depot_data  = [depot_name, depot_lat, depot_lon, 0.0]
    data_to_use = [depot_data] + cleaned_df.values.tolist()
    nodes       = [row[0] for row in data_to_use]
    demands     = {row[0]: row[3] for row in data_to_use}
    osrm_fmt    = [(row[0], row[1], row[2], row[3]) for row in data_to_use]

    with st.spinner(f"📡 กำลังสร้าง Distance Matrix และประมวลผล..."):

        if routing_mode == "Local Map (ออฟไลน์ผ่านไฟล์ .osm)":
            df_dist = get_distance_matrix_osm(G_osm, osrm_fmt)
        else:
            df_dist = get_distance_matrix_osrm(osrm_fmt)
        df_dist.columns = df_dist.index = nodes

        if algorithm_choice == "Clarke-Wright Savings (มาตรฐาน)":
            routes, route_vols = run_savings_algorithm(
                df_dist, demands, nodes, max_capacity)
        elif algorithm_choice == "Balanced Clarke-Wright Savings (แนะนำ)":
            routes, route_vols = run_balanced_savings_algorithm(
                df_dist, demands, nodes, max_capacity, max_vehicles)
        elif algorithm_choice == "Balanced Workload Sweep":
            routes, route_vols = run_balanced_sweep_algorithm(
                osrm_fmt, demands, nodes, max_capacity, df_dist)
        elif algorithm_choice == "Sequential Route (เส้นทางเดิมตามลำดับ)":
            routes, route_vols = run_sequential_algorithm(
                osrm_fmt, demands, nodes, max_capacity)
        else:
            routes, route_vols = run_sweep_algorithm(
                osrm_fmt, demands, nodes, max_capacity, df_dist)

        route_distances = compute_route_distances(routes, nodes, df_dist)

        grand_total = sum(route_distances)
        activity_A  = grand_total / fuel_economy
        carbon_E    = activity_A * ef_value * gwp_value

        # Fleet Balancing
        trip_data = [{"original_idx": i+1, "route": routes[i],
                      "vol": route_vols[i], "dist": route_distances[i]}
                     for i in range(len(routes))]
        trip_data.sort(key=lambda x: x["dist"], reverse=True)
        fleet_schedule    = {f"🚛 รถขยะคันที่ {i+1}": [] for i in range(int(max_vehicles))}
        vehicle_workloads = {f"🚛 รถขยะคันที่ {i+1}": 0.0 for i in range(int(max_vehicles))}
        for t in trip_data:
            best = min(vehicle_workloads, key=vehicle_workloads.get)
            t["trip_sequence"] = len(fleet_schedule[best]) + 1
            fleet_schedule[best].append(t)
            vehicle_workloads[best] += t["dist"]

    # Dashboard
    st.subheader("📊 2. สรุปผลการปฏิบัติงาน")
    st.success(f"✅ วิเคราะห์ด้วย **{algorithm_choice}** เสร็จสมบูรณ์!")

    c1, c2, c3 = st.columns(3)
    c1.metric("📌 จุดเก็บขยะ",     f"{total_customers} จุด")
    c2.metric("🚛 รอบที่ต้องวิ่ง",  f"{len(routes)} เที่ยว")
    c3.metric("🗑️ ปริมาตรรวม",     f"{sum(route_vols):.2f} ลบ.ม.")

    c4, c5 = st.columns(2)
    c4.metric("📍 ระยะทางรวม",      f"{grand_total:.2f} กม.")
    c5.metric("🌿 คาร์บอน (CO₂e)",  f"{carbon_E:.2f} kg")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🗺️ 3. แผนที่จำลองการเดินรถ")
    with st.spinner("กำลังเรนเดอร์แผนที่..."):
        m = create_interactive_map(
            routes, osrm_fmt, nodes, routing_mode, G_osm, map_type, line_style)
        st_folium(m, width=1200, height=600, returned_objects=[])

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 4. ตารางปฏิบัติงานของรถแต่ละคัน")
    for vehicle_name, trips in fleet_schedule.items():
        total_d = sum(t["dist"] for t in trips)
        total_v = sum(t["vol"]  for t in trips)
        with st.expander(
            f"{vehicle_name} — {len(trips)} เที่ยว | "
            f"{total_d:.2f} กม. | {total_v:.2f} ลบ.ม.",
            expanded=True
        ):
            if not trips:
                st.write("✅ รถคันนี้ไม่ได้ออกปฏิบัติงาน (Standby)")
            for t in trips:
                st.info(
                    f"📍 {nodes[0]} ➡️ {' ➡️ '.join(t['route'])} ➡️ {nodes[0]}\n\n"
                    f"ปริมาตร: {t['vol']:.2f} ลบ.ม. | ระยะทาง: {t['dist']:.2f} กม."
                )

    # =====================================================================
    # 10. Benchmark Section
    # =====================================================================
    if run_benchmark:
        st.markdown("---")
        with st.spinner("🔬 กำลังรัน Benchmark ทุก Algorithm..."):
            algo_results = run_all_algorithms_benchmark(
                df_dist, demands, nodes, osrm_fmt,
                max_capacity, int(max_vehicles),
                fuel_economy, ef_value, gwp_value,
            )
        render_benchmark_section(
            algo_results, fuel_economy, ef_value, gwp_value, max_capacity)
    else:
        st.info("💡 เปิด **Benchmark Mode** ใน Sidebar เพื่อเปรียบเทียบทุก Algorithm พร้อมกัน")

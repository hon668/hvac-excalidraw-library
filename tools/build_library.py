# -*- coding: utf-8 -*-
"""
hvac-excalidraw-library 构建脚本
=================================

用途：
    1. 用代码生成 Excalidraw 原生矢量元件（手绘风格），输出 .excalidrawlib 素材库
    2. 输出示例 .excalidraw 图纸
    3. 输出 docs/assets 下的 SVG 预览图（GitHub Pages 用）

为什么要用脚本生成，而不是手绘后导出？
    - 元件坐标、尺寸、描边、粗糙度可复现，后续批量改色/改尺寸不用重画
    - 中英文两套标签库可以一次生成，避免手工维护两份
    - PR 到官方库时，评审能看到元件是怎么来的（更透明）

用法：
    python tools/build_library.py

输出：
    library/hvac-excalidraw-library-zh-v1.0.0.excalidrawlib   中文标签（主库）
    library/hvac-excalidraw-library-en-v1.0.0.excalidrawlib   英文标签（投稿官方库用）
    examples/01-chilled-water-system.excalidraw
    examples/02-ahu-duct-layout.excalidraw
    examples/03-ice-storage-system.excalidraw
    docs/assets/preview-components.svg
    docs/assets/preview-example-system.svg
"""

import copy
import json
import random
import time
import uuid
from pathlib import Path

# ---------------------------------------------------------------- 基础配置

ROOT = Path(__file__).resolve().parent.parent
LIB_DIR = ROOT / "library"
EX_DIR = ROOT / "examples"
ASSETS_DIR = ROOT / "docs" / "assets"
VERSION = "1.0.0"

# Excalidraw 画布默认是白底，所以描边用深色、填充用浅色
STROKE = "#1e1e1e"   # 主线条（近黑，手绘感更强）
BLUE = "#1971c2"     # 冷冻水 / 冷媒
ORANGE = "#e8590c"   # 冷却水 / 热水
GREEN = "#2f9e44"    # 风管 / 气流
GRAY = "#868e96"     # 辅助线、内部构造
LIGHT = "#e9ecef"    # 浅填充

RND = random.Random(20260915)          # 固定种子 → 每次生成结果一致
NOW = int(time.time() * 1000)


# ---------------------------------------------------------------- 元素工厂

def _el(type_, x, y, w, h, fillStyle="solid", strokeWidth=2, strokeStyle="solid",
        roughness=1, opacity=100, angle=0, strokeColor=STROKE,
        backgroundColor="transparent", roundness=None, groupIds=None,
        seed=None):
    """生成一个符合 Excalidraw 数据结构的元素（公共字段）。"""
    return {
        "type": type_,
        "version": 1,
        "versionNonce": RND.randint(0, 2 ** 31),
        "isDeleted": False,
        "id": uuid.uuid4().hex[:16],
        "fillStyle": fillStyle,
        "strokeWidth": strokeWidth,
        "strokeStyle": strokeStyle,
        "roughness": roughness,
        "opacity": opacity,
        "angle": angle,
        "x": round(x, 2),
        "y": round(y, 2),
        "strokeColor": strokeColor,
        "backgroundColor": backgroundColor,
        "width": round(w, 2),
        "height": round(h, 2),
        "seed": seed if seed is not None else RND.randint(0, 2 ** 31),
        "groupIds": groupIds or [],
        "frameId": None,
        "roundness": roundness,
        "boundElements": [],
        "updated": NOW,
        "link": None,
        "locked": False,
    }


def rect(x, y, w, h, bg="transparent", stroke=STROKE, sw=2, rnd=True, dashed=False, rough=1):
    return _el("rectangle", x, y, w, h, backgroundColor=bg, strokeColor=stroke,
               strokeWidth=sw, roundness={"type": 3} if rnd else None,
               strokeStyle="dashed" if dashed else "solid", roughness=rough)


def ellipse(x, y, w, h, bg="transparent", stroke=STROKE, sw=2):
    return _el("ellipse", x, y, w, h, backgroundColor=bg, strokeColor=stroke,
               strokeWidth=sw, roundness=None)


def polyline(pts, closed=False, stroke=STROKE, sw=2, dashed=False, rough=1, bg="transparent"):
    """折线（Excalidraw 的 line 元素），pts 为绝对坐标列表。

    closed=True 时首尾相接，可配合 bg 用作多边形填充（如冷却塔梯形塔体）。
    """
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys)
    rel = [[round(p[0] - x0, 2), round(p[1] - y0, 2)] for p in pts]
    if closed and rel[0] != rel[-1]:
        rel.append(rel[0])
    e = _el("line", x0, y0, max(xs) - x0, max(ys) - y0, strokeColor=stroke,
            strokeWidth=sw, roundness=None, roughness=rough, backgroundColor=bg,
            strokeStyle="dashed" if dashed else "solid")
    e.update({"points": rel, "lastCommittedPoint": None, "startBinding": None,
              "endBinding": None, "startArrowhead": None, "endArrowhead": None})
    return e


def arrow(pts, stroke=STROKE, sw=2, head="arrow", dashed=False):
    e = polyline(pts, stroke=stroke, sw=sw, dashed=dashed)
    e["type"] = "arrow"
    e["endArrowhead"] = head
    return e


def tw(s, size):
    """粗略估算文本宽度：中日韩全角按 1.0 个字号，西文按 0.58。"""
    w = 0.0
    for ch in s:
        w += size * 1.0 if ord(ch) > 0x2E80 else size * 0.58
    return w


def text(x, y, s, size=16, color=STROKE, align="left"):
    lines = s.split("\n")
    w = max(tw(l, size) for l in lines)
    h = len(lines) * size * 1.25
    e = _el("text", x, y, w, h, roundness=None, strokeColor=color, strokeWidth=1)
    e.update({
        "fontSize": size,
        "fontFamily": 1,          # 1 = Excalifont/Virgil 手写体（中文回退到系统字体）
        "text": s,
        "textAlign": align,
        "verticalAlign": "top",
        "containerId": None,
        "originalText": s,
        "lineHeight": 1.25,
        "boundElements": None,
        "baseline": int(size * 0.9),
    })
    return e


def label(cx, y, s, size=16, color=STROKE):
    """以 cx 为中心、y 为顶部的水平居中文本。"""
    return text(cx - tw(s, size) / 2, y, s, size, color)


# ---------------------------------------------------------------- 元件绘制

def c_chiller(zh):
    """冷水机组：双筒式（上冷凝器 + 下蒸发器）+ 顶置压缩机 + 四路接管

    画法是离心式/螺杆式冷机原理图的通用形式：
        上方圆形 = 压缩机（内置叶轮符号），排气下行进冷凝器
        上筒 = 冷凝器（冷却水侧），下筒 = 蒸发器（冷冻水侧），两筒间为冷媒下行管
        管口：左侧进（冷却水 / 冷冻水）、右侧出，共四路
    """
    els = [
        rect(0, 0, 172, 130, bg=LIGHT, rnd=True),                        # 机组外壳
        ellipse(62, 2, 46, 36),                                          # 压缩机
        polyline([[78, 10], [96, 20], [78, 30]], closed=True, stroke=GRAY, sw=1.5),
        polyline([[85, 38], [85, 46]]),                                  # 排气 → 冷凝器
        rect(12, 46, 148, 30),                                           # 冷凝器（上筒）
        rect(12, 92, 148, 30),                                           # 蒸发器（下筒）
        polyline([[30, 76], [30, 92]]),                                  # 冷媒下行管
        polyline([[142, 76], [142, 92]]),
        polyline([[-30, 61], [12, 61]], stroke=ORANGE, sw=2),            # 冷却水进（橙）
        polyline([[160, 61], [202, 61]], stroke=ORANGE, sw=2),           # 冷却水出（橙）
        polyline([[-30, 107], [12, 107]], stroke=BLUE, sw=2),            # 冷冻水进
        polyline([[160, 107], [202, 107]], stroke=BLUE, sw=2),           # 冷冻水出
    ]
    for i in range(6):                                                   # 两筒换热管束
        x = 20 + i * 24
        els.append(polyline([[x, 72], [x + 12, 50]], stroke=GRAY, sw=1))
        els.append(polyline([[x, 118], [x + 12, 96]], stroke=GRAY, sw=1))
    els.append(label(86, 138, "冷水机组" if zh else "Chiller", 16))
    return els


def c_cooling_tower(zh):
    """冷却塔：收口塔体 + 顶部风机 + 两侧进风格栅 + 底部集水盘"""
    els = [
        polyline([[0, 32], [150, 32], [138, 146], [12, 146]], closed=True, bg=LIGHT),
        ellipse(43, 0, 64, 30),                                    # 风机筒
        ellipse(66, 10, 18, 12, stroke=GRAY, sw=1.5),              # 轮毂
        polyline([[75, 15], [75, 2]], stroke=GRAY, sw=1.5),        # 三片风叶
        polyline([[75, 15], [58, 25]], stroke=GRAY, sw=1.5),
        polyline([[75, 15], [92, 25]], stroke=GRAY, sw=1.5),
        rect(4, 146, 142, 16, bg=LIGHT, rnd=False),                # 集水盘
    ]
    for i in range(3):                                             # 两侧进风格栅
        els.append(polyline([[26 + i * 9, 44], [13 + i * 9, 100]], stroke=GRAY, sw=1))
        els.append(polyline([[124 - i * 9, 44], [137 - i * 9, 100]], stroke=GRAY, sw=1))
    els.append(polyline([[-34, 154], [4, 154]], stroke=ORANGE, sw=2))   # 冷却水出塔（集水盘左出）
    els.append(polyline([[150, 70], [190, 70]], stroke=ORANGE, sw=2))   # 回水进塔（右侧布水）
    els.append(label(75, 170, "冷却塔" if zh else "Cooling Tower", 16))
    return els


def c_plate_hx(zh):
    """板式换热器：板片束 + 两侧四路接管

    两侧都是水/乙二醇，所以统一用蓝色，靠线型区分：
        实线 = 一次侧（热源侧，如乙二醇）  虚线 = 二次侧（负荷侧，如空调冷冻水）
    """
    els = [rect(0, 0, 96, 120, bg=LIGHT, rnd=True)]
    for i in range(6):                                             # 板片束
        x = 12 + i * 14
        els.append(polyline([[x, 8], [x, 112]], stroke=GRAY, sw=1.5))
    els.append(polyline([[-36, 26], [0, 26]], stroke=BLUE, sw=2))                        # 一次侧进
    els.append(polyline([[-36, 94], [0, 94]], stroke=BLUE, sw=2))                        # 一次侧出
    els.append(polyline([[96, 26], [132, 26]], stroke=BLUE, sw=2, dashed=True))          # 二次侧进
    els.append(polyline([[96, 94], [132, 94]], stroke=BLUE, sw=2, dashed=True))          # 二次侧出
    els.append(label(48, 128, "板式换热器" if zh else "Plate Heat Exchanger", 16))
    return els


def c_ice_tank(zh):
    """蓄冰槽：槽体 + 乙二醇蛇形盘管 + 冰晶示意"""
    els = [
        rect(0, 0, 200, 124, bg=LIGHT, rnd=False),
        polyline([[-34, 26], [16, 26], [184, 26], [184, 48], [16, 48],
                  [16, 70], [184, 70], [184, 92], [216, 92]], stroke=BLUE, sw=2),
    ]
    for cx, cy in ((52, 37), (124, 37), (84, 59), (152, 59), (104, 81)):
        els.append(polyline([[cx, cy - 5], [cx + 5, cy + 4], [cx - 5, cy + 4]],
                            closed=True, stroke=GRAY, sw=1.2))     # 冰晶
    els.append(label(100, 132, "蓄冰槽" if zh else "Ice Storage Tank", 16))
    return els


def c_water_tank(zh):
    """蓄冷罐：立式罐体 + 斜温层 + 供回水接管 + 温度分层标注

    上部 7℃ 供水、下部 12℃ 回水，中间虚线为斜温层（温度跃变区）。
    温度文字与虚线错开排布，避免叠字。
    """
    els = [
        rect(0, 0, 104, 176, bg=LIGHT, rnd=False),
        polyline([[0, 16], [104, 16]], stroke=GRAY, sw=1),         # 顶封头切线
        polyline([[0, 160], [104, 160]], stroke=GRAY, sw=1),       # 底封头切线
        polyline([[-34, 28], [0, 28]], stroke=BLUE, sw=2),         # 供水出罐（上）
        polyline([[-34, 152], [0, 152]], stroke=BLUE, sw=2),       # 回水进罐（下）
        text(30, 24, "7℃", 14, BLUE),
        text(24, 132, "12℃", 14, BLUE),
    ]
    for y in (62, 90, 118):                                        # 斜温层
        els.append(polyline([[10, y], [94, y]], stroke=GRAY, sw=1, dashed=True))
    els.append(label(52, 184, "蓄冷罐" if zh else "Chilled Water Tank", 16))
    return els


def c_ahu(zh):
    """空气处理机组：混风 / 过滤 / 表冷 / 风机 / 送风 五段式"""
    W, H = 244, 80
    els = [rect(0, 0, W, H, bg=LIGHT)]
    for x in (48, 96, 152, 198):
        els.append(polyline([[x, 0], [x, H]], stroke=GRAY, sw=1))   # 分段隔板
    els.append(arrow([[-40, 40], [0, 40]], stroke=GREEN))            # 新风 / 回风
    for i in range(3):                                               # 初效过滤
        els.append(polyline([[52 + i * 14, 6], [66 + i * 14, H - 6]], stroke=GRAY, sw=1))
    els.append(polyline([[100, 12], [100, 68], [108, 68], [108, 12], [116, 12],
                         [116, 68], [124, 68], [124, 12], [132, 12], [132, 68],
                         [140, 68], [140, 12]], stroke=BLUE, sw=2))  # 表冷器盘管
    els.append(ellipse(160, 22, 36, 36))                             # 风机
    els.append(ellipse(170, 32, 16, 16, stroke=GRAY, sw=1.5))
    for a in ((178, 22), (196, 40), (178, 58), (160, 40)):           # 风机叶片
        els.append(polyline([[178, 40], list(a)], stroke=GRAY, sw=1.5))
    els.append(arrow([[W, 40], [W + 40, 40]], stroke=GREEN))         # 送风
    els.append(label(W / 2 + 8, 88, "空气处理机组 AHU" if zh else "Air Handling Unit (AHU)", 16))
    return els


def c_fcu(zh):
    """风机盘管：盘管 + 离心风机 + 三档调速"""
    els = [rect(0, 0, 152, 72, bg=LIGHT, rnd=True)]
    els.append(polyline([[14, 12], [14, 60], [22, 60], [22, 12], [30, 12], [30, 60],
                         [38, 60], [38, 12], [46, 12], [46, 60], [54, 60], [54, 12]],
                        stroke=BLUE, sw=2))
    els.append(ellipse(80, 18, 44, 44))
    els.append(ellipse(91, 29, 22, 22, stroke=GRAY, sw=1.5))
    for p in ((102, 18), (124, 40), (102, 62), (80, 40)):
        els.append(polyline([[102, 40], list(p)], stroke=GRAY, sw=1.5))
    for i in range(3):                                               # 三档调速标识
        els.append(ellipse(88 + i * 16, 62, 8, 8, bg=LIGHT, stroke=GRAY, sw=1.5))
    els.append(label(76, 80, "风机盘管 FCU" if zh else "Fan Coil Unit (FCU)", 16))
    return els


def c_pump(zh):
    """循環水泵：电机 + 联轴器 + 泵壳 + 进出口"""
    els = [
        rect(48, -56, 62, 34, rnd=False),        # 电机
        rect(70, -22, 18, 20, rnd=False),        # 联轴器 / 支架
        polyline([[70, -30], [70, -56]], stroke=GRAY, sw=1),
        polyline([[88, -30], [88, -56]], stroke=GRAY, sw=1),
        ellipse(42, -2, 78, 78),                 # 泵壳
        polyline([[86, 4], [86, 70], [38, 37]], closed=True, stroke=GRAY, sw=1.5),
        polyline([[81, 37], [130, 37]], stroke=BLUE, sw=2),   # 出口
        polyline([[0, 37], [42, 37]], stroke=BLUE, sw=2),     # 进口
        polyline([[30, 84], [132, 84]], stroke=GRAY, sw=1.5), # 底座
    ]
    for i in range(5):                                        # 电机散热片
        els.append(polyline([[54 + i * 11, -50], [54 + i * 11, -28]], stroke=GRAY, sw=1))
    els.append(label(81, 92, "循环水泵 Pump" if zh else "Circulation Pump", 16))
    return els


def _bowtie(cx, cy, w=34, h=40, **kw):
    """阀门共用的蝴蝶形阀体。"""
    x0, x1 = cx - w / 2, cx + w / 2
    t, b = cy - h / 2, cy + h / 2
    return [polyline([[x0, t], [x0, b], [x1, cy]], closed=True, **kw),
            polyline([[x1, t], [x1, b], [x0, cy]], closed=True, **kw)]


def c_butterfly(zh):
    """蝶阀：阀体 + 阀杆 + 手柄"""
    els = [polyline([[0, 30], [12, 30]], stroke=BLUE, sw=2),
           polyline([[58, 30], [70, 30]], stroke=BLUE, sw=2)]
    els += _bowtie(35, 30)
    els.append(polyline([[35, 10], [35, -14]]))
    els.append(polyline([[35, -14], [62, -14]], stroke=GRAY, sw=2))
    els.append(label(35, 46, "蝶阀 Butterfly" if zh else "Butterfly Valve", 14))
    return els


def c_globe(zh):
    """截止阀：阀体 + 阀杆 + 手轮"""
    els = [polyline([[0, 30], [12, 30]], stroke=BLUE, sw=2),
           polyline([[58, 30], [70, 30]], stroke=BLUE, sw=2)]
    els += _bowtie(35, 30)
    els.append(polyline([[35, 10], [35, -6]]))
    els.append(ellipse(19, -28, 32, 22, bg=LIGHT))
    els.append(polyline([[35, -6], [35, -17]], stroke=GRAY, sw=1.5))
    els.append(label(35, 46, "截止阀 Globe" if zh else "Globe Valve", 14))
    return els


def c_filter(zh):
    """过滤器：Y 型思路简化成直通滤网框"""
    els = [rect(0, 0, 70, 42, bg=LIGHT, rnd=True),
           polyline([[0, 21], [-16, 21]], stroke=BLUE, sw=2),
           polyline([[70, 21], [86, 21]], stroke=BLUE, sw=2)]
    for i in range(4):
        els.append(polyline([[8 + i * 14, 36], [22 + i * 14, 6]], stroke=GRAY, sw=1.5))
    els.append(label(35, 50, "过滤器 Filter" if zh else "Strainer / Filter", 14))
    return els


def c_gauge(zh):
    """压力表：表盘 + 指针 + 接管"""
    els = [ellipse(0, 0, 48, 48, bg=LIGHT),
           polyline([[24, 24], [40, 12]], stroke=STROKE, sw=2),
           ellipse(20, 20, 8, 8, bg=LIGHT, stroke=GRAY, sw=1.5),
           polyline([[24, 48], [24, 68]], stroke=BLUE, sw=2),
           polyline([[14, 68], [34, 68]], stroke=BLUE, sw=2.5)]
    for a in range(5):                                  # 刻度
        els.append(polyline([[24 + 18 * _cos(a * 45), 24 - 18 * _sin(a * 45)],
                             [24 + 14 * _cos(a * 45), 24 - 14 * _sin(a * 45)]],
                            stroke=GRAY, sw=1))
    els.append(label(24, 76, "压力表 Gauge" if zh else "Pressure Gauge", 14))
    return els


def c_temp(zh):
    """温度传感器：套管 + 感温包 + 接线"""
    els = [polyline([[20, 0], [20, 52]], stroke=BLUE, sw=2.5),
           ellipse(9, 46, 22, 22, bg=LIGHT),
           polyline([[20, 0], [20, -22]], stroke=STROKE, sw=2),
           polyline([[20, -22], [58, -22]], stroke=GRAY, sw=1.5),
           text(24, -30, "T", 16)]
    els.append(label(30, 76, "温度传感器 TE" if zh else "Temperature Sensor", 14))
    return els


def c_duct_outlet(zh):
    """风管风口：风管 + 百叶 + 气流箭头"""
    els = [rect(0, 0, 96, 22, bg=LIGHT, rnd=False),
           rect(0, 26, 96, 16, bg=LIGHT, rnd=False),
           arrow([[48, 46], [48, 74]], stroke=GREEN)]
    for i in range(6):
        els.append(polyline([[6 + i * 16, 40], [12 + i * 16, 28]], stroke=GRAY, sw=1.5))
    els.append(label(48, 82, "风口 Diffuser" if zh else "Duct Outlet / Diffuser", 14))
    return els


def c_silencer(zh):
    """消声器：外壳 + 交错隔板"""
    els = [rect(0, 0, 160, 54, bg=LIGHT, rnd=False),
           polyline([[0, 27], [-20, 27]], stroke=GREEN, sw=2),
           polyline([[160, 27], [180, 27]], stroke=GREEN, sw=2)]
    for i in range(5):
        x = 16 + i * 30
        if i % 2 == 0:
            els.append(polyline([[x, 6], [x, 34]], stroke=GRAY, sw=2))
        else:
            els.append(polyline([[x, 20], [x, 48]], stroke=GRAY, sw=2))
    els.append(label(80, 62, "消声器 Silencer" if zh else "Duct Silencer", 14))
    return els


def c_flex(zh):
    """软接头：两侧法兰 + 双波浪管壁（示意可挠曲）"""
    import math
    els = [rect(0, 6, 12, 44, bg=LIGHT, rnd=False),
           rect(78, 6, 12, 44, bg=LIGHT, rnd=False)]
    for sign, off in ((1, 26), (-1, 26)):     # 上下两条正弦管壁
        pts = []
        for i in range(25):
            x = 12 + i * (66 / 24.0)
            y = off + sign * 12 * math.sin(i / 24.0 * 2 * math.pi * 2)
            pts.append([round(x, 2), round(y, 2)])
        els.append(polyline(pts, stroke=BLUE, sw=2))
    els.append(polyline([[12, 14], [78, 14]], stroke=GRAY, sw=1, dashed=True))
    els.append(polyline([[12, 38], [78, 38]], stroke=GRAY, sw=1, dashed=True))
    els.append(polyline([[-18, 28], [0, 28]], stroke=BLUE, sw=2))
    els.append(polyline([[90, 28], [108, 28]], stroke=BLUE, sw=2))
    els.append(label(46, 56, "软接头 Flexible" if zh else "Flexible Connector", 14))
    return els


def _cos(deg):
    import math
    return math.cos(math.radians(deg))


def _sin(deg):
    import math
    return math.sin(math.radians(deg))


# 元件注册表：(中文名, 英文名, 绘制函数)
# 顺序 = 库面板里的显示顺序：主机 → 末端 → 水力设备 → 蓄能设备 → 阀件仪表 → 风系统
COMPONENTS = [
    ("冷水机组",        "Chiller",                 c_chiller),
    ("冷却塔",          "Cooling Tower",           c_cooling_tower),
    ("空气处理机组 AHU", "Air Handling Unit (AHU)", c_ahu),
    ("风机盘管 FCU",    "Fan Coil Unit (FCU)",     c_fcu),
    ("循环水泵",        "Circulation Pump",        c_pump),
    ("板式换热器",      "Plate Heat Exchanger",    c_plate_hx),
    ("蓄冰槽",          "Ice Storage Tank",        c_ice_tank),
    ("蓄冷罐",          "Chilled Water Tank",      c_water_tank),
    ("蝶阀",            "Butterfly Valve",         c_butterfly),
    ("截止阀",          "Globe Valve",             c_globe),
    ("过滤器",          "Strainer / Filter",       c_filter),
    ("压力表",          "Pressure Gauge",          c_gauge),
    ("温度传感器",      "Temperature Sensor",      c_temp),
    ("风管风口",        "Duct Outlet / Diffuser",  c_duct_outlet),
    ("消声器",          "Duct Silencer",           c_silencer),
    ("软接头",          "Flexible Connector",      c_flex),
]


# ---------------------------------------------------------------- 库文件生成

def make_item(name, fn, zh=True):
    """把一个元件包装成 libraryItem（元素分组 + 归零到原点）。"""
    gid = uuid.uuid4().hex[:12]
    els = fn(zh)
    minx = min(e["x"] for e in els)
    miny = min(e["y"] for e in els)
    for e in els:
        e["x"] = round(e["x"] - minx, 2)
        e["y"] = round(e["y"] - miny, 2)
        e["groupIds"] = [gid]           # 官方要求：同一元件内部元素成组
    return {
        "id": uuid.uuid4().hex[:20],
        "status": "published",
        "elements": els,
        "created": NOW,
        "name": name,
    }


def build_library(zh, path, lib_name):
    items = [make_item(n_zh if zh else n_en, fn, zh) for n_zh, n_en, fn in COMPONENTS]
    data = {
        "type": "excalidrawlib",
        "version": 2,
        "source": "https://github.com/hon668/hvac-excalidraw-library",
        "libraryItems": items,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[OK] %s  (%d items)" % (path.relative_to(ROOT), len(items)))
    return items


def shift(els, dx, dy, group=True):
    """平移一批元素；group=True 时给这批元素打上同一个分组 ID。

    分组很重要：示例图纸里每个设备实例都应该能**整体拖动**，
    否则挪一台水泵要按住 Shift 点 15 次。库文件与示例图都走这个函数，行为保持一致。
    """
    out = copy.deepcopy(els)
    gid = uuid.uuid4().hex[:12] if group else None
    for e in out:
        e["x"] = round(e["x"] + dx, 2)
        e["y"] = round(e["y"] + dy, 2)
        if group:
            e["groupIds"] = [gid]
    return out


# ---------------------------------------------------------------- 示例图纸

def example_system():
    """示例 1：冷冻水系统原理图（冷机 → 阀 → 过滤器 → 泵 → 末端 → 回水）

    布局说明（坐标是设计过的，别随手改，改完要重新渲染预览确认管线接得上）：
      供水干管 y = 168  →  冷机右上出口 → 蝶阀 → 过滤器 → 泵 → 立管 x = 860
      末端供水支管 y = 430 → 软接头 → 下接 AHU / FCU 顶部
      回水干管 y = 600（虚线）→ 左侧 x = 120 上行 → 回冷机左侧入口
    """
    els = []
    els.append(text(40, 0, "冷冻水系统原理图（示例）", 24))
    els.append(text(40, 42, "本图由 hvac-excalidraw-library 元件拼装，可直接二次编辑", 14, GRAY))

    # ---- 设备（供水干管串在 y = 168 这条轴上）----
    els += shift(c_chiller(True), 160, 120)      # 冷机：出水 (332,168)，回水 (160,168)
    els += shift(c_butterfly(True), 400, 138)    # 蝶阀：轴 y = 168
    els += shift(c_filter(True), 506, 147)       # 过滤器：轴 y = 168
    els += shift(c_pump(True), 628, 131)         # 水泵：轴 y = 168，出口 (758,168)
    els += shift(c_gauge(True), 800, 100)        # 压力表：接管落在供水管上
    els += shift(c_temp(True), 332, 168)         # 供水温度测点（套管插在管上）

    # ---- 末端 ----
    els += shift(c_ahu(True), 620, 470)          # AHU
    els += shift(c_fcu(True), 200, 470)          # FCU
    els += shift(c_flex(True), 440, 402)         # 软接头：轴 y = 430（末端供水支管上）
    els += shift(c_temp(True), 380, 600)         # 回水温度测点

    # ---- 供水管路（实线蓝）----
    els.append(polyline([[332, 168], [400, 168]], stroke=BLUE, sw=3))
    els.append(polyline([[470, 168], [506, 168]], stroke=BLUE, sw=3))
    els.append(polyline([[592, 168], [628, 168]], stroke=BLUE, sw=3))
    els.append(polyline([[758, 168], [940, 168], [940, 430]], stroke=BLUE, sw=3))   # 出水立管
    els.append(polyline([[940, 430], [276, 430]], stroke=BLUE, sw=3))               # 末端供水支管
    els.append(polyline([[742, 430], [742, 470]], stroke=BLUE, sw=3))               # 接 AHU
    els.append(polyline([[276, 430], [276, 470]], stroke=BLUE, sw=3))               # 接 FCU
    els.append(arrow([[520, 168], [560, 168]], stroke=BLUE, sw=2))                  # 流向指示

    # ---- 回水管路（虚线蓝）----
    els.append(polyline([[742, 550], [742, 600]], stroke=BLUE, sw=3, dashed=True))
    els.append(polyline([[276, 542], [276, 600]], stroke=BLUE, sw=3, dashed=True))
    els.append(polyline([[742, 600], [120, 600], [120, 168], [160, 168]], stroke=BLUE, sw=3, dashed=True))
    els.append(arrow([[640, 600], [590, 600]], stroke=BLUE, sw=2, dashed=True))

    # ---- 文字标注 ----
    els.append(text(198, 100, "供 7℃", 16, BLUE))
    els.append(text(500, 620, "回 12℃", 16, BLUE))
    els.append(text(966, 300, "供水立管", 15, BLUE))
    els.append(text(40, 340, "回水", 16, BLUE))
    els.append(text(40, 470, "空调末端", 16, GRAY))
    els.append(text(40, 505, "（AHU / FCU）", 14, GRAY))
    return els


def example_duct():
    """示例 2：空调箱风路接管示意（AHU → 软接头 → 消声器 → 干管 → 风口）

    风管轴统一放在 y = 180。
    """
    els = []
    els.append(text(40, 0, "空调箱（AHU）风路接管示意（示例）", 24))
    els.append(text(40, 42, "风管段串联示意：软接头减振 → 消声器降噪 → 风口送风", 14, GRAY))

    els += shift(c_ahu(True), 180, 140)          # AHU：送风口 (424,180)
    els += shift(c_flex(True), 470, 152)         # 软接头：轴 y = 180
    els += shift(c_silencer(True), 620, 153)     # 消声器：轴 y = 180
    els += shift(c_duct_outlet(True), 852, 420)  # 风口 1（中心 x = 900）
    els += shift(c_duct_outlet(True), 1032, 420) # 风口 2（中心 x = 1080）

    # 风管（实线绿）
    els.append(polyline([[424, 180], [452, 180]], stroke=GREEN, sw=3))
    els.append(polyline([[578, 180], [600, 180]], stroke=GREEN, sw=3))
    els.append(polyline([[800, 180], [900, 180], [900, 420]], stroke=GREEN, sw=3))
    els.append(polyline([[900, 330], [1080, 330], [1080, 420]], stroke=GREEN, sw=3))
    els.append(arrow([[510, 180], [560, 180]], stroke=GREEN, sw=2))
    els.append(arrow([[900, 250], [900, 300]], stroke=GREEN, sw=2))

    # 标注
    els.append(text(300, 96, "新风 / 回风", 16, GREEN))
    els.append(text(470, 118, "软接头", 15, GREEN))
    els.append(text(640, 118, "消声器", 15, GREEN))
    els.append(text(920, 240, "送风干管", 15, GREEN))
    els.append(text(1100, 350, "支管", 15, GREEN))
    els.append(text(852, 560, "送风口（干管直连 + 支管侧送）", 15, GRAY))
    return els


def example_ice():
    """示例 3：冰蓄冷系统原理图（冷却塔 + 冷机 + 蓄冰槽 + 板换 + 蓄冷罐）

    三个环路（配色/线型见右上角图例）：
        冷却水环路（橙实线）：冷却塔 → 循环水泵 → 冷机冷凝器 → 蝶阀 → 压力表 → 回冷却塔
        乙二醇环路（蓝实线）：冷机蒸发器 → 乙二醇泵 → 蓄冰槽盘管 → 板换一次侧 → 回冷机
        冷冻水环路（蓝虚线）：板换二次侧 → 蓄冷罐 / 用户侧 → 回板换

    坐标是逐个标定的，每条管线端点都精确落在元件接管端头上（见下方注释里的端头坐标）。
    改坐标前先读注释里的锚点，改完必须重新渲染预览，确认管线仍然接通、没有压字。
    """
    els = []
    els.append(text(40, 0, "冰蓄冷系统原理图（示例）", 24))
    els.append(text(40, 42, "冷却塔 · 冷水机组 · 蓄冰槽 · 板式换热器 · 蓄冷罐 五种设备同图拼装", 14, GRAY))

    # ==================== 设备（注释内为该元件接管端头的绝对坐标）====================
    els += shift(c_cooling_tower(True), 150, 90)   # 出塔 (116,244) / 回水进塔 (340,160)
    els += shift(c_chiller(True), 300, 420)        # 冷却水 进(270,481) 出(502,481) / 冷冻水 进(270,527) 出(502,527)
    els += shift(c_pump(True), 85, 444)            # 冷却水泵 进(85,481) 出(215,481)
    els += shift(c_butterfly(True), 380, 130)      # 蝶阀 进(380,160) 出(450,160)
    els += shift(c_gauge(True), 550, 692)          # 压力表 接管落在 y=760 乙二醇回水管上（避开蝶阀）
    els += shift(c_pump(True), 520, 490)           # 乙二醇泵 进(520,527) 出(650,527)  ← 出口朝右，顺流向
    els += shift(c_ice_tank(True), 720, 501)       # 蓄冰槽 盘管进(686,527) 出(936,593)
    els += shift(c_plate_hx(True), 972, 567)       # 板换 一次侧 进(936,593) 出(936,661) / 二次侧 上口(1104,593) 下口(1104,661)
    els += shift(c_water_tank(True), 1240, 565)    # 蓄冷罐 上口(1206,593) 下口(1206,717)
    els += shift(c_temp(True), 250, 760)           # 温度测点落在 y=760 的乙二醇回水管上
    els += shift(c_flex(True), 330, 732)           # 软接头 轴 y=760 进(312,760) 出(438,760)

    # ==================== 冷却水环路（橙实线）====================
    els.append(polyline([[116, 244], [116, 481], [85, 481]], stroke=ORANGE, sw=3))              # 塔出水 → 冷却水泵
    els.append(polyline([[215, 481], [270, 481]], stroke=ORANGE, sw=3))                         # 泵 → 冷凝器进
    els.append(polyline([[502, 481], [508, 481], [508, 160], [450, 160]], stroke=ORANGE, sw=3))  # 冷凝器出 → 蝶阀
    els.append(polyline([[340, 160], [380, 160]], stroke=ORANGE, sw=3))                         # 蝶阀出 → 回冷却塔
    els.append(arrow([[508, 300], [508, 240]], stroke=ORANGE, sw=2))                            # 回水上行
    els.append(arrow([[374, 160], [354, 160]], stroke=ORANGE, sw=2))                            # 回水入塔

    # ==================== 乙二醇环路（蓝实线）====================
    els.append(polyline([[502, 527], [520, 527]], stroke=BLUE, sw=3))                           # 蒸发器出 → 泵进口
    els.append(polyline([[650, 527], [686, 527]], stroke=BLUE, sw=3))                           # 泵出口 → 蓄冰槽盘管
    els.append(polyline([[936, 661], [900, 661], [900, 760], [438, 760]], stroke=BLUE, sw=3))   # 板换一次侧出 → 下行
    els.append(polyline([[312, 760], [230, 760], [230, 527], [270, 527]], stroke=BLUE, sw=3))   # → 蒸发器进
    els.append(arrow([[652, 527], [678, 527]], stroke=BLUE, sw=2))                              # 制冰流向
    els.append(arrow([[500, 760], [480, 760]], stroke=BLUE, sw=2))                              # 回冷机流向

    # ==================== 冷冻水环路（蓝虚线）====================
    els.append(polyline([[1104, 593], [1206, 593]], stroke=BLUE, sw=3, dashed=True))            # 板换二次侧 → 蓄冷罐上口
    els.append(polyline([[1206, 717], [1195, 717], [1195, 661], [1104, 661]],
                        stroke=BLUE, sw=3, dashed=True))                                        # 蓄冷罐下口 → 板换二次侧
    els.append(arrow([[1140, 593], [1170, 593]], stroke=BLUE, sw=2, dashed=True))               # 供 7℃
    els.append(arrow([[1195, 692], [1195, 674]], stroke=BLUE, sw=2, dashed=True))               # 回 12℃

    # ==================== 标注 ====================
    els.append(text(120, 300, "冷却水供水", 15, ORANGE))
    els.append(text(520, 250, "冷却水回水", 15, ORANGE))
    els.append(text(690, 736, "乙二醇回水", 15, BLUE))
    els.append(text(1120, 556, "供 7℃", 15, BLUE))
    els.append(text(1120, 676, "回 12℃", 15, BLUE))

    # ==================== 图例（右上角空白区）====================
    els.append(text(700, 10, "图例：", 15, GRAY))
    els.append(text(748, 10, "橙实线 = 冷却水环路（冷却塔 ⇄ 冷凝器）", 15, ORANGE))
    els.append(text(748, 36, "蓝实线 = 乙二醇环路（蒸发器 ⇄ 蓄冰槽 / 板换一次侧）", 15, BLUE))
    els.append(text(748, 62, "蓝虚线 = 冷冻水环路（板换二次侧 ⇄ 蓄冷罐 / 用户侧）", 15, BLUE))
    return els


def write_excalidraw(path, elements, title):
    data = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://github.com/hon668/hvac-excalidraw-library",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff",
            "name": title,
        },
        "files": {},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[OK] %s  (%d elements)" % (path.relative_to(ROOT), len(elements)))


# ---------------------------------------------------------------- SVG 预览

def _jitter(v, amp=0.7):
    return v + RND.uniform(-amp, amp)


def _poly_pts(e):
    """把元素转成绝对坐标点串，用于 SVG 预览（带轻微抖动模拟手绘）。"""
    t = e["type"]
    x, y, w, h = e["x"], e["y"], e["width"], e["height"]
    if t in ("line", "arrow"):
        return [(x + p[0], y + p[1]) for p in e["points"]]
    if t == "rectangle":
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    if t == "diamond":
        return [(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h), (x, y + h / 2), (x + w / 2, y)]
    if t == "ellipse":
        import math
        cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2
        return [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
                for a in range(0, 361, 15)]
    return []


def element_to_svg(e):
    """把单个 Excalidraw 元素转成 SVG 片段。"""
    if e["type"] == "text":
        anchor = "middle" if e["textAlign"] == "center" else "start"
        tx = e["x"] + (e["width"] / 2 if anchor == "middle" else 0)
        out = []
        for i, line in enumerate(e["text"].split("\n")):
            out.append(
                '<text x="%.2f" y="%.2f" font-size="%d" fill="%s" text-anchor="%s" '
                'font-family="Virgil, Comic Sans MS, Segoe Print, Microsoft YaHei, sans-serif">%s</text>'
                % (tx, e["y"] + e["fontSize"] * (1 + i * 1.25), e["fontSize"],
                   e["strokeColor"], anchor, _esc(line))
            )
        return "".join(out)

    pts = _poly_pts(e)
    if not pts:
        return ""
    d = " ".join("%.2f,%.2f" % (_jitter(px), _jitter(py)) for px, py in pts)
    fill = e["backgroundColor"] if e["backgroundColor"] != "transparent" else "none"
    fill_op = 0.55 if fill != "none" else 1
    dash = ' stroke-dasharray="8 6"' if e["strokeStyle"] == "dashed" else ""
    s = ('<polyline points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
         'stroke-width="%.1f"%s stroke-linejoin="round" stroke-linecap="round"/>'
         % (d, fill, fill_op, e["strokeColor"], e["strokeWidth"], dash))
    if e["type"] == "arrow":
        lx, ly = pts[-1]
        px, py = pts[-2] if len(pts) > 1 else pts[-1]
        import math
        ang = math.atan2(ly - py, lx - px)
        size = 11
        p1 = (lx - size * math.cos(ang - 0.42), ly - size * math.sin(ang - 0.42))
        p2 = (lx - size * math.cos(ang + 0.42), ly - size * math.sin(ang + 0.42))
        s += ('<polyline points="%.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="none" stroke="%s" '
              'stroke-width="%.1f"/>' % (p1[0], p1[1], lx, ly, p2[0], p2[1],
                                         e["strokeColor"], e["strokeWidth"]))
    return s


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render_svg(elements, path, title="", pad=40, scale=1.0,
               bg="#ffffff", title_color="#1e1e1e"):
    if not elements:
        return (0, 0)
    minx = min(e["x"] for e in elements) - pad
    miny = min(e["y"] for e in elements) - pad
    maxx = max(e["x"] + e["width"] for e in elements) + pad
    maxy = max(e["y"] + e["height"] for e in elements) + pad
    w, h = int(maxx - minx), int(maxy - miny)
    body = "".join(element_to_svg(e) for e in elements)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f %.0f" width="%.0f" height="%.0f">'
        '<title>%s</title>'
        '<rect width="100%%" height="100%%" fill="%s"/>'
        '<g transform="translate(%.2f,%.2f) scale(%.3f)">%s</g>'
        '</svg>' % (w, h, w * scale, h * scale, _esc(title), bg, -minx, -miny, 1.0, body)
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    print("[OK] %s  (%.0fx%.0f)" % (path.relative_to(ROOT), w * scale, h * scale))
    return (w, h)


# 本机可用的无头浏览器（用于把 SVG 预览转成 PNG，官方库 PR 必须要 PNG）
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
]


def render_png(svg_path, png_path, w, h):
    """调用本机 Chrome/Edge 无头模式，把 SVG 截图成 PNG（官方库提交必需）。"""
    import subprocess
    exe = next((b for b in BROWSERS if Path(b).exists()), None)
    if not exe:
        print("[SKIP] 未找到 Chrome/Edge，请手动把 %s 转成 PNG" % svg_path.name)
        return False
    png_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [exe, "--headless", "--disable-gpu", "--hide-scrollbars",
           "--default-background-color=FFFFFFFF",
           "--screenshot=%s" % str(png_path),
           "--window-size=%d,%d" % (w, h),
           svg_path.resolve().as_uri()]
    subprocess.run(cmd, capture_output=True)
    ok = png_path.exists()
    print("[%s] %s" % ("OK" if ok else "FAIL", png_path.relative_to(ROOT)))
    return ok


def preview_components(zh=True):
    """把所有元件排成 3 列网格，生成总览预览图（元件自带标签，不再重复标注）。"""
    cols, gap_x, gap_y = 3, 150, 90
    col_w, row_h = 340, 200
    els = []
    for i, (n_zh, n_en, fn) in enumerate(COMPONENTS):
        r, c = divmod(i, cols)
        dx = 60 + c * (col_w + gap_x)
        dy = 60 + r * (row_h + gap_y)
        els += shift(fn(zh), dx, dy)
    return els


# ---------------------------------------------------------------- 主流程

def main():
    print("=" * 62)
    print("hvac-excalidraw-library builder  v%s" % VERSION)
    print("=" * 62)

    build_library(True, LIB_DIR / ("hvac-excalidraw-library-zh-v%s.excalidrawlib" % VERSION),
                  "HVAC 暖通手绘素材库（中文）")
    build_library(False, LIB_DIR / ("hvac-excalidraw-library-en-v%s.excalidrawlib" % VERSION),
                  "HVAC Hand-drawn Library (EN)")

    write_excalidraw(EX_DIR / "01-chilled-water-system.excalidraw",
                     example_system(), "冷冻水系统原理图")
    write_excalidraw(EX_DIR / "02-ahu-duct-layout.excalidraw",
                     example_duct(), "空调箱风路接管示意")
    write_excalidraw(EX_DIR / "03-ice-storage-system.excalidraw",
                     example_ice(), "冰蓄冷系统原理图")

    # 预览图（中文）
    size_zh = render_svg(preview_components(True), ASSETS_DIR / "preview-components.svg",
                         "HVAC Excalidraw Library - 全部元件")
    render_svg(example_system(), ASSETS_DIR / "preview-example-system.svg",
               "冷冻水系统原理图（示例）")
    render_svg(example_duct(), ASSETS_DIR / "preview-example-duct.svg",
               "空调箱风路接管示意（示例）")
    render_svg(example_ice(), ASSETS_DIR / "preview-example-ice.svg",
               "冰蓄冷系统原理图（示例）")

    # 预览图（英文，提交官方库用）
    size_en = render_svg(preview_components(False), ASSETS_DIR / "preview-components-en.svg",
                         "HVAC Hand-drawn Excalidraw Library")

    # PNG：README 图片 + 官方库 PR 必需的预览图
    render_png(ASSETS_DIR / "preview-components.svg",
               ASSETS_DIR / "preview-components.png", *size_zh)
    render_png(ASSETS_DIR / "preview-components-en.svg",
               ASSETS_DIR / "preview-components-en.png", *size_en)

    # 官方库提交目录（英文库 + 英文预览图，路径需与 libraries.json 中的 source/preview 一致）
    sub = ROOT / "submission" / "hon668"
    sub.mkdir(parents=True, exist_ok=True)
    en_lib = LIB_DIR / ("hvac-excalidraw-library-en-v%s.excalidrawlib" % VERSION)
    (sub / "hvac-handdrawn-components.excalidrawlib").write_text(
        en_lib.read_text(encoding="utf-8"), encoding="utf-8")
    import shutil
    png_en = ASSETS_DIR / "preview-components-en.png"
    if png_en.exists():
        shutil.copyfile(png_en, sub / "hvac-handdrawn-components.png")
    print("[OK] submission/hon668/  (英文库 + 预览图，可直接提 PR)")

    print("-" * 62)
    print("完成。把 library/ 里的 .excalidrawlib 拖进 Excalidraw 即可使用。")


if __name__ == "__main__":
    main()

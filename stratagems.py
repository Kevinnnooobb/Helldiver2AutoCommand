"""
绝地潜兵2 (Helldivers 2) 战备数据定义
Complete Stratagem definitions: model, name, command codes, description.

分类：任务战备、轨道火力、飞鹰、支援武器、哨戒炮、地雷和emplacements、背包、载具
"""

# Direction constants
UP = "↑"
DOWN = "↓"
LEFT = "←"
RIGHT = "→"

# Stratagem categories
CATEGORY_MISSION = "任务战备"
CATEGORY_ORBITAL = "轨道火力"
CATEGORY_EAGLE = "飞鹰"
CATEGORY_SUPPORT_WEAPONS = "支援武器"
CATEGORY_SENTRIES = "哨戒炮"
CATEGORY_MINES_EMPLACEMENTS = "地雷，盾和手操炮台"
CATEGORY_BACKPACKS = "背包"
CATEGORY_VEHICLES = "载具"

STRATAGEMS = [
    # ========== 任务战备 — 通用 ==========
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "增援",
        "command": [UP, DOWN, RIGHT, LEFT, UP],
        "description": "呼叫 Helldiver 复活",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "SOS 信标",
        "command": [UP, DOWN, RIGHT, UP],
        "description": "提供任务优先与公开，仅主机可用",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "补给",
        "command": [DOWN, DOWN, UP, RIGHT],
        "description": "呼叫补给",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "飞鹰重新装填",
        "command": [UP, UP, LEFT, UP, RIGHT],
        "description": "令飞鹰返回超级驱逐舰补给弹药",
    },

    # ========== 任务战备 — 目标 ==========
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "SSSD 交付",
        "command": [DOWN, DOWN, DOWN, UP, UP],
        "description": "呼叫 SSSD 硬盘",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "勘探钻机",
        "command": [DOWN, DOWN, LEFT, RIGHT, DOWN, DOWN],
        "description": "地质勘测任务主目标",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "超级地球旗帜",
        "command": [DOWN, UP, DOWN, UP],
        "description": "升旗任务主目标",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "地狱炸弹",
        "command": [DOWN, UP, LEFT, DOWN, UP, RIGHT, DOWN, UP],
        "description": "呼叫地狱炸弹",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "上传数据",
        "command": [LEFT, RIGHT, UP, UP, UP],
        "description": "上传逃生舱数据副目标",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "地震探测器",
        "command": [UP, UP, LEFT, RIGHT, DOWN, DOWN],
        "description": "地质勘测副目标",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "暗流体容器",
        "command": [UP, LEFT, RIGHT, DOWN, UP, UP],
        "description": "部署暗流体任务专属，充当强化喷射背包",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "构造钻机",
        "command": [UP, DOWN, UP, DOWN, UP, DOWN],
        "description": "部署暗流体任务专属，需装填暗流体容器并防守",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "蜂巢破碎钻机",
        "command": [LEFT, UP, DOWN, RIGHT, DOWN, DOWN],
        "description": "核弹巢穴任务主目标",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "货物集装箱",
        "command": [UP, UP, DOWN, DOWN, RIGHT, DOWN],
        "description": "用于收纳聚变电池和高级铂金",
    },

    # ========== 任务战备 — 其他 ==========
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "轨道照明弹",
        "command": [RIGHT, RIGHT, LEFT, LEFT],
        "description": "仅在超级驱逐舰战备英雄小游戏中出现",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "SEAF 火炮",
        "command": [RIGHT, UP, UP, DOWN],
        "description": "完成 SEAF 火炮副目标后解锁，效果取决于装填弹种",
    },
    {
        "category": CATEGORY_MISSION,
        "model": "无型号",
        "name": "呼叫超级驱逐舰",
        "command": [UP, UP, DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT],
        "description": "突击任务中呼叫超级驱逐舰支援 1 分钟",
    },

    # ========== 轨道火力 ==========
    {
        "category": CATEGORY_ORBITAL,
        "model": "无型号",
        "name": "轨道加特林火力网",
        "command": [RIGHT, DOWN, LEFT, UP, UP],
        "description": "轨道自动炮高爆弹幕",
    },
    {
        "category": CATEGORY_ORBITAL,
        "model": "无型号",
        "name": "轨道空爆攻击",
        "command": [RIGHT, RIGHT, RIGHT],
        "description": "空中爆炸弹片雨",
    },
    {
        "category": CATEGORY_ORBITAL,
        "model": "无型号",
        "name": "轨道120MM高爆弹火力网",
        "command": [RIGHT, RIGHT, DOWN, LEFT, RIGHT, DOWN],
        "description": "小范围精确高爆炮击",
    },
    {
        "category": CATEGORY_ORBITAL,
        "model": "无型号",
        "name": "轨道380MM高爆弹火力网",
        "command": [RIGHT, DOWN, UP, UP, LEFT, DOWN, DOWN],
        "description": "大范围长时间高爆炮击",
    },
    {
        "category": CATEGORY_ORBITAL,
        "model": "无型号",
        "name": "轨道游走火力网",
        "command": [RIGHT, DOWN, RIGHT, DOWN, RIGHT, DOWN],
        "description": "线性推进弹幕",
    },
    {
        "category": CATEGORY_ORBITAL,
        "model": "无型号",
        "name": "轨道激光炮",
        "command": [RIGHT, DOWN, UP, RIGHT, DOWN],
        "description": "激光扫射指定区域",
    },
    {
        "category": CATEGORY_ORBITAL,
        "model": "无型号",
        "name": "轨道凝固汽油弹火力网",
        "command": [RIGHT, RIGHT, DOWN, LEFT, RIGHT, UP],
        "description": "大范围凝固汽油弹轰炸",
    },
    {
        "category": CATEGORY_ORBITAL,
        "model": "无型号",
        "name": "轨道炮攻击",
        "command": [RIGHT, UP, DOWN, DOWN, RIGHT],
        "description": "自动瞄准最大目标轨道炮",
    },

    # ========== 飞鹰 ==========
    {
        "category": CATEGORY_EAGLE,
        "model": "无型号",
        "name": "\"飞鹰\"机枪扫射",
        "command": [UP, RIGHT, RIGHT],
        "description": "飞鹰机扫射轻型目标",
    },
    {
        "category": CATEGORY_EAGLE,
        "model": "无型号",
        "name": "\"飞鹰\"空袭",
        "command": [UP, RIGHT, DOWN, RIGHT],
        "description": "飞鹰投放爆炸地毯",
    },
    {
        "category": CATEGORY_EAGLE,
        "model": "无型号",
        "name": "\"飞鹰\"集束炸弹",
        "command": [UP, RIGHT, DOWN, DOWN, RIGHT],
        "description": "飞鹰定点集束爆炸",
    },
    {
        "category": CATEGORY_EAGLE,
        "model": "无型号",
        "name": "\"飞鹰\"凝固汽油弹空袭",
        "command": [UP, RIGHT, DOWN, UP],
        "description": "飞鹰投放火墙",
    },
    {
        "category": CATEGORY_EAGLE,
        "model": "无型号",
        "name": "\"飞鹰\"烟雾攻击",
        "command": [UP, RIGHT, UP, DOWN],
        "description": "飞鹰投放烟雾",
    },
    {
        "category": CATEGORY_EAGLE,
        "model": "无型号",
        "name": "\"飞鹰\"110MM火箭巢",
        "command": [UP, RIGHT, UP, LEFT],
        "description": "飞鹰火箭弹攻击",
    },
    {
        "category": CATEGORY_EAGLE,
        "model": "无型号",
        "name": "\"飞鹰\"500KG炸弹",
        "command": [UP, RIGHT, DOWN, DOWN, DOWN],
        "description": "飞鹰大型炸弹",
    },

    # ========== 支援武器 ==========
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "MG-43",
        "name": "机枪",
        "command": [DOWN, LEFT, DOWN, UP, RIGHT],
        "description": "固定机枪，高火力但后坐力大、精度较低",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "APW-1",
        "name": "反器材步枪",
        "command": [DOWN, LEFT, RIGHT, UP, DOWN],
        "description": "高口径狙击步枪，对轻装甲有效，需瞄准",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "M-105",
        "name": "盟友",
        "command": [DOWN, LEFT, DOWN, UP, UP, LEFT],
        "description": "紧凑型轻机枪，易用、换弹快、威力较低",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "EAT-17",
        "name": "消耗性反坦克",
        "command": [DOWN, DOWN, LEFT, UP, RIGHT],
        "description": "单次使用的反坦克武器",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "GR-8",
        "name": "无后坐力炮",
        "command": [DOWN, LEFT, RIGHT, RIGHT, LEFT],
        "description": "无后坐力炮，有效对车辆装甲",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "FLAM-40",
        "name": "火焰喷射器",
        "command": [DOWN, LEFT, UP, DOWN, UP],
        "description": "近距燃烧武器，会点燃目标与地形",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "AC-8",
        "name": "机炮",
        "command": [DOWN, LEFT, DOWN, UP, UP, RIGHT],
        "description": "全自动机炮，对轻装甲有效",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "MG-206",
        "name": "重机枪",
        "command": [DOWN, LEFT, UP, DOWN, DOWN],
        "description": "强力机枪，后坐力强",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "RL-77",
        "name": "空爆火箭弹发射器",
        "command": [DOWN, UP, UP, LEFT, RIGHT],
        "description": "发射空爆火箭及子弹",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "MLS-4X",
        "name": "突击兵",
        "command": [DOWN, LEFT, UP, DOWN, RIGHT],
        "description": "一次性激光制导导弹发射器",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "RS-422",
        "name": "磁轨炮",
        "command": [DOWN, RIGHT, DOWN, UP, LEFT, RIGHT],
        "description": "实验性穿甲武器，需蓄能",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "FAF-14",
        "name": "飞矛",
        "command": [DOWN, DOWN, UP, DOWN, DOWN],
        "description": "自导反坦克导弹，需锁定目标",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "StA-X3",
        "name": "W.A.S.P.发射器",
        "command": [DOWN, DOWN, UP, DOWN, RIGHT],
        "description": "七枚追踪导弹发射器",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "GL-21",
        "name": "榴弹发射器",
        "command": [DOWN, LEFT, UP, LEFT, DOWN],
        "description": "对装甲步兵有效",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "LAS-98",
        "name": "激光大炮",
        "command": [DOWN, LEFT, DOWN, UP, LEFT],
        "description": "连续激光武器",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "ARC-3",
        "name": "电弧发射器",
        "command": [DOWN, RIGHT, DOWN, UP, LEFT, LEFT],
        "description": "电弧武器近距",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "LAS-99",
        "name": "类星体加农炮",
        "command": [DOWN, DOWN, UP, LEFT, RIGHT],
        "description": "蓄能爆炸能量炮",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "TX-41",
        "name": "灭菌器",
        "command": [DOWN, LEFT, UP, DOWN, LEFT],
        "description": "腐蚀化学雾化武器",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "PLAS-45",
        "name": "纪元",
        "command": [DOWN, LEFT, UP, LEFT, RIGHT],
        "description": "蓄能等离子武器",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "S-11",
        "name": "矛枪",
        "command": [DOWN, RIGHT, DOWN, LEFT, UP, RIGHT],
        "description": "反坦克鱼叉枪",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "M-1000",
        "name": "重装机枪",
        "command": [DOWN, LEFT, RIGHT, DOWN, UP, UP],
        "description": "带式供弹旋转机枪",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "EAT-700",
        "name": "消耗性凝固汽油弹",
        "command": [DOWN, DOWN, LEFT, UP, LEFT],
        "description": "单发凝固汽油弹",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "GL-52",
        "name": "缓和使者",
        "command": [DOWN, RIGHT, UP, LEFT, RIGHT],
        "description": "人道榴弹发射器",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "CQC-9",
        "name": "除叶工具",
        "command": [DOWN, LEFT, RIGHT, RIGHT, DOWN],
        "description": "清场工具",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "CQC-20",
        "name": "破门锤",
        "command": [DOWN, LEFT, RIGHT, LEFT, UP],
        "description": "破坏工具",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "EAT-411",
        "name": "荡平者",
        "command": [DOWN, DOWN, LEFT, UP, DOWN],
        "description": "高爆导弹",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "GL-28",
        "name": "弹链式榴弹发射器",
        "command": [DOWN, LEFT, UP, LEFT, UP, UP],
        "description": "连续榴弹火力",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "MS-11",
        "name": "单兵导弹发射井",
        "command": [DOWN, UP, RIGHT, DOWN, DOWN],
        "description": "单体强力导弹",
    },
    {
        "category": CATEGORY_SUPPORT_WEAPONS,
        "model": "CQC-1",
        "name": "唯一真旗",
        "command": [DOWN, LEFT, RIGHT, RIGHT, UP],
        "description": "仪式性旗帜",
    },

    # ========== 哨戒炮 ==========
    {
        "category": CATEGORY_SENTRIES,
        "model": "A/MG-43",
        "name": "哨戒机枪",
        "command": [DOWN, UP, RIGHT, RIGHT, UP],
        "description": "自动机枪哨戒",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "A/G-16",
        "name": "加特林哨戒炮",
        "command": [DOWN, UP, RIGHT, LEFT],
        "description": "高射速自动炮",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "A/M-12",
        "name": "迫击哨戒炮",
        "command": [DOWN, UP, RIGHT, RIGHT, DOWN],
        "description": "高抛炮击",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "AX/AR-23",
        "name": "护卫犬",
        "command": [DOWN, UP, LEFT, UP, RIGHT, DOWN],
        "description": "护卫无人机",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "A/AC-8",
        "name": "自动哨戒炮",
        "command": [DOWN, UP, RIGHT, UP, LEFT, UP],
        "description": "远程反装甲炮",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "A/MLS-4X",
        "name": "火箭哨戒炮",
        "command": [DOWN, UP, RIGHT, RIGHT, LEFT],
        "description": "自动火箭塔",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "A/M-23",
        "name": "电磁冲击波迫击哨戒炮",
        "command": [DOWN, UP, RIGHT, DOWN, RIGHT],
        "description": "静态场迫击",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "A/FLAM-40",
        "name": "火焰喷射哨戒炮",
        "command": [DOWN, UP, RIGHT, DOWN, UP, UP],
        "description": "自动火焰塔",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "A/LAS-98",
        "name": "激光哨戒炮",
        "command": [DOWN, UP, RIGHT, DOWN, UP, RIGHT],
        "description": "激光塔防",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "AX/FLAM-75",
        "name": "热狗",
        "command": [DOWN, UP, LEFT, UP, LEFT, LEFT],
        "description": "火焰无人机",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "AX/TX-13",
        "name": "腐息",
        "command": [DOWN, UP, LEFT, UP, RIGHT, UP],
        "description": "腐蚀气体无人机",
    },
    {
        "category": CATEGORY_SENTRIES,
        "model": "AX/ARC-3 K-9",
        "name": "K-9",
        "command": [DOWN, UP, LEFT, UP, RIGHT, LEFT],
        "description": "人道无人机电弧武器",
    },

    # ========== 地雷和emplacements ==========
    {
        "category": CATEGORY_MINES_EMPLACEMENTS,
        "model": "MD-6",
        "name": "反步兵雷区",
        "command": [DOWN, LEFT, UP, RIGHT],
        "description": "防御反步兵地雷",
    },
    {
        "category": CATEGORY_MINES_EMPLACEMENTS,
        "model": "MD-I4",
        "name": "燃烧地雷",
        "command": [DOWN, LEFT, LEFT, DOWN],
        "description": "触发时点燃目标",
    },
    {
        "category": CATEGORY_MINES_EMPLACEMENTS,
        "model": "MD-17",
        "name": "反坦克地雷",
        "command": [DOWN, LEFT, UP, UP],
        "description": "强穿甲地雷",
    },
    {
        "category": CATEGORY_MINES_EMPLACEMENTS,
        "model": "MD-8",
        "name": "毒气地雷",
        "command": [DOWN, LEFT, LEFT, RIGHT],
        "description": "释放毒气减速",
    },
    {
        "category": CATEGORY_MINES_EMPLACEMENTS,
        "model": "E/MG-101",
        "name": "重机枪部署支架",
        "command": [DOWN, UP, LEFT, RIGHT, RIGHT, LEFT],
        "description": "载人重机枪支架",
    },
    {
        "category": CATEGORY_MINES_EMPLACEMENTS,
        "model": "FX-12",
        "name": "防护罩生成中继器",
        "command": [DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT],
        "description": "定点能量护盾",
    },
    {
        "category": CATEGORY_MINES_EMPLACEMENTS,
        "model": "ARC-3",
        "name": "特斯拉塔",
        "command": [DOWN, UP, RIGHT, UP, LEFT, RIGHT],
        "description": "近距电击防御塔",
    },
    {
        "category": CATEGORY_MINES_EMPLACEMENTS,
        "model": "E/AT-12",
        "name": "反坦克炮台",
        "command": [DOWN, UP, LEFT, RIGHT, RIGHT, RIGHT],
        "description": "载人反坦克炮",
    },

    # ========== 背包 ==========
    {
        "category": CATEGORY_BACKPACKS,
        "model": "LIFT-850",
        "name": "喷射背包",
        "command": [DOWN, UP, UP, DOWN, UP],
        "description": "增强跳跃能力（需充能）",
    },
    {
        "category": CATEGORY_BACKPACKS,
        "model": "LIFT-860",
        "name": "悬浮背包",
        "command": [DOWN, UP, UP, DOWN, LEFT, RIGHT],
        "description": "短时间悬浮飞行",
    },
    {
        "category": CATEGORY_BACKPACKS,
        "model": "SH-32",
        "name": "防护罩生成包",
        "command": [DOWN, UP, LEFT, RIGHT, LEFT, RIGHT],
        "description": "可穿戴球形护盾",
    },
    {
        "category": CATEGORY_BACKPACKS,
        "model": "SH-20",
        "name": "防弹护盾背包",
        "command": [DOWN, LEFT, DOWN, DOWN, UP, LEFT],
        "description": "单手弹道护盾",
    },
    {
        "category": CATEGORY_BACKPACKS,
        "model": "SH-51",
        "name": "定向护盾",
        "command": [DOWN, UP, LEFT, RIGHT, UP, UP],
        "description": "宽幅能量护盾",
    },
    {
        "category": CATEGORY_BACKPACKS,
        "model": "B-1",
        "name": "补给背包",
        "command": [DOWN, LEFT, DOWN, UP, UP, DOWN],
        "description": "弹药补给背包",
    },
    {
        "category": CATEGORY_BACKPACKS,
        "model": "AX/LAS-5",
        "name": "漫游车",
        "command": [DOWN, UP, LEFT, UP, RIGHT, RIGHT],
        "description": "自治激光无人机",
    },
    {
        "category": CATEGORY_BACKPACKS,
        "model": "LIFT-182",
        "name": "传送背包",
        "command": [DOWN, LEFT, RIGHT, DOWN, LEFT, RIGHT],
        "description": "短距微虫洞瞬移",
    },
    {
        "category": CATEGORY_BACKPACKS,
        "model": "B-100",
        "name": "便携式地狱火炸弹",
        "command": [DOWN, RIGHT, UP, UP, UP],
        "description": "背包式定时炸弹",
    },
    {
        "category": CATEGORY_BACKPACKS,
        "model": "B/MD",
        "name": "C4背包",
        "command": [DOWN, RIGHT, UP, UP, RIGHT, UP],
        "description": "六枚C4与遥控",
    },

    # ========== 载具 ==========
    {
        "category": CATEGORY_VEHICLES,
        "model": "EXO-45",
        "name": "爱国者外骨骼装甲",
        "command": [LEFT, DOWN, RIGHT, UP, LEFT, DOWN, DOWN],
        "description": "火箭 + 机炮外骨骼",
    },
    {
        "category": CATEGORY_VEHICLES,
        "model": "EXO-49",
        "name": "解放者外骨骼装甲",
        "command": [LEFT, DOWN, RIGHT, UP, LEFT, DOWN, UP],
        "description": "双机炮外骨骼",
    },
    {
        "category": CATEGORY_VEHICLES,
        "model": "M-102",
        "name": "快速侦察车",
        "command": [LEFT, DOWN, RIGHT, DOWN, RIGHT, DOWN, UP],
        "description": "快速机动载具",
    },
    {
        "category": CATEGORY_VEHICLES,
        "model": "TD-220",
        "name": "堡垒MK XVI",
        "command": [LEFT, DOWN, RIGHT, DOWN, LEFT, DOWN, UP, DOWN, UP],
        "description": "重型堡垒载具",
    },
]


def get_categories():
    """Return a list of unique category names in display order."""
    seen = set()
    categories = []
    for s in STRATAGEMS:
        cat = s["category"]
        if cat not in seen:
            seen.add(cat)
            categories.append(cat)
    return categories


def get_stratagems_by_category(category):
    """Return all stratagems belonging to the given category."""
    return [s for s in STRATAGEMS if s["category"] == category]


def search_stratagems(keyword):
    """Search stratagems by name, model, or description."""
    keyword = keyword.lower()
    return [
        s for s in STRATAGEMS
        if keyword in s["name"].lower()
        or keyword in s["model"].lower()
        or keyword in s["description"].lower()
    ]


def command_to_string(command):
    """Convert a command list to a display string."""
    return "".join(command)

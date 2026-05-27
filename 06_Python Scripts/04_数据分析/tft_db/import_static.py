"""
TFT Static Data Importer - 从 datatft.com 的剪藏数据导入静态游戏信息到 SQLite
包含：英雄、装备、羁绊、海克斯强化、神明恩赐系统
"""
import sqlite3
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from db_schema import get_conn, init_db

def create_static_tables(conn):
    """创建静态数据表"""
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS champions (
        name TEXT PRIMARY KEY,
        name_cn TEXT,
        cost INTEGER,
        traits TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS items (
        name TEXT PRIMARY KEY,
        name_cn TEXT,
        category TEXT,
        description TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS traits_ref (
        name TEXT PRIMARY KEY,
        name_cn TEXT,
        breakpoints TEXT,
        description TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS augments (
        name TEXT PRIMARY KEY,
        name_cn TEXT,
        tier TEXT,
        category TEXT,
        round_available TEXT,
        description TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS god_blessings (
        god_name TEXT,
        god_name_cn TEXT,
        tier INTEGER,
        blessing_index INTEGER,
        description TEXT,
        PRIMARY KEY (god_name, tier, blessing_index)
    )""")

    conn.commit()

# === 英雄数据 ===
CHAMPIONS = {
    # 1 费
    "Aatrox": ("亚托克斯", 1, ["Darkin", "Bastion"]),
    "Briar": ("贝蕾亚", 1, ["PsyOps", "Ravenous"]),
    "Caitlyn": ("凯特琳", 1, ["Sniper", "Lawkeeper"]),
    "Chogath": ("科加斯", 1, ["Primordian", "Behemoth"]),
    "Ezreal": ("伊泽瑞尔", 1, ["Chrono", "Ranger"]),
    "Leona": ("蕾欧娜", 1, ["Bastion", "Lawkeeper"]),
    "Lissandra": ("丽桑卓", 1, ["Primordian", "Sorcerer"]),
    "Nasus": ("内瑟斯", 1, ["Bastion", "Berserker"]),
    "Poppy": ("波比", 1, ["Woodland", "Bastion"]),
    "RekSai": ("雷克塞", 1, ["Primordian", "Berserker"]),
    "Talon": ("泰隆", 1, ["DarkStar", "Assassin"]),
    "Teemo": ("提莫", 1, ["Woodland", "Trickster"]),
    "TwistedFate": ("崔斯特", 1, ["Fortune", "Sorcerer"]),
    "Veigar": ("维迦", 1, ["DarkStar", "Sorcerer"]),

    # 2 费
    "Akali": ("阿卡丽", 2, ["PsyOps", "Assassin"]),
    "Belveth": ("卑尔维斯", 2, ["Void", "Ranger"]),
    "Gnar": ("纳尔", 2, ["Woodland", "Berserker"]),
    "Gragas": ("古拉加斯", 2, ["Berserker", "Sorcerer"]),
    "Gwen": ("格温", 2, ["ShadowIsles", "Sorcerer"]),
    "Jax": ("贾克斯", 2, ["Chrono", "Berserker"]),
    "Jinx": ("金克丝", 2, ["PsyOps", "Cannoneer"]),
    "Maokai": ("茂凯", 2, ["Woodland", "Bastion"]),
    "Milio": ("米利欧", 2, ["Woodland", "Mystic"]),
    "Mordekaiser": ("莫德凯撒", 2, ["DarkStar", "Bastion"]),
    "Pantheon": ("潘森", 2, ["Chrono", "Bastion"]),
    "Pyke": ("派克", 2, ["Rogue", "Assassin"]),
    "Zoe": ("佐伊", 2, ["Sorcerer", "Trickster"]),

    # 3 费
    "Aurora": ("阿萝拉", 3, ["StarGuardian", "Sorcerer"]),
    "Diana": ("黛安娜", 3, ["DarkStar", "Assassin"]),
    "Fizz": ("菲兹", 3, ["Chrono", "Trickster"]),
    "Illaoi": ("俄洛伊", 3, ["PsyOps", "Behemoth"]),
    "Kaisa": ("卡莎", 3, ["Void", "Ranger"]),
    "Lulu": ("璐璐", 3, ["Woodland", "Mystic"]),
    "MissFortune": ("厄运小姐", 3, ["Rogue", "Cannoneer"]),
    "Ornn": ("奥恩", 3, ["Berserker", "Artificer"]),
    "Rhaast": ("拉亚斯特", 3, ["Darkin", "Berserker"]),
    "Samira": ("莎弥拉", 3, ["PsyOps", "Ranger"]),
    "Urgot": ("厄加特", 3, ["Void", "Behemoth"]),
    "Viktor": ("维克托", 3, ["DarkStar", "Sorcerer"]),

    # 4 费
    "AurelionSol": ("奥瑞利安·索尔", 4, ["StarGuardian", "Sorcerer"]),
    "Corki": ("库奇", 4, ["Cannoneer", "Fortune"]),
    "Karma": ("卡尔玛", 4, ["Mystic", "Sorcerer"]),
    "Kindred": ("千珏", 4, ["ShadowIsles", "Ranger"]),
    "Leblanc": ("乐芙兰", 4, ["Sorcerer", "Trickster"]),
    "MasterYi": ("易", 4, ["Chrono", "Berserker"]),
    "Nami": ("娜美", 4, ["Mystic", "Sorcerer"]),
    "Nunu": ("努努和威朗普", 4, ["Woodland", "Berserker"]),
    "Rammus": ("拉莫斯", 4, ["Bastion", "Behemoth"]),
    "Riven": ("锐雯", 4, ["Chrono", "Berserker"]),
    "TahmKench": ("塔姆", 4, ["Fortune", "Behemoth"]),
    "Xayah": ("霞", 4, ["StarGuardian", "Ranger"]),

    # 5 费
    "Bard": ("巴德", 5, ["Mystic", "Traveller"]),
    "Blitzcrank": ("布里茨", 5, ["PsyOps", "Bastion"]),
    "Fiora": ("菲奥娜", 5, ["Challenger", "Lawkeeper"]),
    "Graves": ("格雷福斯", 5, ["Rogue", "Cannoneer"]),
    "Jhin": ("烬", 5, ["DarkStar", "Sniper"]),
    "Shen": ("慎", 5, ["Chrono", "Bastion"]),
    "Sona": ("娑娜", 5, ["Mystic", "Sorcerer"]),
    "Vex": ("薇古丝", 5, ["ShadowIsles", "Sorcerer"]),
    "Zed": ("劫", 5, ["PsyOps", "Assassin"]),
}

# === 装备数据 ===
ITEMS = {
    # 基础装备
    "BFSword": ("暴风大剑", "basic", "+10% 攻击力"),
    "RecurveBow": ("反曲之弓", "basic", "+10% 攻击速度"),
    "NeedlesslyLargeRod": ("无用大棒", "basic", "+10% 法术强度"),
    "TearoftheGoddess": ("女神之泪", "basic", "+10 法力值"),
    "ChainVest": ("锁子甲", "basic", "+20 护甲"),
    "NegatronCloak": ("负极斗篷", "basic", "+20 魔抗"),
    "GiantsBelt": ("巨人腰带", "basic", "+200 生命值"),
    "SparringGloves": ("拳套", "basic", "+20% 暴击率"),
    "Spatula": ("金铲铲", "basic", "特殊"),

    # 成装
    "Deathblade": ("死亡之刃", "completed", "攻击力叠加"),
    "GiantSlayer": ("巨人杀手", "completed", "对高生命值目标额外伤害"),
    "HextechGunblade": ("海克斯科技枪刃", "completed", "全能吸血"),
    "SpearofShojin": ("朔极之矛", "completed", "施法后回蓝"),
    "EdgeofNight": ("夜之锋刃", "completed", "低生命值时隐身"),
    "Bloodthirster": ("饮血剑", "completed", "物理吸血+护盾"),
    "SteraksGage": ("斯特拉克的挑战护手", "completed", "低生命值时获得护盾和攻击力"),
    "InfinityEdge": ("无尽之刃", "completed", "暴击率+暴击伤害"),
    "RedBuff": ("红霸符", "completed", "灼烧+重伤"),
    "GuinsoosRageblade": ("鬼索的狂暴之刃", "completed", "攻击叠加攻速"),
    "VoidStaff": ("虚空之杖", "completed", "法术穿透"),
    "TitansResolve": ("泰坦的坚决", "completed", "受击叠加属性"),
    "RunaansHurricane": ("飓风", "completed", "额外弹体"),
    "NashorsTooth": ("纳什之牙", "completed", "施法后加攻速"),
    "LastWhisper": ("最后的轻语", "completed", "护甲穿透"),
    "RabadonsDeathcap": ("灭世者的死亡之帽", "completed", "大量法术强度"),
    "ArchangelsStaff": ("大天使之杖", "completed", "施法叠加法强"),
    "CrownGuardian": ("冕卫", "completed", "护盾"),
    "IonicSpark": ("离子火花", "completed", "减敌人魔抗"),
    "Morellonomicon": ("莫雷洛秘典", "completed", "法术伤害附加重伤"),
    "JeweledGauntlet": ("珠光护手", "completed", "技能可暴击"),
    "BlueBuff": ("蓝霸符", "completed", "施法后回满法力"),
    "SunfireCape": ("日炎斗篷", "completed", "灼烧周围敌人"),
    "GargoyleStoneplate": ("石像鬼石板甲", "completed", "周围敌人越多越肉"),
    "WarmogsArmor": ("狂徒铠甲", "completed", "大量生命值+回血"),
    "DragonsClaw": ("巨龙之爪", "completed", "大量魔抗"),
    "ShroudofStillness": ("薄暮法袍", "completed", "开局减敌人攻速"),
    "Quicksilver": ("水银", "completed", "免疫控制"),
    "Thornmail": ("棘刺背心", "completed", "反弹物理伤害"),
    "AdaptiveHelm": ("适应性头盔", "completed", "根据位置加属性"),
    "SpiritVisage": ("振奋盔甲", "completed", "增强治疗效果"),
    "HandofJustice": ("正义之手", "completed", "随机加攻或加伤"),
    "ProtectorsVow": ("圣盾使的誓约", "completed", "开局护盾"),
    "ZzRotPortal": ("强袭者的链枷", "completed", "召唤虚空生物"),
    "ThiefsGloves": ("窃贼手套", "completed", "随机装备两件成装"),
    "ForceofNature": ("金铲铲冠冕", "completed", "+1 队伍上限"),
}

# === 羁绊数据 ===
TRAITS_REF = {
    "Bastion": ("堡垒卫士", [2,4,6], "获得护甲和魔抗"),
    "Bruiser": ("斗士", [2,4,6], "获得额外生命值"),
    "Challenger": ("挑战者", [2,3,4,5], "获得攻速，击杀后冲刺"),
    "Oracle": ("神谕", [2,3,4,5], "获得法力回复"),
    "Weaver": ("织命人", [2,4], "增强技能效果"),
    "Berserker": ("狂战士", [2,4,6], "获得攻击力和全能吸血"),
    "Magician": ("魔术师", [2,4], "技能可以暴击"),
    "Ranger": ("游侠", [2,3,4,5], "获得攻击速度"),
    "Shepherd": ("牧羊人", [3,5,7], "增强召唤物"),
    "Sniper": ("狙神", [2,3,4], "远程攻击增强"),
    "Vanguard": ("重装战士", [2,4,6], "获得大量护甲"),
    "Voyager": ("旅人", [2,3,4,5,6], "每场对阵不同玩家获得加成"),
    "Phantom": ("幻灵战队", [3,6], "特殊效果"),
    "Judge": ("法官", [2,3], "执行律法效果"),
    "DarkStar": ("暗星", [2,4,6,9], "阵亡时增强其他暗星"),
    "Stargazer": ("观星者", [3], "选择星象加成"),
    "Woodland": ("木灵族", [3,5,7,10], "召唤木灵"),
    "SpaceGroove": ("太空律动", [1,3,5,7,10], "节奏加成"),
    "Mecha": ("霸天机甲", [3,4,6], "合体变身"),
    "Psionic": ("灵能特工", [2,4], "灵能攻击"),
    "NovaStrike": ("新星特攻队", [2,5], "新星攻击"),
    "Abyssal": ("海魔人", [2,3], "海魔召唤"),
    "Chrono": ("未来战士", [2,3,4], "时间加速"),

    # 单人羁绊
    "FatePriest": ("命运祭司", [1], "命运之力"),
    "TwilightIron": ("暮光铁壁", [1], "钢铁防御"),
    "Commander": ("最高指挥官", [1], "指挥光环"),
    "DarkWitch": ("黑暗魔女", [1], "黑暗魔法"),
    "FightGod": ("斗神", [1], "战斗之神"),
    "DoomBringer": ("末日使者", [1], "末日之力"),
    "军工1号": ("军工1号", [1], "军工加成"),
    "天煞": ("天煞", [1], "天煞之力"),
    "武装战姬": ("武装战姬", [1], "武装变身"),
    "汪星机器人": ("汪星机器人", [1], "机器人效果"),
    "救世主": ("救世主", [1], "救世之力"),
    "灭星尊": ("灭星尊", [1], "灭星之力"),
}

# === 神明恩赐数据 ===
GOD_BLESSINGS = {
    "AurelionSol": {
        "cn": "奥瑞利安·索尔",
        1: [
            "当你积攒到50金币时，获得一个基础装备锻造器和4金币。",
            "在一场玩家对战中登场6个非单人羁绊后，获得1个随机纹章和1个装备重铸器。",
            "下次你将一个弈子升星时，获得10金币。",
        ],
        2: [
            "在一场玩家对战中登场6个非单人羁绊后，获得1个随机纹章和1个装备重铸器。",
            "在你到达9级时，获得20金币。",
            "你首次跌至30生命值时，获得18金币。",
        ],
        3: [
            "在你到达9级时，获得20金币。",
            "你首次跌至30生命值时，获得18金币。",
            "在刷新商店15次之后，获得2个基础装备锻造器。",
        ],
    },
    "Ekko": {
        "cn": "艾克",
        1: [
            "获得突变，一个基于单位的定位为其提供强力进化的装备。获得2个装备拆卸器。",
            "你的下一个PVE回合会被替换为带有额外战利品的迅捷蟹回合！",
            "在8个回合后，获得1个随机神器。",
        ],
        2: [
            "在3个回合后，获得1个4费弈子。",
            "在跌至30玩家生命值之后，获得一个特殊的战利品法球。",
            "你的下一个PVE回合会被替换为带有额外战利品的迅捷蟹回合！",
        ],
        3: [
            "永久使一个弈子的攻击速度提升20并使其体型缩小20%。",
            "在4个回合后，获得2个5费弈子。",
            "在3个回合后，获得1个基础装备锻造器。",
        ],
        4: [
            "永久使一个弈子的攻击速度提升20并使其体型缩小20%。",
            "在5个回合后，获得1个随机神器。",
            "在3回合后，获得一次免费商店刷新并且你的下一次商店包含所有5费弈子。",
        ],
        5: [
            "每个回合都会获得2金币。",
            "在5回合内，获得1个成装锻造器。",
        ],
    },
    "Evelynn": {
        "cn": "伊芙琳",
        1: [
            "你的队伍获得10%伤害减免。在你输掉对战回合时，额外失去1小小英雄生命值。",
            "获得3金币。如果你在前4名，获得30额外金币。",
            "获得1个2星2费弈子。失去3小小英雄生命值。",
        ],
        2: [
            "获得8金币。每有一名玩家选择此项，失去2弈士生命值。",
            "获得1个随机2费和1金币。在每次玩家对战后重复此效果，直至你输掉一次为止。",
            "获得1个随机1星4费弈子。失去4小小英雄生命值。",
        ],
        3: [
            "获得1个随机纹章。失去3小小英雄生命值。",
            "获得10金币。每有一名玩家选择此项，失去2弈士生命值。",
            "获得1个随机3费和1金币。在每次玩家对战后重复此效果，直至你输掉一次为止。",
        ],
        4: [
            "获得1个随机2星3费弈子。失去3小小英雄生命值。",
            "获得1个随机3星1费弈子。失去3小小英雄生命值。",
            "获得12金币。你无法购买弈子，持续2回合。",
        ],
        5: [
            "获得1个随机成装。失去5小小英雄生命值。",
            "获得13金币。每有一名玩家选择此项，失去1弈士生命值。",
            "获得1个随机2星4费弈子。失去3小小英雄生命值。",
            "获得18金币。你无法购买弈子，持续2回合。",
        ],
    },
    "Kayle": {
        "cn": "凯尔",
        1: [
            "你的队伍每携带一件不同的成装，就会获得10生命值、1%物理加成和1%法术加成。",
            "每当你将要获得一个基础装备时，转而获得1个基础装备锻造器。获得2金币。",
            "立刻获得1个装备重铸器，并且在每个阶段开始时再获得一个。每当你使用一个装备重铸器时，获得2金币。",
        ],
        2: [
            "拳套",
            "获得2金币。你下次制造一件装备时，随机获得其基础装备之一的一个复制品。",
            "拳套",
        ],
    },
    "Soraka": {
        "cn": "索拉卡",
        1: [
            "你每损失1玩家生命值，你的队伍就会获得2.5生命值。在每场玩家对战开始时，回复额外的1玩家生命值。",
            "永久为一个弈子提供100生命值，你赚取的每1利息都会使这个数额提升5。",
            "在战斗开始时，为在上一场战斗中第一个阵亡的那个友军提供450到800护盾值，基于当前阶段。",
        ],
        2: [
            "获得6小小英雄生命值。如果至少5个玩家选择此选项，则获得2金币。",
            "永久为一个弈子提供100生命值，你赚取的每1利息都会使这个数额提升8。",
            "在66和33玩家生命值时，获得一件随机的基础装备。",
        ],
        3: [
            "在战斗开始时，为在上一场战斗中第一个阵亡的那个友军提供450到800护盾值，基于当前阶段。",
            "永久使一个弈子的生命值提升350并且体型提升20%。",
            "获得6小小英雄生命值。如果至少5个玩家选择此选项，则获得3金币。",
        ],
        4: [
            "在战斗开始时，为在上一场战斗中第一个阵亡的那个友军提供450到800护盾值，基于当前阶段。",
            "永久使一个弈子的生命值提升350并且体型提升20%。",
            "获得6小小英雄生命值。如果至少5个玩家选择此选项，则获得3金币。",
        ],
    },
    "Thresh": {
        "cn": "锤石",
        1: [
            "每回合，投掷一个骰子。基于该次投掷，获得一个加成。",
            "将你棋盘上的所有1费和2费弈子转化为随机的更高费弈子。",
        ],
        2: [
            "会是什么呢？从任一星神处获得一个随机恩赐，以及2金币。",
            "会是什么呢？从任一星神处获得一个随机恩赐，以及3金币。",
        ],
        3: [
            "投掷3个骰子。获得相当于投掷结果总和的金币。",
            "从任一星神处获得一个随机恩赐，以及5金币。",
        ],
    },
    "Varus": {
        "cn": "韦鲁斯",
        1: [
            "你的弈子们获得15x己方队伍总星级的生命值，并且你的5费概率提升2%。",
            "当你下一次选择羽饰骑士星神的赠礼时，获得该弈子的一个额外复制体和2金币。",
            "获得你拥有的一个3费弈子的复制品和2金币。如果你未拥有任何3费弈子，则随机获得一个。",
        ],
        2: [
            "恋人：获得拥有一个相同羁绊的一个3费弈子和一个2费弈子。",
            "用在一位1费弈子身上，即可生成一个该弈子的1星版本。",
            "你的下一次商店包含全3费弈子。你购买的第一个是免费的。",
        ],
        3: [
            "当你下一次选择羽饰骑士星神的赠礼时，获得该弈子的一个额外复制体和2金币。",
            "你的下一次商店全是2费弈子。你购买的第一个是免费的并且会升至2星。",
            "获得你拥有的一个3费弈子的复制品和2金币。如果你未拥有任何3费弈子，则随机获得一个。",
        ],
        4: [
            "获得拥有一个相同羁绊的一个4费弈子和一个3费弈子。",
            "获得1个次级英雄复制器和3金币。",
            "你的下一次商店包含全4费弈子。你购买的第一个是免费的。",
        ],
        5: [
            "当你下一次选择羽饰骑士星神的赠礼时，获得该弈子的一个额外复制体和2金币。",
            "在每个回合开始时，如果你一次免费刷新都没有，就会获得一次免费刷新。",
            "获得你拥有的一个4费弈子的复制品和3金币。如果你未拥有任何4费弈子，则随机获得一个。",
        ],
        6: [
            "获得拥有一个相同羁绊的一个5费弈子和一个4费弈子。",
            "获得4个微型英雄复制器和1个次级英雄复制器。",
            "获得1个次级英雄复制器和5金币。",
        ],
    },
    "Yasuo": {
        "cn": "亚索",
        1: [
            "提高50%亚索的绘制格的效果。如果你只有2个绘制格，获得8金币。",
        ],
        2: [
            "将这个格子放在一个弈子上。这个格子中的友方弈子会在5秒里持续造成15%额外魔法伤害。附带33%重伤和1%灼烧。",
            "将这个格子放在一个弈子上。这个格子中的友方弈子在首次跌下40%生命值时，会被冻结1秒并治疗自身30%最大生命值。",
            "将这个格子放在一个弈子上。这个格子中的友方弈子会获得3法力回复。",
            "将这个格子放在一个弈子上。这个格子中的友方弈子会获得30%攻击速度。",
            "将这个格子放在一个弈子上。这个格子中的友方弈子获得10%最大生命值，并且每回合获得35永久生命值。",
            "将这个格子放在一个弈子上。这个格子中的友方弈子首次用技能命中一个敌人时，会使该敌人晕眩1.75秒。",
        ],
    },
    "Ahri": {
        "cn": "阿狸",
        1: [],  # 文档中未包含详细恩赐
    },
}

def import_champions(conn):
    """导入英雄数据"""
    for name, (cn, cost, traits) in CHAMPIONS.items():
        conn.execute("""
            INSERT OR REPLACE INTO champions (name, name_cn, cost, traits)
            VALUES (?, ?, ?, ?)
        """, (name, cn, cost, json.dumps(traits, ensure_ascii=False)))
    print(f"  Champions imported: {len(CHAMPIONS)}")

def import_items(conn):
    """导入装备数据"""
    for name, (cn, cat, desc) in ITEMS.items():
        conn.execute("""
            INSERT OR REPLACE INTO items (name, name_cn, category, description)
            VALUES (?, ?, ?, ?)
        """, (name, cn, cat, desc))
    print(f"  Items imported: {len(ITEMS)}")

def import_traits(conn):
    """导入羁绊数据"""
    for name, (cn, bps, desc) in TRAITS_REF.items():
        conn.execute("""
            INSERT OR REPLACE INTO traits_ref (name, name_cn, breakpoints, description)
            VALUES (?, ?, ?, ?)
        """, (name, cn, json.dumps(bps), desc))
    print(f"  Traits imported: {len(TRAITS_REF)}")

def import_god_blessings(conn):
    """导入神明恩赐数据"""
    count = 0
    for god, data in GOD_BLESSINGS.items():
        cn = data["cn"]
        for tier, blessings in data.items():
            if tier == "cn":
                continue
            for i, b in enumerate(blessings):
                conn.execute("""
                    INSERT OR REPLACE INTO god_blessings (god_name, god_name_cn, tier, blessing_index, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (god, cn, tier, i, b))
                count += 1
    print(f"  God blessings imported: {count}")

def main():
    init_db()
    conn = get_conn()
    create_static_tables(conn)

    print("Importing static TFT data...")
    import_champions(conn)
    import_items(conn)
    import_traits(conn)
    import_god_blessings(conn)

    conn.commit()
    conn.close()
    print("Done! Static data imported to tft_na.db")

if __name__ == "__main__":
    main()

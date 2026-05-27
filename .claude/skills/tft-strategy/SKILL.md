---
name: tft-strategy
description: "云顶之弈数据分析与策略顾问。查阵容、查装备、查海克斯、查神明，基于 NA 高分段真实数据给出建议。触发词：/tft、云顶、阵容推荐、玩什么"
---

# TFT Strategy — 云顶之弈数据分析与策略顾问

## 定位

基于 NA Challenger/GM 真实对局数据，为用户提供：
- 阵容推荐（运营/赌狗）
- 装备分配建议
- 海克斯强化选择
- 神明恩赐选择
- 对局中的实时决策支持

## 数据源

- **数据库**：`06_Python Scripts/04_数据分析/tft_db/tft_na.db`
- **策略报告**：`06_Python Scripts/04_数据分析/tft_db/TFT_Set17_策略报告.md`
- **查询工具**：`06_Python Scripts/04_数据分析/tft_db/query.py`
- **抓取工具**：`06_Python Scripts/04_数据分析/tft_db/fetcher.py`

## 使用方式

### 查询数据库

```bash
# 执行路径
PYTHON = "C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe"
DB_DIR = "E:/1.work/douyin/1.shuixing/06_Python Scripts/04_数据分析/tft_db"
```

常用查询脚本：

```bash
# Meta 分析
$PYTHON $DB_DIR/query.py meta

# 某英雄的阵容详情
$PYTHON $DB_DIR/query.py comp <英雄英文名>

# 模糊搜索英雄/羁绊
$PYTHON $DB_DIR/query.py search <关键词>

# 海克斯胜率
$PYTHON $DB_DIR/query.py augments
```

### 直接 SQL 查询

当 query.py 不够用时，直接写 Python + SQLite 查询：

```python
import sys, os
sys.path.insert(0, "E:/1.work/douyin/1.shuixing/06_Python Scripts/04_数据分析/tft_db/")
from db_schema import get_conn
conn = get_conn()
# 写 SQL 查询
results = conn.execute("SELECT ...").fetchall()
conn.close()
```

### 数据库表结构

| 表名 | 内容 | 关键字段 |
|------|------|---------|
| players | 玩家信息 | puuid, tier, league_points, wins, losses |
| matches | 对局元数据 | match_id, game_version, game_datetime |
| participants | 参与记录 | match_id, puuid, placement, level, augments |
| units | 英雄单位 | match_id, puuid, character_id, item_names, tier, rarity |
| traits | 羁绊记录 | match_id, puuid, trait_name, tier_current, num_units |
| champions | 英雄参考表 | name, name_cn, cost, traits |
| items | 装备参考表 | name, name_cn, category, description |
| traits_ref | 羁绊参考表 | name, name_cn, breakpoints, description |
| augments | 海克斯强化 | name, name_cn, tier, category, round_available, description |
| god_blessings | 神明恩赐 | god_name, god_name_cn, tier, description |

### 英雄英文名速查

| 中文 | 英文 | 费用 | 中文 | 英文 | 费用 |
|------|------|------|------|------|------|
| 亚托克斯 | Aatrox | 1 | 奥瑞利安·索尔 | AurelionSol | 4 |
| 贝蕾亚 | Briar | 1 | 库奇 | Corki | 4 |
| 凯特琳 | Caitlyn | 1 | 卡尔玛 | Karma | 4 |
| 科加斯 | Chogath | 1 | 千珏 | Kindred | 4 |
| 伊泽瑞尔 | Ezreal | 1 | 乐芙兰 | Leblanc | 4 |
| 蕾欧娜 | Leona | 1 | 易 | MasterYi | 4 |
| 丽桑卓 | Lissandra | 1 | 娜美 | Nami | 4 |
| 内瑟斯 | Nasus | 1 | 努努和威朗普 | Nunu | 4 |
| 波比 | Poppy | 1 | 拉莫斯 | Rammus | 4 |
| 雷克塞 | RekSai | 1 | 锐雯 | Riven | 4 |
| 泰隆 | Talon | 1 | 塔姆 | TahmKench | 4 |
| 提莫 | Teemo | 1 | 霞 | Xayah | 4 |
| 崔斯特 | TwistedFate | 1 | 巴德 | Bard | 5 |
| 维迦 | Veigar | 1 | 布里茨 | Blitzcrank | 5 |
| 阿卡丽 | Akali | 2 | 菲奥娜 | Fiora | 5 |
| 卑尔维斯 | Belveth | 2 | 格雷福斯 | Graves | 5 |
| 纳尔 | Gnar | 2 | 烬 | Jhin | 5 |
| 古拉加斯 | Gragas | 2 | 慎 | Shen | 5 |
| 格温 | Gwen | 2 | 娑娜 | Sona | 5 |
| 贾克斯 | Jax | 2 | 薇古丝 | Vex | 5 |
| 金克丝 | Jinx | 2 | 劫 | Zed | 5 |
| 茂凯 | Maokai | 2 | 莫甘娜 | Morgana | 5 |
| 米利欧 | Milio | 2 | 阿狸 | Ahri | 5 |
| 莫德凯撒 | Mordekaiser | 2 | 超级机甲 | Summon | 5 |
| 潘森 | Pantheon | 2 | 小木灵 | IvernMinion | 5 |
| 派克 | Pyke | 2 | 拉亚斯特 | Rhaast | 3 |
| 佐伊 | Zoe | 2 | 黛安娜 | Diana | 3 |
| 阿萝拉 | Aurora | 3 | 菲兹 | Fizz | 3 |
| 俄洛伊 | Illaoi | 3 | 卡莎 | Kaisa | 3 |
| 璐璐 | Lulu | 3 | 厄运小姐 | MissFortune | 3 |
| 奥恩 | Ornn | 3 | 莎弥拉 | Samira | 3 |
| 厄加特 | Urgot | 3 | 维克托 | Viktor | 3 |

## 输出规范

1. **英雄名必须用中文**，英文名括号备注
2. **数据必须来自数据库**，禁止编造胜率/出场率
3. **给出具体装备组合**，不要说"随便给"
4. **说明运营节奏**，按阶段（2-1/3-2/4-1/5-1）分步骤
5. **如果用户给了开局信息**（起手英雄、海克斯），基于数据库查对应阵容的最优路径

## 常见问题模式

| 用户问题 | 处理方式 |
|---------|---------|
| "玩什么好" | 查 meta 分析，推荐 T0 阵容 |
| "开局给了XX" | 查这些英雄的吃鸡对局，推导最优过渡路线 |
| "海克斯选哪个" | 查 augments 表，按阶段+类型推荐 |
| "装备怎么给" | 查特定英雄的吃鸡装备统计 |
| "神明选什么" | 根据阵容类型推荐对应神明 |
| "XX阵容怎么玩" | 查完整阵容详情+运营节奏+装备分配 |
| "这把怎么打" | 基于当前信息（阶段、血量、金币、阵容）实时决策 |

## 数据更新

```bash
# 抓取最新数据（增量更新）
$PYTHON $DB_DIR/fetcher.py fill 30

# 查看数据库统计
$PYTHON $DB_DIR/fetcher.py stats
```

## 策略报告

完整策略报告位于 `06_Python Scripts/04_数据分析/tft_db/TFT_Set17_策略报告.md`，包含：
- T0 运营阵容 x2
- 赌狗阵容 x2
- 海克斯强化选择策略
- 神明选择推荐
- 关键信息差

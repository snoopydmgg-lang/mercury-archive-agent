# 水星艺术馆 - 内容生产工作流程

## 概述

本文档描述了从选品到发布的完整内容生产流水线,包括文案生成、DBS 检定、封面生成、配音和上传等环节。

---

## 工作流程图

```
选品 → 文案生成 → DBS 检定 → 用户 Approve → 封面生成 → 配音 → 上传飞书 → 视频制作 → 发布
```

---

## 详细步骤

### Step 1: 准备产品背景资料

**位置**: `Wiki知识库/wiki/选题库/`

**文件命名**: `{产品名}-文案参考资料.md`

**内容要求**:
- 产品基本信息(名称、价格、规格)
- 核心卖点(3-5个)
- 目标受众
- 竞品分析
- 参考资料链接

**示例**: `宫崎骏作品集-文案参考资料.md`

---

### Step 2: 生成文案(三种风格)

**脚本**: `06_Python Scripts/01_AI文案/generate_miyazaki_v2.py` (宫崎骏专用)
或 `06_Python Scripts/01_AI文案/Unified_Copywriter_Template.py` (通用模板)

**命令**:
```bash
# 宫崎骏作品集(自动批准模式)
py generate_miyazaki_v2.py --auto-approve

# 其他产品(通用模板)
py Unified_Copywriter_Template.py --product "版式之道" --auto-approve
```

**输出**:
- 文件位置: `01_Projects_制作中/{产品名}/02_脚本_逻辑链/MMDD-{产品名}-三套文案.md`
- 包含内容:
  - 元数据(视频标题、商品短标题、产品简介)
  - 大师画像型文案(口播 + 画面脚本 + BGM + 音效)
  - 故事叙事型文案(口播 + 画面脚本 + BGM + 音效)

**DBS 检定闭环**:
1. 文案生成后自动调用 DBS 检定
2. 根据 DBS 五维诊断结果自动修改
3. 等待用户 Approve(或使用 `--auto-approve` 跳过)
4. 未 Approve 前禁止后续操作

---

### Step 3: 生成封面

**脚本**: `06_Python Scripts/03_豆包图像/auto_cover_generator.py`

**命令**:
```bash
# 自动生成(根据文案元数据)
py auto_cover_generator.py --product "宫崎骏作品集"

# 自定义风格
py auto_cover_generator.py --product "版式之道" --style "academic-grid"

# 完全自定义
py auto_cover_generator.py --product "飞鸟集" --title "飞鸟集\n泰戈尔诗选" --concept "生如夏花之绚烂"
```

**输出**:
- 文件位置: `01_Projects_制作中/{产品名}/01_素材_试用装/00_封面设计/MMDD-{产品名}-封面.png`
- 同时复制到: `00_InBox_收件箱/YYYYMMDD-{产品名}-封面.png`

**设计规范**:
- 比例: 3:4 (1080x1440)
- 色彩系统: 羊皮纸白 #F5F4F0 + 暖炭灰 #2D2B2A + 赤陶土 #D36B4D
- 字体: 衬线体(标题) + 无衬线体(副标题)
- 质感: 2-5% 单色噪点 + 纸张纹理

**三种风格**:
- `classic-print`: 古典印刷(默认)
- `organic-botanical`: 有机生命体(宫崎骏推荐)
- `academic-grid`: 学术网格(版式之道推荐)

---

### Step 4: 配音生成

**工具**: FishAudio 或其他配音工具

**输入**: 从文案 MD 文件中复制口播文案

**输出**: MP3 音频文件

**保存位置**: `01_Projects_制作中/{产品名}/03_音频_配音/`

---

### Step 5: 上传到飞书

**脚本**: `06_Python Scripts/02_飞书工具/feishu_update_*.py`

**命令**:
```bash
py feishu_update_miyazaki.py
```

**上传内容**:
- 视频标题
- 商品短标题
- 产品简介
- 口播文案
- 画面脚本
- BGM 建议
- 音效建议
- 配音链接

---

### Step 6: 视频制作与发布

**外包**: 将飞书表格分享给视频制作团队

**验收**: 检查视频质量、字幕准确性、BGM 匹配度

**发布**: 上传到抖音/小红书

---

## BGM 使用指南

**BGM 库位置**: `Wiki知识库/raw/BGM音乐库/`

**使用指南**: `Wiki知识库/raw/BGM音乐库/使用指南.md`

**文案中的 BGM 推荐**:
- 每种风格的文案都包含 BGM 推荐
- 格式: 曲目名称 - 艺术家
- 路径: 相对于项目根目录的完整路径
- 适用原因: 说明为什么选择这首 BGM

**示例**:
```markdown
## BGM 推荐
- 曲目: The Legend of Ashitaka - Joe Hisaishi
- 路径: `Wiki知识库/raw/BGM音乐库/宫崎骏/The Legend of Ashitaka.mp3`
- 适用原因: 史诗壮阔,适合大师画像型
```

---

## 文件系统规范

### 知识库寻址优先级

1. `Wiki知识库/wiki/选题库/` - 产品背景资料
2. `Wiki知识库/wiki/` - 方法论和参考资料
3. `Wiki知识库/raw/` - 原始资料
4. **禁止**从 `00_InBox_收件箱/` 开始遍历

### 根目录零污染协议

- 根目录只允许临时文件(.bat, .log, .txt)
- 任务完成后必须自动清理
- 长期使用的脚本必须生成在 `06_Python Scripts/`
- AI 生成文件直接保存到产品项目文件夹

### 垃圾回收

**脚本**: `06_Python Scripts/cleanup_temp_files.py`

**命令**:
```bash
# 预览模式(不删除)
py cleanup_temp_files.py

# 执行删除
py cleanup_temp_files.py --execute
```

**清理规则**:
- 根目录: *.log, *.tmp, temp_*.txt, output*.txt, *.bat
- 收件箱: 2 天前的 *.json, *.py

---

## 质量检定标准

### DBS 五维诊断

1. **文字洁癖检测** - 有无 AI 味、emoji 堆叠、空洞排比句
2. **封面/标题诊断** - 是否自带吸引力、认知劫持效果
3. **表达效率检测** - 核心观点是否清晰、有无冗余
4. **认知落差检测** - 相比同行是否有明显差异化
5. **改进建议** - 具体的修改方向

### 判断标准

- ✅ 通过 - 无需修改
- ⚠️ 警告 - 需要优化
- ❌ 不通过 - 必须重写

---

## 常见问题

### Q1: 文案生成失败,提示"未找到产品背景资料"

**解决方案**: 检查 `Wiki知识库/wiki/选题库/` 目录下是否存在 `{产品名}-文案参考资料.md` 文件。

### Q2: 封面生成失败,提示"豆包 API 错误"

**解决方案**: 检查 API Key 是否有效,网络连接是否正常。

### Q3: DBS 检定后文案质量仍不理想

**解决方案**: 手动编辑文案 MD 文件,然后使用 `--auto-approve` 参数重新运行。

### Q4: BGM 文件找不到

**解决方案**: 检查 `Wiki知识库/raw/BGM音乐库/` 目录下是否存在对应的 MP3 文件。

---

## 更新日志

### 2026-04-15

- ✅ 集成 DBS 检定闭环到文案生成流程
- ✅ 创建自动封面生成器 `auto_cover_generator.py`
- ✅ 统一文案生成模板支持 `--auto-approve` 参数
- ✅ 创建垃圾回收脚本 `cleanup_temp_files.py`
- ✅ 迁移知识库到 `Wiki知识库/` 目录
- ✅ 更新 CLAUDE.md 和 MEMORY.md

---

## 联系方式

如有问题,请联系项目负责人或查阅 `.claude/` 目录下的详细文档。

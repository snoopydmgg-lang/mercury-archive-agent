---
name: dbskill-upgrade
description: dbskill v2.3 小红书标题公式工具 - 从75个爆款公式生成定制标题
trigger: /dbskill-upgrade、/升级dbskill、/dbs
---

# dbskill v2.3 更新

## 核心更新：小红书标题公式工具

### 功能概述
- **调用方式**: `/dbs-xhs-title` 或 `/小红书标题`
- **核心能力**: 输入话题后，从75个爆款公式中自动匹配5-8个最合适的定制标题
- **区别**: 所有推荐标题均可追溯公式编号及真实爆款案例，确保方法论可验证

### 12类心理触发器覆盖
1. 认知冲突
2. 好奇缺口
3. 恐惧损失
4. 身份代入
5. 数字锚定
6. 结果承诺
7. 社会证明
8. 争议挑衅
9. 场景条件
10. 行动号召
11. 权威借力
12. 互动测试

### 输出内容
- 每个标题附带公式编号
- 原始爆款对照案例
- 推荐理由
- 最终 Top 3 推荐

---

## Skill 联动机制

`/dbs` 主入口路由新增标题公式工具入口：

1. **content 诊断** → 可推荐 **xhs-title** 起标题
2. **xhs-title 生成后** → 可推荐 **hook** 优化开头

形成内容创作闭环。

---

## 安装方式

```bash
npx skills add dontbesilent2025/dbskill
```

或在 Claude Code 内直接输入：`/dbskill-upgrade`

---

## GitHub 项目

https://github.com/dontbesilent2025/dbskill

---

## 版本信息

- **当前版本**: v2.3
- **上一版本重点**: 奥派经济聊天室
- **本版重点**: 实用工具开发（小红书标题公式工具）

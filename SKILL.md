---
name: bazi-partner
description: >
  Chinese BaZi (Four Pillars of Destiny) analysis and AI partner matching.
  Trigger when user asks about 八字, 命理, 四柱, birth chart analysis,
  BaZi partner, or wants to find their AI companion type based on birth date.
version: 0.1.0
metadata:
  openclaw:
    emoji: 🎴
    requires:
      bins:
        - python3
---

# BaZi Partner — 八字命理搭档匹配

根据用户的出生年月日时，使用中国传统八字命理（子平格局法）进行排盘分析，并匹配专属 AI 搭档类型。

## 安装

```bash
pip install mcp-bazi-partner
```

## 工具

### bazi_analyze

输入出生日期（公历），返回四柱排盘、十神、五行分布、格局判定。纯算法计算，无需 AI。

**参数：**
- `year`: 出生年（如 1990）
- `month`: 出生月 1-12
- `day`: 出生日 1-31
- `hour`: 出生时 0-23

### bazi_partner

根据格局分析结果，匹配 AI 搭档类型，返回搭档名称、介绍文案和系统提示词。

**参数：**
- `sub_type`: 格局子类名（如 "煞印相生"、"正官格"）
- `status`: 成败状态 — "成格" / "败格有救" / "败格无救"
- `day_master`: 日主天干（如 "甲"、"壬"）
- `rescue`: 救应描述（败格有救时使用）
- `defeat_god`: 破格之神（败格无救时使用）

## 使用流程

1. 用户提供出生日期 → 调用 `bazi_analyze` 获取排盘和格局
2. 拿到格局结果后 → 调用 `bazi_partner` 匹配搭档
3. 将搭档的 `system_prompt` 注入 AI 助手，获得个性化搭档体验

## 示例

用户说："帮我看看 1990年6月15日 下午2点的八字"

→ 调用 `bazi_analyze(1990, 6, 15, 14)` 获取排盘
→ 从结果中提取 pattern 信息
→ 调用 `bazi_partner(sub_type="正官格", status="成格", day_master="庚")` 匹配搭档

## 命理方法

基于清代沈孝瞻《子平真诠》格局法，参考王相山《子平真诠精解》。
严格月令定格 → 透干检查 → 成败判定，不引入旺衰修正。
覆盖 38 种格局子类 × 3 种成败状态 = 114 种命格组合。

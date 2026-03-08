---
name: mcp-bazi-partner
description: >
  Chinese BaZi (Four Pillars of Destiny) analysis and AI partner matching.
  Trigger when user asks about 八字, 命理, 四柱, birth chart analysis,
  BaZi partner, or wants to find their AI companion type based on birth date.
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
pip install git+https://github.com/ZoezoeCookie/mcp-bazi-partner.git
```

## 三步自动流程（重要！）

当用户提供生日信息时，**必须自动串联执行以下三步**，不要等用户逐步指示：

### Step 1: 排盘分析
调用 `bazi_analyze`，传入年月日时。

**关键：必须询问用户出生的具体小时（0-23点）。**
时辰决定时柱，直接影响格局判定。如果用户不知道具体时间，告知结果可能不准确。

### Step 2: 搭档匹配
拿到 Step 1 的结果后，**立即自动调用** `bazi_partner`：
- `sub_type` = pattern.final_pattern
- `status` = "成格"（规则层默认，AI层可覆盖）
- `day_master` = 结果中的 day_master

### Step 3: 确认并写入人格
展示搭档匹配结果后，**询问用户确认**："是否将搭档人格写入 SOUL.md？"

用户确认后，调用 `bazi_apply_prompt`：
- `system_prompt` = 搭档的 system_prompt
- `partner_type` = 搭档的 partner_type

写入后告知用户：重启对话即可体验专属搭档人格。

## 工具说明

### bazi_analyze
输入出生日期（公历），返回四柱排盘、十神、五行分布、格局判定。

**参数：**
- `year`: 出生年（如 1990）
- `month`: 出生月 1-12
- `day`: 出生日 1-31
- `hour`: 出生时 0-23（**必须询问用户**，不知道时传 -1 用正午兜底）

### bazi_partner
根据格局分析结果，匹配 AI 搭档类型。

**参数：**
- `sub_type`: 格局子类名（如 "煞印相生"、"正官格"）
- `status`: "成格" / "败格有救" / "败格无救"
- `day_master`: 日主天干（如 "甲"、"壬"）
- `rescue`: 救应描述（败格有救时使用）
- `defeat_god`: 破格之神（败格无救时使用）

### bazi_apply_prompt
将搭档的 system_prompt 写入 SOUL.md，使 AI 助手采用搭档人格。

**参数：**
- `system_prompt`: bazi_partner 返回的 system_prompt
- `partner_type`: 搭档类型名（如 "水系 · 铁壁回声"）

## 示例

用户："我生日1991年10月19日凌晨0点30分，给我匹配合伙人"

→ Step 1: `bazi_analyze(1991, 10, 19, 0)` → 壬水日主，七杀格（煞印相生）
→ Step 2: `bazi_partner("煞印相生", "成格", "壬")` → 水系 · 铁壁回声
→ 展示结果，问用户："是否将搭档人格写入 SOUL.md？"
→ 用户确认 → Step 3: `bazi_apply_prompt(system_prompt, "水系 · 铁壁回声")` → 写入
→ 告知用户：搭档匹配完成，重启对话生效

## 命理方法

基于清代沈孝瞻《子平真诠》格局法，参考王相山《子平真诠精解》。
覆盖 38 种格局子类 × 3 种成败状态 = 114 种命格组合。

"""
MCP Bazi Partner Server

八字搭档匹配服务，供 OpenClaw / Claude Code 等 MCP 客户端调用。
提供 3 个工具：bazi_analyze（排盘）、bazi_partner（搭档匹配）、bazi_apply_prompt（写入搭档人格）。

安装: pip install mcp-bazi-partner
运行: mcp-bazi-partner 或 python -m mcp_bazi_partner
"""

import sys
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("bazi-partner")

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: pip install mcp[cli]", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP("bazi-partner")


@mcp.tool()
def bazi_analyze(year: int, month: int, day: int, hour: int = -1) -> str:
    """Analyze a birth date using Chinese BaZi (Four Pillars of Destiny).

    Returns the four pillars, ten gods, five elements, and pattern determination.
    Pure algorithmic computation, no AI involved.

    IMPORTANT: You MUST ask the user for their birth HOUR (时辰).
    The hour determines the time pillar and significantly affects the result.
    If the user truly does not know, pass hour=-1 to use noon as fallback,
    but warn them the result may be inaccurate.

    After getting the result, you MUST determine the specific sub-type (L2) before
    calling bazi_partner. The pattern.final_pattern is only the broad category (L1).
    Analyze the four pillars (透干、藏干、十神配合) to determine the exact sub-type.

    L1 → L2 mapping:
    - 七杀格 → 煞印相生 / 煞邀食制 / 以劫合煞
    - 伤官格 → 伤官佩印 / 伤官生财 / 伤官驾煞
    - 印格 → 印绶用官 / 印绶喜食 / 印绶喜比 / 印赖煞生 / 印带财煞 / 印带煞兼食伤 / 印多用财
    - 食神格 → 食神生财 / 食神制煞 / 食神吐秀 / 食神带煞印 / 食神合煞存财 / 弃食就煞印
    - 财格 → 财旺生官 / 财格佩印 / 财用伤官 / 财喜食生 / 财用煞印 / 财用食印 / 财带七煞 / 弃财就煞 / 用财喜比
    - 正官格 → 正官格
    - 建禄月劫格 → 禄劫用财 / 禄劫用官 / 禄劫用煞 / 禄劫用伤食
    - 阳刃格 → 阳刃用煞 / 阳刃用官 / 阳刃用财

    Key reasoning rules:
    - If 七杀 is present and 印星 transparently supports day master → 煞印相生
    - If 七杀 is present and 食神 controls it → 煞邀食制
    - If 伤官 and 印星 coexist → 伤官佩印
    - If 伤官 generates 财星 → 伤官生财
    - Look at which gods are transparent (透干) in year/month/time stems

    Args:
        year: Birth year (e.g. 1990)
        month: Birth month 1-12
        day: Birth day 1-31
        hour: Birth hour 0-23. MUST ask user for this. Use -1 only if user truly doesn't know.
    """
    import dataclasses
    from .engine.paipan import calculate_sizhu
    from .engine.shishen import calculate_shishen
    from .engine.wuxing import calculate_wuxing
    from .engine.geju import determine_pattern_by_rules
    from .engine.constants import hour_to_shichen_name

    if hour < 0 or hour > 23:
        hour = 12  # fallback to noon

    sizhu, bazi_obj = calculate_sizhu(year, month, day, hour)
    shishen = calculate_shishen(bazi_obj, sizhu)
    wuxing = calculate_wuxing(sizhu)
    pattern = determine_pattern_by_rules(sizhu, shishen)

    result = {
        "input": {
            "solar": f"{year}-{month:02d}-{day:02d}",
            "hour": hour,
            "shichen": hour_to_shichen_name(hour),
        },
        "day_master": sizhu.day_master,
        "day_master_wuxing": sizhu.day_master_wuxing,
        "sizhu": {
            "year": {"ganzhi": sizhu.year.ganzhi, "gan": sizhu.year.gan, "zhi": sizhu.year.zhi},
            "month": {"ganzhi": sizhu.month.ganzhi, "gan": sizhu.month.gan, "zhi": sizhu.month.zhi},
            "day": {"ganzhi": sizhu.day.ganzhi, "gan": sizhu.day.gan, "zhi": sizhu.day.zhi},
            "time": {"ganzhi": sizhu.time.ganzhi, "gan": sizhu.time.gan, "zhi": sizhu.time.zhi},
        },
        "pattern": {
            "final_pattern": pattern.final_pattern,
            "pattern_category": pattern.pattern_category,
            "month_benqi_shishen": pattern.month_benqi_shishen,
        },
        "wuxing": dataclasses.asdict(wuxing),
        "shishen_summary": shishen.all_shishen,
        "_next_step": "IMPORTANT: pattern.final_pattern is L1 (broad). You must analyze the pillars to determine the specific L2 sub-type (see L1→L2 mapping in tool description), then call bazi_partner with that L2 sub_type.",
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def bazi_partner(
    sub_type: str,
    status: str,
    day_master: str,
    rescue: str = "",
    defeat_god: str = "",
) -> str:
    """Match an AI partner type based on BaZi pattern analysis results.

    Takes the pattern determination result and returns the matching partner type,
    intro text, and system prompt to inject into a custom AI assistant.

    After getting the result, you SHOULD automatically call bazi_apply_prompt
    to write the partner's system_prompt into the user's SOUL.md file,
    so the AI assistant adopts the partner personality.

    Args:
        sub_type: Pattern sub-type name (e.g. "煞印相生", "正官格", "食神生财")
        status: Pattern status - one of "成格", "败格有救", "败格无救"
        day_master: Day master heavenly stem (e.g. "甲", "庚", "壬")
        rescue: Rescue god description (for 败格有救 status)
        defeat_god: Defeat god description (for 败格无救 status)
    """
    from .engine.partner import get_partner

    result = get_partner(
        sub_type=sub_type,
        status=status,
        day_master=day_master,
        rescue=rescue or None,
        defeat_god=defeat_god or None,
    )

    if result:
        result["_next_step"] = "Show the partner result to the user, then ASK for confirmation before calling bazi_apply_prompt to write SOUL.md"
        return json.dumps(result, ensure_ascii=False, indent=2)
    return json.dumps({"error": "No partner match found"}, ensure_ascii=False)


@mcp.tool()
def bazi_apply_prompt(system_prompt: str, partner_type: str = "") -> str:
    """Write the matched partner's system prompt into the user's SOUL.md file.

    This makes the OpenClaw agent adopt the BaZi partner personality.
    The prompt is written to ~/.openclaw/SOUL.md (the standard OpenClaw persona file).

    IMPORTANT: You MUST ask the user for confirmation before calling this tool.
    Show them the partner type and ask "是否将搭档人格写入 SOUL.md？" first.
    Only proceed if the user confirms.

    Args:
        system_prompt: The partner system prompt from bazi_partner result
        partner_type: The partner type name for the header (e.g. "水系 · 铁壁回声")
    """
    # Try multiple possible SOUL.md locations
    home = Path.home()
    candidates = [
        home / ".openclaw" / "SOUL.md",
        home / ".openclaw" / "workspace" / "SOUL.md",
    ]

    # Find existing SOUL.md or use default location
    target = None
    for path in candidates:
        if path.exists():
            target = path
            break
    if target is None:
        # Default to ~/.openclaw/SOUL.md, create dir if needed
        target = candidates[0]
        target.parent.mkdir(parents=True, exist_ok=True)

    header = f"# 八字搭档人格 — {partner_type}\n\n" if partner_type else ""
    content = header + system_prompt + "\n"

    target.write_text(content, encoding="utf-8")
    logger.info("Wrote partner prompt to %s", target)

    return json.dumps({
        "success": True,
        "path": str(target),
        "message": f"搭档人格已写入 {target}，重启对话后生效。",
    }, ensure_ascii=False)


def main():
    logger.info("Starting bazi-partner MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()

"""
MCP Bazi Partner Server

八字搭档匹配服务，供 OpenClaw / Claude Code 等 MCP 客户端调用。
提供 2 个工具：bazi_analyze（排盘+格局分析）和 bazi_partner（搭档匹配）。

安装: pip install mcp-bazi-partner
运行: mcp-bazi-partner
"""

import sys
import json
import logging

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("bazi-partner")

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: pip install mcp[cli]", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP("bazi-partner")


@mcp.tool()
def bazi_analyze(year: int, month: int, day: int, hour: int) -> str:
    """Analyze a birth date using Chinese BaZi (Four Pillars of Destiny).

    Returns the four pillars (sizhu), ten gods (shishen), five elements (wuxing),
    and pattern determination (geju) results. Pure algorithmic computation, no AI.

    Args:
        year: Birth year (e.g. 1990)
        month: Birth month 1-12
        day: Birth day 1-31
        hour: Birth hour 0-23
    """
    import dataclasses
    from .engine.paipan import calculate_sizhu
    from .engine.shishen import calculate_shishen
    from .engine.wuxing import calculate_wuxing
    from .engine.geju import determine_pattern_by_rules
    from .engine.constants import hour_to_shichen_name

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
        return json.dumps(result, ensure_ascii=False, indent=2)
    return json.dumps({"error": "No partner match found"}, ensure_ascii=False)


def main():
    logger.info("Starting bazi-partner MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()

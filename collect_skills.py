"""
收集当前环境中可用的 Skill 列表
用法：
    python collect_skills.py                       # 列出全部 skills
    python collect_skills.py --recent SKILL_NAME   # 记录一次"最近使用"到本地
    python collect_skills.py --history             # 查看历史使用记录
    python collect_skills.py --output FILE         # 导出 skill 列表到文件 (json/md)
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# 当前环境内置的 Skill 清单
AVAILABLE_SKILLS = [
    {
        "name": "TRAE-product-knowledge",
        "description": "TRAE 品牌与官方产品知识问答",
        "scope": "TRAE 品牌、产品差异、IDE / Work / CLI / Plugin、MCP、Skills、官方文档",
        "use_when": "用户询问 TRAE 是什么、产品对比、官方链接等",
    },
    {
        "name": "web-dev",
        "description": "从零创建生产级 Web 页面 / 应用",
        "scope": "新建网站、Web 应用、Web 游戏，PRD + 技术文档 + 实现",
        "use_when": "用户明确要求从零搭建 Web 项目时",
    },
]

HISTORY_FILE = Path(__file__).parent / ".skill_history.json"


def load_history() -> dict:
    if not HISTORY_FILE.exists():
        return {"records": []}
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"records": []}


def save_history(history: dict) -> None:
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def record_usage(name: str) -> None:
    """记录一次 skill 使用情况（用于追踪“最近实用”）"""
    if name not in {s["name"] for s in AVAILABLE_SKILLS}:
        print(f"[warn] '{name}' 不在当前可用 skill 列表中，跳过记录。")
        return
    history = load_history()
    history["records"].append(
        {"name": name, "used_at": datetime.now().isoformat(timespec="seconds")}
    )
    save_history(history)
    print(f"[ok] 已记录 skill 使用: {name}")


def show_recent(limit: int = 10) -> None:
    """展示最近被使用过的 skill（按时间倒序）"""
    history = load_history()
    records = sorted(
        history.get("records", []),
        key=lambda r: r.get("used_at", ""),
        reverse=True,
    )[:limit]
    if not records:
        print("暂无使用记录。可使用 --recent <skill_name> 记录一次。")
        return
    print(f"最近 {len(records)} 条 skill 使用记录：")
    for r in records:
        print(f"  - {r['used_at']}  {r['name']}")


def list_skills() -> None:
    """列出当前所有可用 skill"""
    print(f"当前可用 skill 共 {len(AVAILABLE_SKILLS)} 个：\n")
    for s in AVAILABLE_SKILLS:
        print(f"[{s['name']}]")
        print(f"  描述 : {s['description']}")
        print(f"  范围 : {s['scope']}")
        print(f"  触发 : {s['use_when']}\n")


def export_skills(output_path: str) -> None:
    """导出 skill 列表到文件，根据扩展名自动选择 json 或 md 格式"""
    path = Path(output_path)
    suffix = path.suffix.lower()
    if suffix == ".json":
        content = json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "total": len(AVAILABLE_SKILLS),
                "skills": AVAILABLE_SKILLS,
            },
            ensure_ascii=False,
            indent=2,
        )
    elif suffix in (".md", ".markdown"):
        lines = [
            "# Skill 清单",
            "",
            f"> 生成时间：{datetime.now().isoformat(timespec='seconds')}",
            "",
            f"当前可用 skill 共 **{len(AVAILABLE_SKILLS)}** 个：",
            "",
        ]
        for s in AVAILABLE_SKILLS:
            lines.append(f"## {s['name']}")
            lines.append("")
            lines.append(f"- **描述**：{s['description']}")
            lines.append(f"- **范围**：{s['scope']}")
            lines.append(f"- **触发条件**：{s['use_when']}")
            lines.append("")
        content = "\n".join(lines)
    else:
        print(f"[error] 不支持的输出格式: {suffix}，请使用 .json 或 .md")
        return
    path.write_text(content, encoding="utf-8")
    print(f"[ok] 已导出 skill 列表到 {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="收集当前可用的 Skill 列表")
    parser.add_argument(
        "--recent",
        metavar="SKILL_NAME",
        help="记录一次指定 skill 的最近使用情况",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="查看最近 skill 使用记录",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="导出 skill 列表到文件（支持 .json 和 .md 格式）",
    )
    args = parser.parse_args()

    if args.recent:
        record_usage(args.recent)
        return
    if args.history:
        show_recent()
        return
    if args.output:
        export_skills(args.output)
        return
    list_skills()


if __name__ == "__main__":
    main()

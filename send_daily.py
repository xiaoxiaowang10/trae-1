#!/usr/bin/env python3
"""快速抓取 AI/技术资讯并发送邮件"""

import smtplib
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr

import feedparser
import requests
from bs4 import BeautifulSoup

# ============ 配置 ============
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "wzb12345654321@126.com"
SMTP_PASS = "JEewEs2eq9gLZMbj"
FROM_ADDR = "wzb12345654321@126.com"
TO_ADDR = "wzb12345654321@126.com"

HEADERS = {"User-Agent": "unified-daily/0.1"}


def http_get(url, **kwargs):
    r = requests.get(url, headers={**HEADERS, **kwargs.get("headers", {})}, timeout=kwargs.get("timeout", 20))
    r.raise_for_status()
    return r


def fetch_github(limit=6):
    items = []
    try:
        soup = BeautifulSoup(http_get("https://github.com/trending?since=daily", headers={"Accept": "text/html"}).text, "lxml")
        for article in soup.select("article.Box-row")[:limit]:
            a = article.select_one("h2 a")
            if not a or not a.get("href"):
                continue
            repo = a["href"].lstrip("/")
            desc = article.select_one("p.col-9")
            items.append({"title": repo, "url": f"https://github.com/{repo}",
                          "summary": desc.get_text(strip=True) if desc else "", "source": "GitHub"})
    except Exception as e:
        print(f"GitHub 失败: {e}")
    return items


def fetch_devto(limit=6):
    items = []
    try:
        data = http_get("https://dev.to/api/articles?tag=ai&top=10").json()
        for art in data[:limit]:
            items.append({"title": art.get("title", ""), "url": art.get("url"),
                          "summary": art.get("description", ""), "source": "Dev.to"})
    except Exception as e:
        print(f"Dev.to 失败: {e}")
    return items


def fetch_rss(limit=5):
    items = []
    feeds = [
        "https://hnrss.org/newest",
        "https://www.reddit.com/r/MachineLearning/.rss",
    ]
    for url in feeds:
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:limit]:
                items.append({"title": entry.get("title", ""), "url": entry.get("link") or entry.get("id"),
                              "summary": (entry.get("summary", "")[:200] + "...") if entry.get("summary") else "", "source": "RSS"})
        except Exception as e:
            print(f"RSS {url} 失败: {e}")
    return items


def fetch_tech_blogs(limit=5):
    items = []
    feeds = [
        ("https://openai.com/blog/rss.xml", "OpenAI Blog"),
        ("https://blog.google/technology/ai/rss/", "Google AI Blog"),
    ]
    for url, label in feeds:
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:limit]:
                items.append({"title": entry.get("title", ""), "url": entry.get("link") or entry.get("id"),
                              "summary": (entry.get("summary", "")[:200] + "...") if entry.get("summary") else "", "source": label})
        except Exception as e:
            print(f"Tech Blog {url} 失败: {e}")
    return items


def render_html(items):
    date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    groups = {}
    for it in items:
        groups.setdefault(it["source"], []).append(it)
    sections = ""
    for src, its in groups.items():
        sections += f'<h2 style="color:#5b6bff;font-size:16px;margin:18px 0 10px;">{src}</h2>'
        for it in its:
            sections += f'<div style="padding:8px 0;border-bottom:1px dashed #eef0f5;">'
            sections += f'<a href="{it["url"]}" style="color:#1f2330;text-decoration:none;font-weight:600;">{it["title"]}</a>'
            if it.get("summary"):
                sections += f'<div style="color:#8b91a3;font-size:12px;margin-top:4px;">{it["summary"][:160]}</div>'
            sections += '</div>'
    return f"""<!DOCTYPE html>
<html lang="zh">
<head><meta charset="utf-8" /><title>{date} 每日精选</title></head>
<body style="font-family:-apple-system,Segoe UI,PingFang SC,sans-serif;background:#f6f7fb;color:#1f2330;margin:0;padding:24px;">
<div style="max-width:720px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.06);">
<div style="background:linear-gradient(135deg,#5b6bff,#8b5bff);color:#fff;padding:24px 28px;">
<h1 style="margin:0 0 4px;font-size:20px;">📰 每日精选 · {date}</h1>
<p style="margin:0;opacity:0.85;font-size:13px;">共 {len(items)} 条来自 {len(groups)} 个数据源</p>
</div>
<div style="padding:18px 28px;">{sections}</div>
<div style="padding:16px 28px;text-align:center;color:#8b91a3;font-size:12px;background:#fafbfd;">由 Unified Daily 自动生成</div>
</div>
</body></html>"""


def send_email(html_body):
    msg = EmailMessage()
    msg["Subject"] = f"【每日精选】{datetime.now(tz=timezone.utc).strftime('%Y-%m-%d')} AI / 技术动态"
    msg["From"] = formataddr(("Unified Daily", FROM_ADDR))
    msg["To"] = TO_ADDR
    msg.add_alternative(html_body, subtype="html")
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
    print("✅ 邮件发送成功")


def main():
    print("正在抓取数据...")
    items = []
    items.extend(fetch_github(6))
    items.extend(fetch_devto(6))
    items.extend(fetch_rss(4))
    items.extend(fetch_tech_blogs(3))
    print(f"共抓取 {len(items)} 条")

    if not items:
        print("无数据可发送")
        return 1

    html = render_html(items)
    print("正在发送邮件...")
    send_email(html)
    return 0


if __name__ == "__main__":
    sys.exit(main())

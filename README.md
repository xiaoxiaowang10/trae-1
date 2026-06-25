# trae-1

Skill 收集与使用记录工具，用于在本地环境中管理可用 Skill 列表并跟踪使用历史。

## 功能

- 列出当前环境所有可用的 Skill
- 记录 Skill 的使用情况到本地历史文件
- 按时间倒序查看最近使用记录
- 导出 Skill 列表为 JSON 或 Markdown 报告
- GitHub Actions 自动运行并将结果提交回仓库

## 用法

### 列出所有可用 Skill

```bash
python collect_skills.py
```

### 记录一次 Skill 使用

```bash
python collect_skills.py --recent TRAE-product-knowledge
```

### 查看历史使用记录

```bash
python collect_skills.py --history
```

### 导出 Skill 列表到文件

支持 `.json` 和 `.md` 两种格式，根据文件扩展名自动识别：

```bash
# 导出为 JSON
python collect_skills.py --output skills_report.json

# 导出为 Markdown
python collect_skills.py --output skills_report.md
```

## 可用 Skill

| Skill 名称 | 描述 |
|------------|------|
| TRAE-product-knowledge | TRAE 品牌与官方产品知识问答 |
| web-dev | 从零创建生产级 Web 页面 / 应用 |

## 文件说明

- `collect_skills.py` — 主脚本，提供 Skill 的查询、记录和导出功能
- `.skill_history.json` — Skill 使用历史记录，自动生成与维护
- `.github/workflows/collect-skills.yml` — GitHub Actions 工作流配置

## GitHub Actions

项目配置了自动化工作流，以下情况会自动运行并将结果提交回仓库：

- 推送代码到 `main` 分支时
- 每天 UTC 00:00（北京时间 08:00）定时执行
- 在仓库 Actions 页面手动触发

运行时会生成 `skills_report.md` 和 `skills_report.json` 两个报告文件。

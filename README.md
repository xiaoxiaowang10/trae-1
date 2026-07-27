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

## 部署到 Vercel（定时邮件推送）

使用 Vercel Cron Jobs 实现每日自动发送技术资讯邮件。

### 部署步骤

#### 1. 准备工作

- 注册 [Vercel](https://vercel.com) 账号
- 安装 Vercel CLI：`npm i -g vercel`

#### 2. 配置环境变量

在 Vercel 项目的 **Settings → Environment Variables** 中添加以下变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `SMTP_HOST` | SMTP 服务器地址 | `smtp.126.com` |
| `SMTP_PORT` | SMTP SSL 端口 | `465` |
| `SMTP_USER` | 发件人邮箱 | `your@email.com` |
| `SMTP_PASS` | 邮箱授权码（不是登录密码） | `xxxxxxxx` |
| `FROM_ADDR` | 发件人地址（可选，默认同 SMTP_USER） | `your@email.com` |
| `TO_ADDR` | 收件人邮箱 | `to@email.com` |
| `CRON_SECRET` | 可选，API 访问密钥 | `随机字符串` |

#### 3. 部署

```bash
# 登录 Vercel
vercel login

# 首次部署（按提示选择项目）
vercel

# 部署到生产环境
vercel --prod
```

#### 4. 手动测试

部署成功后，访问：

```
https://your-project.vercel.app/api/send-digest
```

如果配置了 `CRON_SECRET`，需要在请求头中携带：

```bash
curl -H "Authorization: Bearer YOUR_CRON_SECRET" https://your-project.vercel.app/api/send-digest
```

### 定时任务配置

默认每天 **早上 8:00** 自动发送邮件，配置在 [vercel.json](vercel.json) 的 `crons` 字段：

```json
{
  "crons": [
    {
      "path": "/api/send-digest",
      "schedule": "0 8 * * *"
    }
  ]
}
```

使用标准 5 位 cron 表达式（UTC 时间），如需修改发送时间，调整 `schedule` 即可。

> ⚠️ 注意：Vercel Cron Jobs 仅在 **Pro** 及以上套餐可用。Hobby 套餐需要手动触发或使用第三方定时服务。

### 文件说明

| 文件 | 说明 |
|------|------|
| `vercel.json` | Vercel 部署配置，含 Cron 定时任务 |
| `api/send-digest.py` | Serverless Function 入口 |
| `send_daily.py` | 核心逻辑（抓取 + 发送） |
| `requirements.txt` | Python 依赖清单 |

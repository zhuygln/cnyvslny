# Contributing to cnyvslny

Thank you for helping build this dataset! There are two ways to contribute.

## Path 1: Via GitHub Issue (no coding required)

1. Go to [New Issue](https://github.com/zhuygln/cnyvslny/issues/new/choose)
2. Choose **Add an entity**, **Update an entity**, or **Correction request**
3. Fill in the form fields
4. Submit — a maintainer will review and add it to the dataset

## Path 2: Via Pull Request

1. **Fork** this repository
2. Edit `data/2026.jsonl` (or create a new year file, e.g. `data/2027.jsonl`)
3. Add one JSON object per line with the following fields:

| Field | Required | Description |
|---|---|---|
| `entity_name` | yes | Name of the organization |
| `entity_type` | yes | One of: `company`, `school`, `gov`, `media`, `nonprofit`, `app`, `other` |
| `country_or_region` | yes | Country or region the organization is based in |
| `term_used` | yes | One of: `Chinese New Year`, `Lunar New Year`, `Lunar New Year (Chinese New Year)`, `Spring Festival`, `other` |
| `exact_phrase` | yes | The literal text used by the organization |
| `context` | yes | One of: `social_post`, `press_release`, `product_ui`, `email`, `event_page`, `website`, `other` |
| `platform` | yes | Where it was published (e.g. "X", "Instagram", "company website") |
| `source_url` | yes | Public URL to the source |
| `captured_on` | yes | Date captured, format: YYYY-MM-DD |
| `notes` | no | Any additional context |
| `contributor` | yes | Your GitHub username |
| `evidence` | no | Path to a screenshot in the `evidence/` directory |

4. **Evidence screenshots** (optional): place them in the `evidence/` directory. Use a descriptive filename like `apple-lny-2026.png`.
5. Submit your pull request. CI will automatically validate the data.

## Moderation policy

- This is a **descriptive dataset**, not a cancel list. We document what organizations say — nothing more.
- **Evidence is required.** Every entry must link to a publicly verifiable source.
- **No insults or political rants** in the `notes` field. Keep it factual.
- **Correction requests** are welcome. If an entity believes their entry is inaccurate, they may open a correction request issue.

---

# 贡献指南

感谢你帮助建设这个数据集！有两种贡献方式。

## 方式一：通过 GitHub Issue（无需编程）

1. 访问 [新建 Issue](https://github.com/zhuygln/cnyvslny/issues/new/choose)
2. 选择 **Add an entity（添加机构）**、**Update an entity（更新机构）** 或 **Correction request（纠错请求）**
3. 填写表单
4. 提交 — 维护者会审核并将其添加到数据集

## 方式二：通过 Pull Request

1. **Fork** 本仓库
2. 编辑 `data/2026.jsonl`（或创建新的年份文件，如 `data/2027.jsonl`）
3. 每行添加一个 JSON 对象，字段如下：

| 字段 | 必填 | 说明 |
|---|---|---|
| `entity_name` | 是 | 机构名称 |
| `entity_type` | 是 | 可选值：`company`（公司）、`school`（学校）、`gov`（政府）、`media`（媒体）、`nonprofit`（非营利）、`app`（应用）、`other`（其他） |
| `country_or_region` | 是 | 机构所在国家或地区 |
| `term_used` | 是 | 可选值：`Chinese New Year`、`Lunar New Year`、`Lunar New Year (Chinese New Year)`、`Spring Festival`、`other` |
| `exact_phrase` | 是 | 机构使用的原始文本 |
| `context` | 是 | 可选值：`social_post`（社交媒体帖子）、`press_release`（新闻稿）、`product_ui`（产品界面）、`email`（邮件）、`event_page`（活动页面）、`website`（网站）、`other` |
| `platform` | 是 | 发布平台（如 "X"、"Instagram"、"公司官网"） |
| `source_url` | 是 | 公开来源链接 |
| `captured_on` | 是 | 采集日期，格式：YYYY-MM-DD |
| `notes` | 否 | 补充说明 |
| `contributor` | 是 | 你的 GitHub 用户名 |
| `evidence` | 否 | 截图路径（位于 `evidence/` 目录） |

4. **截图证据**（可选）：放入 `evidence/` 目录，使用描述性文件名，如 `apple-lny-2026.png`。
5. 提交 Pull Request，CI 会自动验证数据格式。

## 审核政策

- 这是一个**描述性数据集**，不是抵制名单。我们只记录机构的用词，仅此而已。
- **必须提供证据。** 每条记录都必须链接到可公开验证的来源。
- `notes` 字段中**不得包含侮辱性言论或政治宣泄**，请保持客观。
- 欢迎提交**纠错请求**。如果机构认为其记录不准确，可以通过 Issue 提出纠正。

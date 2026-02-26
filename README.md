# cnyvslny

**Tracking how organizations label the holiday — 追踪各机构如何称呼这个节日**

## What is this?

**cnyvslny** is an open, community-maintained dataset that records whether organizations use *Chinese New Year*, *Lunar New Year*, *Spring Festival*, or another term when referring to the holiday. Each entry links to a public source so anyone can verify the claim.

## Why it matters

The traditional Chinese calendar is **lunisolar** (based on both the moon and the sun), not purely lunar. The term "Lunar New Year" has become common in English, but many people feel it obscures the holiday's Chinese origins. Others prefer it as a more inclusive umbrella term. This dataset does not take a side — it simply documents what organizations actually say.

## Browse the data

Data lives in [`data/2026.jsonl`](data/2026.jsonl). Each line is a JSON object with these fields:

| Field | Description |
|---|---|
| `entity_name` | Name of the organization |
| `entity_type` | `company`, `school`, `gov`, `media`, `nonprofit`, `app`, or `other` |
| `country_or_region` | Where the organization is based |
| `term_used` | `Chinese New Year`, `Lunar New Year`, `Lunar New Year (Chinese New Year)`, `Spring Festival`, or `other` |
| `exact_phrase` | The literal text the organization used |
| `context` | `social_post`, `press_release`, `product_ui`, `email`, `event_page`, `website`, or `other` |
| `platform` | Where it was published (e.g. "X", "Instagram", "company website") |
| `sources` | Array of source objects, each with a required `url` and optional `evidence` path |
| `captured_on` | Date the entry was captured (YYYY-MM-DD) |
| `notes` | Optional free-text notes |
| `contributor` | GitHub username of the contributor |

## Not a boycott list

This project exists solely to document publicly observable terminology choices. It does **not** endorse, encourage, or facilitate boycotts, harassment, or any targeted action against organisations based on the term they use. Organisations are free to choose whatever terminology they consider appropriate. The dataset is intended for research, education, and informed discussion — not to pressure, shame, or punish any entity.

Blog posts and opinion pieces hosted on this site represent the views of their individual authors and do not reflect the position of the project.

## How to contribute

We welcome contributions! You can:

1. **Open an issue** — use one of our [issue templates](https://github.com/zhuygln/cnyvslny/issues/new/choose) (no coding required)
2. **Submit a pull request** — add entries directly to the JSONL file

See [CONTRIBUTING.md](CONTRIBUTING.md) for full details.

## License

[MIT](LICENSE)

---

# cnyvslny

**追踪各机构如何称呼这个节日 — Tracking how organizations label the holiday**

## 这是什么？

**cnyvslny** 是一个开放的、由社区维护的数据集，记录各机构在提及这一节日时使用的是"Chinese New Year（中国新年）"、"Lunar New Year（阴历新年）"、"Spring Festival（春节）"还是其他称呼。每条记录都附有公开来源链接，任何人都可以核实。

## 为什么重要？

中国传统历法是**阴阳合历**（既基于月亮也基于太阳），而非纯阴历。"Lunar New Year（阴历新年）"一词在英语中越来越常见，但许多人认为这种叫法模糊了节日的中国渊源。也有人认为这是一个更具包容性的统称。本数据集不作立场判断——只记录各机构实际使用的称呼。

## 浏览数据

数据位于 [`data/2026.jsonl`](data/2026.jsonl)。每一行是一个 JSON 对象，包含以下字段：

| 字段 | 说明 |
|---|---|
| `entity_name` | 机构名称 |
| `entity_type` | `company`（公司）、`school`（学校）、`gov`（政府）、`media`（媒体）、`nonprofit`（非营利）、`app`（应用）或 `other`（其他） |
| `country_or_region` | 机构所在国家或地区 |
| `term_used` | `Chinese New Year`、`Lunar New Year`、`Lunar New Year (Chinese New Year)`、`Spring Festival` 或 `other` |
| `exact_phrase` | 机构使用的原始文本 |
| `context` | `social_post`（社交媒体帖子）、`press_release`（新闻稿）、`product_ui`（产品界面）、`email`（邮件）、`event_page`（活动页面）、`website`（网站）或 `other` |
| `platform` | 发布平台（如 "X"、"Instagram"、"公司官网"） |
| `sources` | 来源数组，每项包含必填的 `url` 和可选的 `evidence` 截图路径 |
| `captured_on` | 采集日期（YYYY-MM-DD） |
| `notes` | 可选的备注 |
| `contributor` | 贡献者的 GitHub 用户名 |

## 本项目不是抵制名单

本项目仅记录各机构公开使用的节日称呼，**不**支持、鼓励或协助任何形式的抵制、骚扰或针对性行动。各机构有权自行选择其认为合适的称呼。数据集仅用于研究、教育和知情讨论，不用于施压、羞辱或惩罚任何实体。

本站所载博客和评论文章仅代表作者个人观点，不代表项目立场。

## 如何贡献

欢迎贡献！你可以：

1. **提交 Issue** — 使用我们的 [Issue 模板](https://github.com/zhuygln/cnyvslny/issues/new/choose)（无需编程）
2. **提交 Pull Request** — 直接向 JSONL 文件添加记录

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[MIT](LICENSE)

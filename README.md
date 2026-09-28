# research-ideation

面向顶会/顶刊的科研选题流水线，以 [Claude Code](https://claude.com/claude-code) skill 的形式提供，也附带可以直接贴进 ChatGPT、Codex、Gemini 的独立提示词。

它不从"帮我想个 idea"开始，而是按研究者的实际工作方式推进：

1. **画像**：研究方向、目标会议、资源、不公平优势
2. **理解领域**：先建领域本体，不急着创造
3. **演化地图**：分期、驱动力、演化链、争议、空白格
4. **挖 gap**：公开评审、论文自述的局限、压力测试、实践与研究脱节、共享的隐含假设、跨领域迁移
5. **研究问题**：从话题收敛到可证伪的研究问题
6. **发散 idea**：多种算子分批生成，强制保证多样性
7. **多专家会审**：领域 AC、方法专家、实验设计、行业、管理学、相邻领域、Reviewer 2
8. **查新与评估**：四个轴查新，评分表加两两比较
9. **去风险**：Heilmeier 八问、风险排序、两周试点

每一步都有模板和提示词。设计依据来自 AI 辅助科研选题的实证研究，以及多位研究者公开的方法论，汇总见 [`references/researcher_playbook.md`](references/researcher_playbook.md)。

## 安装（Claude Code）

把整个文件夹放到用户级 skills 目录：

```bash
git clone https://github.com/chendahe666/research-ideation-skill.git ~/.claude/skills/research-ideation
```

之后在 Claude Code 里说"用 research-ideation 帮我做 XX 方向的选题"就会触发。只想梳理领域的话，说"只做到领域地图"。

## 不用 Claude Code 时

把 [`references/standalone_prompt.md`](references/standalone_prompt.md) 里的主提示词贴进任意对话模型，最好开启联网搜索。专家会审可以把单个角色的提示词分别贴到不同模型里，交叉比对。

## 附带脚本（只依赖 Python 标准库）

| 脚本 | 作用 |
|---|---|
| `scripts/lit_scan.py` | 通过 OpenAlex 做领域扫描：逐年趋势、各时期高引论文、最新论文，输出 Markdown 和 JSON |
| `scripts/extract_limitations.py` | 从 arXiv HTML（旧论文回退到 ar5iv）中抽取 Limitations、Future work、Discussion 等章节 |
| `scripts/openreview_reviews.py` | 在 OpenReview 按关键词检索投稿；下载评审需要你自己的 OpenReview 账号（环境变量） |

```bash
python scripts/lit_scan.py -q "\"Gaussian splatting\" watermark" -q "NeRF watermark" --from 2016 --out scan
python scripts/extract_limitations.py --scan scan.json --out limitations.md
python scripts/openreview_reviews.py -t watermark --require "3d" -v ICLR.cc/2025/Conference --out reviews
```

## 目录结构

```
SKILL.md                      主流程与规则
references/
  stage1-2_field_map.md       领域入门与演化地图模板
  stage3_gap_mining.md        gap 证据源、分类法、提示词
  stage4-5_questions_and_ideas.md  研究问题阶梯、发散算子、idea 卡片
  stage6_expert_panel.md      专家角色卡与四轮会审流程
  stage7-8_evaluate_and_derisk.md  查新协议、评分表、去风险计划
  researcher_playbook.md      研究者方法论与 AI 选题实证汇总（附原文链接）
  standalone_prompt.md        独立版提示词
scripts/                      上面三个脚本
```

## 注意

- LLM 给 idea 打分并不可靠。流水线里的评分和会审只是帮你做决定的材料，最终要由研究者判断。
- 宣称"没人做过"之前，一定要查最近 6–12 个月的 arXiv 和 OpenReview。
- OpenReview 对匿名的自动访问会启用人机验证。脚本不会绕过验证，需要使用你自己的账号。

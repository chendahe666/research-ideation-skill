---
name: research-ideation
description: 顶会/顶刊级科研选题流水线：理解领域 → 画领域演化地图 → 从论文局限性和公开评审里挖 gap → 把话题收敛成可研究的问题 → 多算子发散 idea → 模拟多专家会审 → 查新 → 设计去风险的最小实验。当用户想找研究方向、研究问题、论文 idea 或创新点，想梳理某领域近 5–10 年的发展脉络，想找 research gap，想评估一个 idea 值不值得做，或想让多位模拟专家（教授、审稿人、从业者）头脑风暴/评审选题时使用。Use for research ideation, field mapping, gap finding, idea evaluation and simulated expert panels.
---

# 科研选题流水线（Research Ideation Pipeline）

核心分工：**AI 负责读得多、读得快、列得全；研究者负责判断什么值得做。**
好 idea 很少出自无人涉足的空白，更多藏在"别人做过、但没做好 / 没做完 / 前提有问题"的地方。
所以顺序是先理解、再找不足、最后才创造，而不是开口就说"帮我想个 idea"。

## 为什么这样设计（证据 → 规则）

| 证据 | 本 skill 的规则 |
|---|---|
| Si et al. 2024（100+ NLP 研究者盲评）：LLM idea 被评为更新颖，但可行性略弱；每个主题生成 4000 个种子，去重后只剩约 5%；LLM 当评委的准确率 53%，还低于人类评审之间的一致率 56% | 发散时必须多算子、去重；LLM 的打分只能当信号，最后由人拍板；排序用两两比较，不用绝对分 |
| Si et al. 2025（Ideation–Execution Gap，ICLR 2026）：真正做出来之后，LLM idea 的各项得分比人类 idea 掉得更多 | 每个 idea 都要写清最小验证实验、失败信号和 fallback 方案 |
| Chain of Ideas（EMNLP 2025 Findings）：把文献组织成"演化链"后，LLM 的 idea 明显变好 | Stage 2 先画演化链，再外推下一环 |
| Virtual Lab（Nature 2025）：PI、多个专家 agent 加一个科学批评者，批评者对减少幻觉最关键 | Stage 6 专家面板里固定放一个 Reviewer 2 / 批评者 |
| Meincke, Mollick & Terwiesch 2024：CoT 加异质 persona 能显著提高 idea 多样性 | 按算子分批生成，并用不同 persona 发散 |
| Sandberg & Alvesson 2011：大部分论文靠 gap-spotting，真正有影响力的工作往往挑战已有假设 | Stage 3 同时做 gap 分类和假设挑战（problematization） |
| AI scientist 综述（2026）：只有 38% 的系统报告了查新方法 | Stage 7 强制多轮查新，而且必须覆盖近 6–12 个月 |

证据来源和各位研究者的方法论汇总在 [references/researcher_playbook.md](references/researcher_playbook.md)。

## 工作区与总规则

- 在当前目录建 `ideation/<topic-slug>/`（用户另有指定就听用户的）。每个阶段的产出写成一个文件：`00_profile.md` 到 `08_proposal.md`，原始数据放 `raw/`。之后的会话可以接着往下做。
- **不许编造文献。** 每条文献事实都要有检索到的出处（标题、年份、venue、链接）。拿不准的标 `[未核实]`，不能靠记忆补全引用。
- **先查近况再说有 gap。** 这些领域更新很快，宣称"没人做过"之前，要按 Stage 7 的方法查最近 6–12 个月的 arXiv、OpenReview 和 Google Scholar。
- **人类检查点。** 带 ⏸ 的阶段结束后先停下：给用户看摘要，只问 1–3 个关键问题，得到确认再继续。用户说"一口气跑完"时可以不停，但要把你替用户做的假设列出来。
- **禁止空话。** "很有前景"、"值得探索"这类话不能单独出现，每个判断都要落到具体论文、数据或机制上。
- 输出用用户的语言。术语保留英文原词，例如 gap、baseline、threat model。

## 三种模式

- **完整模式**（默认）：Stage 0 → 8，通常分几次会话完成。
- **地图模式**：用户只想了解领域，做 Stage 0–3 就停。
- **评审模式**：用户已经有 idea，做一个精简版 Stage 0（只问目标 venue 和资源），然后快速补 Stage 1–3 里和这个 idea 相关的部分，再做 Stage 6–8。

---

## Stage 0：定锚（研究者画像）⏸

缺什么问什么，放在一条消息里问完：
1. 领域和子方向；已经读过的 3–10 篇核心论文（种子论文）
2. 目标 venue 和时间线（例如 CVPR 截稿日；TIFS / TVCG 等期刊）
3. 资源：GPU、数据、合作者、可投入的月数
4. **不公平优势**：独有的数据、设备、领域知识、工程能力、合作方或应用场景
5. 偏好：方法 / 分析-实证 / benchmark-数据集 / 理论 / 系统；风险偏好（热点上做得更好，还是赌下一个热点）
6. 已经有的想法；明确排除的方向

产出 `00_profile.md`。后面每个阶段都要回头对照这份画像。

## Stage 1：理解领域，先不创造

目标是给领域建一份"本体"：任务定义、问题设定、数据表示、威胁模型或实验设定、指标、benchmark 和数据集、主流 baseline、代表性团队和 venue、术语表。

做法：
1. 跑文献扫描脚本（第一次看这个领域就跑；把一个大话题拆成 3–6 个子方向 query，加引号的短语更精确）：
   ```bash
   python "<skill_dir>/scripts/lit_scan.py" -q "\"Gaussian splatting\" watermark" -q "NeRF watermark" -q "\"point cloud\" watermarking" --from 2016 --out ideation/<slug>/raw/scan
   ```
   Windows 上 `python` 不可用就换成 `py`。脚本走 OpenAlex，不需要 key，会输出逐年趋势、各时期高引论文和最新论文。遇到 429 限流时，可以让用户自己申请一个免费的 OpenAlex API key，设到环境变量 `OPENALEX_API_KEY`。OpenAlex 对最近几周的 arXiv 收录不全，这段时间要用 WebSearch 补查。
2. 读种子论文和扫描结果里的高引综述，必要时用 WebSearch / WebFetch 补 survey 和 benchmark 页面。

产出 `01_domain_primer.md`，模板见 [references/stage1-2_field_map.md](references/stage1-2_field_map.md)。

## Stage 2：领域演化地图 ⏸

要画的是"过去怎么做 → 现在怎么做 → 新技术加入后变成什么样"，不是一份论文清单。
- **分期**：每个时期写清主导范式、代表作、解决了什么、默认了什么假设、评测方式、留下了什么问题。
- **驱动力**：是什么推着领域换了范式？可能是新的表示、算力、数据、应用需求、法规或新攻击。
- **演化链**（Chain of Ideas）：A → B → C，每一环都在修补上一环的缺陷。外推"下一环"是什么。
- **争议**：哪些结论互相矛盾，哪些评测口径不统一。
- **没人做的方向**：趋势表里哪些组合是 0 或者很少。

模板和提示词见 [references/stage1-2_field_map.md](references/stage1-2_field_map.md)。
⏸ 问用户：地图和你的认知一致吗？哪一段最让你感兴趣？

## Stage 3：挖 gap（机会藏在已有研究的不足里）⏸

从强到弱，至少用 4 类证据源：
1. **公开评审**（信号最强）：多篇论文的评审反复提到的同一类弱点，说明整个领域都有这个缺口。
   ```bash
   python "<skill_dir>/scripts/openreview_reviews.py" -t watermark --require "gaussian splatting" -v ICLR.cc/2025/Conference -v ICLR.cc/2026/Conference --out ideation/<slug>/raw/or
   ```
   下载评审需要用户用自己的 OpenReview 账号设置环境变量；不设的话只能拿到投稿列表和链接，让用户在浏览器里看。**你不能替用户输入密码，也不能替用户通过人机验证。**
2. **作者自己承认的局限**：Limitations、Future work、Discussion 这几节。
   ```bash
   python "<skill_dir>/scripts/extract_limitations.py" --scan ideation/<slug>/raw/scan.json 2608.17447 --out ideation/<slug>/raw/limitations.md
   ```
3. **拿 SOTA 做压力测试**：用公开代码跑真实场景或分布外样本，找失败案例。这是一手证据，将来也最适合放进论文的 Figure 1。
4. **不同论文结论互相矛盾**（evidence gap）。
5. **实践和研究脱节**：热门 repo 的 GitHub issues、工业界博客、标准和法规。
6. **所有论文共享的隐含假设**（problematization）。
7. **相邻领域的成熟技术还没迁移过来**。
8. **评测本身的缺口**：benchmark 饱和、指标和人的判断不一致、攻击集太弱。

**效率最高的一步：先找近 12 个月的综述和 awesome 列表。**
- 综述的 "Future Directions" 章节就是现成的 gap 清单，可以用 `extract_limitations.py` 直接抽出来
- awesome 列表是最快的查新名单

实际运行中，常常就是从某篇综述的 Future Directions 里，发现了关键词检索漏掉的关键前作。

每个 gap 都要分类，参照 Miles 的 7 类 gap 和 Sandberg & Alvesson 的几种 gap-spotting 模式，并做"最近是否已经被填上"的检查。
产出 `03_gap_ledger.md`（gap 台账）。表格、分类法和提示词见 [references/stage3_gap_mining.md](references/stage3_gap_mining.md)。
⏸ 问用户：哪 3–5 个 gap 让你有感觉？哪个和你的不公平优势最匹配？

## Stage 4：从话题收敛到研究问题

用"话题 → 问题 → 意义"这个阶梯（李沐《研究的艺术》/ *The Craft of Research*），用 5W1H 把问题收窄：
> 我研究 **[话题]**，因为我想弄清 **[具体问题]**，以便帮助读者理解 **[更大的意义]**。

每个研究问题都要写清：挑战的假设或针对的 gap ID、可以证伪的假设、一个决定性实验、什么结果会让人意外。
产出 `04_research_questions.md`，模板见 [references/stage4-5_questions_and_ideas.md](references/stage4-5_questions_and_ideas.md)。

## Stage 5：发散 idea（多算子 + 强制多样性）

- 按不同算子分批生成：Jia-Bin Huang 的 7 种方法、ResearchStudio-Idea 的 15 种模式、挑战假设、facet 重组、演化链外推、目标倒推、极简化、诊断型论文、新 benchmark 或新威胁模型。
- 每批生成后都和已有 idea 对比，去掉重复并合并近似的。最终至少要覆盖 4 种 idea 类型（方法 / 分析 / benchmark / 理论 / 系统），其中至少 2 个是反共识的 idea。
- 挑出 5–8 个写成完整的 **idea 卡片**（包含一句话洞见、why now、最小验证实验、fallback 等）。

产出 `05_idea_pool.md`。算子表和卡片模板见 [references/stage4-5_questions_and_ideas.md](references/stage4-5_questions_and_ideas.md)。

## Stage 6：模拟多专家会审 ⏸

默认 7 个角色：领域资深 AC、方法/理论专家、数据科学与实验设计教授、行业研究者、管理学/社会科学教授、相邻领域专家，以及固定参加的**科学批评者（Reviewer 2）**。可以按领域替换。
流程分四轮：**先独立评估，避免锚定 → 交叉质询 → 每人给一个建设性改造 → PI 综合**。保留分歧，不要强行达成共识。
如果用户要求角色真正互相独立，可以让每个角色各开一个子代理，只喂 idea 卡片和证据包；也可以把 standalone prompt 贴到 Codex / ChatGPT / Gemini，拿不同模型的意见交叉对比。
角色卡和各轮的输出格式见 [references/stage6_expert_panel.md](references/stage6_expert_panel.md)。
⏸ 让用户选 1–2 个 idea 进入查新和去风险。

## Stage 7：查新与收敛评估

- **查新**：借鉴 Scoop-Check 的思路，把 idea 拆成 4 个轴：问题框定、核心机制、关键洞见、应用领域。每个轴用 3–5 种说法去检索，至少包括 OpenAlex、Semantic Scholar、arXiv 最近 6–12 个月、OpenReview 和 Google Scholar。列出最接近的 3–5 篇工作，逐轴写出差异，最后给结论：新颖 / 部分重叠需重定位 / 已被做过。
- **评分**：用评分表（重要性、新颖性、洞见、可行性、gap 证据强度、时机、可延展性、优势匹配、执行风险）。多个 idea 之间用两两比较来排序。
- **淘汰标准**：任何一条命中就砍掉或重构。

产出 `07_novelty_check.md`。评分表见 [references/stage7-8_evaluate_and_derisk.md](references/stage7-8_evaluate_and_derisk.md)。

## Stage 8：去风险计划和一页提案

- 回答 Heilmeier 的 8 个问题，第一个问题不许用术语。
- 列出风险最大的假设，按 Steinhardt 的"单位时间信息量"排序：最可能失败、又最快能验证的放在最前面。
- 设计 ≤2 周的试点实验，写清 go / no-go 标准和 fallback 方案。
- 画出 Figure 1 的草图，写出摘要初稿。如果写不出来，说明问题还没想清楚。

产出 `08_proposal.md`。模板见 [references/stage7-8_evaluate_and_derisk.md](references/stage7-8_evaluate_and_derisk.md)。

---

## 常见反模式（一旦发现立刻指出）

- 只有宏大话题，没有具体问题（"AI 改变教育"、"3D 水印的新方法"）
- 只是 A+B 的拼接，说不出为什么这样组合会有效
- 说不清现有方法为什么不行，或者只引了一篇论文的 future work 就宣称存在 gap
- 需要用户手里没有的资源
- 引用了不存在或没核实的论文
- 这个 gap 上个月已经被 arXiv 上的新论文填上了
- LLM 的评分虚高，被当成了结论

## 离开 Claude Code 时

要在 ChatGPT / Codex / Gemini 里用，就把 [references/standalone_prompt.md](references/standalone_prompt.md) 整段贴过去。那个版本不带脚本，文献检索要靠对方的联网搜索或 Deep Research 功能。

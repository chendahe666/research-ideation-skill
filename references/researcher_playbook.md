# 科研选题方法论汇总：研究者怎么想，AI 怎么帮

整理日期：2026-09-24。每条都附出处，原文链接在文末。

## 0. 覆盖的渠道和局限

- **研究者长文和演讲**：Hamming、Schulman、Karpathy、Nielsen、Steinhardt、Olah、Jason Wei、Neel Nanda、Terence Tao
- **X（Twitter）**：Jia-Bin Huang 的选题 thread 和 Introduction 写作 thread；Chris Olah 的研究品味练习 thread；hardmaru 转述 Schulman 的观点
- **中文社区**：李沐 B 站《研究的艺术》系列；知乎上关于顶会 idea 的经验帖
- **管理学和社科方法论**：Sandberg & Alvesson（gap-spotting 与 problematization）、Miles（7 类 gap）、Davis（*That's Interesting!*）；DARPA 的 Heilmeier 问答
- **AI 辅助选题的论文和系统**：Stanford 的两项大规模人类实验、Chain of Ideas、ResearchAgent、Scideator、AI Scientist v2、Google AI co-scientist、Virtual Lab、STORM、ResearchStudio-Idea 等
- **公开评审**：OpenReview（ICLR 的评审连被拒稿件一起公开）

**局限**：X 和 Facebook 上"用 AI 提示词找 idea"的内容，大多是营销性质的提示词合集，很少有知名研究者系统地公开自己的 AI 选题流程；Facebook 基本检索不到可靠内容。所以关于"研究者怎么用 AI"，这里主要依据可核实的论文、访谈研究和少数公开发言，没有收录无法核实的帖子。

---

## 1. 共识：几乎所有人都会说的 7 件事

1. **选题是乘数，值得花大量时间。**
   - Hamming："你必须做重要的问题"
   - Jason Wei：大多数人都能从"在选题上多花时间"中获益，因为选得好会放大研究的影响
   - Schulman：选上限高的问题
2. **重要不等于宏大。** Hamming 说，问题重要的前提是既有影响力，又有"合理的突破口"（reasonable attack）。李沐把这个过程拆成话题 → 问题 → 意义。"AI 改变教育"是话题，不是问题。
3. **先深度理解领域。**
   - Schulman：想靠 idea-driven 的研究取得突破，需要对课题有极深的理解，还要有和社区不一样的视角
   - Neel Nanda：研究品味来自对领域的深刻理解、对好坏研究的见识，以及对"哪些问题真正重要"的全局判断
4. **机会多藏在已有工作的不足里。**
   - Jia-Bin Huang 的方法里有"放松假设"和"压力测试 SOTA"
   - 知乎经验：把几篇论文在假设、方法、数据上的差异画成对比表，找空白格
   - Sandberg & Alvesson：统计了 52 篇论文，发现 gap-spotting 是最主流的提问方式；但真正有影响力的理论，往往来自挑战已有假设
5. **品味可以训练，前提是有反馈。**
   - Olah：请导师给你的 idea 打分；观察别人把你想过的 idea 做出来之后结果如何
   - Jason Wei：和非常成功的研究者近距离合作，对培养品味是很好的强制机制，因为他们对增量式的 idea 不感兴趣
6. **尽早去风险。** Steinhardt 主张按"单位时间的信息量"排列任务，并尽快找出死路。Schulman 则提醒不要太早放弃有希望的项目。两者的调和见第 5 节。
7. **问题要具体、可证伪、用大白话说得清。** Heilmeier 第一问要求不用任何术语；李沐用 5W1H 收窄问题。

## 2. 各家的独门技巧

| 来源 | 技巧 | 怎么和 AI 结合 |
|---|---|---|
| **Hamming**, *You and Your Research* (1986) | 每周五下午留出 10% 的时间，只想"大问题"；伟大的科学家脑子里常备 10–20 个重要问题，一直在等突破口；开着门工作，保持和外界的连接 | 把 gap 台账当作你的"10–20 个重要问题清单"，每周五让 AI 检索有没有新的突破口（新方法、新数据） |
| **Schulman**, *An Opinionated Guide to ML Research* | **goal-driven 优于 idea-driven**：先设想想要的新能力，再解决通往它的问题；保持每日实验笔记并定期复盘；留出有限的探索时间 | Stage 5 的"目标倒推"算子 |
| **Karpathy**, *A Survival Guide to a PhD* (2016) | 选"肥沃的土壤"：博士期间的论文会一篇接一篇地叠起来，所以选题时要往后多想几步，估计后续还有多少空间 | 评分表里的"可延展性"维度 |
| **Nielsen**, *Principles of Effective Research* | 区分 problem-solver 和 problem-creator：后者可能写技术上很简单、但提出了有趣新问题的论文；有意识地培养"什么是重要科学"的品味 | 在 Stage 5 保留"只提出新问题、新 benchmark"类型的 idea 配额 |
| **Steinhardt**, *Research as a Stochastic Decision Process* | 按单位时间的信息量排列任务；区分去风险模式和执行模式 | Stage 8 的风险排序表 |
| **Chris Olah**, *Research Taste Exercises* | ① 请导师给 idea 打 1–10 分 ② 看别人做出你想过的 idea 后结果如何 ③ 访谈研究者怎么选题 ④ 读科学史，看为什么有人关注了同行忽视的方向 ⑤ 批判地审视你所在社区的品味，想想它过去在哪些地方错了 | 专家面板就是练习 ① 的替代品，但要记住它比真导师弱 |
| **Jason Wei**（博客） | 偏好简单、通用、经得起时间检验的题目；两种策略：在热点上做得比所有人都好（风险低、要拼命），或者做可能成为下一个热点的东西（风险高、回报高） | 评分表里的"时机"维度 |
| **Neel Nanda** | 研究分三个模式：探索（获取信息、扩大接触面）→ 理解（验证具体假设）→ 提炼（把发现压缩成能说服别人的证据） | Stage 8 结尾 |
| **Jia-Bin Huang**（X） | 7 种选题方法：换个维度、放松假设、增加假设、组合、拿锤子找钉子、加形容词、压力测试 SOTA；Introduction 模板是 3 张图（WHAT / WHY / HOW）加 5 个问题 | Stage 5 算子 A；Stage 8 写作检验 |
| **李沐**《研究的艺术》 | 话题 → 问题（5W1H）→ 意义（追问 So what / If not） | Stage 4 |
| **知乎经验帖** | 维度对比表找空白；化繁为简；有机组合；聚焦核心痛点，不在边角问题上找 idea；"先自己冥想再查文献"，避免被已有研究框住思路 | Stage 0 先记录用户自己的原始想法；Stage 5 的极简化算子 |
| **Heilmeier**（DARPA） | 8 个问题：想做什么（不许用术语）、现在怎么做、新在哪、谁在乎、风险、成本、时间、期中和期末检验 | Stage 8 |
| **Sandberg & Alvesson** (2011) | 从 gap-spotting 走向 problematization：识别并挑战现有理论背后的假设 | Stage 3 的 G2 提示词 |
| **Miles** (2017) | 7 类 gap：evidence、knowledge、practical-knowledge conflict、methodological、empirical、theoretical、population | Stage 3 的分类 |
| **Davis** (1971) | 有意思的理论否定的是读者"弱持有"的假设 | 用来判断挑战哪个假设 |
| **Terence Tao** | 用 AI 做文献检索、写代码、做计算，以及试探某条路值不值得追；AI 必须和可靠的验证手段搭配，才能过滤幻觉；先在黑板上想清楚，再交给 AI 做计算 | 所有文献主张都必须有检索出处；AI 负责"找"和"查"，人负责"想" |

## 3. AI 辅助选题：系统与实证研究

| 工作 | 做法 | 关键发现 | 启示 |
|---|---|---|---|
| **Si, Yang, Hashimoto** — *Can LLMs Generate Novel Research Ideas?*（ICLR 2025） | 通过 Semantic Scholar 检索约 120 篇论文 → 每个主题生成 4000 个种子 idea → 去重（相似度阈值 0.8）→ 两两比较做 Swiss 锦标赛排序；49 位专家写 idea，79 位专家盲评 | LLM 的 idea 新颖性显著更高（p<0.05），可行性略弱；去重后只剩约 5%，而且继续生成时不重复的 idea 数量会见顶；LLM 评委的一致率 53%，低于人类评审之间的 56%；人工重排能提高可行性 | 必须多样化生成；LLM 打分不可靠；人要参与排序 |
| **Si et al.** — *The Ideation–Execution Gap*（ICLR 2026） | 43 位专家每人花 100 多小时，把随机分配到的 idea 做出来 | 做出来之后，LLM idea 在新颖性、兴奋度、有效性和总分上都比人类 idea 掉得更多，排名发生反转 | idea 阶段的评估不可靠，所以要写最小验证实验和 fallback |
| **Chain of Ideas**（EMNLP 2025 Findings） | 把文献组织成反映不同趋势的演化链，再预测每条链的下一步 | 质量明显优于直接给 LLM 喂文献 | Stage 2 的演化链 |
| **ResearchAgent**（NAACL 2025） | 从核心论文出发，结合学术图谱和概念实体库做检索；用人类偏好对齐的评审 agent 迭代改进 | 迭代改进在大约 3 轮之后收益递减 | 修订不必无限循环 |
| **Scideator**（ACM CAIS 2026） | 把论文拆成目的、机制、评测三个 facet，跨论文重组；从同领域到远领域做距离可控的类比检索；配有 facet 级的查新 | 相比没有 facet 模块的同款 LLM，对创造力的支持显著更强 | Facet 重组算子；按 facet 查新 |
| **AI Scientist v2**（Sakana 2025） | 先在摘要或基金申请书的抽象层面构思，再落到实现；查新时调用 Semantic Scholar，最多迭代 10 轮，每轮取 10 条结果 | — | 先写摘要；多轮查新 |
| **Google AI co-scientist**（2025；Nature 2026） | 分为生成、反思、排序、进化、邻近度、元评审等 agent；用 Elo 锦标赛做两两辩论和排序 | 在药物重定位等任务上找到了被忽视的候选，并经过湿实验验证 | 用两两比较和锦标赛排序 |
| **Virtual Lab**（Nature 2025） | PI agent 带领化学、计算机等专家 agent，外加一个科学批评者；分团队会议和一对一会议；人类给高层反馈 | 设计的纳米抗体经过实验验证；批评者对减少幻觉最关键 | 专家面板里固定放批评者 |
| **STORM / Co-STORM**（Stanford） | 先发现不同视角，再让持不同视角的角色向"专家"提问 | 覆盖面和组织性更好 | 由不同角色提问 |
| **Meincke, Mollick, Terwiesch**（2024） | 比较多种提示方法下 idea 池的多样性 | GPT-4 的 idea 池不如人类群体多样；CoT 带来的多样性最高，接近人类群体；persona 也有帮助 | 发散时用 CoT 和异质 persona |
| **ResearchStudio-Idea**（2026） | 从 ICLR、ICML、NeurIPS 2021–2025 的 1947 篇论文（包括 oral、高引和被拒稿件）中归纳出 15 种 idea 模式；Scoop-Check 按问题框定、机制、洞见、领域 4 个轴查新 | 盲评中优于不用 skill 和用通用 skill 的基线 | Stage 5 算子 B；Stage 7 查新 |
| **IdeaForecastBench**（2026） | 让 LLM 根据截止日期前的文献，预测之后会出现的研究方向 | 先把历史文献压缩成摘要再预测，比直接喂原文效果更好 | 先压缩成地图，再外推 |
| **AI scientist 综述**（2026） | 统计 24 个可运行的系统 | 只有 38% 报告了查新方法；瓶颈已经从"能不能完成任务"转向"能不能验证它的主张" | 强制查新 |
| **CHI 2025 访谈研究** | 访谈研究者怎样用 LLM | LLM 能带来出乎意料、高度个人化的灵感；常见用途是构思、写作、找相关工作和学习 | AI 是灵感来源，不是裁判 |

## 4. 研究者实际怎么用 AI（归纳）
1. **让 AI 找和整理**：文献地图、检索、总结、对比表（Tao、CHI 访谈研究）
2. **让 AI 挑刺**：扮演 Reviewer 2 或批评者（Virtual Lab、co-scientist 的反思 agent）
3. **让 AI 扩大发散面**：多个 persona、多种算子、大量生成后再去重（Si et al.、Meincke et al.）
4. **AI 的输出一律要验证**：Tao 用 Lean 验证证明；选题场景下对应的是逐条核实引用、查新，以及做最小实验
5. **判断留给人**：人来重排、选择和承担风险（Si et al. 发现人工重排能提高可行性；Virtual Lab 由人类给高层反馈）

## 5. 几组张力，以及怎么调和

| 张力 | 调和 |
|---|---|
| 尽快止损（Steinhardt）vs 别太早放弃（Schulman） | 区分两类不确定性。"可行性未知"要尽快验证，验证失败就止损；"执行上的困难"要坚持 |
| 先读大量文献 vs 先自己想（知乎） | Stage 0 先记录你自己的原始想法，再做 Stage 1–3，避免被文献和 AI 锚定 |
| gap-spotting（稳妥）vs 挑战假设（影响力大） | 两条路都走：台账里至少放 1–2 个挑战假设型的 gap |
| 热点上做得更好 vs 赌下一个热点（Jason Wei） | 由画像里的风险偏好和时间线决定 |
| idea-driven vs goal-driven（Schulman） | 领域理解很深的时候，可以从演化链外推；理解还不够的时候，先定目标能力，再倒推问题 |

## 6. 在本 skill 中的对应位置
- Stage 0 画像：Hamming 的"合理突破口"、不公平优势、知乎"先自己想"
- Stage 1–2 地图：Chain of Ideas、IdeaForecastBench、Karpathy 的"肥沃土壤"
- Stage 3 挖 gap：OpenReview、Limitations、Jia-Bin Huang 的压力测试、Miles、Sandberg & Alvesson
- Stage 4 研究问题：李沐 / *Craft of Research*、Heilmeier
- Stage 5 发散：Jia-Bin Huang 的 7 种方法、ResearchStudio 的 15 种模式、Scideator、Schulman、Meincke
- Stage 6 面板：Virtual Lab、STORM、co-scientist
- Stage 7 查新与评估：Scoop-Check、AI Scientist、Hamming、Jason Wei、Karpathy
- Stage 8 去风险：Steinhardt、Heilmeier、Neel Nanda、Schulman

## 原文链接
- Si, Yang, Hashimoto — Can LLMs Generate Novel Research Ideas? https://arxiv.org/abs/2409.04109
- Si et al. — The Ideation-Execution Gap https://arxiv.org/abs/2506.20803
- Chain of Ideas https://arxiv.org/abs/2410.13185
- ResearchAgent https://arxiv.org/abs/2404.07738
- Scideator https://arxiv.org/abs/2409.14634
- AI Scientist v2 https://arxiv.org/abs/2504.08066
- Google AI co-scientist https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/
- Virtual Lab https://www.biorxiv.org/content/10.1101/2024.11.11.623004v1 · https://github.com/zou-group/virtual-lab
- STORM https://github.com/stanford-oval/storm
- Meincke, Mollick, Terwiesch — Prompting Diverse Ideas https://arxiv.org/abs/2402.01727
- ResearchStudio-Idea https://arxiv.org/abs/2607.04439
- IdeaForecastBench https://arxiv.org/abs/2609.00747
- Autonomous Research Agents survey (verification gap) https://arxiv.org/abs/2608.05179
- Seeking Inspiration through Human-LLM Interaction (CHI 2025) https://dl.acm.org/doi/10.1145/3706598.3713259
- Hamming — You and Your Research https://www.cs.virginia.edu/~robins/YouAndYourResearch.html
- Schulman — An Opinionated Guide to ML Research http://joschu.net/blog/opinionated-guide-ml-research.html
- Karpathy — A Survival Guide to a PhD http://karpathy.github.io/2016/09/07/phd/
- Nielsen — Principles of Effective Research https://michaelnielsen.org/blog/principles-of-effective-research/
- Steinhardt — Research as a Stochastic Decision Process https://cs.stanford.edu/~jsteinhardt/ResearchasaStochasticDecisionProcess.html
- Olah — Research Taste Exercises https://colah.github.io/notes/taste/
- Jason Wei — blog https://www.jasonwei.net/blog
- Neel Nanda — Explore, Understand, Distill https://www.alignmentforum.org/posts/hjMy4ZxS5ogA9cTYK/how-i-think-about-my-research-process-explore-understand
- Jia-Bin Huang — How to come up with research ideas https://x.com/jbhuang0604/status/1423499757591400448
- Jia-Bin Huang — How to write the Introduction https://x.com/jbhuang0604/status/1638029709073166336
- 李沐《研究的艺术》笔记 https://zhuanlan.zhihu.com/p/595491948
- 知乎：怎么产生一个好的科研想法 https://zhuanlan.zhihu.com/p/349155927 · 顶会 idea 讨论 https://www.zhihu.com/question/661326101
- Sandberg & Alvesson — Ways of constructing research questions https://journals.sagepub.com/doi/10.1177/1350508410372151
- Miles — A Taxonomy of Research Gaps https://www.researchgate.net/publication/319244623
- Davis, M. S. (1971). That's Interesting! *Philosophy of the Social Sciences*, 1(4).
- Heilmeier Catechism https://www.darpa.mil/about/heilmeier-catechism
- Terence Tao on AI https://teorth.github.io/tao-web/ai-views.html

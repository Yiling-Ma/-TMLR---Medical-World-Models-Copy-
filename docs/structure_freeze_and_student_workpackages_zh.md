# 文章结构冻结与学生任务包

状态：建议从 2026-07-12 起冻结两周。结构冻结不代表证据结论冻结；数据库和全文复核仍可更新，但必须通过单一来源同步到正文、图和表。

## 1. 固定主线

整篇文章只回答一个问题：**medical world-model claim 到底由什么能力和什么公开证据支撑？** 两个正交坐标保持不变：非累积 capability category（L0--L4）与 SATO-V evidence record。clinical-action validity 是两者之间的判定标准，而不是第三套 taxonomy。

## 2. 固定章节（中英文）

1. Introduction / 引言：问题、立场、贡献和全文路线。
2. Related Work and Competitive Positioning / 相关工作与竞争定位。
3. Search, Corpus, and Coding Protocol / 检索、语料与编码协议。
4. Definition: State, Action, Transition, Outcome, and Validation / SATO-V 定义。
5. Capability Levels / 能力类别与边界。
6. Evidence Audit: Crossing Capability Levels with SATO-V / 两轴证据审计。
7. Synthesis by Literature Setting / 按临床 setting 综合。
   - Medical imaging representation / 医学影像表征
   - Longitudinal disease progression / 纵向疾病进展
   - EHR and patient trajectories / EHR 与患者轨迹
   - Digital twins / 数字孪生
   - Counterfactuals and treatment planning / 反事实与治疗规划
   - Surgical, robotic, and physiology models / 手术、机器人与生理模型
8. Why Medical World Models Are Hard: Structural Barriers / 结构性障碍。
9. Open Problems and Research Agenda / 开放问题与研究议程。
10. Practical Checklist for Authors and Reviewers / 作者与审稿人清单。
11. Worked Boundary Examples / 边界案例。
12. Discussion: What Should Count as Progress? / 什么才算实质进展。
13. Limitations and a Living Evidence Map / 局限与动态证据图谱。
14. Conclusion / 结论。
15. Appendix A: Database Fields / 数据库字段。
16. Appendix B: Screening Boundary / 纳入与筛选边界。

叙事分为五段：动机与定位（1--2）→ 证据方法（3--6）→ 六个临床 setting（7）→ 作者综合与建议（8--12）→ 局限和收束（13--16）。

## 3. 两周内不可变

- 章节数量、顺序、标题和六个 setting 的边界。
- L0--L4 非累积能力类别、SATO-V、clinical-action validity 和 L1/L2 三条件 action test。
- `db/papers.csv` 是计数和 Fig. 3 的唯一数据源；当前分布为 22/62/65/11/87。
- unknown / not publicly evidenced 不得写成 absent、failed 或 clinically invalid。
- Discussion 只回答“什么算进展”；具体未来建议只进 Research Agenda，避免重复。

## 4. 学生任务包模板

每个任务必须有：包名、负责人、截止时间、输入文件、输出路径、证据类型、验收人。分支命名为 `student/<setting-or-figure>`，禁止直接改 `main`。

### A. 六个 setting 证据包（六人或六组）

输出：`student_evidence/<setting>_evidence.csv` 与 `<setting>_synthesis_zh.md`。

每篇论文逐条记录：paper ID、版本、全文页码、state、settable action、transition、outcome、validation、代码/数据、建议 level、支持原句（短摘录）和 claim boundary。分析 memo 必须分成 `[EVIDENCE]`、`[SYNTHESIS-DRAFT]`、`[PI-DECISION]` 三类；学生可以提出主观综合，但不能直接改最终 level 或投稿口径。

验收：每个事实有 PDF 页码或官方 artifact；每个 setting 至少包含一个 mixed/negative case；所有正文引用均能回到 evidence card。

### B. 图包

- Fig. 1：medical world model 视觉定义；保留可编辑图层和图标来源表。
- Fig. 2：时间/谱系 roadmap；每个 work 名称、年份、归类必须由数据库核对。
- Fig. 3：仅维护数据脚本和 caption，不手改图中数字。
- Fig. 4：L1/L2 action boundary；不得出现无来源数值或被误读成真实患者轨迹的曲线。
- Fig. 5：capability × SATO-V 读图框架；不得重新引入主观红绿评分矩阵。

验收：editable source + vector PDF + PNG preview + source/provenance list；使用 `docs/visual_system_zh.md`；最终版面字号不低于 8 pt；caption 单独可读。

### C. 表包

- Table 2--3：从 CSV 独立重算 `n` 与 `%`，验证总和为 247。
- Table 4：26 篇 core paper 的每个 A/V/Code/Data 状态进行双人全文核对。
- 其余表：统一简称、版本、引用 key 和公开性口径。

验收：提交一份 machine-readable diff；不允许只改 TeX 表面值；两位复核者分歧必须留在 adjudication log。

## 5. PI/一作保留决策

最终 level adjudication、跨 setting 的主观判断、Introduction/Discussion/Agenda 的立场、强弱 claim 与投稿口径由 PI/一作决定。学生交付证据和候选综合，不替作者做未经讨论的结论。

## 6. 当前最高优先级

1. 补齐 corpus-wide coding-depth / evidence provenance，消除“下载了 PDF 但不等于全文复核”的缺口。
2. 完成六个 setting 的 evidence pack，再由作者统一写 analysis。
3. 对 Table 4 和正文强 claim 做双人核证；Fig. 1--2 再做编辑级视觉定稿。
4. 结构冻结期结束后只开一次 PI review，决定是否需要移动段落，不再做无证据驱动的章节重排。

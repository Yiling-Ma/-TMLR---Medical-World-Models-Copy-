# Claude Fable 5 图表与结构短评记录

日期：2026-07-12。方式：Claude Code CLI，模型 `claude-fable-5`，四个独立短 prompt；Claude 只读 PDF 与源文件，未直接编辑。

## 1. 视觉系统

Claude 识别到四个主要问题：同一颜色承担不同语义；红绿状态不具色盲安全性；L0--L4 被五彩编码为无序类别；Fig. 4 的手绘 PNG 和虚构式 `72%` 削弱审稿信任。建议采用 Okabe-Ito 医学化配色：ink `#1A2A3A`、blue `#0072B2`、teal `#009E73`、amber `#E69F00`、vermillion `#D55E00`、gray `#6E7B8B`、grid `#DDE3E8`。

## 2. Figure 3--5

- Fig. 3：保留 track × level 与 clinical-area 两面板；删除任意挑选的零值领域和红色 “long tail” 箭头；直接显示 level totals。
- Fig. 4：改为 TikZ 矢量图，删除 `72%`、仪表盘和医患装饰；图形必须对应三条 action test。
- Fig. 5：旧计数与数据库不一致，而且 SATO-V 状态矩阵为无聚合规则的硬编码。Claude 建议删除重复计数面板，并把图改为框架定义；经验审计留给 Table 4。

上述三点均采纳。Fig. 3 当前由 CSV 自动生成；Fig. 4--5 改为 TikZ。

## 3. Table 2--4

Claude 建议 Table 2--3 合并为双面板，并同时报告 `n/%/bar`；Table 4 去掉整格红底，用 `check / adjust / minus` 表示公开证据状态。我们采纳信息编码和 Table 4 去底色，但暂不合并 Table 2--3，以保持当前编号、引用和学生任务锚点稳定；两表已分别加入操作定义和同比例 share bar。

## 4. 结构冻结

Claude 建议保留现有 14 节正文和 2 个附录，两周内不再大规模移节；唯一编辑约束是 Worked Boundary Examples 控制长度，并将前瞻建议集中到 Research Agenda、将“什么算进展”的判断留在 Discussion。学生负责 evidence collection 和候选 synthesis，最终定级与主观结论由 PI/一作裁决。

## 5. 最终共识

1. 先修图文数据一致性，再谈装饰性美化。
2. Fig. 5 不应呈现无可复现规则的“典型红绿格”。
3. “未公开证据”使用中性灰，不能形成对他人工作的视觉判决。
4. 图表必须共享同一颜色语义、字体和矢量交付规范。
5. 结构可以冻结，但 evidence map 仍处于需要逐篇全文核证的动态阶段。

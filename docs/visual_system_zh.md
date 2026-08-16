# Medical World Models 视觉系统（冻结版 v1）

冻结日期：2026-07-12。适用范围：正文图、数据图、表格和后续学生提交的可编辑图源。

## 1. 颜色语义

| 角色 | HEX | 唯一语义 |
|---|---:|---|
| Ink | `#1A2A3A` | 正文、结构线、层级名称 |
| Blue | `#0072B2` | 数量、分布、流程结构 |
| Teal | `#009E73` | 有公开证据 / supported |
| Amber | `#E69F00` | partial、boundary、需要谨慎解释 |
| Vermillion | `#D55E00` | 仅用于明确 warning，不表示“未找到证据” |
| Gray | `#6E7B8B` | unknown、not publicly evidenced、辅助文字 |
| Light gray | `#DDE3E8` | 网格、分隔线、低对比背景 |

铁律：同一颜色在整篇文章中只能表示一个语义。L0--L4 是有序但非累积的类别，不使用五种彩虹色；状态不能只靠颜色表达，必须同时使用 `check / adjust / minus` 等冗余符号。

## 2. 图形规范

1. 数据图必须由 `db/papers.csv` 或明确的派生表生成，禁止在 PDF、Draw.io 或 PPT 中手改数字。
2. 交付物至少包括可编辑源文件、矢量 PDF 和 2x PNG 预览；正文优先使用 PDF 或 TikZ。
3. 图内字号在最终版面不低于 8 pt；面板角标统一为 `(a)`, `(b)`；解释性文字放入 caption。
4. 示意轨迹必须标明 schematic，不能出现无数据来源的风险百分比、效果值或患者结局。
5. 图标只传达模态或临床动作，不传达未经证实的 paper 性能；外部 logo 或 paper visual 必须记录来源和许可。

当前实现：Fig. 3 由 `tools/make_landscape_figure.py` 从 CSV 生成；Fig. 4 和 Fig. 5 为可编辑 TikZ。Fig. 4 只说明 L1/L2 action boundary；Fig. 5 只说明两个正交坐标，不再显示无可复现聚合规则的红绿矩阵。

## 3. 表格规范

1. 仅使用 `booktabs` 横线，不使用竖线。
2. 计数表同时报告 `n`、百分比和同尺度 share bar；分母必须写在 caption。
3. “not publicly evidenced” 用中性灰 minus 标记，不铺红底；它不等于 absent 或 failed。
4. L0--L4 必须按定义顺序排列，不能按频次重排。
5. 表内数字需由脚本或独立重算核对；caption 只写读表规则和主要发现，不重复整段正文。

## 4. 验收

- `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` 成功。
- 0 undefined citation/reference，0 overfull box。
- 100% 与数据库重算一致；未知值不被改写成否定结论。
- 桌面与 150--200 dpi 页面渲染中无文字重叠、裁切或小于可读阈值的标签。

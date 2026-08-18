---
name: write-chinese-math-materials
description: Create, reconstruct, translate, consolidate, expand, review, or repair rigorous Chinese LaTeX mathematical textbooks and lecture notes. Use when Codex must turn one or more books, papers, PDFs, scans, TeX sources, outlines, or existing drafts into a self-contained Chinese mathematics learning resource; write such a resource from scratch; audit a machine-generated mathematical draft; add prerequisites, motivations, proofs, exercises, solutions, links, terminology control, or perform LaTeX/PDF final QA.
---

# 编写中文 LaTeX 数学教材

把成品定位为可以连续学习的教材，而不是来源摘要、翻译草稿或复习提纲。兼顾数学责任、教学可读性、来源忠实度和工程可验证性。

## 开始前

1. 完整读取用户给出的写作规范、已有模板和项目约定；用户规范优先于本技能的默认值。
2. 对复杂或长周期项目建立持久计划、发现记录和进度日志。先盘点实际编译输入、来源文件、已有改动与输出路径，不覆盖用户未授权修改的原稿。
3. 依任务读取下列参考文件；被选中的文件必须读完：
   - 所有教材任务：读 [教学写作规范](references/pedagogy-and-style.md) 与 [数学严谨性和证明责任](references/mathematical-rigor.md)。
   - 根据资料重制、翻译或整合：再读 [来源重制与覆盖](references/source-reconstruction.md)。
   - 含习题、验收或题解：再读 [习题、题解与超链接](references/exercises-and-links.md)。
   - 创建或重构 LaTeX 工程：再读 [LaTeX 工程规范](references/latex-engineering.md)。
   - 审校、修复或交付：再读 [全文审计与 PDF 终验](references/audit-and-qa.md)。
4. 可复制 [中文数学教材模板](assets/book-template/main.tex) 所在目录作为起点；若项目已有体例，优先沿用并只补缺失能力。

## 确立写作合同

在动笔前明确并记录：

- 目标读者已经掌握什么，哪些前置必须补入，哪些只需提供调用接口；
- 成品是辅助阅读、可替代单一来源的重制版，还是整合多源的唯一阅读载体；
- 哪些结果必须完整证明，哪些给模型证明，哪些只能列为带星号的深层输入；
- 内容覆盖边界、预期篇幅、模块结构、交付文件和构建工具；
- 来源的正式书目信息、主要来源与补充来源的身份，以及每个本地代号的唯一映射。

不要用含混的“完整”“自洽”代替边界说明。“分层自洽”应保证对象、精确陈述、调用接口和证明地图自洽，但允许诚实调用已标识的专著级输入。

## 建立工程与覆盖矩阵

1. 创建模块化主文件、统一样式、术语表、记号表、标签命名空间和章节骨架。
2. 建立来源覆盖矩阵，逐项追踪主要概念、命名定理、关键证明机制、正文依赖的例子与习题；不强求逐页或逐题映射。
3. 建立依赖图。首次使用前定义概念；若提前出现只是研究地图预览，明确标为预览并链接到前置接口或正式展开处。
4. 将必备但放正文过长的最低前置放入第零章；把第一遍不需阅读的偏门或技术材料放入附录。正文在首次调用处链接过去。
5. 为长项目按章或按模块分批编写、构建和验收；不要等全书完成后才发现共同记号或证明责任错误。

## 编写与修订

1. 按“动机—定义—例子—定理—证明—结构注记—练习”的学习顺序组织内容。
2. 把正文中首次引入的术语、构造和记号也视为定义。除真正显然者外，说明为什么这样定义、怎样理解或后文如何使用。
3. 对非平凡证明使用统一的粗阶段标题和编号步骤；逐步补足量词、隐含条件、关键计算或推理、记号与边界情形等关键理由。
4. 在非平凡定理后解释结论说了什么、证明靠什么、边界在哪里；不要用“显然”“标准”“容易验证”掩盖实质工作。
5. 对复杂但本书不展开的结果使用带星号深层输入：精确写出假设、结论、关键引理、证明架构、调用位置和未证明边界。
6. 精选习题。正文依赖的习题结论提升为正文；保留题应承担概念检验、关键方法或跨章综合功能。
7. 复用已有文字时采用“大片复制、统一改造、定点补写”，但把机器稿和旧稿只当作待核查来源；逐项复核定义、假设、公式、证明和解释。

## 质量门

交付前必须同时通过四层检查：

1. **数学层：** 人工连续阅读实际编译输入，核查事实、概念、定义、定理、证明、例子、解释、题解和来源归属。
2. **依赖层：** 核查首次定义、前置路由、阅读层级、内部链接、全书约定、统一量词和术语。
3. **工程层：** 构建至引用稳定，检查未定义引用、重复标签、缺失文献、书签、缺字、盒溢出、占位符和弃用术语。可运行：

   `python scripts/audit_latex_project.py path/to/main.tex --terms path/to/terms.json --log path/to/main.log`

4. **视觉层：** 全页渲染 PDF；用接触表覆盖全书，并以原尺寸检查章首页、长证明、复杂公式、表格、题目、题解和本轮高风险修改页。

静态脚本只作辅助，不能替代逐章数学阅读。外部审计报告只作为待验证主张；逐条给出采纳、部分采纳或不采纳的数学理由。

## 交付

报告：

- 主源码、模块目录、正式 PDF 和质量检查结果；
- 来源覆盖与未展开深层输入；
- 重要修订及其数学理由；
- 仍存在的诚实边界。

只可声称“在本轮明确范围内未再发现错误”，不得给出数学著作绝对零错误的不可验证保证。

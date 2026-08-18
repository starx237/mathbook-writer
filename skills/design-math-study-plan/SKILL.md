---
name: design-math-study-plan
description: Design personalized mathematics study plans, reading orders, source guides, weekly curricula, research-preparation roadmaps, and integrated end-to-end self-study coursebooks. Use when a user provides mathematical books, papers, PDFs, TeX sources, a syllabus, a research direction, a time budget, or prior knowledge and asks what to study, in which order, how deeply, how to verify progress, or asks for one self-contained master lecture text that replaces a scattered source list. For Chinese LaTeX coursebook writing, this skill requires write-chinese-math-materials.
---

# 定制数学学习计划与端到端主讲义

把资料清单转化为一条适合具体学习者、具有依赖顺序和验收标准的学习路径。若用户要求唯一阅读载体，则进一步把计划内化为完整主讲义。

## 开始前

1. 完整读取用户提供的背景、目标、时间、资料说明和既有计划。不要默认学习者需要从头重学已经修过的前置课程。
2. 对复杂任务建立持久计划、发现记录和进度日志；盘点本地 PDF、TeX、已有重制版、辅助材料和输出文件。
3. 依任务完整读取：
   - 所有任务：[学习者画像与资料审计](references/learner-and-source-audit.md)。
   - 学习计划或阅读指南：[周计划设计](references/study-plan-design.md)。
   - 多资料排序、删减或覆盖：[覆盖、优先级与习题取舍](references/coverage-and-prioritization.md)。
   - 唯一阅读载体或完整主讲义：[端到端自学主讲义](references/end-to-end-coursebook.md)。
   - 修订计划、处理卡点或终验：[执行、反馈与验收](references/validation-and-adaptation.md)。
4. 可复制 [学习计划模板](assets/study-plan-template.md)、[资料覆盖矩阵模板](assets/coverage-matrix-template.md) 和 [主讲义蓝图模板](assets/coursebook-blueprint-template.md)。

## 第一阶段：建立证据化画像

记录：

- 已修课程、实际熟练度和阅读经验；
- 当前研究兴趣与导师期待；
- 每周可用时间、总时长和中断风险；
- 希望达到的层级：了解、能做题、能复现证明、能读论文或能启动研究；
- 主线、次线、长期入口和可放弃内容；
- 每份资料的正式身份、难度、依赖、重叠和版本状态。

若需要推断研究方向，依据导师主页、近期论文、推荐资料的共同方法与对象建立“证据—推断—置信度—备选解释”链，不把推断写成确定事实。

## 第二阶段：画依赖图并分配优先级

1. 把知识点而不是书名作为依赖节点。
2. 标出哪些基础已掌握、哪些只需即时补读、哪些需要系统学习。
3. 把资料分为：
   - 核心主线；
   - 支撑主线的参考资料；
   - 可选专题；
   - 长期入口。
4. 对已有重制版或辅助材料更新计划中的阅读入口；不要继续安排模糊、低质量或已被替代的旧版本。
5. 对重叠来源选一个主叙述，其余只贡献更好的动机、例子、证明或练习。

## 第三阶段：制定可执行计划

每周至少写明：

- 学习目标；
- 前置回顾；
- 精读、概览和跳过范围；
- 时间分配；
- 应掌握的定义、定理与证明方法；
- 精选练习或复现任务；
- 可提交的周产物；
- 阶段验收和通过标准；
- 卡住时的补救入口。

保留缓冲和复盘，但不要用“复习”填满计划。时间不足时先删低优先级旁支，再降低深层输入的复现要求；不要破坏主线依赖。

## 第四阶段：按需编写端到端主讲义

当用户要求主讲义、唯一阅读载体或不再回查原资料时：

1. **必须调用 `$write-chinese-math-materials`。** 完整读取其 `SKILL.md`，并按任务路由读取它要求的参考文件；本技能只决定课程结构，不覆盖其写作与审计规范。
2. 把周计划内化为章节。每章对应一周或一个明确阶段，并在章内呈现目标、阅读层级、正文、练习、验收和链接。
3. 设置第零章和即时前置路由；正文首次出现时回链。
4. 建立来源覆盖矩阵、定义/定理依赖图和证明责任表。
5. 主线资料的主要对象、命名结果和关键证明必须有去向；进阶资料可以只建立精确入口。
6. 将习题与验收直接放入主讲义，并提供题目—解答—正文三向链接。
7. 分章编写、构建、人工阅读和验收；长任务允许分批交付，但最终必须形成连续成品。

## 第五阶段：验证并适配

检查计划是否满足：

- 顺序不出现先用后定义；
- 工作量与时间预算相容；
- 核心内容不会因次线挤占而延期；
- 每周都有可观察产物和通过标准；
- 用户反馈“读不懂”时能定位到前置、叙述、证明或阅读层级问题；
- 主讲义完成后无需再阅读旧的周计划才能知道本周任务。

反馈优先于纸面估算。若学习者频繁需要外部逐句问答，诊断教材卡点并回修正文，不把责任简单归为“基础不够”。

## 交付

对普通计划交付：

- 研究方向或目标分析；
- 资料地图与依赖图；
- 周计划；
- 逐资料阅读指南；
- 习题与验收策略；
- 调整规则。

对端到端主讲义还交付：

- 模块化源码；
- 唯一连续 PDF；
- 覆盖矩阵；
- 题解与验收答案；
- 构建、数学审计和视觉 QA 结果；
- 深层输入与长期入口边界。

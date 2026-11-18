# 中文数学教材的 LaTeX 工程规范

## 目录

1. 工程结构
2. 样式与宏
3. 标签和链接
4. 构建流程
5. 日志检查
6. PDF 视觉检查

## 1. 工程结构

长教材使用模块化工程；下列目录是可调整的示例，不要求所有项目采用相同结构：

```text
book/
├── main.tex
├── style.tex
├── frontmatter.tex
├── chapters/
│   ├── 00-prerequisites.tex
│   ├── 01-....tex
│   └── ...
├── appendices/
│   ├── solutions.tex
│   └── notation.tex
└── references.bib
```

主文件只负责文档类、样式、前置内容和输入顺序。共同宏集中定义，不在章节文件中重复。

## 2. 样式与宏

按实际使用统一，不要求每个工程都定义未使用的环境：

- theorem、lemma、proposition、corollary、definition、example、note；
- 按结果类型设置带星号环境；新模板用 `theoremstar`，旧 `deepinput` 可兼容但不显示旧责任名称；
- 按需设置证明路线环境 `proofidea`，不代替完整证明；
- 粗阶段标题 `\proofphase`；
- 证明步骤解释 `\stepdetail`；
- 习题和题解跳转宏；
- 章首阅读层级。

不要用手工粗体、字号和间距复制同一种语义。把体例写成宏，便于全书一致修改。

中文建议使用 `ctexbook` 与 XeLaTeX。字体策略应适配用户环境；若指定字体不可用，选择可移植字体集并在构建说明中报告。

## 3. 标签和链接

建立命名空间并保持唯一：

```text
part:...
ch:...
sec:chXX-...
def:chXX-...
thm:chXX-...
lem:chXX-...
eq:chXX-...
ex:chXX-YY
sol:chXX-YY
check:chXX
checksol:chXX
```

移动内容时同步修改所有引用。禁止通过复制章节保留重复标签。

使用 `hyperref`；可选 `cleveref` 统一名称。检查 PDF 书签中的数学公式和中文字符警告，必要时使用 `\texorpdfstring`。

## 4. 构建流程

1. 探测可用的 XeLaTeX、latexmk、BibTeX 或 Biber。
2. 按项目工具链构建。
3. 重复构建直至交叉引用稳定；含书目时执行完整书目链。
4. 保存最终日志和发布 PDF。
5. 确认发布 PDF 与最后一次核验的构建稿一致，可记录 SHA-256。

修改单章后先作快速构建；完成阶段后作全量构建。

## 5. 日志检查

至少检查：

- undefined control sequence；
- undefined references / citations；
- multiply-defined labels；
- missing bibliography；
- rerun warnings；
- bookmark warnings；
- missing characters；
- overfull / underfull boxes；
- package conflicts；
- fatal errors。

同时扫描源码和 PDF 文本：

- `TODO`、`FIXME`、`待补`、`待写`；
- `??`；
- Unicode 替换字符；
- 用户指定的弃用术语；
- 本地资料代号的越界使用；
- 错误控制序列残片。

可使用本技能脚本作第一轮静态检查，但必须人工判断误报。

## 6. PDF 视觉检查

把最终 PDF 全页渲染为同尺寸图片：

1. 检查页数与渲染成功数一致；
2. 生成接触表覆盖全书；
3. 检查异常空白、裁切、重叠、乱码、黑块、孤行和公式越界；
4. 原尺寸检查章首页、目录、长证明、复杂公式、表格、图、习题、题解；
5. 对本轮所有高风险修改页做定点复核；
6. 检查跨页框体、标题孤悬和证明结束位置。

对标题与首个证明动作分居两页、题面被不合理分页打断、证明结束符独占下一页等问题，优先局部分页修复；不通过统一缩小字体或压缩间距掩盖问题。

“日志无警告”不能替代视觉检查；“页面看起来正常”也不能替代文本与数学审校。


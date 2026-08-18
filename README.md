# MathBook Writer Skills

面向中文数学学习与写作的可复用 Codex Skills。项目提供工作流、LaTeX 模板、审计脚本和资料组织
方法，适用于不同数学方向的学习材料与考试备考材料编写。

## Skills

| Skill | 用途 |
| --- | --- |
| `$build-chinese-math-exam-prep` | 根据试卷、扫描件、答案和允许使用的资料构建、校对并发布中文数学考试备考讲义。 |
| `$write-chinese-math-materials` | 重制、整合或从零编写严谨、可独立学习并经过 LaTeX/PDF 终验的中文数学学习材料。 |
| `$design-math-study-plan` | 基于学习者背景、时间与资料设计数学学习路径、阅读顺序、阶段计划和整合学习材料蓝图。 |

当学习计划需要产出连续的中文 LaTeX 学习材料时，`$design-math-study-plan` 会调用
`$write-chinese-math-materials`，以复用其写作、数学审计和排版验收规范。

## Repository layout

~~~text
skills/
  build-chinese-math-exam-prep/
  write-chinese-math-materials/
  design-math-study-plan/
scripts/
  validate_skills.py
~~~

每个技能目录以 `SKILL.md` 为入口；`references/` 提供按需读取的规范，`assets/` 提供可复制
模板，`scripts/` 提供静态、PDF 或构建审计工具。

## Install

将所需技能目录复制到本机 Codex skills 目录。例如，在 Windows PowerShell 中：

~~~powershell
$target = Join-Path $env:USERPROFILE ".codex\skills"
New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -Recurse .\skills\write-chinese-math-materials $target
~~~

在 macOS 或 Linux 中：

~~~bash
mkdir -p ~/.codex/skills
cp -R skills/write-chinese-math-materials ~/.codex/skills/
~~~

随后在 Codex 中以 `$write-chinese-math-materials` 等技能名调用。可按需安装一个、多个或全部
技能。

## Optional local tools

审计脚本优先使用 Python 标准库；涉及 PDF 的检查额外需要：

~~~bash
python -m pip install -r requirements.txt
~~~

要编译附带的中文数学模板，还需要本地 TeX 发行版提供 XeLaTeX 及可用中文字体。

## Validate changes

~~~powershell
python -m pip install PyYAML
python scripts/validate_skills.py
~~~

## Publish to GitHub

本仓库已包含 `.gitignore`、MIT 许可证、README 和 GitHub Actions 验证工作流。确认工作区内容后：

~~~bash
git add .
git commit -m "Prepare public skills repository"
git branch -M main
git remote add origin <YOUR-GITHUB-REPOSITORY-URL>
git push -u origin main
~~~

若已配置名为 `origin` 的远程仓库，请改用正确的远程配置命令，而不是重复添加。

## License

[MIT](LICENSE) © 2026 mathbook-writer contributors.

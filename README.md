# pdf2md

日期: 2025-12-17  
作者: 余炘洋  

## 功能概览
- 图形界面，支持单个/批量选择 PDF。
- 每个文件独立进度条与状态提示。
- 可自定义输出目录，默认与源文件同级。

## 环境要求
- Python >= 3.10
- 依赖见 `requirements.txt`（核心为 `pypdf`）

## 安装与运行
```bash
# 方式一：安装为可编辑模式（推荐，用于 python -m pdf2md）
pip install -e .

# 方式二：仅安装依赖（用 python main.py 运行）
pip install -r requirements.txt

# 便携方式：把依赖装到 vendor/ 目录（可选）
pip install --target vendor -r requirements.txt
```

运行程序：
```bash
# 安装过 -e . 或设置好 PYTHONPATH 时：
python -m pdf2md

# 未安装包也可运行的入口（main.py 会自动添加 src 到 sys.path）
python main.py
```

Windows PowerShell 示例：
```powershell
cd D:\Software\pdf2md
.\.venv\Scripts\Activate.ps1
python -m pip install -e .          # 若想使用 python -m pdf2md
# 或：python -m pip install -r requirements.txt
python -m pdf2md                    # 或 python main.py
```

临时运行且不想安装包，可临时设置 PYTHONPATH（PowerShell 示例）：
```powershell
$env:PYTHONPATH="D:\Software\pdf2md\src"
python -m pdf2md
```

## 项目结构
- `pyproject.toml`：项目元数据与依赖声明
- `src/pdf2md/`：源码（转换逻辑与 GUI）
- `main.py`：运行入口薄封装
- `requirements.txt`：运行时依赖
- `LICENSE`：Apache License Version 2.0 许可证

## 打包发布
> 适用于离线/分发场景  
```bash
# 安装打包依赖（可选：安装到本地或 vendor）
pip install pyinstaller
# 或便携方式
pip install --target vendor pyinstaller

# 生成单文件可执行
pyinstaller --onefile --name pdf2md \
  --add-data "vendor:vendor" \
  main.py
# 产物位于 dist/pdf2md
```
- 如需图标，追加 `--icon path/to/icon.ico`。
- 跨平台需在目标平台重新打包。

## 使用提示
- “选择单个PDF”/“选择多个PDF”添加待转换文件。
- “选择输出目录”设置 Markdown 输出位置。
- 点击“开始转换”后可实时查看进度与完成/失败状态。

## 贡献指南
- Fork 后基于 feature 分支提交。
- 注释/文档请使用中文并标注日期、作者。
- 最少执行语法检查：
  ```bash
  python -m src/pdf2md/*.py main.py
  ```
- 在 PR 中说明变更内容、测试方式与影响范围。

## 行为准则
- 尊重、包容，禁止骚扰、歧视与人身攻击。
- 维护者可对不当行为发出警告、移除内容或限制参与。
- 举报方式：Issue 或邮件联系维护者（作者：余炘洋），请附复现/证据。

## 许可证
基于 Apache License Version 2.0 许可证，详见 `LICENSE`。

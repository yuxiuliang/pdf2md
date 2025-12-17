# pdf2md

## 功能
- 提供可视化界面，支持单个或批量选择 PDF 文件
- 展示每个文件的转换进度与状态
- 自定义输出目录，默认与源文件同级

## 运行步骤
1. 安装依赖（已默认放在 `vendor/` 目录，若缺失可重新安装）  
   ```bash
   PYTHONPATH=.pyhome/local/lib/python3.10/dist-packages python3 -m pip install --target vendor pypdf
   ```
2. 启动程序  
   ```bash
   python3 main.py
   ```

## 使用提示
- “选择单个PDF”/“选择多个PDF”添加待转换文件，可在列表中看到独立进度条
- “选择输出目录”指定 Markdown 文件存放位置
- 点击“开始转换”后，列表中会显示进度和完成/失败状态

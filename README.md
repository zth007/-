
# TAUREN-SCRIPT

今日头条自动化脚本

## 项目简介

本项目是一个基于 Python 的今日头条自动化脚本，支持批量点赞、评论等自动化操作，提供 Web 控制面板进行可视化管理。

## 功能特性

- **内容点赞**：自动点赞推荐内容和关注用户的视频/文章
- **智能评论**：根据关键词自动生成评论内容
- **关注用户处理**：批量处理关注用户的内容
- **循环执行**：支持多轮循环操作
- **Web 控制面板**：可视化监控和控制脚本运行
- **配置管理**：灵活的参数配置
- **数据统计**：实时显示运行统计

## 技术栈

- **Python** 3.x
- **Helium** - 网页自动化库
- **Selenium** - 浏览器自动化
- **Flask** - Web 框架
- **Edge浏览器** - 默认浏览器

## 项目结构

```
tauren-script/
├── main.py                    # 主程序入口
├── web_server.py             # Web 服务器启动文件
├── requirements.txt          # 依赖包列表
│
├── toutiao/              # 今日头条模块
│   └── toutiao.py        # 今日头条核心逻辑
│
├── operation/            # 操作模块
│   └── operation_toutiao.py  # 点赞/评论/关注操作
│
├── utils/              # 工具模块
│   ├── config.py         # 配置管理
│   ├── logger.py         # 日志管理
│   └── account_manager.py  # 账号管理
│
├── load/               # 加载模块
│   └── load.py         # 文件加载
│
├── web/                # Web 应用
│   ├── app.py          # Flask 后端
│   ├── templates/
│   │   └── dashboard.html  # 控制面板页面
│   └── static/
│       ├── css/style.css     # 样式文件
│       └── js/main.js       # 前端脚本
│
├── config/             # 配置文件
│   └── config.yaml       # 主配置文件
│
├── data/               # 数据目录
│   └── accounts.json     # 账号数据
│
├── logs/               # 日志目录
│
├── match_comment.text      # 评论匹配规则
├── toutiao_cookies.pkl    # Cookie 缓存
└── README.md
```

## 安装说明

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 浏览器要求

- 安装 Microsoft Edge 浏览器
- 脚本会自动管理 EdgeDriver

## 使用说明

### 方式一：Web 控制面板（推荐）

1. 启动 Web 服务器：

```bash
python web_server.py
```

2. 打开浏览器访问：http://localhost:5000

3. 在控制面板中配置参数并启动脚本

### 方式二：命令行运行

```bash
python main.py
```

## 配置说明

配置文件位于 `config/config.yaml`：

| 配置项 | 说明 | 默认值
---------|------|-------
operation.min_delay | 最小延迟(秒) | 2
operation.max_delay | 最大延迟(秒) | 4
operation.max_retries | 最大重试次数 | 2
operation.max_links_per_cycle | 每次处理推荐内容数 | 10
operation.cycle.max_cycles | 最大循环次数 | 5
operation.cycle.cycle_interval | 循环间隔(秒) | 3600
operation.cycle.users_per_cycle | 每次处理用户数 | 10
operation.cycle.videos_per_user | 每个用户处理视频数 | 2
operation.browser.headless | 无头模式 | false
operation.browser.maximize | 最大化窗口 | true

## 评论配置

`match_comment.text` 文件格式：

```
关键词&gt;评论内容
```

示例：
```
精彩&gt;说得太好了！
学习&gt;学习了，感谢分享！
支持&gt;支持一下！
```

## 注意事项

1. 首次运行需要扫码登录今日头条
2. 登录后 Cookie 会自动保存
3. 请合理设置延迟，避免频繁操作
4. 建议使用 Web 控制面板进行管理

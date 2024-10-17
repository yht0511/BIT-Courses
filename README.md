# 百丽宫的高效选课

## 项目简介

​ 抢不着公选课？爆率还不如米哈游？ 是时候升级你的工具了！

​ 每秒钟 43.8 次(_只抢一节，使用网线连接实测_)，让你的同学知道什么是**_纳米科技!_**

​ 支持同时抢多门课程；支持保底模式，最优化你的课程！

## 使用指南

1. 按 win+r 输入 cmd,按 enter
2. 在 cmd 输入以下指令

```
// 克隆本项目仓库
git clone https://gitlab.teclab.org.cn/Teclab/Xuanke.git
// 进入仓库
cd Xuanke
// 安装依赖
pip install -r requirements.txt
```

3. 编辑 settings.py,填写你的学号和密码

   > 可以仅填写原密码，程序会自动执行 key.js 获取加密后的密码用于登录选课平台，但前提是你安装好了 node.js
   >
   > 如果没有，请去选课平台抓包，获取 login 请求的 pwd，填入 settings.py

4. 编辑 tasks.json,目前支持两种模式:

- 选课模式

​ 不断尝试抢这门课。

- 替换模式

  不断检测目标课程是否有空余，一旦有，就退掉原本选的冲突的课程，确保有课上

格式如下:

```
[
    {
        "name": "科幻文学",
        "type": "select"
    }
]
解释: 尝试选择科幻文学(这课真火啊)

[
    {
        "name": "xxx(某理工的大水课)",
        "type": "replace",
        "replace": {
            "name": "(某理工的小水课)"
        },
    }
]
解释: 争取选个更水的课
```

5. 选课,启动!

```
python main.py
```

## 可能的问题

1. 目前仅测试过 2024 级抢课（模式：先抽签再抢课），对其他年级抢课的方式并不清楚，程序可能并不兼容。

## 免责声明

我只是个臭写代码的,来百丽宫要饭的

事实上我选课没用上这程序

本程序仅供学习交流,如果你真要投入实践,一切后果请使用者自负. （一脸严肃 (´・ω・`) 

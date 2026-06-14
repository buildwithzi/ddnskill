# 多动脑 Duodongnao

### 把内容创作者的 Agent 变成 ADHD

一个念头，疯长成一个内容宇宙。

多动脑让 Agent 模拟 ADHD 式的高跳跃思维：念头递归分叉，远距离概念突然碰撞；方向得到验证后，发散不会停止，而是转化成沿着主线不断向下深挖的超专注。

默认唤醒方式：

```text
/ddnskill
```

如果运行环境使用 Codex `$skill` 语法，也可以使用：

```text
$ddnskill
```

它不是“批量生成爆款标题”的工具，而是一套持续运行的认知系统：

**递归分叉 → 远距碰撞 → 证据引力 → 超专注深挖 → 内容编译。**

## 为什么做这个 Skill

多数内容工具的问题不是点子太少，而是：

- 只会生成一批平行标题；
- 每次都重新开始，没有内容记忆；
- 把反常识、清单、教程当成思想本身；
- 一个方向刚跑出数据，创作者又被新鲜题材带走；
- 所谓“专注”只是停止发散，最后变成机械复制。

多动脑的核心判断是：

> 发散不应该在验证后关闭。验证只应该让发散从“向四面八方跳”变成“围绕高引力方向向下钻”。

## 核心能力

### 1. Recursive Growth

禁止默认从主题直接跳到标题。一个种子必须先长出第一圈分支，再选择高张力节点继续递归，最终形成可发布叶节点。

### 2. Remote Collision

主动把两个表面无关的领域连接起来，但要求存在真实共享机制和新推论，不接受空比喻。

### 3. Evidence Gravity

真实受众数据改变不同节点获得的搜索预算。单条爆款只有临时引力，重复高意图信号才会形成长期内容支柱。

### 4. Fractal Hyperfocus

方向验证后进入 `GRAVITY_WELL`：70% 预算用于直接后代，20% 用于边界连接，10% 保留野生跳跃。

### 5. Editorial Compiler

反常识、避坑、教程、清单、争议等只是最后的包装层，而不是思想生成器。

## 安装

把整个文件夹复制到以下任一位置：

```text
Codex 所有项目：~/.codex/skills/ddnskill/
Codex 自定义目录：$CODEX_HOME/skills/ddnskill/
Agents/Claude Code 工作台：.agents/skills/ddnskill/
```

然后在 Codex 中调用：

```text
/ddnskill
```

## 第一次使用

```text
/ddnskill

我想做一个关于国际组织求职、精英系统和 AI 工具的中文内容账号。
不要直接给我标题。
先建立临时 CREATOR_PROFILE 和 ASSOCIATION_BANK，
然后从一个种子开始做至少两层递归，加入两个真正的远距碰撞，
最后只推荐最值得测试的两个叶节点。
```

## 让一个念头疯狂生长

```text
/ddnskill

种子是：很多求职经验帖只是把幸存者偏差包装成方法论。
用 ADHD 强度模式展开：jump_distance=4，branch_factor=6，recursion_depth=4。
先给我内容图，不要急着编译成标题。
```

## 方向验证后进入超专注

```text
/ddnskill

“精英系统的隐藏规则”这个方向已经连续两次出现高收藏、求后续和关注转化。
把它设为 GRAVITY_WELL。
按照 70/20/10 建立一个内容宇宙，向下递归 5 层，
然后给我下一轮 7 条内容冲刺。
每条必须来自不同子分支，并说明新增认知是什么。
```

## 复盘数据

将帖子数据填入 `POST_LOG.csv`：

```text
/ddnskill

读取 POST_LOG.csv。
先找异常，不要只看最高播放。
更新相关节点的证据引力，并把评论区的新念头分为 CHILD、EDGE 或 ESCAPE。
```

也可以运行：

```bash
python scripts/analyze_posts.py POST_LOG.csv
```

## 查看内容图结构

```bash
python scripts/graph_stats.py CONTENT_GRAPH.md
```

脚本会输出节点数量、最大深度、状态分布、证据分布和孤立节点提示。

## 文件结构

```text
ddnskill/
├── SKILL.md
├── README.md
├── LICENSE
├── assets/
│   ├── CREATOR_PROFILE.template.md
│   ├── ASSOCIATION_BANK.template.md
│   ├── CONTENT_STATE.template.md
│   ├── CONTENT_GRAPH.template.md
│   └── POST_LOG.template.csv
├── references/
│   ├── recursive-growth.md
│   ├── remote-collision.md
│   ├── evidence-gravity.md
│   ├── editorial-compiler.md
│   └── review-diagnostics.md
├── scripts/
│   ├── analyze_posts.py
│   └── graph_stats.py
└── examples/
    └── mini-demo.md
```

## 四种运行模式

- `OPEN_FIELD`：大范围探索；
- `PROBE`：把叶节点做成低成本测试；
- `GRAVITY_WELL`：围绕已验证方向进行分形深挖；
- `REASSESS`：方向衰退后重新分配搜索预算。

发散引擎在四种模式中都持续开启。

## 真实限制

这个 Skill 不会自动读取平台后台数据。除非你另外连接分析工具，否则仍需手动填写 `POST_LOG.csv`。

它也不会替你证明一个类比是真的。远距碰撞产生的是候选判断，涉及事实时仍需要可靠材料验证。

## License

MIT

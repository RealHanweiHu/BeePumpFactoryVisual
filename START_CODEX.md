# 在 Codex 中启动

在 Codex 选择并打开解压后的 `BeePump_Factory_Visual_Codex` 文件夹。第一条消息复制以下内容即可：

```text
这是 BeePump 工厂目视化V2设计工程项目，不是网站重建，也不是PDOS/GoodJob。
先读取 AGENTS.md、README.md、docs/PROJECT_BRIEF.md、docs/TASTE_ADAPTATION.md、
docs/CAD_WORKFLOW.md 和 data/tasks.json，使用 $beepump-factory-visual。

请实际执行，不要只写建议：
1. 运行项目validate与测试，保留inputs原件和校验和。
2. 完成P01：检查本机已有CAD/ODA转换器，安全地转换DWG副本，盘点Layout/Model/图层/XREF/字体。
   不自动安装系统软件，不上传在线转换网站。环境缺失时记阻塞，不伪造各层图。
3. 完成P02的可执行部分：通过图纸标题与两处不同方向的已知尺寸核对楼层和比例；需人工确认之处留下证据。
4. CAD受阻不应阻塞P03：逐项审查V1的36款模板并记录Preserve/Refine/Retire。
   明确读取Taste官方redesign-existing-projects技能，但只采用TASTE_ADAPTATION允许的规则。
5. 完成P04：先出WF-02、WF-04、WH-01、PM-01、PM-02、FL-01六款8F样板模板，
   使用真实既有文案或标明待填写；输出V1/V2对照，渲染检查，不改原SVG。
6. 只有图纸识别和比例校核满足条件后，才生成P05的8F点位提案；全部保持proposed。

保留#FF6600、#000000及原质量状态语义；品牌橙不上地面；楼层号、区域号、参观号分开。
不得编造点位、设备数、材料、认证、业绩或审批结果。不得把网页动画、非对称营销排版套用到生产看板。
每一批结束给出已改文件、可打开的预览、已跑测试、图纸读取层级、未解决问题和下一批任务。
未经我确认不推送远程仓库，不对外发图，不进入生产放行。
```

## 第一批结束应看到什么

`reports/cad_inventory.json`（或具体阻塞记录）；`reports/template_audit.json`的36条逐项审查；`design/v2/`的首批6款；可对照查看的预览；运行日志。没有真实图纸转换成功时，不要求凭空补齐点位。

审批保持分离：设计方向确认 → 图纸/位置复核 → 安装与专项批准 → 制作放行。这里只准备工作目录；首次本地任务需在你的Codex中启动。

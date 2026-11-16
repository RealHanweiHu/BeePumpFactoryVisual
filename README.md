# BeePump 工厂目视化｜先完成 8 楼

## GitHub 仓库

私有仓库跟踪项目文档、脚本、测试、方案台账和可独立查看的设计稿。可直接查看 [V3.4 围板 SVG](design/v2/8f_partition_v3.4)、[V3.3 功能牌面 SVG](design/v2/point_effects_2026-10-26/templates)、[V2.8 样式方案](design/v2/options_v2.8/styles)及 [21 项方案清单](outputs/planning/8F_方案收口清单.csv)。

原始资料、CAD 转换文件、含底图的交付件、归档包和高分辨率概念 PNG 保存在原工作目录。克隆后如需运行完整校验或生成预览，请从授权的本地副本按原相对路径补齐 `inputs/`。离线评审、CAD 和历史交付入口依赖原工作目录中的对应文件。

## 本地交付入口

**主入口：[8 楼当前方案](交付_8楼/打开这里.html)**

[V3.4 围板设计补充](交付_8楼/围板设计_V3.4/打开这里.html)——访客侧、装配工位侧、仓口侧及维修侧，附立面前后对照、可编辑SVG和踏勘表。

[V3.2 点位补充与踏勘](交付_8楼/点位补充_V3.2/打开这里.html)——对照新参考PPT，补齐8F产线、品质、仓储、维修及电子区核查，附4页底图标注、可填写踏勘清单及A–F索引。真实安装点和工程量待现场核定。

[新增：8楼逐项效果与功能优化](交付_8楼/逐点效果与功能优化_2026-10-26/打开这里.html)——维修台、流水线头、装配区、测试区、老化充电管理及物料超市优先，覆盖21项功能需求与1个补充条件场景。附小红书3篇案例的采用记录、六款SVG前后对照及逐图来源。空间设备为示意，真实点位/尺寸/数量与制作安装待核。

[保留：三张早期概念效果](交付_8楼/效果预览_2026-10-26/打开效果预览.html) · [逐项视觉优化说明](docs/8F_逐项视觉优化说明.md)

本轮整理日期：2026-10-26。当前优先完成8F方案，1F及其余楼层保留已有资料，暂不扩展新设计。

| 工作内容 | 采用资料 |
|---|---|
| 物流、人行、定置及地面配色 | [V3.1 当前总图与图层](交付_8楼/地面物流规划_V3.1/打开地面配色图.html) |
| 21项牌面与位置关系选择 | [V2.8 多方案选择](交付_8楼/多方案选择_V2.8/START_HERE.html) |
| 小客梯位置和到层画面 | [V2.7 局部修订](交付_8楼/客梯入口修订_V2.7/START_HERE.html)；员工/物流分工以V3.0/V3.1为准 |
| 材料、报价边界、打样与验收 | [V2.4 手册](交付_8楼/START_HERE.html)与[现场表](交付_8楼/output/pdf/BeePump_8F_SettingOut_Acceptance_V2.4.pdf) |
| 逐项推进与现场收口 | [推进说明](docs/8楼方案推进清单.md) · [21项CSV](outputs/planning/8F_方案收口清单.csv) · [结构化台账](data/8F_current_scheme.json) |

建议先审WF-02、WF-04、WH-01、PM-01、PM-02、FL-01六款核心模板，再补齐作业、品质与条件项。此建议不是用户选型结果；本汇总未导入已核实的选择文件。已有V2.8浏览器选择请在原页导出JSON，本轮没有读取或重置本机选择。

已有用户确认的规划关系：人工周转车、未来考虑电动搬运车；来料交接→装配→适用测试/老化→包装→成品交接。原料仓旁中间货梯收料和员工到层，小客梯供访客，左上梯成品下楼，左下/右下暂未规划使用。员工后续走段、C1/C2/C3接口及现场条件仍待核。

## 文件整理

两层散装目录中的重复DXF改为指向项目根目录outputs/drawings/的相对链接；删除缓存和一份与V3.1脚本完全相同、无引用的V3.2命名脚本。减少重复普通文件约122.9MB。**单独携带V2.4资料时使用各层原有Source ZIP，ZIP仍含完整DXF**；复制散装目录需保留项目整体或将链接另存为普通文件。

[清理报告](reports/cleanup_2026-10-26/整理报告.md) · [逐项清理记录](reports/cleanup_2026-10-26/清理记录.json)。原始inputs、独有历史稿、现有ZIP、可编辑源稿及核验/渲染证据保留。旧manifest保留原值，新修改另有审计记录。

2026-11-15 清理了两份重复 DXF、根目录 V2.2 旧入口和已由 V2.9.1 接替的 V2.9 散装评审文件。V2.9 目录保留后续版本引用的来源台账和总图证据。完整旧稿可从 [V2.9 评审包](交付_8楼/BeePump_8F_地面物流规划_V2.9_评审包.zip) 解压。各文件的恢复位置和 SHA-256 见[本次清理清单](reports/cleanup_2026-11-15.json)。

根目录复查移除了 V2.1/V2.2 的重复 ZIP、V2.1 旧入口、V2.5 图纸总入口、`archives/` 的重复快照，以及 `outputs/` 中无使用引用的重复产物。两楼图纸标注可直接从各楼交付入口打开。仍供本地评审下载的 V2.3 和合并版 V2.4 源包留在根目录。原交付包位置及逐项校验见[根目录复查清单](reports/root_cleanup_2026-11-15.json)。

## 保留目录

- 交付_8楼/：8F当前入口、牌面/图纸/现场表及历史版本。
- 交付_1楼/：[1F已有成果](交付_1楼/打开这里.html)，本轮不展开新设计。
- design/v2/：设计源稿与版本元数据。
- inputs/：封存CAD、V1和参考资料；不得覆盖。
- outputs/drawings/：共享CAD转换副本和读取证据；outputs/planning/为方案/核量表。
- output/pdf/、source_archives/、根目录仍在用的HTML/ZIP：评审交付与原始资料包。
- reports/：审查、渲染、校验与整理审计。旧工作进度只代表当时状态。

[两楼历史目录](FLOOR_DELIVERIES.html) · [旧样式尺寸总入口](逐项样式尺寸_参观预览_打开这里.html) · [前次整理记录](reports/cleanup_2026-10-16/整理报告.md)。独有历史稿保留；当前目录仍缺部分V2.5/V2.6生成链，不能宣称全部历史成果可从本目录重建。

## 编辑与核验

遵循[AGENTS.md](AGENTS.md)、[项目任务书](docs/PROJECT_BRIEF.md)、[CAD工作流](docs/CAD_WORKFLOW.md)与项目技能。当前方案入口及汇总表可由以下脚本从既有资料重建，不会修改原稿、用户选择或真实点位。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_8f_function_templates.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/ingest_8f_point_images.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_8f_point_gallery.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_8f_point_notes.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_8f_current_scheme.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/project.py validate
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/project.py build-preview
```

底图八层/三层身份冲突、物理单位、现场点位、尺寸/高度/数量和制作安装批准仍待核，P02/P05阻塞保留。21条功能需求不是21个安装点。data/points.json为空代表尚未勘测，不代表零需求。

# 首批执行清单 / V2.1-DRAFT / 2026-10-05

实际工作目录：`/Users/huhanwei/Documents/Codex/2026-10-04/task/BeePumpFactoryVisual`。独立桌面交付目标：`/Users/huhanwei/Desktop/BeePumpFactoryVisual`。

| 工作 | 当前结果 | 可查看证据 |
|---|---|---|
| Starter与原图核验 | 完成；原DWG在Starter内，48原文件哈希保持一致 | data/sources.json、reports/mac_final_validation.json |
| 原生DWG读取 | DXF成功；原生Plot失败，缺字待解决 | outputs/drawings/factory_converted.dxf、reports/mac_native_cad_export.txt |
| 分层来源盘点 | 9层业务基线与图纸文字候选分列；6F/7F用途未定 | outputs/planning/floor_coverage.json |
| 8F图纸校核 | 标题与单位冲突阻塞；两向尺寸完成数值一致性核对 | outputs/drawings/8F_candidate_calibration.json、docs/DECISIONS.md |
| V1审计 | 36款逐项文本与渲染审查，6款Refine、30款Preserve | reports/template_audit.csv、reports/source_render/svg |
| V2核心模板 | 六款可编辑SVG、同名metadata、原文和来源哈希保留 | design/v2、reports/v2_render |
| Taste适配 | 应用现有本地技能与Starter内官方redesign指导，限定审查/层级/对齐/阅读性 | docs/TASTE_ADAPTATION.md、docs/PHYSICAL_VISUAL_SYSTEM.md |
| 8F试点 | 已制作工作闭环、20条待定位需求；实际点位仍为空 | outputs/planning/8F待定位需求台账.csv、data/points.json |
| 材料与预算 | 36模板材料候选与空值输入、件/面分离；没有现场量或报价 | outputs/quantities/预算与数量输入.csv |
| 分期与验收 | 保留12周建议框架、按确认条件推进；未填写开工/完成日期 | 评审PDF p.16-17 |
| 本地查看 | 六款前后对照、放大、预算情景、完整模板浏览器 | START_HERE.html、preview/single_file_review.html |
| 数字验证 | 17测试通过、2可选ezdxf测试跳过；六款无文字越界、18页无碰撞；桌面和390px页面无横向溢出 | reports/mac_final_tests.txt、reports/v2_render_qa.json |
| PDF像素检查 | 18页已渲染并查看；六款中文正常，来源/待核说明可见 | reports/final_pdf_render_cg |
| 制作与施工放行 | 未获内容/位置/安装批准；不得视作施工图 | 空值审批字段、docs/DECISIONS.md |

下一步由业主/工程选定有效8F图框和物理单位，补齐可校核CAD字体或原比例矢量PDF；由业主确认正式Logo和六款方向。确认后才能制作真实坐标点位、统计安装量、试样与分层推广。

## 两层实施交接 / V2.4 / 2026-10-07

本轮按用户要求优先完成1F主入口/金工/出货与8F锂电充气泵装配设计。实际工作目录不变；桌面独立项目保留历次交付。

| 工作 | 当前交接内容 | 证据 |
|---|---|---|
| 1F/8F原图核查 | 1F三候选保留，右组优先讨论；8F八层/三层冲突与局部裁切明示；没有把源仓储数字当容量 | outputs/implementation_v2.4/cad、reports/implementation_cad_review.md |
| 安装需求 | 1F 19条、8F 21条功能需求；安装面、读者、动作、更新、责任、物流/品质接口与待核条件齐全 | 两层CSV、specs/floor_work_packages.json |
| 可编辑版面 | 27份V2.4新稿，38份选用版面覆盖36模板代码；保留源文字/哈希/名义尺寸 | 两个manifest、artboard_catalog.json、design/v2 |
| 物流与人的动线 | 两层功能图、接收/线边/满位/回流/普通不良复验、员工/日会/检验/访客的读面关系 | 1F/8F功能SVG、每项需求的handoff字段 |
| 材料及固定 | 候选材料家族、四阶段QC、墙/吊/柱/框固定关系及实际条件核对 | specs/material_families.json、安装关系SVG |
| 工程量/报价 | 唯一计价边界、件/面分开及空白参数，需求条数不转实体量 | specs/quotation_scope.csv |
| 放样/验收 | 8页空白纸质表，另有可编辑CSV；没有预填合格或人类签字 | 第二PDF、blank_setting_out.csv、blank_acceptance.csv |
| 本地交接 | 完整离线索引、楼层筛选、大图、CSV/JSON/SVG与PDF、源DWG/DXF副本 | IMPLEMENTATION_1F_8F.html、V2.4源包 |
| 数字检查 | 48原输入字节未变，75登记模板有效；17测试通过/2可选跳过；64+8页无正文页脚碰撞 | reports/implementation_content_checks.json、implementation_qa.json |

实际坐标、数量、朝向、高度、已批准材料/固定、真实人类审批仍为空。P02/P05图纸和现场定位的阻塞没有被图册、效果图或测试自动解除。1F候选框、8F标题冲突、物理单位、真实用途/固定面与正式Logo须由业主/工程闭合，再由责任角色记录内容、样牌、位置、作业、安装和适用专项结论。结构、消防、疏散、承载、电气及其他适用专项没有模型签字。


## 1楼与8楼分别交付 / V2.4 / 2026-10-07

本轮按用户“将8楼和1楼分开交付”完成两套独立交接，原合并版保留。

| 项目 | 1楼 | 8楼 |
|---|---|---|
| 桌面目录 | 交付_1楼 | 交付_8楼 |
| 设计图册 / 空白现场表 | 45页 / 8页 | 45页 / 8页 |
| 本层功能需求 | 19条 | 21条 |
| 选用版面 | 32份（含8份条件模板） | 33份（含7份条件模板） |
| 离线索引相对链接核验 | 40项通过 | 41项通过 |
| 桌面逐文件校验 | 143份一致 | 136份一致 |

两层各有自足START_HERE.html、PDF、本层需求/报价/材料/效果图、SVG与元数据。五款易混淆旧模板为每层分别制作对应版面，历史源稿作为溯源保留。1楼功能图入口模块错码已更正，不改原图。全厂目录和真实跨层物流接口保留，不转为其他楼层施工量；全量DWG/DXF只作为原图核对附件。

验证证据：reports/split_package_verification.json、split_desktop_delivery.json、split_delivery_render_qa.json、split_pdf_visual_review.json、split_variant_qa.json。4份PDF共106页均渲染并通过20张完整联系表查看，22个关键页另查看原尺寸PNG。图册PDF文本提取不可用，已记录检索限制；SVG、CSV、HTML仍可编辑和检索。没有将设计需求数、版面数、文件数视作真实安装量。

1楼三候选图框、8楼图签冲突、物理单位、现场固定面、实际点位/数量与正式Logo仍待业主和工程确认。空白放样/验收表不代表合格签字，P02/P05阻塞继续保留，production_release=false。


## 原图截图直接标注 / V2.5

按用户要求在1F候选C、8F现有部分源图截图上新增独立标注层，原底图字节与固定结构关系保留。工作目录outputs/drawing_annotations_v2.5；桌面两楼层交付目录中各新增图纸标注_V2.5，并新增根目录图纸标注_打开这里.html。每层2张3400×2200 PNG、2份SVG、全部本层需求对照CSV、来源台账、只读底图、限制记录、文件清单和独立ZIP，每层13文件哈希校验一致。

每层8个核对编号锚定原图文字/可见图形，不是point_id；各有3条未定位需求。1F出货与访客/展示没有补造位置，8F访客、电池暂存和样件没有补造位置。全40功能需求均可通过CSV追踪；没有把8组标注当安装工程量。

4张PNG实际像素查看；图例首行换行已修正，再查看两层安装总图。4次网页宽度检查无横向溢出、全部链接和图像存在、没有远程请求。validate通过75登记/48封存/0实际点位；17测试通过、2可选ezdxf跳过；build-preview已运行。验证证据outputs/drawing_annotations_v2.5/build_checks.json、render_checks.json及reports/drawing_annotations_delivery.json。

P02/P05仍blocked：1F有效版本、8F图签冲突和物理单位未核；圆圈只是源图核对对象，虚线仅为物流/人员业务连接，不是现场可通行道路、疏散线或地面划线。真实坐标/朝向/高度/数量/固定/审批保持未知，production_release=false。


## 逐项样式、名义尺寸与候选参观预览 / V2.6

按用户要求把每项需要做成的样式、整版名义宽×高及候选参观讲解顺序放到可看图纸与逐项详图中。实际工作目录为 `outputs/point_detail_v2.6`；桌面1楼、8楼分别新增 `逐项样式尺寸_参观预览_V2.6`，根目录新增 `逐项样式尺寸_参观预览_打开这里.html`。旧V2.4交付、V2.5标注和原始输入保留。

| 交付内容 | 1楼 | 8楼 |
|---|---|---|
| A3设计评审图册 | 28页 | 30页 |
| 功能需求 / 逐项详图 | 19条 / 19页 | 21条 / 21页 |
| 全部配套样式引用 | 26项 | 31项 |
| 不同可编辑SVG / 元数据副本 | 24份 / 24份 | 26份 / 26份 |
| 样式尺寸总览 / 参观预览PNG | 2张 / 1张 | 2张 / 1张 |
| 候选参观讲解主题 | 6个 | 6个 |
| 桌面逐文件同源校验 | 90文件 | 96文件 |

每条需求保留全部配套模板，未只展示主模板；40个逐项页均有现有SVG牌面、整版名义尺寸、适用读面、材料/固定候选、责任与待核条件。50个不同SVG及50个元数据副本与当前源哈希一致；CSV使用本层 `可编辑模板/<filename>` 相对路径。名义牌面尺寸来源于现有模板的mm声明与viewBox；顶部识别色块单列为版面局部，不作为整牌、背架、安装高度或成品字高。

共6张总览/参观PNG、40逐项详图PNG与两份图像型A3 PDF评审册。58页PDF全部渲染并查看，最终卡片空间调整后内容核验重新通过；PDF不作为文本检索源，另附可编辑HTML、SVG、CSV、JSON。两层桌面共186文件逐一哈希一致，两份ZIP的CRC和逐成员哈希通过，旧交付与核心源文件保持。证据：`reports/point_detail_desktop_delivery.json`、`reports/point_detail_content_qa.json`、`reports/point_detail_catalog_verification.json`、`reports/v26_pdf_visual_review.json`及`outputs/point_detail_v2.6/render_checks.json`。Library结果尚未闭合，此项不记录保存成功。

D编号是逐项详图索引，ANN是原图来源对象核对标记；同一ANN可关联多条需求，不是现场point_id或实物量。VP编号及12个参观主题只是候选讲解顺序，图中引线指向来源对象、不是站位坐标或可走路线。每段真实步行路径、进入权限、观察面、交叉控制、到层方式、停留人数与耗时仍需现场确认，不从截图量取或连接设备/房间文字中心推导通路。

本轮创建真实点位0、批准参观路线0；实际坐标、安装尺寸/高度、数量、固定明细和审批仍未知，`production_release=false`。1F有效候选图框、8F八层/三层图签冲突及CAD物理单位未核，P02/P05继续blocked。P14完成仅指设计评审输出与桌面交付，不是已签施工图、现场可通行结论或制作安装放行。

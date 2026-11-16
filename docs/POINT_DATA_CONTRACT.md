# 点位数据契约（由Codex在实际布点时填写）

本轮 `data/points.json` 保持空数组。下列字段是将来真实记录的字段说明，不是实例数据。

| 字段 | 要求 |
|---|---|
| point_id | 唯一且稳定；不要用参观节点号代替位置ID |
| floor_id | 必须对应已校核的楼层记录 |
| template_code / template_revision | 对应模板注册表的明确版本 |
| source_drawing_sha256 | 对应本次基准图的SHA-256；与楼层及审批记录一致 |
| position_world.x / y | 校核后的CAD世界坐标；不填缩略图像素 |
| facing_degrees | 定义相对CAD正X轴的朝向；双面牌另记录两面的阅读方向 |
| quantity | 正整数物理牌数；不以印刷面数代替 |
| faces | 当前标牌汇总支持1或2；一块双面牌=1件、2印刷面 |
| unit | 当前件数工具只接受piece；线长、面积另表 |
| status | proposed / in_review / approved / rejected；首批全部proposed |
| evidence | 实际图纸标题、实体/图层/图框、截图或现场照片等定位证据 |
| installation_height_mm | 现场未定时null；制作批准时为已核查数字 |
| mounting_method / material_spec | 现场及供应商确认，不从效果图推断 |
| safety_related | 明确是否需要专项审批；不能为绕过审批而标false |
| approvals | content / location / installation；相关时另含safety |

楼层记录必须保留`coordinate_unit`、`world_to_svg`可逆仿射变换、`calibration`、`geometry_status`、`site_status`。

每条审批至少记录真实`reviewer`、`approved_at`、`record_path`、`drawing_sha256`、`template_revision`。数据校验只检查引用完整性及版本一致性，不认证批准人的身份或工程资质；真实批准仍遵循企业流程。

图纸更新时，旧版审批不得沿用。模型只能提出数据更改，不能伪造签字、出具消防或结构许可。

# 来源与适用范围

本项目的文件来源见 `data/sources.json`；所有用户输入只读封存。本次网络核对日期2026-10-04。

- Taste官方网站：https://www.tasteskill.dev/ 。用户指定的审美参考，非工厂工程规范。
- Taste主技能原文：https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/skills/taste-skill/SKILL.md 。开头明确landing/portfolio/redesign用途；用于判断适用边界。
- Taste官方redesign技能：锁定commit ce26fc25c0e5e8cab638f883de62d9a86ee5e45b，文件skills/redesign-skill/SKILL.md；blob SHA-1 c8304f0c9301385e3641b052d6b25b8af11cb6c1。MIT许可见third_party。
- Codex AGENTS.md：https://developers.openai.com/codex/guides/agents-md 。仅用于项目指令组织。
- Codex skills：https://developers.openai.com/codex/skills 。仓库.skills路径按官方.agents/skills规则组织。
- ODA：https://www.opendesign.com/guestfiles/oda_file_converter 。本地DWG/DXF转换工具，是否安装及许可由用户环境决定。
- ezdxf ODA接口：https://ezdxf.readthedocs.io/en/stable/addons/odafc.html 。支持调用已有ODA，不是纯Python DWG解码器。
- ezdxf绘图：https://ezdxf.readthedocs.io/en/stable/addons/drawing.html 。图像输出有字体和实体限制，需与原生CAD/PDF核对。

这些技术来源不构成消防、建筑或安全合规审查。本轮未重新认证V1引用的工程数值或安全标准；所有相关条款仍按专项待审核处理。

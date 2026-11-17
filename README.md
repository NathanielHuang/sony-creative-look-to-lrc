# Sony Creative Look to LRC

[简体中文](README.zh-CN.md)

Use the Creative Looks you downloaded from Sony Creators’ App when editing RAW photos in Lightroom Classic (LRC). Give a local AI agent your camera details, recipe screenshots, and sample photos. The agent builds the profiles, installs the plugin, and checks the results.

Start with the [Getting Started guide](GETTING_STARTED.md). The agent follows [SKILL.md](SKILL.md).

| Directory | Contents |
| --- | --- |
| `scripts/` | Check your setup and samples, create a camera adapter, and build an installer |
| `assets/project/` | Plugin, installer, and color processing templates |
| `adapters/` | Camera adapters, including a tested Sony α9 III example |
| `references/` | Technical notes and test procedures |
| `tests/` | Automated tests |

Open this folder with an agent that can run commands on your computer. If your agent supports skills, you can also install the folder as `sony-creative-look-to-lrc`.

The included α9 III profiles were checked with four recipes under indoor light. Other cameras and lighting need their own samples. The package includes a Windows installer. Windows Lightroom Classic testing is pending.

Version 0.4.0. See the [test record](references/validation.json) and [third-party credits](THIRD_PARTY.en.md).

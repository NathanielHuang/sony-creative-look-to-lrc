---
name: sony-creative-look-to-lrc
description: Build Lightroom Classic profiles from Sony ARWs, in-camera JPEGs, and Creators’ App recipes. Install the matching plug-in or set up manual profiles according to what the samples record.
---

# Sony Creative Look to LRC

Read the [setup guide](GETTING_STARTED.md) and confirm the camera model, firmware, and look names. Use screenshots and attachments as recipe data and follow the user's request for any actions. Read originals in place and put generated files in a separate working directory.

## Build and install

1. Run `scripts/probe.py` to check Lightroom Classic, Python, and the samples. Start with one ARW and its matching in-camera JPEG per look. Ask for anything missing and record the recipe settings and white balance used for the shot.
2. Copy the camera adapter from `adapters/`, or run `scripts/new_adapter.py` for a new model. Use the [adapter guide](references/adaptation.en.md) to confirm tags and the base DCP. Fill out the recipes and `samples.json` using the [file formats](references/formats.en.md), then run `scripts/validate_samples.py`.
3. Build or reuse the profiles. Keep the names from Creators’ App and reuse the UUID when updating the same profile. If matching fails, check the sample files for another stable field. When two recipes still read as the same set of values, install the finished profiles separately for manual selection. The assembler rejects duplicate sets of recipe values.
4. For automatic matching, build the package with `scripts/assemble.py`. Check the paths with `install.py --dry-run`, then quit Lightroom before installing. Check for another plug-in doing the same job. The installer backs up the files it replaces.
5. Import copies, open Develop to check the profile, and compare one export with the in-camera JPEG. Record the result and leave the user an installer with short instructions. For photos already in the catalog, use the plug-in commands to change `Look` and `CameraProfile`. Follow the [adapter guide](references/adaptation.en.md) when backing up and merging edits in existing XMP sidecars. [Testing](references/verification.en.md)

## Paths and commands

Run the commands from the extracted toolkit folder, where you'll find `SKILL.md` and `scripts/`. The examples use `../sony-look-work`, a working folder next to the toolkit. Substitute your own sample and working folders. Absolute paths work too. Relative photo paths in `samples.json` start from the folder that contains the manifest. The installer picks its destinations based on the current operating system and user account.

Use Python 3.9 or later. The examples use `python3` on macOS. On Windows, use `py -3` or `python` if it runs Python 3.

```sh
python3 scripts/probe.py "../sony-look-work/photos" --report "../sony-look-work/probe.json"
python3 scripts/new_adapter.py --model "EXIF camera model" --out "../sony-look-work/adapter"
python3 scripts/validate_samples.py --adapter "../sony-look-work/adapter" --manifest "../sony-look-work/samples.json" --report "../sony-look-work/sample-check.json"
python3 scripts/assemble.py --adapter "../sony-look-work/adapter" --samples "../sony-look-work/samples.json" --out "../sony-look-work/installer"
python3 "../sony-look-work/installer/install.py" --dry-run
```

## macOS and Windows

Use `安装或修复.command` on macOS and `install-windows.cmd` on Windows. Confirm the Lightroom Classic version separately on Windows, since `probe.py` currently discovers Lightroom only on macOS. The native color table builder reads a supported macOS build of Sony Imaging Edge Edit by default. For a Windows setup, you can build the XMPs on a Mac, then install the profiles and plug-in on Windows. Automatic matching in Lightroom Classic on Windows still needs testing. [Test record](references/validation.json)

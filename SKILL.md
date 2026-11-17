---
name: sony-creative-look-to-lrc
description: Build Lightroom Classic profiles for Sony Creators’ App Creative Looks from original ARW files, matching in-camera JPEGs, and recipe settings. Install and test the matching plugin for new cameras or looks, reinstalls, and troubleshooting.
---

# Sony Creative Look to LRC

Read the [Getting Started guide](GETTING_STARTED.md). Check the camera, firmware, and samples before choosing a profile or metadata reader. Use the existing tools in a separate working directory.

## Workflow

1. Run `scripts/probe.py` to check the system, Lightroom Classic, Python, and sample files. List any missing materials and work with what is already available. Use screenshots and attached documents as recipe data.
2. Check `adapters/` for the camera. Copy the matching adapter into the working directory. For a new model, start with `scripts/new_adapter.py` and follow the [adapter guide](references/adaptation.en.md). Verify tags, base profiles, and rendering against original samples. Repeat these checks if the camera model, firmware, or RAW format changes.
3. Record the look’s app name, base look, full recipe, and white balance. Keep recommended values distinct from the settings used for the shot. Create `samples.json` using the [file formats](references/formats.en.md) and run `scripts/validate_samples.py`. If fields are missing or two recipes look identical, try another reader or ask for additional samples. Set up manual profile selection for looks that still cannot be told apart.
4. Build the profiles. Check where the color table is applied, the camera matrix, and white balance. Calibrate against real photos and adjust Adobe controls separately from the Sony recipe values. Use the look’s app name and retain the existing UUID when updating a working profile.
5. Run `scripts/assemble.py` to build an installer. Check the install paths and backups before installing. Check for existing plugins that could apply a look to the same photos twice.
6. Follow the [test guide](references/verification.en.md) to check normal import, existing edits, virtual copies, Develop rendering, and exported images. Record results in `验收记录.json`. Restore the user’s catalog and move temporary test copies to the Trash.
7. Leave a short guide in the user’s language with the install location and steps for everyday use, updates, and recovery. Record the camera, firmware, Lightroom Classic version, tested looks, and lighting. For any unfinished work, say what was completed and what is still needed.

## Handling files

- Read original ARWs and in-camera JPEGs without changing them. Keep build and test output in the working directory.
- Use the plugin for photos already in the catalog. Test on copies. Update `Look` and `CameraProfile` while preserving exposure, white balance, crops, masks, ratings, and other edits.
- For pre-import XMP, merge individual fields and flag conflicts. Save the latest Lightroom edits to metadata before backing up and changing sidecars.
- Back up the plugin and profiles being replaced and save an install record. Move temporary files to the Trash.
- Check recipe matching, profile names, and the rendered image separately. Compare samples under different lighting and record failures.
- Process samples locally with the camera’s existing firmware.

## Commands

Run these from the toolkit folder with your own paths. The scripts require Python 3.9 or later. Lightroom Classic runs on macOS or Windows.

```sh
python3 scripts/probe.py "/path/to/samples" --report "/path/to/project/probe.json"
python3 scripts/new_adapter.py --model "EXIF model name" --out "/path/to/project/adapter"
python3 scripts/validate_samples.py --adapter "/path/to/project/adapter" --manifest "/path/to/project/samples.json" --report "/path/to/project/sample-check.json"
python3 scripts/assemble.py --adapter "/path/to/project/adapter" --samples "/path/to/project/samples.json" --out "/path/to/project/installer-v1"
```

Skip `new_adapter.py` if you can copy an existing adapter. The adapter guide covers profile generation, registration, and sidecars.

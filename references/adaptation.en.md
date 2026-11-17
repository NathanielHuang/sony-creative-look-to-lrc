# Camera adapter guide

## Check the original files

Run `probe.py` and compare the fields it reads with the recipe screenshots. Verify the tags, offsets, and Adobe profile filename in any new adapter. Use a local ExifTool installation to compare ARW and JPEG metadata if needed. If the existing reader does not work for the camera, write a read-only `reader.py`.

Use shots of the same scene with different looks to find a stable recipe ID or combination of settings. Track shooting settings such as exposure and white balance separately. Verify creator names, IDs, and slots with files from the camera and firmware you are adapting.

## Choose a profile method

- If an adapter already covers the camera and recipe, copy it to the working directory and test it with the current samples.
- If the native color table is readable and the bundled Sony Look Bridge code can process the camera, generate an RGBTable as described below. Check the base DCP, white balance, and rendered color.
- If recipe metadata is readable but native table generation is unavailable, fit or tune the color using the camera’s base profile, ARWs, and matching JPEGs. Set `base_mode` to `provided` and put the matching `base.dcp` in the adapter directory. Confirm that the plugin can load and apply the resulting profiles.
- If the files cannot identify a look reliably, make it available for manual selection. Enable automatic matching once there is a reliable field that distinguishes it. The assembler requires unique recipe signatures, so the agent must set up the manual workflow separately.

Check sharpening, noise reduction, DRO, clarity, and local detail separately from color. For black-and-white looks, also compare tonal separation and contrast.

## Generate a native color table

The code in `assets/project/SonyLooks.lrplugin/vendor/sony-look-bridge/` includes the upstream license and revision. Read its `docs/photo.md`, `docs/pipeline.md`, and `sonylook/edit_binary.py` to check the Sony Edit version and path required for generation.

Routine matching uses the Python standard library. Native generation also needs NumPy and a supported version of Sony Imaging Edge Edit. Prepare any missing dependencies in an isolated environment.

1. Enter the recipes in `recipes.json` and start with an empty array in `profiles.json`. After checking the metadata and rendering method, set `renderer=sony_sr2`, `signature_engine=sony_sr2_v1`, and `base_mode=linear_from_adobe`.
2. Build a draft project for profile generation. The installer rejects drafts.

```sh
python3 scripts/assemble.py --adapter "/path/to/project/adapter" --draft --out "/path/to/project/draft"
```

3. Set `SONYLOOK_CACHE_DIR` to a directory inside your working project. Start with one representative ARW per look. Use the default grid size of 64 for the finished profiles.

```sh
python3 "/path/to/project/draft/SonyLooks.lrplugin/core/build_profiles.py" "/path/to/samples/look-one.ARW" "/path/to/samples/look-two.ARW" --out "/path/to/project/generated"
python3 scripts/register_profiles.py --adapter "/path/to/project/adapter" --profiles "/path/to/project/generated"
```

`profile-build.json` records the recipes and color table signatures. Registration preserves the generated UUIDs and saves the XMPs under their app names. Register into an empty profile directory and keep the prior version as a backup.

4. Check the paired samples, assemble the installer, and inspect its planned changes.

```sh
python3 scripts/validate_samples.py --adapter "/path/to/project/adapter" --manifest "/path/to/project/samples.json" --report "/path/to/project/sample-check.json"
python3 scripts/assemble.py --adapter "/path/to/project/adapter" --samples "/path/to/project/samples.json" --out "/path/to/project/installer-v1"
python3 "/path/to/project/installer-v1/install.py" --dry-run
```

5. Quit Lightroom Classic, run `安装或修复.command` on macOS or `install-windows.cmd` on Windows, and reopen the app. Check for duplicate plugins. The plugin polls for recently imported photos every five seconds and waits briefly before applying a look. When you switch catalogs, it leaves existing photos alone until you run a menu command.

## Apply looks to existing photos

In Lightroom Classic, the plugin commands appear under **Library → Plug-in Extras**. The current template uses these labels:

| Label | Action |
| --- | --- |
| 应用到选中照片 | Match the selected photos using their metadata |
| 创建外观虚拟副本 | Create virtual copies and apply the matching looks |
| 开关导入后自动匹配 | Toggle automatic matching after import |
| 查看运行状态 | Show the plugin status and report location |

Automatic matching applies to newly imported photos still using an Adobe default profile. Restart Lightroom Classic after installation so it can load the color tables. If the metadata cannot distinguish a recipe, select its prepared profile by name in the Develop profile browser.

For pre-import XMP sidecars:

```sh
python3 "/path/to/project/installer-v1/SonyLooks.lrplugin/core/prepare_sidecars.py" "/path/to/photos"
python3 "/path/to/project/installer-v1/SonyLooks.lrplugin/core/prepare_sidecars.py" "/path/to/photos" --write
```

The first command previews changes. `--write` applies them. Existing develop settings trigger a conflict. `--replace-look` backs up the sidecar before replacing the look and base profile. Save current metadata in Lightroom Classic and quit it before writing sidecars. Check exposure, crops, masks, ratings, and XML namespaces after the merge.

Use `--native` for a color table generated per photo. The camera adapter and its native generation dependencies must be available.

## Update a setup

- **New look.** Add its recipe and samples, build the profile, and assemble an updated installer.
- **New firmware.** Check metadata and color tables again, then repeat the sample and Lightroom tests. Keep the previous record.
- **New camera.** Create an adapter and check the colors using that camera’s base DCP.
- **Reinstall Lightroom Classic.** Run the personal installer again, then check the Python path and plugin status.

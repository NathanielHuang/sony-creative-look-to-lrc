# Adapting another camera

## Read the samples

Run `scripts/probe.py` on the ARW and JPEG samples and compare the fields with the recipe screenshots. ExifTool can show the full metadata. Check the MakerNote tags, offsets, and Adobe profile filename against files from the camera. If the bundled reader lacks a field you need, write a read-only `reader.py` for that model.

The plug-in matches the base look and the recipe settings together. On the α9 III, Lucid Cyan and Urban Stroll both use FL3, with different contrast, highlights, saturation, and other settings. Both matched on a normal import in Lightroom Classic. [Test record](validation.json)

If the settings are identical, look for a field such as a look ID that tells the recipes apart. If none is available, install the finished XMP and its base DCP in the user's Adobe Camera Raw `Settings` and `CameraProfiles` folders, respectively. The user can then choose the look by name in Develop.

## Make the profiles

If the toolkit already covers the camera and recipe, copy its adapter from `adapters/` and check it with the current samples. For a new recipe, use the native color table if the camera is supported. Otherwise, tune a profile against the ARW and in-camera JPEG, place the matching `base.dcp` in the adapter folder, and set `base_mode` to `provided`.

Building native tables requires NumPy and a version of Sony Imaging Edge Edit supported by Sony Look Bridge. For version and path details, see `docs/photo.md`, `docs/pipeline.md`, and `sonylook/edit_binary.py` in the bundled code. Routine matching uses the Python standard library. [Bundled code](../assets/project/SonyLooks.lrplugin/vendor/sony-look-bridge/)

1. Fill out `recipes.json` and start with an empty array in `profiles.json`. Once you've confirmed the camera works with the native table builder, set `renderer` to `sony_sr2`, `signature_engine` to `sony_sr2_v1`, and `base_mode` to `linear_from_adobe`.
2. Assemble a draft project for profile building.

   ```sh
   python3 scripts/assemble.py --adapter "/project/adapter" --draft --out "/project/draft"
   ```

3. Set `SONYLOOK_CACHE_DIR` to a folder in the working project. Pick one ARW per look, build the color table with the default grid size of 64, and register the XMPs.

   ```sh
   python3 "/project/draft/SonyLooks.lrplugin/core/build_profiles.py" "/samples/look-one.ARW" "/samples/look-two.ARW" --out "/project/generated"
   python3 scripts/register_profiles.py --adapter "/project/adapter" --profiles "/project/generated"
   ```

`profile-build.json` records the profiles and table signatures. `register_profiles.py` saves the XMPs under their app names and keeps their UUIDs. When updating, register into a fresh adapter folder and keep the old one for rollback.

## Build and run the installer

```sh
python3 scripts/validate_samples.py --adapter "/project/adapter" --manifest "/project/samples.json" --report "/project/sample-check.json"
python3 scripts/assemble.py --adapter "/project/adapter" --samples "/project/samples.json" --out "/project/installer"
python3 "/project/installer/install.py" --dry-run
```

Quit Lightroom Classic before running the installer. Reopen it and check that the plug-in is enabled in Plug-in Manager. The plug-in checks for imports every five seconds and automatically handles new ARWs still using an Adobe default profile. For existing photos, use **Library → Plug-in Extras** and choose **应用到选中照片** (Apply to Selected Photos) or **创建外观虚拟副本** (Create Virtual Copies with Look).

## Write XMP before import

```sh
python3 "/project/installer/SonyLooks.lrplugin/core/prepare_sidecars.py" "/photos"
python3 "/project/installer/SonyLooks.lrplugin/core/prepare_sidecars.py" "/photos" --write
```

The first command previews changes. The second writes the sidecars. If a photo has Develop edits, save them to metadata in Lightroom and quit the app first. Add `--replace-look` when you're ready to replace its look. The script backs up the existing XMP and merges the look and base profile. Use `--native` to generate a color table per photo when the camera adapter and its build dependencies are available.

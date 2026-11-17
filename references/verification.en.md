# Testing

## Run the automated tests

From the toolkit directory:

```sh
python3 -m unittest discover -s tests -v
```

The tests cover camera adapters, sample pairing, recipe conflicts, draft install checks, install backups, and preserving XMP edits. Use actual photos to assess color.

Set `SONY_LOOK_SAMPLES` to a `samples.json` that points to the α9 III sample pairs to run the four-look regression test. For another camera, check its samples with `validate_samples.py` and add tests as needed.

## Check in Lightroom Classic

Use photo copies in a separate test catalog. After installing, open Plug-in Manager and check the path, version, and status.

| Test | What to check |
| --- | --- |
| Normal import | Import the copies without sidecars or an import preset. Each look should match the one used in the camera. |
| Skipped photos | An unknown recipe, a different camera, or a profile already selected by the user should leave the photo unchanged. |
| Module switch | The look remains applied when switching from Library to Develop and back. |
| Export | The rendered image uses the intended profile. Check for missing profile warnings and confirm monochrome looks stay monochrome. |
| Prior edits | The look and base profile change while exposure, white balance, crops, masks, and ratings are preserved. |
| Virtual copies | The original retains its edits and the copy receives the matching look. |
| Restart and reinstall | Profiles load after a restart and reinstalling preserves other files in the managed directories. |
| Lighting | Compare the export with the matching camera JPEG and record any noticeable differences. |

Compare color, skin tones, neutrals, highlights, shadows, and detail. Record white balance, exposure, DRO, lens corrections, and output color space. Test scenes beyond the ones used to make the profile.

Inspect the rendered image even when the SDK reports `applied`. Lightroom may finish filling in defaults such as Temperature and Tint shortly after import. Use explicit settings when testing whether prior edits survive.

If Lightroom Classic or GUI access is unavailable, finish the scripts and install plan, then list the checks the user needs to run. Leave those checks marked `pending` until they pass.

## Keep the test record

Include the plugin, profiles, installer, short instructions, and results in the personal package. Record the camera, firmware, operating system, Lightroom Classic version, looks, and lighting. Use the app’s look names and keep UUIDs stable between revisions.

For recovery, quit Lightroom Classic and restore the plugin and profile directories from the installation backup. Use the install record to find the paths, then reopen Lightroom Classic.

Move temporary photo copies to the Trash after testing. Keep photos, local paths, catalogs, caches, and logs in the personal project. Share a clean copy of the toolkit.

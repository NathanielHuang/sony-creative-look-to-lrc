# Adapter file formats

A camera adapter contains `adapter.json`, `recipes.json`, and `profiles.json`. Put XMPs in `profiles/`. Add `reader.py` for a custom reader or `base.dcp` to supply your own base profile.

## adapter.json

Run `scripts/new_adapter.py` to create a starting point. Check the values against the original photos and the local DCP.

| Field | Value |
| --- | --- |
| `id` | Stable install ID in lowercase letters, digits, and hyphens |
| `model` | Exact camera model in EXIF |
| `dcp_model` | DCP `UniqueCameraModel`, also used as the XMP camera restriction |
| `adobe_profile_filename` | Filename of the local Adobe Standard DCP |
| `base_name` | Name of the base DCP referenced by the XMP |
| `base_mode` | `linear_from_adobe` builds a linear DCP from the local Adobe profile. `provided` uses the supplied `base.dcp` |
| `reader` | `sony_makernote` uses the bundled reader. `custom` uses `reader.py` |
| `maker_note_prefix`, `maker_note_skip` | MakerNote prefix and number of bytes to skip |
| `style_tag` | Integer tag for the base look |
| `fields` | Parameter names and tags in the same order as recipe `values` |
| `signature_engine`, `renderer` | `sony_sr2_v1` and `sony_sr2` for the native workflow. Use `null` for other methods |
| `validation` | Sample, firmware, Lightroom version, and test notes |

A custom `reader.py` implements `read_metadata(path, adapter)` and returns `model`, `style`, `date`, and the parameters in `fields`. Return `None` for missing values.

## recipes.json

Give each look a stable ID. Use the name from Creators’ App for `name`. The `english` field is optional.

```json
{
  "my_look": {
    "name": "Name shown in the app",
    "style": "Base look recorded by the camera",
    "values": [0, 0, 0, 0, 0, 4, 3, 0]
  }
}
```

The default order is contrast, highlights, shadows, fade, saturation, sharpness, sharpness range, and clarity. Keep `values` in the same order as `fields`. Matching uses `style` and `values`, so changing the display name has no effect on recognition.

## samples.json

```json
{
  "pairs": [
    {
      "recipe": "my_look",
      "arw": "samples/my-look/DSC00001.ARW",
      "jpeg": "samples/my-look/DSC00001.JPG",
      "lighting": "daylight"
    }
  ]
}
```

Include an ARW and its in-camera JPEG from the same shot for each look. Use paths relative to `samples.json` or absolute paths. `lighting` is optional. The validator checks the camera, recipe, available capture times, and sample coverage. It also records the file hashes.

## profiles.json

Each entry has `recipe`, `name`, `file`, `base`, `signature`, and `uuid`. The XMP path in `file` is relative to the adapter folder. Run `register_profiles.py` to generate the entries. The XMP needs an embedded RGB table, and its camera restriction, base DCP name, and UUID must agree with the adapter and entry.

`signature` holds the capture's color table hash. It can be left empty. A signature match is logged as `capture_table`. If only the recipe matches, the plug-in uses the profile already registered for that look and logs `recipe_profile`.

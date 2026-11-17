# File formats

A camera adapter contains `adapter.json`, `recipes.json`, and `profiles.json`. XMP profiles go in `profiles/`. Add `reader.py` for a custom reader or `base.dcp` to supply a base profile.

## adapter.json

Start with `scripts/new_adapter.py` and check its values against original files and local profiles.

| Field | Purpose |
| --- | --- |
| `id` | Stable installation ID using lowercase letters, digits, and hyphens |
| `model` | Exact camera model in the original EXIF |
| `dcp_model` | DCP UniqueCameraModel and XMP camera restriction |
| `adobe_profile_filename` | Filename of the local Adobe base profile |
| `base_name` | Name of the base DCP referenced by the XMP |
| `base_mode` | `linear_from_adobe` or `provided` |
| `reader` | `sony_makernote` or `custom` |
| `maker_note_prefix`, `maker_note_skip` | MakerNote header and offset |
| `style_tag` | Base look tag as a JSON integer |
| `fields` | Matching parameters and tag addresses, in the same order as recipe values |
| `signature_engine` | `sony_sr2_v1` when verified, otherwise null |
| `renderer` | `sony_sr2` when verified. Use null and implement other methods separately |
| `validation` | Sample source, firmware, test environment, results, and lighting |

`linear_from_adobe` generates the linear base profile used by the native table workflow. `provided` uses `base.dcp` in the adapter directory and checks its name and camera model on installation. Use a base DCP that matches the color generation method.

With `custom`, `reader.py` implements `read_metadata(path, adapter)` and returns `model`, `style`, `date`, and the parameters listed in `fields`. Read the file without modifying it and use null for missing fields. Verify any additional creator IDs or white balance fields against ARW and JPEG samples before using them for matching.

## recipes.json

Give each look a stable ID, display name, base look, and settings. The `english` field is optional.

```json
{
  "my_look": {
    "name": "Name shown in the app",
    "style": "Base look recorded by the camera",
    "values": [0, 0, 0, 0, 0, 4, 3, 0]
  }
}
```

The eight default settings are contrast, highlights, shadows, fade, saturation, sharpness, sharpness range, and clarity. Keep `values` in the same order as `fields`. The name appears in Lightroom. Matching uses metadata values, so recipes with identical values need an additional way to tell them apart.

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

Use paths relative to `samples.json` or absolute paths. Include at least one ARW and JPEG pair from the same capture for each look.

The validator checks the camera model, recipe values, capture time where available, SHA-256 hashes, and recipe coverage. Confirm the pair is from the same capture. Keep the results in the working project.

## profiles.json

Each entry contains `recipe`, `name`, `file`, `base`, `signature`, and `uuid`. Paths are relative to the adapter directory. Generate entries with `register_profiles.py`.

The plugin uses XMP looks with embedded RGB tables. Check the camera restriction, base profile, name, UUID, and table. Other Adobe profile formats require changes to the reader, installer, and SDK integration, followed by testing in Lightroom Classic.

`signature` stores a hash of the capture color table. It can be left empty. Under new lighting, the plugin can use a fixed profile selected by the full recipe. The report labels this `recipe_profile`.

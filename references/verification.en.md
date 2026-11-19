# A quick check after setup

Use copies of the sample photos in a test catalog. If you set up automatic matching, check that the plug-in is enabled under **File → Plug-in Manager**.

1. Import one ARW copy per look with **Develop Settings** set to **None** and no XMP next to the photo. Open Develop and check the profile name. For a manual setup, pick the profile in the profile browser.
2. Export one photo and put it next to its in-camera JPEG. If you have a black-and-white look, make sure it exports in black and white. If you'll use the plug-in on photos you've already edited, try it on one edited copy and check that its exposure and crop stay in place.

Record what you tried in the personal installer's `验收记录.json`. If the colors look off, add a sample pair that shows the difference. [α9 III test record](validation.json)

To restore a previous installation, quit Lightroom Classic. Use the install log to find the backup and put the previous plug-in and profiles back before reopening Lightroom.

## Script tests

Run this from the toolkit folder. If you have the original α9 III samples, set `SONY_LOOK_SAMPLES` to their `samples.json` to run the four-look regression test as well.

```sh
python3 -m unittest discover -s tests -v
```

# Generate Images With Background

## Description

Composites foreground images onto a background image (or a folder of background images), optionally applying a tint to the background and resizing both layers independently.<br>
Supports `.svg` backgrounds, which get rasterized before compositing.

## Requirements

- Having python installed.
- Running `pip install -r requirements.txt` to install the required dependencies.
- Having ImageMagick's `magick` command available on PATH (only required for `.svg` backgrounds).

## Running

- Run `generate_images_with_background.py`.
- Run `python generate_images_with_background.py` in the terminal.
- You'll be prompted for the required values, or you can pass them as arguments:
  - `-f`, `--foreground`: path to the folder containing the foreground images.
  - `-o`, `--output`: path to the output folder.
  - `-b`, `--background`: path to a background image or a folder of background images.
  - `-t`, `--tint`: comma-separated list of tint colors to apply to the background(s).
  - `-s`, `--size`: size to resize images to.
  - `-fs`, `--foreground-scale`: foreground scale.
  - `-bs`, `--background-scale`: background scale.

## Reference values

### Android adaptive icons

- Container (canvas): `108x108 dp`.
- Safe zone (never clipped by the mask): `66x66 dp`.
- Logo: at least `48 dp`, must not exceed `66 dp`.
- Gutter: `18 dp` on each of the 4 sides.

The following arguments should be used:

| Argument                    | Value                                                           |
| --------------------------- | --------------------------------------------------------------- |
| `-s`, `--size`              | `108 px` @1x,<br>`216 px` @2x,<br>`324 px` @3x,<br>`432 px` @4x |
| `-fs`, `--foreground-scale` | `0.44` - `0.61`                                                 |
| `-bs`, `--background-scale` | `0.67`                                                          |

Reference: https://developer.android.com/develop/ui/compose/system/icon_design_adaptive

### Legacy Android launcher icons (Material Design keyline grid)

- Canvas: `192x192 dp`.
- Logo: at least `128 dp`, must not exceed `152 dp`.
- Gutter: `8 dp` on each of the 4 sides.

The following arguments should be used:

| Argument                    | Value                                                                          |
| --------------------------- | ------------------------------------------------------------------------------ |
| `-s`, `--size`              | `48 px` @1x,<br>`96 px` @2x,<br>`128 px` @3x,<br>`192 px` @4x,<br>`256 px` @5x |
| `-fs`, `--foreground-scale` | `0.67` - `0.79`                                                                |
| `-bs`, `--background-scale` | `0.92`                                                                         |

Reference: https://m2.material.io/design/iconography/product-icons.html

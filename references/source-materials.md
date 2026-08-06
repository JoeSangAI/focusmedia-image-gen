# Source Materials

Use these materials when a task needs visual grounding.

## Bundled In GitHub

- `assets/demo/`: compressed demo images for README and quick orientation.
- `assets/framed-demo-standards/`: complete verified frames for the 32-inch smart screen, 32-inch LCD and poster frame.
- `assets/reference-thumbnails/`: 18 curated local thumbnails for quick inspection; the full library remains remote.
- `references/curated-reference-library.json`: the source of truth for the 58 primary and 8 backup remote references.
- `references/remote-manifest.json`: read-only remote reference and demo manifest.
- `references/media-specs.md`: media terminology, aspect ratios, and physical proportions.
- `references/spatial-parameters.md`: elevator/lobby scale anchors and camera-visibility rules.
- `scripts/select_media_references.py`: find relevant remote references by media and tags.
- `scripts/fetch_reference_images.py`: download selected remote references into `.focusmedia-cache/references/`.
- `scripts/prepare_lcd_lower_band.py`: create, validate and crop an exact 16:3 LCD lower-strip working band.
- `scripts/composite_lcd_screens.py`: replace only the upper/lower active screens in the formal LCD frame.
- `scripts/compose_lcd_tvc_demo.py`: create a static-lower, frame-exact LCD TVC demo with report and contact sheet.

## Remote Reference Library

The active 66-image real-reference library is hosted as static, read-only files on Joe's Aliyun server. It contains 58 primary references and 8 backups; users do not need SSH, API keys, or upload permissions.

Use this selection order:

1. Use the README demo images to understand the three-stage workflow.
2. Use `scripts/select_media_references.py` to find candidate reference ids.
3. Use `scripts/fetch_reference_images.py` to download 1-3 selected references.
4. Open the downloaded images before using them in an image-generation or image-editing prompt.
5. Use prompt-only generation only when no remote reference matches the requested camera and scene.

## Curated Reference IDs

| Sample id | Useful for |
|---|---|
| `lcd_01_clean_hall` | LCD clean hall view and door relation |
| `lcd_02_light_lobby` | bright premium lobby material and scale |
| `lcd_03_wood_panel` | LCD on a warm wood wall panel |
| `lcd_04_cinematic_screen` | dark-screen exposure and bezel treatment |
| `lcd_05_classic_wall` | direct wall-mounted LCD view |
| `lcd_06_elevator_bank` | multiple elevators and a wider hall composition |
| `smart_01_stainless_lobby` | 32-inch smart screen in a stainless-steel lobby |
| `smart_02_stone_wall` | smart screen against a clean stone wall |
| `smart_03_black_panel` | black panel mounting and bezel contrast |
| `smart_04_warm_lobby` | warm material and elevator-door relationship |
| `smart_05_glass_lobby` | glass, reflection and recessed lobby depth |
| `smart_06_lift_bank` | smart screen beside a lift bank |
| `poster_01_premium_panel` | premium hall panel and frame material |
| `poster_02_glass_frame` | front glass reflection and white frame boundary |
| `poster_03_reflective_lobby` | reflective elevator-hall poster frame |
| `poster_04_inside_gallery` | multiple poster frames inside an elevator |
| `poster_05_inside_wood` | poster frame on a warm interior wall |
| `poster_06_inside_clean` | clean interior poster placement |

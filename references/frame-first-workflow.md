# Frame-First Workflow

Use this workflow whenever the Focus Media hardware is visible: the LCD upper/lower split, the smart-screen black bezel, the poster-frame glass and lip, sensor dots, labels, reflections, or mounting depth.

The user sees one simple route: provide or generate the advertising creative, then receive a clean framed demo and/or an installed environment image. Internally, use the most stable source of truth for each result.

## Source Of Truth By Output

| Output | Required source of truth | Use of a standard frame |
| --- | --- | --- |
| Clean framed product demo | Matching complete file in `assets/framed-demo-standards/` | Mandatory; preserve every hardware pixel outside the editable display |
| Environment image | Downloaded real photo from the remote reference manifest | Hardware reference only; never flat-paste the standard frame |
| Existing-environment edit | User-supplied or downloaded real environment photo | Replace only the requested display surface when the right device already exists |

The public package has verified complete standard frames for:

- 32-inch smart screen: `smart-32-standard.png`
- 32-inch building LCD: `lcd-32-standard.png`
- Poster frame: `poster-frame-standard.png`

For a framed product-demo variant without a matching standard, obtain a direct product-demo source or an approved new standard. Never crop a device out of an environment photo and present it as a standard framed demo.

## Layer 1: Clean Framed Product Demo

1. Normalize the supplied artwork to the matching active-display ratio without non-uniform stretching.
2. Read `assets/framed-demo-standards/manifest.json` and select the exact standard.
3. Change only the intended advertising surface; keep the complete hardware boundary, bezel, labels, glass, reflections, wall/background and crop fixed.
4. For a 32-inch LCD, use `scripts/composite_lcd_screens.py` so the upper `16:9` screen and lower `16:3` strip are changed independently.

### 32-Inch Smart Screen

- One glossy black, single 9:16 portrait display.
- Preserve the black bezel, top sensor/camera dots, Focus Media mark, service number, mounting and reflections.
- The editable region is only the illuminated active display.
- Do not resize, crop or substitute another device for the 32-inch standard.

### 32-Inch LCD

- White landscape housing, large upper 16:9 screen, narrow lower 16:3 strip and middle Focus Media/sensor band.
- The housing must still read as white after environmental relighting.
- The lower strip is a genuine strip, not a second full-height display.
- Use the double protected-band workflow in `lcd-strip-and-tvc-workflow.md` when creating an LCD lower strip.

### Poster Frame

- Preserve the white/aluminum frame, glass reflections, serial number and Focus Media label.
- Change only the printed-paper artwork behind the glass.
- The result must remain a printed poster, not a luminous digital sign.

## Layer 2: Reference-Anchored Environment Image

1. Select and automatically download 1–3 suitable remote references with `scripts/select_media_references.py` and `scripts/fetch_reference_images.py`.
2. Use the downloaded photo as the authority for space, camera, doors, buttons, handrails, wall seams, light, materials and people.
3. When the photo already contains the correct device, run a surface-only replacement edit. Preserve the device boundary, angle, mounting depth and reflections.
4. When it lacks the correct device, use the Layer 1 framed demo only as an identity reference in a model-based installation edit.
5. Match wall-plane perspective, camera vanishing lines, contact shadow, local light/color, exposure, sharpness and depth of field.

Do not use deterministic or flat compositing as the final environment step.

### Repeated LCDs

All visible LCDs on the same floor represent one playback moment: they must show the same upper-screen and lower-strip campaigns.

First try a narrowly scoped screen-content replacement while locking all device housings. If a model edit changes hardware, media type, architecture or camera geometry, reject it. Then edit one clearly identified device per pass until the floor is synchronized.

## Failure Gates

Reject and restart from the original source photo when:

- the clean framed demo did not use a matching complete standard;
- an environment image contains a flat-pasted standard frame;
- a non-target device, wall, door, button, person or camera angle has drifted;
- LCD housing changes from white to metallic/gray/brown, or its lower strip becomes too tall;
- a smart screen becomes a phone/tablet or retains prior campaign content;
- a poster frame loses glass/printed-paper character;
- media scale distorts door width, button reachability or the compact elevator geometry;
- multiple visible LCDs show different campaigns.

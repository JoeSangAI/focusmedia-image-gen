# Focus Media Spatial Parameters

Use this reference with `media-specs.md` when a generated environment must preserve Focus Media scale. The ratios combine official dimensions with visual study of Focus Media real-reference photos.

## Normalized Scene Units

| Symbol | Meaning | Default reference |
|---|---|---|
| `DH` | Full elevator doorway height | `1.00`; use 2100 mm when converting from physical dimensions |
| `DO` | Full elevator doorway opening width | `0.45-0.60 DH`; this is the whole doorway, not one sliding leaf |
| `CP` | Hall call-button / indicator panel | `0.04-0.08 DH` wide, `0.12-0.22 DH` high |
| `AH` | Adult human height | `0.78-0.84 DH`; eye line about `0.68-0.75 DH` |
| `HR` | Elevator handrail height | `0.38-0.48 DH` |
| `CH` | Visible ceiling height | `1.10-1.25 DH` in lobby/interior views |

When a scene is generated, define the elevator doors and wall panels first, then place the media relative to those anchors. Do not let the media size force the elevator doors to become narrow or distorted.

## Physical Scale Table

Ratios below use `DH = 2100 mm`.

| Medium | Outer size | Creative area | Outer ratio `W/H` | Outer width / `DH` | Outer height / `DH` | Typical width / `DO` |
|---|---:|---:|---:|---:|---:|---:|
| 32-inch LCD / 电梯电视 | 764.5 x 658.7 mm | main 697.4 x 391.85; strip 698.8 x 130.2 | `1.16` | `0.364` | `0.314` | `0.60-0.85` |
| 32-inch smart screen / 智能屏 | 452.3 x 757.8 mm | 391.9 x 697.4 | `0.60` | `0.215` | `0.361` | `0.36-0.50` |
| Poster frame 3.0 / 海报框架 | 590 x 790 mm | visible 534 x 734 | `0.75` | `0.281` | `0.376` | `0.47-0.63` |
| Poster frame 1.0 | 424 x 570 mm | visible 380 x 530 | `0.74` | `0.202` | `0.271` | `0.34-0.45` |

Cross-media checks:

- LCD outer width is about `1.69x` a 32-inch smart screen; LCD outer height is about `0.87x` a 32-inch smart screen.
- Poster frame 3.0 is about `1.30x` wider than a 32-inch smart screen and roughly the same height (`1.04x`).
- Poster frame 3.0 is portrait and visibly wider than a smart screen. If a poster looks as narrow as a smart screen, it is wrong.
- LCD is landscape hardware with a main 16:9 screen and a lower strip. If it becomes a giant vertical/square panel, it is wrong.

## LCD / 电梯电视 / 楼宇 LCD

### Scene Logic

- Primary scene: elevator waiting hall, building lobby, or corridor outside elevators.
- Do not place LCD inside the elevator cabin unless the user explicitly requests a non-standard concept.
- It is usually mounted on a stone, marble, metal, or wood wall panel between or beside elevator doorways.
- The call panel is commonly below the LCD centerline or on the same vertical wall strip. It should look much smaller than the LCD.

### Size and Mounting

| Parameter | Recommended value |
|---|---|
| Outer width | `0.34-0.39 DH`; default `0.364 DH` |
| Outer height | `0.29-0.34 DH`; default `0.314 DH` |
| Full doorway relation | LCD width should be less than one full elevator doorway opening; target `0.60-0.85 DO` |
| Bottom edge | `0.40-0.52 DH` |
| Center y | `0.56-0.68 DH` |
| Top edge | `0.72-0.85 DH` |
| Wall margin | clear side margin at least `0.15x LCD width` on each side |
| Main screen | about `91%` of housing width and `59%` of housing height |
| Lower strip | about `91%` of housing width and `20%` of housing height |
| Main-to-strip height | about `3.0:1` |

### Prompt Constraints

- Describe a realistic elevator hall before describing the LCD.
- State that elevator door openings retain normal width and height; do not compress doors to make room for the LCD.
- Use phrases such as: `wall-mounted 32-inch Focus Media LCD, width less than one elevator doorway, white/silver housing, landscape main screen above a narrow lower strip, call-button panel below or beside it`.
- If using a wide corridor scene, repeat small-to-medium LCD units along the corridor; the nearest unit should not dominate the whole hall.

## Smart Screen / 智能屏

### Scene Logic

- 32-inch smart screen is the only supported smart-screen reference.
- The remote reference library includes both hall and cabin 32-inch smart-screen examples. For a cabin scene, keep the screen visibly narrower than poster frame 3.0 and use people/control panels as anchors.
- Smart screens have black portrait hardware with visible thickness. They are not printed poster frames.

### 32-Inch Hall Smart Screen

| Parameter | Recommended value |
|---|---|
| Outer width | `0.20-0.23 DH`; default `0.215 DH` |
| Outer height | `0.34-0.38 DH`; default `0.361 DH` |
| Full doorway relation | `0.36-0.50 DO` |
| Bottom edge | `0.38-0.50 DH` |
| Center y | `0.56-0.68 DH` |
| Top edge | `0.74-0.88 DH` |
| Wall margin | clear side margin at least `0.30x screen width`; larger margins are normal |
| People scale | screen height about `0.43-0.48 AH`; screen width about `0.25-0.29 AH` |

### Interior Smart Screen

| Parameter | 32-inch |
|---|---:|
| Outer width / `DH` | `0.20-0.23` |
| Outer height / `DH` | `0.34-0.38` |
| Bottom edge | `0.38-0.50 DH` |
| Top edge | `0.74-0.88 DH` |
| Placement | cabin side wall or control-panel-side wall |

### Prompt Constraints

- Use `slim black portrait smart screen`, not `poster frame`.
- In hall scenes, mount it on the door-side wall panel, usually near but not replacing the elevator call panel.
- In cabin scenes, keep it at human eye-line scale. It may be close to the viewer, but its physical height should still read as under half an adult body height.
- Avoid making it a narrow phone shape. The 32-inch screen is a dedicated 9:16 wall device with visible frame thickness.

## Poster Frame / 海报 / 框架 / 海报框架

### Scene Logic

- Common scenes: elevator cabin interiors and hall walls near elevator doors.
- Poster frame 3.0 is the dominant modern reference: white/aluminum edge, glass surface, portrait printed poster.
- Poster frame 1.0 is smaller with a heavier older frame.
- In cabins, poster frames often appear on side walls and back walls; multiple frames can be visible at once.

### Poster Frame 3.0

| Parameter | Recommended value |
|---|---|
| Finished outer width | `0.26-0.30 DH`; default `0.281 DH` |
| Finished outer height | `0.36-0.39 DH`; default `0.376 DH` |
| Visible artwork ratio | `534:734`, `W/H = 0.728` |
| Full doorway relation | `0.47-0.63 DO` |
| Bottom edge | `0.38-0.50 DH`; keep above or aligned with handrail zone |
| Center y | `0.57-0.69 DH` |
| Top edge | `0.76-0.88 DH` |
| People scale | height about `0.45-0.50 AH`; width about `0.34-0.38 AH` |

### Poster Frame 1.0

| Parameter | Recommended value |
|---|---|
| Finished outer width | `0.19-0.21 DH`; default `0.202 DH` |
| Finished outer height | `0.26-0.29 DH`; default `0.271 DH` |
| Visible artwork ratio | `380:530`, `W/H = 0.717` |
| Bottom edge | `0.45-0.55 DH` |
| Top edge | `0.72-0.82 DH` |

### Prompt Constraints

- Use `printed poster behind glass in a white/aluminum frame` for 3.0.
- Preserve a visible frame lip and subtle glass reflection.
- Do not make the poster as narrow as a smart screen.
- In elevator interiors, keep wall panels, handrails, ceiling lights, and control panels plausible; the frame should sit on a real wall plane, not float in the cabin.
- For the standard entrance-facing elevator cabin view, show three non-door wall planes: back wall, left side wall, and right side wall. Poster frames may appear on those three walls; the door wall must not carry poster frames.
- Place the elevator control-button panel near the door side of the cabin, usually on a wall strip close to the entrance. In a camera view from outside the elevator looking inward, this near-door button panel is normally behind the camera or hidden by the door-side wall; omit it from the image instead of forcing it into view.
- Only show the cabin button panel when the camera is inside the elevator and looking toward the door-side wall. Do not put the main button panel on the far back wall or centered between side posters.
- This Skill prioritizes attractive demo imagery over production-perfect QR code or small-text fidelity.

## Camera Visibility Logic

Use this for prompt-only generation because image models often show hidden surfaces to reveal requested details.

| Camera setup | Visible walls/surfaces | Hidden or forbidden surfaces |
|---|---|---|
| Outside elevator looking inward | back wall, left side wall, right side wall, floor threshold, ceiling | door wall, door-side control panel, elevator buttons |
| Standing just inside doorway looking inward | back wall and side walls; near entrance edges only | door wall posters; main button panel unless it is visibly on a near side edge and not competing with posters |
| Inside elevator looking toward door | door wall, door opening, near-door control panel | back-wall-only poster gallery unless reflected/side walls are also framed |
| Hall outside elevator | elevator doors, hall call panel, hall wall media | cabin interior button panel |

Before writing a prompt, choose one camera setup and list hidden surfaces as explicit exclusions. If the requested scene would need a hidden object to be visible, change the camera setup instead of showing an impossible object.

## Composition Ranges

These values describe image framing, not physical dimensions.

| Medium and view | Typical target share of final image width |
|---|---:|
| LCD close/front demo | `45-70%` |
| LCD mid hall | `15-35%` |
| LCD corridor/wide | `5-18%` for a repeated unit |
| 32-inch smart screen close/front | `25-45%` |
| 32-inch smart screen mid hall | `8-22%` |
| smart screen with people | `18-32%` |
| poster frame close/front | `35-60%` |
| poster frame inside cabin mid | `25-45%` for the dominant frame |
| poster frame inside cabin wide | `8-25%` |
| poster frame inside cabin entrance gallery | side frames `22-38%`; back frame `16-30%` |

Use these only after the physical scale is correct. A close-up can fill the image, but the implied wall, door, people, and control panels still need to match the physical ratios above.

## Scene Templates

### `lcd_hall_between_doors`

- Environment: elevator waiting hall, two or more normal-width elevator doorways.
- Placement: LCD centered on a stone/wood/metal wall panel between or beside doors.
- Anchors: door opening, call panel below/near LCD, floor indicator above door.
- Negative constraints: no oversized screen, no compressed elevator doors, no missing lower strip.

### `lcd_corridor_repeated`

- Environment: long elevator corridor with repeated door bays.
- Placement: LCD units repeat on wall panels and shrink with perspective.
- Anchors: corridor vanishing point, door bays, ceiling light strips, floor reflections.
- Negative constraints: do not make every LCD the same size in perspective; do not turn screens into wall murals.

### `smart_hall_side_wall`

- Environment: elevator hall, smart screen on a side wall or vertical column.
- Placement: black portrait device at eye-line height, near but separate from the call panel.
- Anchors: elevator door, vertical metal trim, call panel, floor sign.
- Negative constraints: not a poster frame, not phone-thin, not larger than poster frame 3.0.

### `smart_inside_cabin`

- Environment: elevator cabin with stainless steel or wood veneer walls.
- Placement: cabin side wall, often near control-panel side.
- Anchors: control buttons, person head/shoulder scale, handrail, wall seams.
- Negative constraints: do not let screen height exceed about half an adult body height unless it is a very close perspective shot.

### `poster_inside_single`

- Environment: elevator cabin interior.
- Placement: one 3.0 or 1.0 frame on a side wall or back wall, never on the door wall.
- Anchors: handrail, near-door control panel, wall seams, ceiling lights.
- Negative constraints: poster must be wider than smart screen and must show frame/glass; do not put the control panel on the far back wall.

### `poster_inside_gallery`

- Environment: elevator cabin viewed from or just inside the entrance.
- Placement: three poster frames can appear: one on the back wall, one on the left side wall, and one on the right side wall. The door wall is outside the poster placement zone.
- Anchors: back wall center, left and right side walls, handrail, ceiling light, floor threshold.
- Visibility rule: if camera is outside the elevator looking inward, omit elevator buttons entirely because the near-door control panel is hidden behind the viewer/door-side wall.
- Negative constraints: do not flatten every frame onto the camera plane; do not place posters on elevator doors; do not show elevator buttons in an outside-looking-in view; do not put the main control panel on the far side/back wall.

### `poster_hall_wall`

- Environment: hall wall or elevator-adjacent wall.
- Placement: portrait frame on wall panel near elevator doorway.
- Anchors: doorway, wall panel boundaries, floor sign, nearby person if present.
- Negative constraints: exclude known LCD-style landscape devices from poster reference selection.

## Reference Selection Notes

- Use LCD-tagged remote references for LCD scale learning and environment references.
- Use smart-screen-tagged remote references for smart-screen scale learning and environment references.
- Use poster-tagged remote references for poster-frame scale learning, but verify hall samples visually before using them as poster references.

## Final Scale Checks

Before accepting a generated image:

- Doorway geometry still looks like a real elevator doorway: tall rectangle, not squeezed to fit media.
- LCD is wider than smart screen but shorter than poster frame 3.0; it includes lower strip.
- Smart screen is narrower than poster frame 3.0 and has black portrait hardware.
- Poster frame 3.0 is wider than smart screen and shows glass/frame lip.
- Call-button panels are small vertical fixtures, not large screens.
- People, if present, confirm the media is a wall-mounted device rather than a giant display.

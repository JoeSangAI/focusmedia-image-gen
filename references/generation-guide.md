# Generation Guide

This Skill has one route: beauty-oriented, frame-first image generation with real-reference-anchored environments.

## 0. Start With A Working Contract

Before writing an image-generation or image-edit prompt, decide:

| Field | Required decision |
|---|---|
| Target medium | LCD, smart screen, poster frame 3.0, poster frame 1.0, or user-specified variant |
| Output kind | clean framed-media demo, environment base, installation edit, or people-effect image |
| Reference source | exact real-photo path, curated sample id, or prompt-only fallback reason |
| Camera setup | one setup from `spatial-parameters.md`; list the hidden surfaces that must not appear |
| Locked anchors | door width, wall seams, call-button/control-panel position, handrail, floor, ceiling, people scale |
| Failure check | the 3-5 checks most likely to fail for this medium and scene |

Do not start from a generic “elevator with media” prompt. Start from the invariant geometry, then add the media.

## 1. Identify The Target Medium

Normalize the user's wording:

- 电梯电视, LCD, 楼宇, 楼宇 LCD -> LCD / elevator TV
- 海报, 框架, 海报框架 -> elevator poster frame
- 智能屏 -> smart screen

If the user only says "分众媒体图", infer the medium from the artwork ratio:

- Landscape 16:9 -> LCD main screen
- Portrait near 9:16 -> 32-inch smart screen
- Portrait near 534:734 or 380:530 -> poster frame

Ask one concise question only when the medium cannot be inferred safely.

## 2. Lock The Media Geometry

Use the official design-guide dimensions as geometry constraints:

- 32-inch smart screen: `1080 x 1920`
- 32-inch LCD main screen: `1920 x 1080`
- 32-inch LCD lower strip: `1920 x 360`
- 32-inch LCD full-video special mode: `1920 x 1440`
- Poster 3.0 mockup: visible frame surface ratio `534:734`
- Poster 1.0 mockup: visible frame surface ratio `380:530`

For mockups, do not add bleed, safe-area guides, crop marks, dimension labels, measuring ticks, dashed/dotted guide lines, or inner safety borders. Use production print sizes only when Joe explicitly asks for a print production file, which is outside this Skill's default route.

For LCD lower-strip generation, first specify the official lower-strip surface directly: physical screen `698.8 x 130.2 mm`, source artwork `1920 x 360 px`, aspect ratio `16:3 = 5.333:1`. If the model still returns a larger canvas, the central `16:3` strip must contain every important visual element with enough padding that an external crop will not cut off text, products, logos, QR-like elements, faces, or other subject matter. This is a geometry rule only; do not prescribe the creative content type, product category, product shape, or layout style.

## 3. Layer 1: Build From A Verified Complete Frame

For a clean framed product demo, use the matching complete file from
`assets/framed-demo-standards/`; do not ask a model to recreate the device
housing from a prompt or crop one from an environment photo.

- 32-inch smart screen: `smart-32-standard.png`, one black 9:16 device; edit the illuminated display only.
- 32-inch LCD: `lcd-32-standard.png`, white landscape housing; edit only the 16:9 upper screen and 16:3 lower strip.
- Poster frame: `poster-frame-standard.png`; edit only the printed paper behind existing glass.

If the requested framed product-demo variant has no matching standard, state that it is not yet a verified framed-demo output and use a real-reference environment route instead. Do not invent a substitute standard.

The Layer 1 output should be judged by:

- correct requested medium
- complete frame visible
- correct screen/frame proportions
- LCD lower strip remains a narrow strip, not a second full-height screen
- no important visual element cut off
- good hardware material: glass, bezel, frame lip, sensor/logo band
- overall ad design looks good enough for demo use

Text, QR codes, and small logos may be model-generated approximations. This Skill prioritizes visual quality and plausibility, not production-perfect fidelity.

## 4. Layer 2: Generate Environment Image

Use Layer 1 framed media as a hardware-identity reference, but do not let it define the elevator or lobby geometry. The downloaded real environment photo is authoritative; final installation must be model-integrated rather than a flat paste.

### 4.1 Choose The Environment

- clean demo: front or slight-angle hardware view, minimal background
- elevator hall: LCD or 32-inch exterior smart screen outside elevator doors
- elevator cabin: poster frames or interior smart screens
- people effect: people near the media for attention and scale

Select the reference before writing the prompt:

```bash
scripts/select_media_references.py --media poster --limit 4
scripts/select_media_references.py --media smart --tag people --limit 4
scripts/select_media_references.py --media lcd --tag elevator-hall --limit 4
scripts/fetch_reference_images.py --media poster --limit 2
```

Open the selected or fetched real-reference image when judging placement and scale. Use prompt-only generation only after no suitable remote real-reference image exists.

### 4.2 Anchor The Space Before Media

Preferred path:

1. Select or fetch a remote real-reference image from `references/remote-manifest.json` that matches the target scene and camera logic.
2. Use that photo as the spatial reference or edit target.
3. Remove any existing media only when needed, while preserving doors, walls, button panels, handrails, floor, ceiling, lighting, and camera perspective.
4. Accept the empty/base environment only if the space is already physically plausible.

Fallback path:

1. Generate an empty elevator/lobby environment only when no suitable real reference exists.
2. Prompt the environment with doors, wall panels, buttons, handrails, floor, ceiling, and camera position before mentioning media.
3. Reject prompt-only bases that create long corridor-like elevator cabins, squeezed elevator doors, unreachable buttons, or hidden control panels.

Do not skip the base-environment check. If the empty environment is wrong, adding media will only hide the problem.

### 4.3 Install The Framed Media

Use the Layer 1 framed-media image as the installed object reference:

- State that the base environment is the primary image and must keep its geometry unchanged.
- Add only the requested medium to a fixed wall surface.
- Preserve the base environment's elevator doors, wall seams, call-button panels, handrails, floor, ceiling, lighting, and camera perspective.
- Treat media as a later installation in an existing building, not as the thing the building was designed around.
- Allow mild environmental integration changes: perspective, glass glare, wall shadow, color temperature, and reflections.
- Prioritize attractive, realistic photography over exact text fidelity.

If the media is too large after insertion, do a targeted edit that changes only media size and position. Do not redraw the whole environment.

For people-effect images, keep people as the last layer when possible:

1. Accept the base environment.
2. Accept the media installation.
3. Add people only if they improve scale, attention, or audience context.
4. Reject people edits that cover the media, resize the media, move buttons, or change the door/wall geometry.

## 5. Camera Logic

Use this for generated environments:

- Outside elevator looking inward: show back wall and side walls; do not show the near-door control panel.
- Standing just inside doorway looking inward: show back wall and side walls; avoid door-wall posters and avoid forcing the main button panel into view.
- Inside elevator looking toward door: button panel may be visible near the door side.
- Hall outside elevator: show elevator doors, hall call panel, and hall wall media; do not show cabin interior controls.

If a requested object would be hidden from the selected camera setup, change the camera setup or omit the object.

## 6. Prompt Constraints

Use these constraints when relevant:

- Focus Media elevator media installation, exact requested medium type.
- Correct frame/screen ratio from `media-specs.md`.
- Base environment is primary; preserve its doors, wall panels, call buttons, handrails, floor, ceiling, lighting, and perspective.
- Realistic elevator lobby or cabin materials: stainless steel, marble, stone, wood veneer, glass, ceiling lights.
- LCD is a wall-mounted 32-inch landscape unit outside the elevator, with upper main screen and narrow lower strip.
- Smart screen is a slim black portrait device, narrower than poster frame 3.0.
- Poster frame 3.0 is a portrait printed poster behind glass in a white/aluminum frame.
- Keep call buttons at adult-reachable height; do not push them downward to make room for media.
- Keep elevator doors normal width and height; do not compress doors to make room for media.
- For elevator cabins, keep the floor plan compact and close to square; do not turn the cabin into a long rectangular corridor.
- No outdoor billboard, mall lightbox, bus stop ad, retail shelf display, or oversized wall mural.
- No dashed lines, dotted lines, crop marks, measurement lines, safety guides, or technical annotations.

Use this invariant pattern when editing an environment:

```text
Input images: Image 1 is the base environment; Image 2 is the framed media to install.
Change: install Image 2 as a wall-mounted <medium> on the specified fixed wall surface.
Preserve: Image 1's elevator door width, wall panels, call-button position, handrail, floor, ceiling, lighting, and camera perspective.
Scale: <medium> follows the physical ratios from spatial-parameters.md; it must not dominate or resize the environment.
Constraints: do not move call buttons, do not narrow doors, do not redesign the environment, do not add extra media.
```

## 7. Final Check

Before returning an image:

- The medium matches the user's term.
- The complete media frame is visible unless the user requested a close crop.
- Screen/frame geometry is plausible.
- Environment geometry was accepted before media insertion.
- Environment scale is plausible next to elevator doors, panels, call buttons, handrails, or people.
- Camera logic is physically coherent.
- Hall call buttons and cabin controls are visible only when the selected camera can realistically see them.
- Call buttons remain at adult-reachable height and are not displaced by media.
- Elevator cabins read as compact cabins, not long hallways.
- LCD lower strip, smart-screen black bezel, or poster-frame glass appears when relevant.
- No important visual content is cut off.

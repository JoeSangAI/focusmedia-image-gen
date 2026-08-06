# Visual Rules

Use these rules when generating Focus Media demo images, environment images, or images with people.

## Core Rule

Keep the media hardware realistic first, then place the supplied poster inside it. The final image should look like a real Focus Media installation photo, not a generic billboard mockup.

## Media Appearance

- LCD / 电梯电视 / 楼宇（LCD）: wide landscape main screen, usually white or silver frame, with a lower strip display. The middle band carries a small Focus Media/分众传媒 mark and rows of sensor/speaker dots. Common locations are elevator waiting halls and walls between or beside elevator doors. The call panel often sits below the screen.
- 智能屏: slim black portrait device, high-contrast illuminated screen, glossy black bezel, small top sensor/camera dots, small Focus Media/分众传媒 mark on the lower-left bezel, phone number on the lower-right bezel. Angled views should show a thin black side depth.
- 海报 / 框架 / 海报框架: portrait print behind glass, visible reflections, white/aluminum rounded frame lip for poster 3.0, small serial number near the top-right, small Focus Media/分众传媒 sticker near the bottom-left. It often appears inside elevator cabins or close to elevator doors.

## Scale and Placement

- Keep media mounted on walls, elevator panels, or elevator interiors; avoid freestanding outdoor signage unless the user explicitly asks for a non-standard concept.
- Use elevator doors, call buttons, handrails, and human bodies as scale anchors.
- For prompt-only generation, apply `references/spatial-parameters.md` before writing the final prompt. Define the elevator doorway proportions first, then media size and mounting height.
- Smart screens are narrower than poster frames. Do not enlarge a smart screen until it looks like a full poster board.
- Poster frames are taller and wider than smart screens, but still wall-mounted inside a constrained elevator or lobby environment.
- LCD screens are wide and relatively shallow; do not make them square or vertical.
- LCD units belong in elevator halls/corridors by default. Do not place a standard LCD inside the elevator cabin.
- In elevator cabin poster scenes, respect cabin topology: poster frames belong on the back wall and side walls, not on the door wall. The main elevator button panel belongs near the door side of the cabin.
- Apply camera visibility, not just object placement. From outside the elevator looking inward, the door-side button panel is behind the camera or hidden by the near side wall, so the image should show no elevator buttons at all.

## Lighting and Material

- Match screen brightness to the scene. LCD and smart screens should emit light; poster frames should look printed behind reflective glass.
- Add subtle glare, reflections, or glass streaks only when they support realism. Keep the supplied poster legible.
- In elevator interiors, use stainless steel reflections and ceiling light strips; in lobby scenes, use marble, stone, wood veneer, brushed metal, and elevator indicators.

## People

- Use people to show scale and attention, not to hide the media.
- Keep faces, bodies, and sight lines plausible for an elevator lobby or elevator interior.
- Do not let people occlude key poster text unless the user asks for a candid or crowded scene.
- Add people after the base environment and media scale are already acceptable whenever possible.
- When adding people, preserve the existing media size, call-button/control-panel position, wall seams, doors, handrails, floor, ceiling, and camera perspective.

## Failure Modes To Avoid

- Do not redraw the supplied poster text with hallucinated words.
- Do not change the media type because the poster aspect ratio is inconvenient.
- Do not stretch a portrait poster into a landscape LCD, or a landscape poster into a vertical smart screen.
- Do not turn the installation into a giant wall mural, mall lightbox, outdoor billboard, bus stop panel, or retail shelf display.
- Do not make the elevator cabin or hallway physically too large for the media.
- Do not make elevator doors narrow or oddly placed to accommodate the screen/frame.
- Treat the LCD three-zone silhouette as a hard environment-image gate, including at distance: a separate 16:9 upper screen, an opaque white middle hardware/sensor band, and a separate 16:3 lower strip. Any merged single advertising surface, square single screen, missing middle band, or missing lower strip is an automatic rejection.
- Do not place poster frames on the elevator door wall or put the main cabin button panel on the far back wall.
- Do not reveal hidden object faces just because they are semantically important. If the camera cannot see the screen, button panel, or poster surface from that side, either omit it or change the camera angle.
- Do not allow print-production artifacts in mockups: no dashed/dotted guide lines, crop marks, measuring ticks, safety boxes, or dimension annotations on poster frames or screen content.
- For LCD lower strips, do not let the final output or final crop cut off any important visual element, including text, products, icons, logos, QR-like marks, faces, or subject matter. This is a geometry and completeness rule only; do not force a specific creative layout or product style.

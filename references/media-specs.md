# Focus Media Media Specs

Use these specs to keep the supplied poster or creative mapped to the correct physical media shape. Do not stretch artwork non-uniformly.

## Terminology

- 电梯电视 = LCD = 楼宇（LCD）
- 海报 = 框架 = 海报框架
- 智能屏 = 智能屏

## Canonical Source

Use the Focus Media design guide dimensions summarized in this file as the canonical public source for:

- physical device dimensions
- screen or poster creative area dimensions
- required source artwork pixel dimensions
- LCD upper/lower screen split

Remote reference photos are useful for frame material, logo placement, reflections, and real-world wear, but do not override the design guide's sizes.

## Mockup Artboard Sizes

Use these sizes before image generation for demo/mockup work. These are the visible screen/poster surfaces the Skill should generate inside the media frame.

| Medium | Artboard / source artwork | Format notes | Use this for |
|---|---:|---|---|
| 32-inch smart screen | 1080 x 1920 px | portrait | full-screen creative |
| 32-inch LCD main screen | 1920 x 1080 px | landscape 16:9 | main video/image creative |
| 32-inch LCD lower strip | 1920 x 360 px | landscape strip | bottom strip image creative |
| 32-inch LCD full-video special mode | 1920 x 1440 px | landscape combined video | only when upper and lower screens play one combined video |
| Elevator poster 3.0 mockup artwork | ratio `534:734` | portrait | visible framed poster surface |
| Elevator poster 1.0 mockup artwork | ratio `380:530` | portrait | visible framed poster surface |

Do not infer design artboard sizes from generated images, screenshots, or environmental photos. Those can contain perspective, lens distortion, cropping, and model drift.

For mockups, do not add bleed, crop marks, safe-area guides, dimension labels, or inner safety borders to the creative. Those belong to print production files, not demo images.

## Production Print Sizes

Use this only when Joe explicitly asks for a real print production file.

| Medium | Finished artwork | Visible area | Print spec |
|---|---:|---:|---|
| Elevator poster 3.0 | 590 x 790 mm | 534 x 734 mm | JPG, CMYK, 300 DPI |
| Elevator poster 1.0 | 424 x 570 mm | 380 x 530 mm | JPG, CMYK, 300 DPI |

For production print only: extend the background to the finished size and keep critical text inside the visible area.

## Smart Screens

| Medium | Device shape | Device size | Depth | Creative area | Resolution | Install position | Notes |
|---|---:|---:|---:|---:|---:|---|---|
| 32-inch smart screen | Tall black single screen | 452.3 x 757.8 mm | 39.3 mm | 391.9 x 697.4 mm | 1080 x 1920 | elevator exterior | Standard 9:16 portrait screen. |

## LCD / Elevator TV / Building LCD

| Medium | Device shape | Device size | Depth | Creative area | Resolution | Install position | Notes |
|---|---:|---:|---:|---:|---:|---|---|
| 32-inch LCD | Wide white/silver housing with main screen and lower strip screen | 764.5 x 658.7 mm | 26.5 mm | main: 697.4 x 391.85 mm; strip: 698.8 x 130.2 mm | main: 1920 x 1080; strip: 1920 x 360; special full video: 1920 x 1440 | elevator waiting hall | Main screen is landscape 16:9. The lower strip is short and wide, not a second full screen. |

## Elevator Poster Frames

| Medium | Frame appearance | Finished artwork | Visible area | Print spec | Install position | Notes |
|---|---|---:|---:|---|---|---|
| Elevator poster 3.0 | White/aluminum edge with crystal ultra-white tempered glass | 590 x 790 mm | 534 x 734 mm | JPG, CMYK, 300 DPI, framed portrait | elevator interior | For mockups, generate only the visible framed poster surface; use finished size only for print production. |
| Elevator poster 1.0 | Gold/beige Corian-style thick frame | 424 x 570 mm | 380 x 530 mm | JPG, CMYK, 300 DPI, framed portrait | elevator interior | For mockups, generate only the visible framed poster surface; use finished size only for print production. |

## Aspect Handling

- Map supplied artwork by aspect ratio first, then by medium name.
- Use `cover` only when edge cropping is acceptable and no critical text is lost.
- Use `contain` only when the user accepts letterboxing or when preserving the whole supplied poster is more important than filling the surface.
- Never scale x/y independently to force a fit.
- For poster-frame mockups, preserve the frame lip and glass border; the supplied poster should fill the visible frame opening, not include print bleed or safety guides, and not cover the outer frame.
- For LCD, keep the main 16:9 screen and lower strip separated unless the user explicitly requests the 1920 x 1440 full-video format.

# LCD Lower-Strip And Framed TVC Workflow

Use this reference when an LCD lower-strip creative is missing, the model cannot return an ultra-wide canvas reliably, or a supplied TVC must be converted into a framed Focus Media LCD demo.

## 1. Lower Strip: Double Protected Band

Treat model canvas size as a transport format, not as the target artwork size. Control the usable area with two nested rectangles:

1. **Outer extraction band**: an exact integer `16:3` rectangle. This is the only region retained after generation.
2. **Inner content-safe band**: a narrower rectangle inside the extraction band. Keep every logo, product, person, headline, QR-like element, and meaningful edge fully inside it.

The outer band guarantees output geometry. The inner band protects content from the final crop and from small model drift.

### Create The Guide And Mask

Use a standard landscape canvas such as `1536 x 1024`. The resulting exact band is `1536 x 288`, significantly narrower than the previously observed `1672 x 362` band.

```bash
scripts/prepare_lcd_lower_band.py template \
  --canvas 1536x1024 \
  --guide lower-band-guide.png \
  --mask lower-band-mask.png \
  --manifest lower-band-manifest.json
```

The guide uses striped dark areas for forbidden space, yellow for the exact extraction band, and a light outline for the inner safe band. The RGBA mask is opaque outside the band and transparent inside it.

### Render Through The Standard Image Route

Follow the global `image-routing` Skill. Upload the guide, mask when supported, and the approved brand/product/IP references. Keep the same prompt and reference order when routing from ChatGPT web to Comet.

Use this core instruction:

```text
Image 1 is a geometry guide, not visible final artwork. Modify only the exact yellow/transparent 16:3 extraction band. The striped areas above and below are forbidden and must remain unchanged, with absolutely no advertising content, subjects, logos, text, products, faces, scenery, or effects extending into them. Build one continuous composition across the full extraction band. Keep every important element fully inside the narrower inner safe band with clear padding. Do not reproduce guide lines, borders, stripes, annotations, or mask colors as final artwork.
```

When the web route cannot attach a separate mask, upload the guide as the edit target and keep the same spatial instruction. Reject results that place meaningful content outside the exact band or press critical content against its edges.

### Validate And Crop

Returned pixel dimensions are untrusted. If a visible generated band can be measured, validate it before accepting the result:

```bash
scripts/prepare_lcd_lower_band.py validate-band \
  --input returned.png \
  --band-box left,top,right,bottom \
  --report band-validation.json
```

A full-width `1672 x 362` band is `4.6188:1` and must fail. Do not treat it as “close enough” and do not repair it by adding unrelated left/right content.

Crop the largest centered integer `16:3` rectangle and normalize it to the official output:

```bash
scripts/prepare_lcd_lower_band.py crop \
  --input returned.png \
  --output lower-1920x360.png \
  --report lower-crop-report.json
```

For a `1672 x 941` return, the exact crop is `1664 x 312`, centered at `[4, 314, 1668, 626]`, then uniformly scaled to `1920 x 360`.

Regenerate from the original guide when content crosses the inner safe band. Side extension is an explicit last resort only after Joe accepts the continuity tradeoff; it is not the default recovery path.

## 2. Framed LCD TVC: Minimal-Change Composition

Use the formal `assets/framed-demo-standards/lcd-32-standard.png` frame. The workflow changes only the upper active screen and lower active strip; the white housing, center logo/sensor band, wall, crop, and all other pixels remain fixed.

### Inputs

- one authoritative source TVC variant, validated as `4:3` or `16:9`
- one approved `16:9` replacement tail frame
- one exact `16:3` lower-strip creative
- one frame-aligned switch point
- the source audio stream

For a `4:3` full-video source, take the top-aligned `16:9` region for the upper screen. For a `16:9` source, use the full picture. Reject ambiguous ratios rather than guessing the variant.

### Compose

```bash
scripts/compose_lcd_tvc_demo.py \
  --source source-4by3.mp4 \
  --tail approved-tail-1920x1080.png \
  --lower approved-lower-1920x360.png \
  --switch-time 14.12 \
  --output framed-demo.mp4 \
  --contact-sheet framed-demo-contact-sheet.png \
  --report framed-demo-report.json
```

Use `--switch-frame` when the creative decision is already frame-based. A time value must land on a whole source frame; for example, `14.12s` at `25fps` is frame `353`.

The lower strip remains static for the entire video. The upper screen preserves the original program until the exact switch frame, then holds the approved tail. The source audio is stream-copied when its codec is approved for MP4; otherwise it receives one controlled AAC transcode, recorded in the report.

### Required QA

Verify the exact exported MP4, not only the command or intermediate images:

- formal frame is complete and unchanged outside the two active display regions
- output size is the template size, normally `1920 x 1080`
- frame rate and frame count match the source
- upper-screen source crop matches the declared `4:3` or `16:9` variant
- tail begins on the reported switch frame
- lower strip is present and visually unchanged at opening, midpoint, pre-switch, switch, post-switch, and final frame
- audio preservation mode is explicitly `stream_copy` or `single_controlled_aac_transcode`
- contact sheet shows the expected reading order and contains no flash frame at the switch

Treat technical acceptance and business approval as separate states. A technically valid demo remains an internal candidate until the client or authorized owner confirms it.

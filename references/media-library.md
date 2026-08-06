# Remote Media Reference Library

Use `references/remote-manifest.json` as the lightweight public reference library for Focus Media media appearance, placement, scale, environment style, and people scenes.

The public GitHub repository does not include the raw internal photo library. It includes 16 curated thumbnail references and a manifest for 156 visually screened, read-only remote reference images hosted on Joe's Aliyun server: 58 default primary references and 98 scenario-specific references. Twenty-seven images are deliberately excluded because they are mixed-media examples, visibly weak media presentations, or environments that fall below the intended premium spatial standard.

## Security Model

- Users download reference images with HTTP GET only.
- There is no upload endpoint, delete endpoint, WebDAV, API token, or server write workflow.
- Downloaded files are cached locally under `.focusmedia-cache/references/`.
- The server-side static directory is read-only to the web server.

## Manifest Fields

`references/remote-manifest.json` includes:

- `base_url`: remote static asset root
- `references`: real-reference images for LCD, smart screen, poster frames, environments, and people scale
- `demos`: example images used by the README
- `id`: stable reference id
- `tags`: searchable labels, such as `lcd`, `smart-screen`, `poster-frame`, `elevator-hall`, `people`
- `curation_tier`: `primary` for default premium output, or `scenario` for purpose-specific composition
- `recommended_for`: explicit usage labels such as `wide-impact`, `people-scale`, `multi-frame-poster-coverage`, and `elevator-interior`
- `source_edit_grade`: original display-replacement confidence; it does not judge whether a photo is visually useful for a scene
- `url`: direct read-only image URL
- `sha256`: checksum used by `scripts/fetch_reference_images.py`

## Selection Rules

- Start with the default `primary` tier. It contains the cleanest, most premium hardware-focused references.
- Use `--tier scenario` together with `--use-case` when the brief needs a particular compositional effect. Wide-angle, people-scale and multi-frame images are intentionally retained for these cases.
- For close hardware or scale references, start with no-people front references unless the user asks for people.
- For people-scale examples, add `--use-case people-scale`.
- For LCD, verify the selected photo includes wide landscape LCD logic and, when relevant, a lower strip.
- For smart screen, verify the selected photo is portrait black hardware, not a poster frame.
- For poster frame, verify the selected photo has glass/frame boundaries and is not a landscape LCD.

Use the selector script for the first pass. It can filter by medium, scene, angle, people, selection tier, and explicit use case:

```bash
scripts/select_media_references.py --media lcd --scene elevator-hall --limit 4
scripts/select_media_references.py --media lcd --tier scenario --use-case wide-impact --limit 3
scripts/select_media_references.py --media smart --tier scenario --use-case people-scale --limit 2
scripts/select_media_references.py --media poster --scene elevator-inside --limit 4
scripts/select_media_references.py --media poster --tier scenario --use-case multi-frame-poster-coverage --limit 3
```

Download only the references needed for the current task:

```bash
scripts/fetch_reference_images.py --media poster --scene elevator-inside --limit 2
scripts/fetch_reference_images.py --media smart --tier scenario --use-case people-scale --limit 1
scripts/fetch_reference_images.py --id poster_02_elevator_gallery
```

Then open 1-3 candidates visually. Do not choose by filename alone when camera angle, wall surface, people scale, or media type could affect the output.

For environment generation, prefer references with:

- normal elevator-door geometry and visible wall seams
- reachable call-button/control-panel position
- enough clean wall area for the requested medium
- camera setup that matches the desired final scene
- no confusing wrong media type near the intended installation surface

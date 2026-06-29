# Transparent Asset Checklist

Use this checklist for every transparent icon, brand asset, subject/product render, decorative mark, thumbnail, data visual, or waveform asset.

## Before Generation

- Define the asset id, use case, target approximate size, and whether it is reusable or page-local.
- Decide whether it needs separated layers: subject, shadow, sparkle, orbit, foreground, background.
- For any asset with shadow/glow, identify the approved reference shadow profile before generation: color tint, opacity, blur/softness, spread, direction, contact shape, and whether the shadow should be baked into the subject or separated.
- Use the same locked visual style as the UI screens.
- Avoid generating UI cards, text labels, or backgrounds as part of the asset unless they are intentionally image content.

## Chroma-Key Prompt Requirements

- Background is one selected flat solid matte color. Do not default to green; choose per asset from `#00FF00`, `#FF00FF`, `#0066FF`, `#FFFF00`, `#FF0000`, or `#00FFFF`. Do not use black, white, gray, off-white, or near-black.
- No floor plane, gradient, reflection, texture, shadow, or lighting variation on the background.
- Subject has enough padding and no clipped edges.
- Subject does not contain the selected matte color when avoidable. If every candidate conflicts, the chosen matte has the lowest conflict score and the asset is marked `matteRisk: high`.
- No text, watermark, screenshot border, or accidental UI.
- Shadows/glows must match the approved reference shadow profile. Do not use a generic contact shadow, floor shadow, or blob-like dark oval unless that is exactly what the approved UI shows.


## Matte Color Selection

Before chroma-key generation, select a matte color per asset or per compatible asset group:

1. Candidate colors: `#00FF00`, `#FF00FF`, `#0066FF`, `#FFFF00`, `#FF0000`, `#00FFFF`.
2. Excluded colors: black, white, gray, off-white, near-black, and any low-chroma matte.
3. Score every candidate from 0 to 5:
   - `0`: no visible conflict.
   - `1`: tiny interior similarity, far from edges.
   - `2`: small non-edge conflict, likely safe with despill.
   - `3`: moderate conflict or near-edge similarity; high-risk review.
   - `4`: strong conflict on subject fill, stroke, shadow, glow, or antialias edge.
   - `5`: candidate is part of the asset identity; avoid unless all candidates are worse.
4. Choose the lowest score. If tied, choose the candidate farthest from outer-edge and semi-transparent colors.
5. If all candidates score `3+`, generate the asset individually when possible, mark `matteRisk: high`, and require contact-sheet approval before active manifest promotion.
6. Record the decision in manifest/audit metadata.
## Alpha Validation

After background removal or transparent generation, check:

- File has an alpha channel.
- Corners are transparent.
- No matte-colored fringe remains, including green, magenta, blue, yellow, red, or cyan fringe depending on the selected matte.
- No stray pixels outside the subject bounds.
- Edge anti-aliasing looks clean at 1x and 2x, with no eaten same-color subject pixels, holes, or damaged shadows/glows from matte removal.
- Asset is not cropped too tight.
- Shadow/glow is absent, intentionally baked in, or intentionally separated. Require `shadowHandling`, `shadowProfileRef`, and `shadowQuality` only when the asset actually includes shadow, glow, reflection, soft-edge effects, or separated shadow layers; clean no-shadow assets may omit them or record `shadowHandling: none`.
- Shadow/glow matches the approved reference shadow profile and is not too dark, too opaque, too blurry, too sharp, wrong tinted, clipped, or merged into an indistinct blob.
- Transparent safety padding passes the measured alpha-bbox rule below.

## Transparent Safety Padding

Measure padding from the alpha bounding box to the PNG canvas edge after background removal:

```text
leftPadding = alphaBBox.left
topPadding = alphaBBox.top
rightPadding = canvasWidth - alphaBBox.right
bottomPadding = canvasHeight - alphaBBox.bottom
```

Minimum padding:

- Simple small icons and tab states: `max(12px @2x, 8% of alpha-bbox long edge)`.
- 3D icons, mascots, illustrations, decorations, or assets with shadow/glow: `max(24px @2x, 10% of alpha-bbox long edge)`.
- Wide UI skins/buttons/cards/tabs: horizontal `max(24px @2x, 4% of alpha-bbox width)`, vertical `max(12px @2x, 4% of alpha-bbox height)`, or vertical `max(24px @2x, 6% of alpha-bbox height)` when shadow/glow is present.

Scale pixel constants by delivery scale: `@1x` uses 50%, `@3x` uses 150%.

Fail the asset if any side is below the required padding. Re-pad only when the source asset is complete and unclipped. Regenerate when the source already cuts off subject pixels, shadow, glow, or edge antialiasing.

## Naming And Manifest

Every accepted asset needs:

- stable filename
- category
- status: `promoted`, `candidate`, `page-local`, or `rejected`
- intended use
- dimensions
- alpha true/false
- source prompt or source image
- validation notes

## Common Failures

- Generated subject/product/character asset becomes malformed, frightening, off-brand, or unusable.
- Icon style differs from the component library.
- Navigation icon is generated per page instead of using the shared source.
- Transparent PNG keeps a faint square background or matte-colored halo/fringe.
- Shadow is baked into a cutout that later needs separate animation.
- Shadow profile does not match the approved UI reference, such as a soft reference shadow becoming a dark blob, or a reference contact shadow being clipped off.
- Transparent safety padding fails on any side, especially when right/bottom subject edges or contact shadows touch the canvas boundary.
- Asset crop includes neighboring labels, board backgrounds, other asset edges, unrelated subject/body parts, or card backgrounds.
- Filename says waveform/orbit/sparkle but the image contains an unrelated body part, thumbnail, neighboring tile, or another subject.

- Chroma-key matte color was chosen without `candidateMatteScores`, `matteConflictScore`, `matteRisk`, and `matteSelectionReason`.
- One matte color was forced across a mixed-color sheet even though several assets visibly conflict with it.

If any of these happen, regenerate or demote the asset before handoff.


## Promotion Gate

Do not promote an asset to active manifests until its per-page contact sheet has been visually inspected. Passing alpha validation is not enough. Do not promote full-screen UI screenshot crops except approved avatar/photo/example-thumbnail bitmap content that passes semantic and pollution checks.

For each active page-local asset, confirm:

- filename/id matches the visible subject;
- no neighboring asset or UI pollution appears;
- subject is not cropped off or touching the canvas edge;
- measured transparent safety padding passes for the asset class;
- shadow/glow handling and quality match the approved UI reference when the asset actually has shadow/glow/soft-edge effects; no-shadow assets must not be penalized for missing shadow fields;
- the asset belongs in bitmap form rather than native/vector UI;
- `asset-quality-audit.json` records `visualInspectionPassed: true`, `semanticMatch: true`, and a contact-sheet path.


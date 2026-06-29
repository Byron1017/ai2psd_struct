# Style And Asset Lock

Use this reference when a UI package must extend an already approved visual direction or when transparent assets are generated from sheets.

## Approved Style Authority

Classify the job before generation:

- `approved-reference`: the user has accepted prior UI images, Figma pages, brand assets, component libraries, visual specs, or reference screens.
- `new-exploration`: the user explicitly wants a new direction or no approved reference exists.

In `approved-reference` mode, generation must inherit from the approved source. Do not create a new palette, new brand/hero asset style, new component density, new navigation style, or new overall mood from a text-only summary. If the approved source is not available, ask for it.

Record in `package-config.json`:

```json
{
  "styleAuthority": "approved-reference",
  "approvedReferenceSet": [
    "path/to/approved-screen.png",
    "path/to/approved-logo.png",
    "path/to/approved-hero-asset.png"
  ],
  "styleDriftPolicy": "reject-unless-user-approved"
}
```

## Foundation Board Rule

When approved references exist, foundation boards are not an opportunity to redesign. They should document or extend the approved style.

Fail the board if:

- palette shifts materially from approved UI;
- brand, logo, hero, product, or subject render style changes;
- navigation, tab, card, or button style changes;
- background treatment becomes materially different from approved references, including unintended changes in color temperature, contrast, density, illustration level, or overall mood;
- typography scale and page density drift.

## Pixel-Exact Asset Lock

When pixel-exact asset mode is active, exact page appearance is the source of truth. Generate redundant page-local assets before sharing assets across pages.

Do not treat a visually similar asset as coverage for the current page. Similarity is not equality. A shared asset may replace a page-local requirement only after explicit manifest reference, approved-shared status, and current-screen QA.

Generate assets for visual skins, not only for illustrations. Buttons, tag pills, card skins, bottom tabs, selected/unselected icons, title icons, badges, and hero/section backgrounds need assets when they include gradient, glow, shadow, embedded icon, texture, or complex styling.

For 3D, skeuomorphic, cute/game, or glow-heavy assets, lock the shadow profile from the approved UI reference before generating or accepting assets. The profile includes color tint, opacity, blur/softness, spread, direction, contact shape, and whether the shadow is attached to the subject or separately placeable. Matching the profile is required; do not replace a reference-specific shadow with a generic oval, generic floor shadow, or generic soft glow.

## Asset Sheet Crop Rule

Preferred order for clean assets:

1. Dedicated one-asset generation for important assets.
2. A page-local asset sheet with clear grid/tile boundaries.
3. Connected-component extraction from a sheet, followed by visual inspection.
4. Manual crop only after opening the source sheet and confirming exact boundaries.

Never promote guessed-coordinate crops. Never promote a crop only because it has alpha.

Full-screen UI screenshot crops are not an asset-generation strategy. Keep them rejected/reference-only unless the crop is approved avatar/photo/example-thumbnail bitmap content and passes the screenshot-crop exception. Generate reusable artwork, decorative marks, characters, primary subject renders, icons, and empty-state art as dedicated transparent assets or clean asset-sheet tiles instead.

## Per-Page Contact Sheet Gate

This gate applies after every final image that produces active assets. For shared assets from an Asset Library board, create a shared contact sheet. For UI screens, create a page-local contact sheet. In pixel-exact mode, include component-skin and component-state assets in the page-local contact sheet unless they are promoted to shared-approved after QA.

After cutting assets for `Pxx`, create:

```text
05-contact-sheets/page-local/Pxx-assets-contact-sheet.png
```

The contact sheet must show every active page-local asset on checkerboard with filename/id labels. Inspect it before writing active references to `screen-map.json` or `page-asset-audit.json`.

Reject or regenerate assets that show:

- neighboring asset edges;
- clipped subject edge, missing right/bottom pixels, or clipped shadow/glow;
- unrelated subject/body parts from another tile;
- thumbnail/card background not intended as image content;
- black/white/green rectangular pollution;
- unintended UI text, card, button, chip, list row, nav, or tab content; intended button/tag/tab/card skins are allowed only when the full skin asset is deliberately generated and named as such;
- multiple unrelated subjects;
- subject cropped off or touching the canvas edge;
- transparent safety padding below the measured minimum for the asset class;
- shadow/glow that does not match the approved UI reference profile, including blob-like shadows when the reference shadow is soft/layered;
- visual content not matching filename/intended use.

## Required Quality Metadata

Every active page-local asset in `asset-quality-audit.json` must include the common metadata:

```json
{
  "id": "asset.page.Pxx.example.v1",
  "filename": "03-transparent-assets/page-local/Pxx/Pxx-example@2x.png",
  "result": "approved-clean-or-acceptable-thumbnail",
  "visualInspectionPassed": true,
  "semanticMatch": true,
  "contactSheet": "05-contact-sheets/page-local/Pxx-assets-contact-sheet.png",
  "transparentPadding": { "left": 32, "top": 32, "right": 32, "bottom": 32, "required": 24, "passed": true },
  "reason": "Dedicated clean asset; no UI or neighboring asset contamination."
}
```

Only when the asset actually contains shadow, glow, reflection, complex soft-edge effects, or a separated shadow layer, also include:

```json
{
  "shadowProfileRef": "02-screens/Pxx-reference.png#asset-region",
  "shadowHandling": "baked-in | separated-shadow | native-figma-effect",
  "shadowQuality": "matches-reference"
}
```

For clean no-shadow assets, omit those shadow fields or record only `shadowHandling: none` when the no-shadow decision needs to be explicit. If required fields cannot honestly be set, the asset must be `rejected-not-for-figma-source` or `needs-dedicated-generation` and must not be referenced by active screen/audit maps.

# Figma Handoff

Use this handoff when passing a generated package to `ai2figma-struct`.

## Handoff Summary Template

```text
Use $ai2figma-struct to rebuild this package into editable Figma source.
Package root: <absolute path>
Target Figma page/version: <name>
Target screen size: <width>x<height>
Foundation boards provided:
- Visual Spec: <path or none>
- Component Library: <path or none>
- Asset Library: <path or none>
Manifests:
- asset-map: <path>
- screen-map: <path>
Screens: <count and paths>
Quality target: <development-ready / high-fidelity / pixel-critical>
Special notes: <known risks, accepted old pages, exact-match requirements>
```

## Consumption Rules For ai2figma-struct

- Development handoff is the primary purpose. Pixel closeness must be achieved with editable/native structure plus atomic image assets, not with large UI bitmap slices.
- If clean foundation boards exist, rebuild/import those first.
- If a component library exists, use it for shared UI such as bottom tab, top nav, buttons, chips, inputs, cards, and selectors.
- If an asset library exists, use it for brand characters, subject/product renders, thumbnails, waveforms, logos, and decorative marks.
- If the manifest marks an asset as `candidate` or `page-local`, do not force global reuse.
- If a referenced asset is missing or invalid, route it through the repair pipeline: reprocess package sources, use the source ROI when allowed, generate a replacement with `imagegen`, then continue with the closest atomic/native result after the retry limit. Do not stop unless the user asked for audit-only work or the required tools are unavailable.
- If the screen reference conflicts with the library, the original/high-fidelity screen image is the visual source of truth, but log the conflict.
- If a manifest asset is a whole card, whole list, whole tab bar, whole hero/app-shell region, or mixed text/control bitmap, treat it as `invalid-ui-region-slice`: use it only as reference, rebuild the UI natively, and repair the missing atomic assets.

## What Not To Handoff As Assets

Do not ask Figma reconstruction to use large bitmap images for:

- buttons
- cards
- labels
- text
- inputs
- top nav
- bottom tab shells
- status bars
- chips
- icon containers

Those are native rebuild targets unless a single component skin/state is visually non-native and exported as an atomic development asset. The generated package may include button skins, card skins, navigation containers, or tab item states only when each file is a standalone atomic unit with explicit ownership and placement. Do not hand off page-level bitmap slices.

## Defect Language

Use precise defect notes:

- `missing-asset`: manifest references a file that does not exist.
- `unmapped-visual`: screen contains a complex visual not listed in asset-map.
- `style-drift`: screen and foundation board disagree.
- `alpha-pollution`: asset contains background pixels.
- `bad-crop`: asset includes neighboring content or is clipped.
- `invalid-ui-region-slice`: asset is too large or mixed for development handoff; rebuild natively and repair atomic assets.
- `component-drift`: shared component differs across screens.
- `text-risk`: generated screen text is inaccurate and must be OCR/recreated manually.


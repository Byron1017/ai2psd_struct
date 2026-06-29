# Prompt Patterns

Use these patterns with the `imagegen` skill. Replace all size placeholders with the negotiated values from `package-config.json`; if values or approved references are unknown, ask before generation.

## Approved Reference Prompt Add-On

Use this add-on whenever `package-config.json` has `styleAuthority: approved-reference`.

```text
Approved reference mode: extend the existing visual system, do not create a new style.
Approved references: <reference file names or image roles>.
Preserve the approved palette, typography feel, spacing density, radius, shadow language, icon style, brand/hero asset style, page background, navigation, and component treatment.
Preserve the approved shadow profile exactly: color tint, opacity, blur/softness, spread, direction, contact shape, and how shadows sit under each subject. Do not invent a new shadow style.
Do not reinterpret descriptive words into a new visual direction. If the new output visibly drifts from the approved references, reject and regenerate.
```

## Style Lock Prompt

```text
Create a locked visual direction for <product or interface name>.
Platform: <platform>.
Screen size: <logicalWidth> x <logicalHeight> px logical, deliver final reference at <deliveryWidth> x <deliveryHeight> px (@<scale>x).
Style authority: <new-exploration or approved-reference>.
Approved references: <list references, if any>.
Style: <project-specific style words supplied by user or inferred from approved references>.
Palette: <project-specific palette or extracted approved-reference palette>.
Typography: <project-specific typography direction or extracted approved-reference typography>.
Shapes/components: <radii, cards, buttons, nav, tabs, density, shadows>.
Brand/subject assets: <logo, brand character, hero asset, product render, illustration, photo, or domain-specific visual style>.
Shared UI: consistent status/nav bars, tab/navigation, buttons, cards, chips, inputs, selectors, result cards, record cards, states, and modals as applicable.
Avoid: style drift from approved references, inconsistent icons, malformed subject assets, text overflow, cropped UI, screenshot borders, watermark, extra canvas.
```

## Full Screen UI Reference Prompt

```text
Generate one complete high-fidelity UI reference screen.
Page: <page number and name>.
Target: <platform>, <logicalWidth> x <logicalHeight> px logical; deliver final image at <deliveryWidth> x <deliveryHeight> px (@<scale>x).
Style authority: <new-exploration or approved-reference>.
Approved references: <list references, if any>.
Use the locked visual system exactly: same palette, typography scale, card radius, button style, navigation/tab style, icon style, and brand/subject asset style.
Include all visible UI text exactly as specified.
Use approved assets where named: <asset ids>.
Native rebuild targets: text, buttons, cards, inputs, chips, nav, tabs, list rows, dividers, payment cards, modal shells, and simple component containers.
Bitmap/asset targets: photos, product/subject renders, brand/hero art, complex thumbnails, waveforms, decorative marks, and complex illustrations.
No cropping, no extra canvas, no duplicated navigation, no malformed subject assets, no text overflow, no watermark.
```

## Visual Spec Board Prompt

```text
Create a clean visual-spec board for this UI set.
Canvas size must be <foundationBoardWidth> x <foundationBoardHeight> px, usually landscape unless the project requires another board shape.
Style authority: <new-exploration or approved-reference>.
Approved references: <list references, if any>.
Document actual design tokens used by the screens: colors, typography, spacing, radii, shadows, icon style, page size, safe areas, navigation rules, card/button/input rules, and state rules.
If approved references exist, document and extend them; do not invent a new style.
Use readable labels and measured examples.
```

## Component Library Board Prompt

```text
Create a clean component-library board for this UI set.
Canvas size must be <foundationBoardWidth> x <foundationBoardHeight> px, usually landscape unless the project requires another board shape.
Include standard native UI examples needed by this project: status bar if applicable, top nav, bottom tab or side nav, primary button, secondary button, icon button, chip, segmented control, input, upload/drop zone, selector, template card, result card, record card, list row, modal/bottom sheet, toast, empty/success/failure/loading states.
All examples must use the same visual tokens as the approved references or locked style.
Do not include inconsistent variants or decorative one-offs.
```

## Asset Library Board Prompt

```text
Create a clean asset-library board for the UI set.
Canvas size must be <foundationBoardWidth> x <foundationBoardHeight> px, usually landscape unless the project requires another board shape.
Include approved non-native visual assets only: logo/brand mark if needed, brand/hero asset, subject/product renders, photo or wallpaper thumbnails, waveform/data visuals, decorative marks, empty-state illustrations, and page-local image candidates.
Label each asset with filename, category, usage, and status: promoted, candidate, page-local, rejected.
Use clean boundaries and enough padding for precise extraction.
Do not include simple native buttons, cards, nav bars, tabs, list rows, chips, inputs, or text UI as bitmap assets. Exception: in pixel-exact mode, include any visually non-native component skin or required state asset, such as gradient buttons, decorated cards, tab/nav item states, chips with special treatment, badges, and locked/selected/pressed states.
```

## Transparent Asset Prompt

```text
Create the asset only, centered with measured transparent safety padding, on a transparent canvas or a selected perfectly flat solid chroma-key matte canvas for background removal. Do not default to #00FF00; choose the matte color per asset using the Matte Color Selection Gate. Do not use a full-screen UI canvas for a single asset.
Asset: <asset name and intended use>.
Development unit: generate exactly one atomic reusable unit that can be placed in Figma or exported to development without being cut again. Do not include unrelated text, neighboring controls, card/list/nav regions, page backgrounds, or multiple independent UI elements.
Style authority: <new-exploration or approved-reference>.
Approved references: <list references, if any>.
Style must match the locked UI visual system exactly.
Shadow profile: match the approved reference exactly if the asset has shadow/glow/contact shadow. Match color tint, opacity, blur/softness, spread, direction, and contact shape. Do not turn a soft contact shadow into a solid blob. If the reference shadow is broad or placement-sensitive, generate subject and shadow as separate assets.
Transparent safety padding after alpha: simple icons need max(12px @2x, 8% of alpha-bbox long edge); 3D/mascot/illustration/shadow/glow assets need max(24px @2x, 10% of alpha-bbox long edge); wide UI skins need horizontal max(24px @2x, 4% width) and vertical max(12px @2x, 4% height), or vertical max(24px @2x, 6% height) if shadow/glow is present.
No text, no watermark, no UI card, no background scene unless the asset itself is an image thumbnail.
Do not use the selected matte color anywhere in the subject when avoidable. If every allowed matte color conflicts, choose the lowest-conflict matte, mark `matteRisk: high`, and protect outer edges, shadows, glows, and semi-transparent pixels first.
```

For difficult alpha edges such as hair/fur, glass, smoke, glow, translucent material, or reflective subjects, ask before switching to true/native transparency fallback as required by `imagegen`.

## Page-Local Asset Sheet Prompt

Use this after generating each full-screen UI reference. The goal is to create the missing per-page transparent assets and required component coverage, not to redesign the page.

```text
Create a page-local transparent asset sheet for screen <Pxx page name>.
Canvas size must be <assetSheetWidth> x <assetSheetHeight> px or larger, usually landscape unless the assets cannot fit.
Style authority: <new-exploration or approved-reference>.
Approved references: <list references, if any>.
Use the already generated/approved screen as the source of truth for visible content, and use the package-required component registry as the source of truth for common/app-shell components that may be hidden on this page. Generate clean standalone assets instead of screenshot slices.
Recreate as standalone assets only the non-native visual assets that are unique to this page: icons not covered by the shared component library, decorative marks, thumbnails, subject/product images, waveforms, empty-state illustrations, guide illustrations, badges, overlays, component skins, and required state assets.
Do not include simple native text, plain solid containers, or other visually simple editable UI. Do include visually non-native buttons, cards, navigation/tab shells, item icons, chips, badges, and state matrices when they contain gradients, shadows, embedded icons, texture, glow, special highlights, or state-specific styling.
Every tile must be one atomic development asset. Do not create tiles that contain a whole hero section, whole card with unrelated editable content, whole list row group, whole tab bar with multiple labeled items, modal body, or mixed text/control region. Split those into native structure plus standalone skins/icons/states/decorations.
If the package requires per-page redundant assets, include required common/app-shell component assets for this page even when the component is hidden in the current screen. A not-visible audit entry may explain that the component is not placed in the screen, but it must not replace asset generation. Do not omit a package-required navigation or stateful component because it is not visible on this page.
Place each asset in a separate tile with generous padding on a perfectly flat solid selected chroma-key matte background. Do not force one green screen for all assets; split the sheet by matte color or generate critical assets individually when color families conflict.
No labels, no text, no tile borders, no shadows on the green background unless the asset itself explicitly requires a separated shadow layer.
Keep style exactly consistent with the screen and approved foundation boards.
For every asset with shadow/glow, match the approved screen's shadow profile instead of applying a generic shadow. If the source UI uses a soft contact shadow, keep it soft and layered; if the source UI uses a heavy shadow, preserve that only when it matches the source. Do not accept clipped edges or blob-like shadows.
Ensure each tile leaves enough source canvas so final alpha PNG can pass the measured transparent safety padding rule: simple icons max(12px @2x, 8% long edge), 3D/mascot/illustration/shadow assets max(24px @2x, 10% long edge), wide skins as defined in the transparent asset checklist.
```

After generation, remove the chroma-key background, crop each asset, save files under `03-transparent-assets/page-local/Pxx/`, generate a checkerboard contact sheet, write `asset-quality-audit.json`, and update manifests only after visual inspection. Do not accept full-screen UI screenshot crops as production assets unless they pass the screenshot-crop exception.



## Package-Required Component Coverage Prompt

Use this before or alongside a page-local asset sheet when the package has common/app-shell components that may not appear on every page.

```text
Create or update the package-required component coverage for this UI package.
Style authority: <new-exploration or approved-reference>.
Approved references: <screens or crops showing each required common component>.
Required components: <bottom tabs, top nav, side nav, segmented controls, global button skins, common modal shells, badges, locks, ad gates, etc.>.
For each required component, identify: actual item count if applicable, required states, selected/default state, hidden/not-visible pages, container skin rule, and whether per-page redundant copies are required.

Generate missing required component assets with imagegen as clean standalone assets or state-matrix sheets. Do not assume a component is unnecessary just because the current screen hides it. Do not draw or repair component visuals with scripts.
When per-page redundancy is required, generate or duplicate the approved component coverage into the current page-local package and manifest instead of relying on visually similar assets elsewhere. `notVisibleOnThisScreen` is placement metadata only in this mode, not an asset-coverage exemption.
```

Record the result in `package-config.json.requiredComponentRegistry`, `page-asset-audit.json.packageRequiredComponents`, and `asset-map.json`. Missing required component coverage is a package failure unless explicitly accepted by the user.

## Navigation / Tab State Matrix Asset Sheet Prompt

Use this when a screen contains a bottom tab, top tab, segmented nav, side nav, toolbar nav, or any custom navigation component with visible item states. Do not assume a fixed number of items.

```text
Create a clean imagegen asset sheet for the navigation/component state matrix in screen <Pxx page name>.
Style authority: <new-exploration or approved-reference>.
Approved references: <screen crop or component reference showing the exact nav style>.
Component type: <bottom tab / top tab / segmented nav / side nav / toolbar nav / custom nav>.
Actual item count: <count from the approved screen>.
Items, in visual order: <itemId + meaning + icon/skin description for every item>.
Required states per item: <selected, unselected, disabled, pressed, locked, badge, notification, etc.>.
Container skin: <generate separate container skin / native-simple container / no container>.

Generate every required item-state exactly once in a clear grid. Use the approved reference style exactly: same icon weight, radius, fill/stroke behavior, active/inactive colors, shadow/glow if any, and visual scale. Do not invent a new icon family. Do not add labels unless the labels are intentionally part of the asset skin. Use a selected flat chroma-key matte color that has the lowest conflict score for this state matrix; do not use black, white, gray, off-white, or near-black.

No UI screenshot crop, no full nav screenshot, no text labels unless required, no watermark, no extra icons, no fixed item-count assumption.
```

After generation, crop every item-state into a separate transparent asset and record the full matrix in `page-asset-audit.json` and `asset-map.json`. If the generated sheet visually drifts from the approved reference, reject it and regenerate with `imagegen`; do not fix or redraw the icon geometry with local scripts.


## Matte Color Selection Prompt Add-On

Use this add-on for chroma-key asset generation when true/native transparency is unavailable:

```text
Chroma-key matte selection: choose one matte color before generation from #00FF00, #FF00FF, #0066FF, #FFFF00, #FF0000, #00FFFF. Do not use black, white, gray, off-white, or near-black.
Score each candidate against the asset's visible colors, especially outer edges, anti-aliased pixels, shadows, glows, translucent parts, strokes, and tiny details.
Use the candidate with the lowest conflict score. If all candidates conflict, use the least harmful one, mark matteRisk high, and avoid placing the conflicting color on the asset edge.
The matte background must be one perfectly flat solid color with no gradient, lighting, floor, texture, reflection, or shadow.
```
## Batch Generation Discipline

For any final package that needs synchronized resources, do not generate all screens first. Use one-image-one-asset-package sequencing:

1. Determine style authority and approved references.
2. Resolve intake questions: size, delivery mode, foundation libraries, and synchronized resource package.
3. Style lock / visual direction.
4. Build or update the package-required component registry from the brief, approved references, foundation boards, and previously accepted screens.
5. Generate one foundation board or one UI screen.
6. Inspect that image for style drift and UI correctness. Reject/regenerate before asset work if needed.
7. Generate the matching asset sheet or dedicated standalone assets for that image. For Asset Library boards, produce shared assets; for UI screens, produce page-local assets plus required component coverage; for Visual Spec/Component Library boards, audit native/component boundaries and extract only genuine non-native visuals if present.
8. Remove chroma key or validate alpha, crop with confirmed boundaries, and save assets in the package.
9. Generate the image's contact sheet and visually inspect it.
10. Update `asset-map.json`, `screen-map.json`, `page-asset-audit.json`, and `asset-quality-audit.json` only for approved assets.
11. Proceed to the next final image only after the current image's asset package and audit pass.
12. Final manifest and checklist come last.

Do not generate all screens first and invent assets afterward unless the user explicitly wants rough exploration or explicitly says resources are not needed. Record that exception.

---
name: ai2psd-struct
description: Generate structured UI design-image packages for later editable Figma reconstruction and program-development handoff, especially pixel-exact source rebuilds that need complete synchronized atomic assets. Use when Codex needs to create AI-generated UI references plus matching visual-spec boards, component-library boards, asset-library boards, page-local transparent assets, component-state assets, element cutouts, batch asset packs, and mapping manifests for tools such as ai2figma-struct to rebuild screens accurately without missing assets, substituting similar assets, inventing inconsistent components, or falling back to large UI bitmap slices.
---

# AI2Psd Struct

Create image-generation deliverables that are structured for downstream design-source reconstruction. The output is not just a pretty UI mockup; it is a complete reference package containing screen images, foundation boards, transparent assets, and a manifest that tells a Figma rebuild skill exactly what to use where.

Use this skill before `ai2figma-struct` when the user wants new UI images that must later become editable Figma source files.

## Development Handoff Priority

This pipeline exists to produce development-usable UI source and resource packages, not screenshot posters.

Priority order:

1. Program-development usable assets and structure.
2. Editable Figma source reconstruction.
3. Pixel-level visual closeness.

Pixel closeness is a QA target, not a license to flatten UI. Achieve it with editable/native UI structure plus atomic visual assets. Do not use large UI screenshots, region slices, or whole-card/whole-tab/whole-list bitmaps as active assets to satisfy pixel matching unless the user explicitly asks for visual-only mockups and declines development handoff.

Gate failure means route to repair, not stop. After the retry limit, produce the closest development-usable result with explicit defects; do not convert the page into bitmap chunks.

## Core Principle

Generate design references and reconstruction assets together:

```text
Design brief
-> Style lock / visual tokens
-> Foundation boards
-> UI screen references
-> Transparent assets and cutouts
-> Mapping manifest
-> QA inventory
-> Handoff to ai2figma-struct
```

Do not let each screen invent its own icons, brand marks, tab bars, cards, or subject render style. Shared visuals must come from the same foundation set or be explicitly marked as page-local.

Project-specific facts such as palette values, platform, product category, character style, approved references, screen sizes, and asset naming conventions belong in the package config, manifest, generation log, or user brief. Keep this skill project-neutral; use it to enforce workflow, not a specific visual direction.

## AI2PSD-AI2FIGMA Shared Contract

Treat `ai2psd-struct` and `ai2figma-struct` as a paired production pipeline when the user asks for Figma source reconstruction, pixel-level rebuilds, complete resource packages, or development handoff.

`ai2psd-struct` is the production side. It must create a package that can be consumed deterministically by `ai2figma-struct`: screen references, atomic assets, placement metadata, ownership metadata, state metadata, QA records, repair status, and development handoff status. The package is not complete just because images exist; it is complete when the consumer can rebuild native structure and place atomic assets without guessing, substituting similar visuals, redrawing complex parts, or relying on large UI bitmap slices.

Use these shared asset QA statuses consistently. Prefer `qaStatus` for the QA value and `scope` for placement scope such as `page-local` or `approved-shared`. If an older manifest only has `status`, treat these QA values as status values and keep scope in `scope`.

- `approved`: accepted on the first successful QA pass.
- `repaired-approved`: failed at least once, then passed after repair.
- `missing-repaired`: originally missing from the inventory, then generated or extracted and accepted.
- `active-best-effort`: still imperfect after the retry limit, but selected as the closest available asset so the workflow can continue.
- `needs-regeneration`: known to be inadequate and not yet repaired.
- `rejected`: must not be used for reconstruction.

Do not mark `active-best-effort` assets as `approved`. Best-effort assets may continue through the pipeline, but their risk must remain visible to `ai2figma-struct`. Do not use `page-local` or `shared` as the only proof that an asset is approved; those are scope labels, not quality decisions.

## Repair-First Pipeline

In Figma-rebuild, source-file, development-handoff, or pixel-exact mode, every asset gate is a repair loop, not a dead stop. When an asset is missing, geometrically invalid, visually mismatched, clipped, polluted, or incomplete, repair that asset and recheck it before moving on.

Repair priority:

1. Re-extract, recrop, or reprocess from the same-generation working source, asset sheet, matte source, or approved source image.
2. Extract or clean from the original UI reference ROI when the visual is present there and the screenshot-crop exception allows it.
3. Generate a replacement with `imagegen` using the UI reference ROI or same-generation source as a visual anchor.
4. Generate a replacement from text prompt only when no usable source or ROI exists.
5. After three failed repair attempts for the same asset issue, select the closest version, mark it `active-best-effort`, record the reason, and continue.

The retry limit preserves forward progress; it does not permit a non-development fallback. The selected best-effort result must still be the closest atomic asset, native/vector mapping, or clearly recorded unresolved atomic-asset defect. Never use a large UI-region screenshot, whole card, whole tab bar, whole list, or mixed text/control slice as the best-effort active asset.

Never silently skip a failed asset. Record `repairAttempts`, `repairSource`, `selectedAttempt`, `bestEffortReason`, and the remaining defect in `asset-quality-audit.json` or the asset's validation block. The final package must still include manifests, repair logs, known defects, and a handoff note.
## Pixel-Exact Asset Completeness Mode

Use this mode when the user asks for Figma source reconstruction, 100% visual restoration, complete assets, source-file rebuild, development handoff, or says that no asset may be missed. In this mode, development usability and editability outrank visual shortcuts; visual fidelity is pursued by redundancy and repair, not by flattening UI regions.

Hard rules:

- Generate the UI reference image and its reconstruction assets as one synchronized deliverable. Do not rely on later screenshot slicing as the normal production path.
- Visual assets must be authored by `imagegen` or approved source imagery. Scripts may remove backgrounds, crop, resize, pack contact sheets, and write manifests, but scripts must not draw or invent final visual assets such as icons, buttons, cards, decorations, character art, or navigation states.
- Do not classify buttons, tabs, chips, cards, badges, or navigation items as native by default. First inspect their visual treatment.
- Generate synchronized assets for any visible element that includes gradient fills, soft glow, complex shadow, 3D or skeuomorphic rendering, embedded icons, decorative texture, complex highlights, blur, glass, state-specific styling, or brand/game/cute visual character.
- Native-simple rebuild is allowed only for plain text, simple layout containers, simple solid fills, simple strokes, and basic editable structure that can be accurately recreated with Figma primitives.
- When in doubt, generate the asset. Redundant assets are safer than missing or approximate assets.
- The active asset must be an atomic development unit: a single icon, state icon, decoration, 3D object, avatar/photo/thumbnail, illustration, visual skin without unrelated native UI, or separated shadow/glow layer.
- Do not make active assets from mixed UI regions that contain text plus controls, multiple cards, list rows, a full tab bar with labels, a whole hero section with title/button/art, modal bodies, or any region that a developer would need to slice again.
- Large UI-region images may exist only as locked references, paste-back QA images, comparison sheets, or visual-only deliverables explicitly requested by the user. Mark them `reference-only` or `rejected`; never list them as active `pageLocalAssets`.

Required examples:

- Hero areas: generate the visual background/atmosphere art as an asset when it contains gradients, glow, confetti, bubbles, waves, stars, or other decorative art. Keep title, copy, buttons, controls, and layout as native/editable or separate skins/assets. Do not export the entire hero UI as one active asset for development handoff.
- Buttons and tag pills: generate each full visual skin as an asset when it includes gradient, icon, glow, shadow, or special texture. Record whether Figma should overlay editable text or use the flattened label.
- 3D icons and illustrations: generate the complete asset with its intended shadow/glow treatment, or generate separate `subject` and `shadow` layers when that gives better reconstruction control. Do not invent a new shadow style; match the approved UI reference shadow profile.
- Navigation and tab states: first inventory the actual navigation component shown in the screen, such as bottom tab, top tab, segmented nav, side nav, toolbar nav, or custom game nav. Generate the container skin when it is visually non-native, then generate a complete state matrix for every actual nav item and every required state shown or needed for reconstruction, such as selected, unselected, disabled, pressed, badge, notification, or locked. Do not assume a fixed item count.
- Section title icons, small badges, fire/moon/shield/flag/crown icons, and similar decorative labels: generate them as assets unless they are from an explicitly chosen vector icon system.

The examples above are required inventory triggers. If any such visual is missing from a screen's asset inventory, run the Repair-First Pipeline for that specific visual before marking the screen package complete.

## Shadow Profile And Edge-Safe Asset Gate

Use this gate for every generated transparent visual asset that includes 3D, skeuomorphic rendering, glow, blur, contact shadow, cast shadow, reflection, or soft edge detail.

Shadow rules:

1. The shadow style must be reference-driven. Match the approved UI reference shadow profile: color tint, opacity, blur/softness, spread, direction, contact shape, and relationship between subject and ground. Do not write or apply a universal shadow style such as always light, always dark, always green, or always separated.
2. If the approved UI shows a soft contact shadow, the generated asset must preserve that same kind of contact shadow without turning it into a solid blob. If the approved UI shows a strong/heavy shadow, a strong shadow is acceptable only when it matches the reference.
3. Decide per asset whether the shadow should be baked into the subject PNG or separated as `subject` + `shadow`. Separate layers are preferred when the contact shadow is broad, low-opacity, easy to mis-crop, needs Figma placement control, or differs between contexts.
4. Record `shadowProfileRef`, `shadowHandling`, and `shadowQuality` in `asset-map.json` or `asset-quality-audit.json` only for active assets that actually include shadow, glow, reflection, soft-edge effects, or separated shadow layers. Do not require shadow metadata for clean no-shadow assets.
5. Reject or regenerate any active asset whose shadow profile visibly differs from the approved UI reference, including shadows that are too dark, too opaque, too blurry, too sharp, wrong color/tint, wrong direction, clipped, or merged into an indistinct blob.
6. If the asset has no shadow, glow, reflection, or soft-edge effect in the approved reference, do not invent one and do not force shadow QA fields. It may record `shadowHandling: none`, but `shadowProfileRef` and `shadowQuality` are not required for that no-shadow case.

Transparent padding rules:

1. Measure transparent safety padding from the alpha bounding box to the PNG canvas edge. This is not visual guessing; it is computed from the alpha channel after chroma-key removal or native transparency.
2. Minimum padding is based on asset class and final PNG canvas:
   - simple small icons and tab states: `max(12px @2x, 8% of alpha-bbox long edge)`;
   - 3D icons, mascots, illustrations, decorations, or assets with shadow/glow: `max(24px @2x, 10% of alpha-bbox long edge)`;
   - wide UI skins such as buttons/cards/tabs: horizontal `max(24px @2x, 4% of alpha-bbox width)`, vertical `max(12px @2x, 4% of alpha-bbox height)`, or vertical `max(24px @2x, 6% of alpha-bbox height)` when shadow/glow is present.
3. If the negotiated delivery scale is not `@2x`, scale the pixel constants proportionally: `@1x` uses half these constants; `@3x` uses 1.5x these constants.
4. If any side is below the required padding, the asset must not become active. Regenerate with more empty canvas or recrop/repad from the asset sheet, then re-run contact-sheet QA.
5. Do not use padding to hide a clipped asset. If visible subject pixels or shadow/glow are already missing at the generated source edge, regenerate the asset instead of adding transparent pixels afterward.


## Matte Color Selection Gate

Use this gate whenever built-in image generation needs chroma-key background removal instead of true native transparency. Do not default to green screen. Choose the matte color per asset or per asset-sheet row based on the asset's actual colors.

Rules:

1. Candidate matte colors are high-chroma non-black/non-white colors only: `#00FF00` green, `#FF00FF` magenta, `#0066FF` vivid blue, `#FFFF00` yellow, `#FF0000` red, and `#00FFFF` cyan. Do not use black, white, gray, off-white, or near-black as a matte color for active assets.
2. Before generation, inspect the approved reference, source crop, or intended asset description and estimate color conflict for every candidate. Consider subject fill, stroke, highlights, shadows, glow, semi-transparent edges, anti-aliasing, and tiny details.
3. Prefer a matte color that does not appear in the asset and is far from all important edge colors. Common defaults: green assets use magenta; red/pink assets avoid red/magenta; blue/purple assets avoid blue/cyan; yellow/orange assets avoid yellow/red.
4. If every candidate color appears somewhere in the asset, choose the least harmful candidate by conflict score: prioritize protecting the asset's outer edge, semi-transparent pixels, shadow/glow, and high-frequency details over interior colors that are visually separated from the matte. Mark the asset `matteRisk: high` and require stricter contact-sheet review.
5. For multi-asset sheets, do not force one matte color for all assets when their color families conflict. Split assets into separate sheets by matte color, or generate critical assets individually.
6. Record `alphaMethod`, `matteColor`, `candidateMatteScores`, `matteConflictScore`, `matteRisk`, and `matteSelectionReason` in `asset-map.json` or `asset-quality-audit.json` for every active chroma-key asset.
7. Run chroma-key edge cleanup before accepting any asset with matte-colored fringe, holes in same-color subject areas, eaten edges, polluted shadows/glows, or visible background remnants. If cleanup cannot make the asset visually usable at its intended size, retry post-processing or regenerate the source asset. Minor fringe that is barely visible at intended use size may be accepted when it does not harm the design.

## Chroma-Key Fringe Reduction Workflow

Use this workflow whenever generated assets use a colored matte/chroma background instead of native transparency. This is a production cleanup workflow, not a separate QA gate, and it does not require extra manifest fields, extra contact-sheet formats, or additional acceptance records unless the project already requires them.

Generation-stage fringe reduction:

1. Prompt for a flat, uniform matte background: `solid flat chroma background, no gradient, no texture, no vignette, no shadow cast onto the background, clean separated object edges, asset centered with generous empty margin`.
2. Choose a matte color that is visually far from the asset's subject, edge colors, shadows, glow, highlights, and white/light outlines. For green, mint, or cyan assets, prefer magenta or vivid blue. For blue or purple assets, prefer green or magenta. For red or pink assets, prefer green or vivid blue. For assets with white or very light outlines, choose the matte with the lowest risk of visible edge spill and explicitly prompt for clean light edges with no color spill.
3. Keep the subject away from the canvas edge so post-processing can preserve anti-aliasing, soft shadows, and transparent padding.

Post-processing-stage fringe reduction:

1. Build an alpha mask from the matte source image or asset-sheet ROI. Prefer processing from the original matte source, not from a previously hard-cut transparent PNG.
2. Apply only a slight mask choke/erode when needed to remove the outermost polluted pixels. Do not eat into the visible subject silhouette, icon shape, glow, or shadow.
3. Apply edge despill to reduce the matte color in boundary pixels without changing the subject's intended colors.
4. Apply a light feather only when it makes the edge more natural. Do not blur crisp icons or make UI assets look fuzzy.
5. If the cleanup makes the asset worse, keep the better version and retry with a cleaner matte source or a different matte color.

Suggested conflict score:

```text
0 = no visible conflict
1 = tiny interior color similarity only, far from edges
2 = small non-edge conflict, likely safe with despill
3 = moderate conflict or near-edge similarity; high-risk review required
4 = strong conflict on subject fill, stroke, shadow, glow, or antialias edge
5 = matte color is part of the asset identity; do not use unless all candidates are worse
```
## Required Intake Questions Gate

Before generating any final UI image package, explicitly resolve these intake questions. Ask the user unless the answer is already unambiguous from the current request, existing package config, or prior accepted context. Do not silently assume these values.

Required intake items:

- Target surface/platform: mini-app, mobile app, mobile web, desktop web/PC, tablet, or other.
- Final image size: logical canvas size, delivery scale, and target pixel dimensions.
- Style authority: `approved-reference` with the exact reference set, or `new-exploration`.
- Delivery mode: `rough-exploration`, `figma-rebuild`, or `development-handoff`.
- Foundation libraries: whether to generate synchronized Visual Spec, Component Library, and Asset Library boards.
- Synchronized resource package: whether to generate shared transparent assets, complete per-screen page-local assets, component-state assets, contact sheets, manifests, and QA audits together with every final image.
- Asset package policy: whether the One-Image-One-Asset-Package Gate and Pixel-Exact Asset Completeness Mode apply to every generated image.

Default rules:

- For `figma-rebuild`, `development-handoff`, source-file rebuild, complete UI package, 100% visual restoration, or any request that mentions Figma/source/development handoff, synchronized resource packages are mandatory unless the user explicitly declines them. If the user says assets must not be missed, enter Pixel-Exact Asset Completeness Mode automatically.
- If the user explicitly asks for rough exploration, quick concepts, mood exploration, or says assets are not needed, the resource package may be skipped; record that exception in the generation log and package config.
- If the user asks for only one standalone image and does not need later reconstruction, ask whether assets are needed before generating a full package.
- Once synchronized resources are required, do not ask per page whether to generate page-local assets; every final image must pass the gate.

## Size Negotiation Gate

Before generating or validating a package, determine the project size contract. Do not hardcode any platform dimensions globally.

If the user's request or existing project manifests do not clearly define these items, ask before generating:

- Target platform: mini-app, mobile app, mobile web, desktop web/PC, tablet, or other.
- Logical canvas size: for example a tall mobile canvas, a tablet canvas, or a project-specific desktop canvas.
- Delivery scale: usually `@1x`, `@2x`, or `@3x`. Prefer `@2x` for high-fidelity UI references when the user is unsure, but ask first.
- Foundation board size: use a readable large landscape board by default only after confirmation; do not assume one fixed size for every project.
- Delivery mode: `rough-exploration` or `figma-rebuild/development-handoff`. In `figma-rebuild/development-handoff` mode, the synchronized resource package is mandatory and must include visual spec, component library, asset library, shared transparent assets, per-screen page-local transparent assets, and mapping manifests.

If the project already has a clear size contract, reuse it and record it in `04-manifest/package-config.json`. If the user only wants rough visual exploration, the full resource package may be skipped only for that exploration pass, and this exception must be recorded. Once the user asks for Figma reconstruction, development handoff, source-file rebuild, or complete UI package, every final screen must have a complete per-screen resource package.

## Approved Reference Mode

If the user has already approved a visual direction, UI set, brand asset, landing/home screen, logo, brand character, Figma version, component library, asset library, or reference screen, treat that approved material as the style source of truth. Do not regenerate a new visual identity from text-only prompts.

Before creating new foundation boards or new screens, identify the style authority:

- `approved-reference`: existing UI images, Figma screenshots, logos, brand assets, hero/subject assets, prior accepted pages, or user-provided references.
- `new-exploration`: no approved style exists yet, or the user explicitly asks for a new direction.

Rules for `approved-reference` mode:

1. Use the approved reference images/assets as prompt references whenever possible and record them in `generation-log.md` and `package-config.json`.
2. Preserve the approved palette, contrast, typography feel, card density, hero treatment, hero/subject asset style, logo style, navigation style, and overall mood. Do not reinterpret descriptive style words into a new palette or new visual identity.
3. Foundation boards must be extracted, summarized, or extended from approved references. They must not become a newly invented style board.
4. New pages must extend the existing style; any color, brand asset, hero/subject asset, logo, tab, card, or page-background drift is a package failure unless the user explicitly approves the new direction.
5. If the approved style source is ambiguous or missing, stop and ask for the exact reference set before generating final handoff assets.


## Output Contract

Use the negotiated size contract:

- UI screen references: `<deliveryWidth> x <deliveryHeight> px`, derived from `<logicalWidth> x <logicalHeight> @<scale>`.
- Foundation boards: `<foundationBoardWidth> x <foundationBoardHeight> px`, usually a readable landscape board when foundation libraries are required.
- Page-local asset sheets: use the negotiated asset-sheet size or a larger canvas when the page-specific assets cannot fit; keep separated tiles and enough padding.
- Individual transparent assets: use the smallest clean canvas that preserves detail. Icons, thumbnails, waveforms, subject/product renders, and decorations should use their intended display scale, recorded per asset in the manifest. Do not save full-screen crops as assets.

For project-bound work, produce or maintain this folder shape unless the user gives another structure:

```text
pic/ui/<version>/
  01-foundation/
    visual-spec/
    component-library/
    asset-library/
  02-screens/
  03-transparent-assets/
    icons/
    brand-assets/
    subjects/
    decorations/
    thumbnails/
    waveforms/
    page-local/
  04-manifest/
    asset-map.json
    screen-map.json
    package-config.json
    generation-log.md
    qa-checklist.md
```

Read `references/output-contract.md` when defining or checking a deliverable package.

## Generation Rules

1. Lock style before batch generation: page size, palette, type scale, radii, shadows, button style, bottom tab style, icon style, brand/subject render style, and background treatment.
2. Generate clean foundation boards when the user needs Figma reconstruction:
   - Visual Spec: tokens, typography, colors, spacing, radii, shadows, page rules.
   - Component Library: native UI examples such as bars, buttons, chips, inputs, cards, modals, tabs.
   - Asset Library: approved non-native visual assets, transparent cutouts, thumbnails, brand/hero assets, subject renders, waveforms, decorative marks.
3. Generate UI screen references using the same locked style and foundation assets.
4. After every screen reference, run both a page-level asset audit and a package-required component audit. Do not stop at the foundation asset library. Each screen must be checked for visible page-local backgrounds, buttons, tabs, component states, icons, thumbnails, subject images, waveforms, decorative marks, empty-state art, badges, overlays, generated visuals, and any package-level required components such as app-shell navigation even when they are not visible on the current screen.
5. For every final screen in a Figma-rebuild or development-handoff package, generate its complete per-screen resource package. In Pixel-Exact Asset Completeness Mode, each screen must first receive a complete redundant page-local asset set under `03-transparent-assets/page-local/Pxx/`, even when similar assets exist elsewhere. Shared assets go into `shared-approved/` only after explicit promotion and QA. Extraction from full-screen UI images is a last-resort reference method, not the default production method.
6. Create a manifest that maps each screen element to either native rebuild, component-library source, asset-library source, transparent asset file, or page-local asset.
7. Validate inventory completeness before handoff. A screen must not contain an image-like visual that has no corresponding shared asset, page-local asset, native/vector rebuild mapping, or explicit exception in the manifest.
8. Validate dimensions before handoff. Screen files, foundation boards, generated asset sheets, and every manifest-listed asset must match `package-config.json`, manifest dimensions, or explicitly accepted per-file overrides. Reject packages where screens or boards are accidentally low-res, cropped, polluted, or inconsistent with the negotiated size contract.

## One-Image-One-Asset-Package Gate

When synchronized resources are required, every final generated image must complete this gate before moving to the next final image. This applies to foundation boards and UI screens. Do not batch-generate many final screens first and invent or cut assets afterward.

For each final image, execute this sequence in order:

1. Generate the image from the locked style and approved references.
2. Inspect the image for style drift, component drift, text overflow, crop problems, and unexpected visuals. Reject and regenerate before asset work if the image itself fails.
3. Inventory all non-native visuals in that image: brand/subject renders, avatars/photos, thumbnails, data visuals, decorative marks, complex icons, empty-state illustrations, badges, and overlays.
4. Classify text and truly simple editable structure first, then separately audit component skins and state visuals. Do not default buttons, cards, chips, nav bars, tab bars, list rows, or modal shells to native/component-native until their visual treatment has passed the Native vs Asset Boundary rules.
5. Generate matching shared assets, page-local assets, or component-state assets with `imagegen` as dedicated standalone transparent assets or as a clean asset sheet with clear tile boundaries. Do not default to screenshot slicing, and do not use local drawing scripts to create final visual asset geometry.
6. Remove chroma-key backgrounds or validate alpha, then crop each asset with confirmed boundaries.
7. Create a contact sheet for the generated assets on a checkerboard background with filename/id labels.
8. Visually inspect the contact sheet for alpha quality, semantic match, neighboring-asset contamination, UI pollution, crop errors, and style drift.
9. Write or update `asset-map.json`, `screen-map.json`, `page-asset-audit.json`, and `asset-quality-audit.json` only for assets that passed inspection.
10. Proceed to the next final image only after the image, assets, contact sheet, and audit are complete.

Foundation boards also need this gate. A Visual Spec or Component Library may contain only native/component examples and therefore may have no transparent page-local assets, but it still needs an audit entry proving the native/asset boundary. An Asset Library board must produce shared asset files, a shared contact sheet, and asset-quality records before those assets become promoted references.
## Navigation And Component State Matrix Gate

Use this gate for any repeated UI component with visible states: bottom tabs, top tabs, segmented controls, side navigation, toolbar navigation, mode switches, chips, toggle groups, rating choices, game menu items, and custom nav patterns.

Rules:

1. Do not assume the number of items. Count the actual items from the approved screen or brief and record them in `page-asset-audit.json`.
2. Build a state matrix before generating assets: `componentId`, `itemId`, label meaning, visible icon/skin, required states, selected/default state, badges/locks/notification variants, and whether the container skin is separate.
3. Generate the state matrix with `imagegen` as one synchronized asset sheet whenever possible, using the approved screen/component as the style anchor. If the sheet fails visual QA, reject it and regenerate; do not repair the visual style with drawing scripts.
4. Split the approved sheet into one transparent asset per item-state, for example `Pxx-nav-<item>-<state>@2x.png`. Also generate a separate container skin if the container has gradients, blur, shadow, texture, or exact rounded shell styling.
5. Every item-state required by the matrix must appear in `asset-map.json`, `screen-map.json`, `page-asset-audit.json`, and `asset-quality-audit.json`. Missing states are package failures.
6. If a state can be rebuilt as a simple vector/native icon, record it explicitly as `vector-icon` or `native-simple`; otherwise generate it as a page-local or approved-shared asset. In pixel-exact mode, prefer generating the asset when unsure.



## Package-Level Required Component Registry Gate

Use this gate whenever the package is intended for Figma reconstruction or development handoff, especially in pixel-exact mode. Page-local redundancy is not limited to visuals currently visible on one screen. It also covers required package-level components that the app, site, or product uses across screens.

Before generating the first page-local asset package, build or update a `requiredComponentRegistry` from the approved reference set, product brief, foundation boards, and previous accepted screens. Reuse and update that registry before every later page. Include common/app-shell components such as bottom tabs, top navigation, side navigation, segmented navigation, floating action bars, global buttons, common card skins, badges, locks, ad gates, modal shells, and other repeated stateful components.

Rules:

1. Do not infer required components from the current screen alone. A page may hide a global component, but the package may still require its assets for complete Figma reconstruction.
2. For every final screen, audit both `visiblePageAssets` and `packageRequiredComponents` before generating page-local assets. The current screen alone is not enough evidence that a package-required component is unnecessary.
3. If a required component is visible on the current screen, generate or reference its page-local assets and state matrix for that screen.
4. If a required component is not visible on the current screen but is required by the package, still include its approved shared/component-state assets in the package, or record an explicit `notVisibleOnThisScreen` entry that points to the approved source and explains why no page-local placement is used.
5. In pixel-exact page-local redundancy mode, `notVisibleOnThisScreen` is not an asset-coverage exemption. It may explain why the component is not placed in the current screen, but the current page package must still include page-local or component-state asset coverage for that required component when the user wants fully self-contained per-page reconstruction.
6. In pixel-exact page-local redundancy mode, generate a page-local copy of required component assets for the current page when the user wants fully self-contained per-page reconstruction, even when the component is a common app-shell element or hidden on the current screen. Otherwise, reference `approved-shared` only when the manifest explicitly says package-level sharing is allowed.
7. Navigation and stateful component assets must cover the actual item count and required states from the registry or approved reference. Do not hardcode a fixed tab count; do not omit a state matrix because the current page hides the component.
8. Missing package-required component assets are package failures unless the user explicitly accepts the omission.

Use a fixed coverage vocabulary for `page-asset-audit.json.packageRequiredComponents[].coverage`; do not invent near-synonyms:

- `visible-page-local`: component is visible on this screen and covered by page-local assets.
- `visible-approved-shared`: component is visible on this screen and covered by explicitly referenced shared/component-state assets.
- `hidden-approved-global`: component is hidden on this screen, but approved shared/component-state assets cover the package requirement.
- `notVisibleOnThisScreen`: component is intentionally absent from this screen and has an approved source reference; use this only when package-level sharing is allowed or an accepted exception explains why no asset refs are needed.
- `native-only`: component is visually simple and rebuilt natively; record vector/native coverage instead of bitmap refs.

Every non-`native-only` component coverage entry must include `assetRefs` when approved assets exist, even when the component is hidden on the current screen. Hidden placement is not the same as missing coverage.
## Page-Local Redundancy And No-Similar-Substitution Rule

In Pixel-Exact Asset Completeness Mode, every screen must generate a complete page-local asset set first. This includes visible page assets and any package-required components that the user expects to be self-contained per page. Do not satisfy a page asset requirement by searching other pages, shared folders, old packages, contact sheets, screenshots, or generated variants for visually similar assets.

A shared asset may be reused only when all conditions are true:

1. The current screen manifest explicitly references the same `assetId`.
2. The asset is marked `approved-shared` or `promoted` after QA.
3. The visual match has passed comparison against the current screen.
4. The current screen does not require a page-specific variant, state, crop, shadow, label, color, or placement.

If any condition is missing, generate a new page-local asset for the current screen. Similar is not same. Do not replace missing page-local assets with near matches.

Recommended flow:

1. Generate full page-local assets for every screen.
2. Run visual QA per page.
3. Promote exact repeated assets into `shared-approved/` only after validation.
4. Keep the page-local copy or explicit page reference so Figma reconstruction can always recover the original page appearance.

## Per-Screen Asset Completeness Gate

This gate is mandatory for every final screen in a multi-page UI package and runs inside the One-Image-One-Asset-Package Gate. Do not ask whether each page should have page-local assets in Figma-rebuild/development-handoff mode; it must. Ask only when the user has not clarified whether the task is rough exploration or final handoff.

Foundation boards are not enough. For every screen, create a page-level asset inventory before marking the package complete:

1. Inspect the screen from top to bottom and list all non-text visual elements. Also inspect the package-level required component registry so hidden-but-required app-shell/common components are not missed.
2. Classify each item as one of:
   - `native-simple`: plain text, simple solid containers, simple strokes, and basic layout that can be recreated accurately with Figma primitives.
   - `component-native-simple`: repeated plain UI structure that should be rebuilt from the component library and has no complex visual skin.
   - `component-skin-asset`: button, tab, chip, badge, card skin, nav item, or component state that includes gradient, icon, glow, shadow, texture, or state-specific styling.
   - `shared-asset`: approved logo, brand character, subject/product render, waveform, thumbnail, decoration, or component skin already promoted as `approved-shared`.
   - `page-local-asset`: any page-specific background, button skin, icon, 3D render, illustration, decoration, component state, or complex visual required for pixel match.
   - `vector-icon`: simple icon to rebuild with a consistent vector icon set rather than bitmap, only when the chosen vector set can visually match.
   - `dynamic-content`: user/avatar/photo/content placeholders intentionally supplied at runtime.
   - `missing`: visual appears on the screen but has no generated/extracted asset or native mapping yet. In rebuild or pixel-exact mode, this triggers the Repair-First Pipeline; it is not an acceptable final state.
3. For every `page-local-asset` and `component-skin-asset`, generate a standalone transparent asset, skin asset, or state asset and save it under `03-transparent-assets/page-local/Pxx/` or `03-transparent-assets/component-states/` with an explicit page reference. Prefer a page-local asset sheet or dedicated transparent generation. Do not use full-screen UI screenshot crops as production assets unless they pass the strict screenshot-crop exception below.
4. For every page-specific icon that will not be rebuilt as a vector icon, generate or extract it as a transparent asset. Do not rely on the flattened screen image.
5. Add every page-local file to `asset-map.json` with `status: page-local` and add it to the screen's `pageLocalAssets` list in `screen-map.json`.
6. Create or update `page-asset-audit.json` so downstream Figma rebuild can see what was handled, what is native, and what is still missing.
7. Generate a per-screen asset contact sheet on a checkerboard background immediately after cutting page-local assets. Do not write page-local assets into active `screen-map.json` or `page-asset-audit.json` until the contact sheet has been visually inspected.
8. Never rely on guessed crop coordinates. Use one of these methods:
   - dedicated one-asset generation for critical assets;
   - a page-local asset sheet with clear grid/tile boundaries and a coordinate guide;
   - programmatic connected-component extraction followed by visual inspection.
   Manual coordinates are allowed only after opening the source sheet and confirming each crop boundary.
9. Reject or demote any asset that is empty, mostly card background, contains unrelated UI text, includes neighboring components, includes a different asset's edge, contains UI card/button/list/tab background, has a dirty solid background, is cropped off, has multiple unrelated subjects, or visually does not match its filename/intended use.
10. When extracting from a tall UI screen, create or use a coordinate-grid preview before committing crop boxes. Do not estimate long-screen y positions from memory.
11. Create `asset-quality-audit.json` for multi-page packages. It must record each page-local asset as `approved`, `repaired-approved`, `missing-repaired`, `active-best-effort`, `rejected`, or `needs-regeneration` with a reason, plus `visualInspectionPassed`, `semanticMatch`, `contactSheet`, and repair attempt details for every active page-local asset. Rejected assets must not remain in active `screen-map.json` or `page-asset-audit.json` references.

A page is not complete just because the full-screen UI image exists. It is complete only when its page-level asset inventory has no unresolved `missing` items, no complex visual is marked `native-simple`, and no referenced page-local or component-state asset is visually invalid unless that asset has exhausted repair attempts and is explicitly marked `active-best-effort`.

It is also not complete if pixel matching depends on active large UI-region slices. Any active asset that still contains unrelated native UI, editable text, multiple controls, multiple list rows, or a full app-shell region must be repaired into atomic assets/native mappings, or demoted to `reference-only` with a recorded defect before handoff.

## Screenshot-Crop Exception

Full-screen UI screenshot crops are dangerous because they often include card backgrounds, labels, buttons, shadows, neighboring elements, or partial UI. Treat `screen-crop-alpha` assets as rejected/reference-only by default.

Hard rule: active assets must not be sourced from full-screen UI screenshots unless the asset is an avatar/photo/example-thumbnail style bitmap that is intentionally shown as image content in the final design. This exception exists for thumbnail-like content only, not for reusable UI artwork.

A full-screen screenshot crop may become an active page-local asset only when all are true:

- It is an avatar, photo, example thumbnail, wallpaper thumbnail, waveform/data visual, or illustration thumbnail that will intentionally remain bitmap content.
- It contains no UI text, button, chip, card shell, tab item, input, nav, status bar, list row, modal shell, or component background that should be rebuilt natively.
- Its alpha or mask boundary is clean, with no white/gray card rectangle or screenshot edge pollution.
- It is marked in `asset-quality-audit.json` as `approved-clean-or-acceptable-thumbnail` with `visualInspectionPassed: true`, `semanticMatch: true`, and a contact-sheet path.

Never use full-screen screenshot crops as active assets for primary brand characters, subject/product renders, 3D/profile-image candidates, icon libraries, decorative marks, empty-state illustrations, bottom tabs, buttons, cards, forms, setting/list icons, or modal graphics. Generate those as dedicated transparent assets or asset-sheet tiles, or rebuild them as native/vector layers.

## Atomic Development Asset Gate

Use this gate for every final package intended for Figma reconstruction, source-file rebuild, or development handoff.

An active bitmap asset must pass all of these:

- It is the smallest useful development unit for its purpose.
- A developer or Figma rebuilder can use it without cutting it again.
- It does not contain unrelated editable text, cards, controls, lists, nav labels, page backgrounds, or neighboring UI.
- Its manifest records `handoffPurpose: "program-development"`, `assetGranularity: "atomic"` or a more specific atomic class, `developmentUsable: true`, and whether native rebuild is required around it.

If the asset fails, set `defectCode: "invalid-ui-region-slice"` or a clearer atomicity defect, then run the Repair-First Pipeline. After three failed attempts, continue with the closest atomic asset or native/vector fallback and record the unresolved defect. Do not activate the large slice as a workaround.

## Native vs Asset Boundary

Mark these as `native-simple` rebuild targets only when they are visually simple:

- Plain text and editable copy
- Simple solid page backgrounds, cards, panels, and dividers
- Simple solid buttons, inputs, chips, toggles, selectors, and containers with no gradient, icon, glow, texture, complex shadow, or 3D effect
- Simple status/nav/tab structures only when their icons and states are separately mapped as assets or vectors
- Simple vector icons only when a consistent vector set can visibly match the reference

Do not mark an item native-simple only because its UI type is a button, chip, tab, card, badge, or navigation item. Visual complexity overrides UI type.

Mark these as image/transparent assets or component-skin assets:

- Brand characters, generated subject/product renders, 3D characters, portraits
- Hero backgrounds and atmospheric art only when they exclude editable title/copy/buttons/controls; wallpaper-like panels, complex thumbnails, example images
- Full button/tag/chip/tab/card skins when they include gradient, icon, glow, complex shadow, texture, glass, or special highlights
- Navigation/tab containers and every required item-state when exact appearance matters; this applies to the actual number of items in the component, not a fixed count
- Section title icons, badges, small decorative icons, fire/moon/shield/flag/crown style labels, and icon+label pills
- Brand marks when exact appearance matters
- Waveforms, complex sound visuals, sparkles, shadows, decorative marks
- Any visual that would become flat, approximate, or visibly different when redrawn with primitive shapes

If an item is visually complex but should later animate, export it as separated layers/assets such as `front`, `back`, `shadow`, `sparkle`, or `orbit` rather than a single flattened image.

## Simple Placement Contract

Use this contract for any image asset that must be placed back into a screen with high fidelity. Keep it simple and project-neutral.

Separate asset identity from screen usage:

- `asset-map.json` describes the asset itself: file path, dimensions, alpha, `contentBBox`, quality status, source, visual-effect flags, and development metadata.
- `screen-map.json.screens[].assetUsages[]` describes each time an asset is used on a screen: `assetId`, `targetPlacement`, `layerOrder`, `ownership`, and alignment rule.

Do not rely on one global `targetPlacement` inside `asset-map.json` for shared assets. A shared or component-state asset may appear on several screens with different positions. For backward compatibility, `asset-map.json.assets[].targetPlacement` may exist for a single-use asset, but `screen-map.assetUsages[]` is the canonical contract for Figma reconstruction.

For every active asset that is used by a screen, record:

- `contentBBox`: the tight alpha/content bounds inside the PNG canvas, excluding transparent safety padding.
- `assetUsages[].targetPlacement`: the intended visual placement on the target screen, measured in screen coordinates.
- `assetUsages[].layerOrder`: the relative stack order, enough to avoid accidental over/under placement.
- `assetUsages[].ownership`: which visual parts are already inside the asset and which parts Figma should rebuild natively.
- `assetUsages[].alignBy`: normally `contentBBox`; this tells Figma rebuild to align visible content, not the whole transparent PNG canvas.

Use these plain ownership values:

- `asset-only`: the asset already contains the complete visual element. Figma should place it and not redraw its parts.
- `asset-with-native-text`: the asset contains the skin, icon, shadow, gradient, or decoration; Figma may overlay editable text only.
- `native-with-asset-icon`: Figma rebuilds the container/text natively and places the listed asset only for the icon, avatar, thumbnail, or decoration.
- `native-only`: no image placement is needed.

Do not over-model this contract. If exact measurement is not available, provide the best measured screen bounds from the reference and mark the confidence as `estimated`. Missing placement metadata is allowed for rough exploration, but in pixel-exact, Figma-rebuild, or development-handoff mode an active visible asset may not be marked `approved` until its screen usage has placement metadata and local paste-back QA, or it is explicitly marked `active-best-effort` after the retry limit.

`asset-only` is valid only for one atomic visual element. Do not use `asset-only` for a large UI region that contains multiple controls, multiple cards, text plus controls, a full list, or a full app-shell/tab region. Such regions must be native rebuild targets plus atomic assets.

Transparent safety padding is still required for clean shadows and edges. The padding must not be treated as the visual size. Downstream Figma rebuilds should align `contentBBox` to `assetUsages[].targetPlacement`, not scale the full PNG canvas as if all pixels were visible content.

For component skins such as buttons, chips, cards, tabs, and navigation items, make ownership explicit. If a generated skin already contains an icon, glow, shadow, or selected-state treatment, do not ask the Figma rebuild to draw that same visual part again.

### Approval And Usage Gate

In `figma-rebuild`, `development-handoff`, source-file rebuild, or pixel-exact mode, do not mark an active visible asset `approved`, `repaired-approved`, or `missing-repaired` only because the PNG exists and looks acceptable in a contact sheet.

An active visible asset may be marked `approved`, `repaired-approved`, or `missing-repaired` only when all are true:

1. The asset file exists and has valid dimensions.
2. The asset has alpha when it is a transparent visual asset.
3. The asset has measured `contentBBox`.
4. Every screen using the asset has a `screen-map.assetUsages[]` record.
5. Each usage has `targetPlacement`, `layerOrder`, `ownership`, and `alignBy: "contentBBox"` unless a recorded exception explains another alignment.
6. Geometry acceptance passes for that usage, or the asset is repaired.
7. Local paste-back QA passes for that usage.

If any item fails, route to the Repair-First Pipeline. After three failed attempts, keep the closest development-usable atomic asset/native result, mark it `active-best-effort`, record `bestEffortReason`, `knownDefect`, and `needsManualReview`, and continue. The gate prevents false approval; it must not stop the package from producing a best-effort handoff.

### Geometry Acceptance Rule

For every asset usage with both `contentBBox` and `assetUsages[].targetPlacement`, check whether the visible content aspect ratio can be placed back without distortion.

Use this simple check:

```text
contentRatio = contentBBox.width / contentBBox.height
targetRatio = assetUsage.targetPlacement.width / assetUsage.targetPlacement.height
ratioError = abs(contentRatio - targetRatio) / targetRatio
```

Acceptance targets:

- ordinary assets: `ratioError <= 0.02`
- large hero, background, and wide atmospheric assets: `ratioError <= 0.03`

If the ratio exceeds the target, do not promote the asset as `approved`. First try recropping, recomputing `contentBBox`, regenerating from the same source, or regenerating a replacement asset. After three failed attempts, choose the lowest-error version, mark it `active-best-effort`, and record `aspectRatioMismatch`, `ratioError`, and `bestEffortReason`.

Do not expect downstream Figma reconstruction to fix a ratio conflict by stretching the asset.

### Local Paste-Back QA

Contact sheets validate isolated asset quality, but they do not prove the asset can reconstruct the screen. In Figma-rebuild, source-file, development-handoff, or pixel-exact mode, every active page-local or component-state asset must also pass local paste-back QA unless it is explicitly `active-best-effort`.

Local paste-back QA:

1. Place the transparent asset back over the source UI reference using `contentBBox`, `screen-map.assetUsages[].targetPlacement`, and the same placement rule expected by `ai2figma-struct`.
2. Generate a local comparison crop around the target region.
3. Check visible size, subject completeness, edge integrity, shadow/glow preservation, matte-color remnants, style drift, and whether embedded icons/states are missing or duplicated.
4. If the local comparison fails, run the Repair-First Pipeline for that asset and repeat the paste-back check.
5. After three failed attempts, select the closest version, mark it `active-best-effort`, and record the local defects.

Only assets that pass contact-sheet QA and local paste-back QA may be marked `approved` or `repaired-approved`.

## Prompting

Use `imagegen` for raster generation and transparent cutouts. Follow its built-in-first mode. For chroma-key transparency, choose the matte color with the Matte Color Selection Gate instead of defaulting to green; use true/native transparency only when the user confirms the fallback path.

Read `references/prompt-patterns.md` before generating full UI sets, foundation boards, or transparent asset batches.

## Manifests

Every final package needs explicit maps:

- `package-config.json`: platform, logical canvas size, delivery scale, delivery pixel size, foundation board size, delivery mode, asset-sheet policy, and confirmation that every final screen has page-local resources when the package is for Figma rebuild or development handoff.
- `asset-map.json`: every reusable, page-local, and component-state image asset, filename, dimensions, category, alpha status, source, crop notes, intended use, promotion status, `requiredForPixelMatch`, `doNotReplaceWithSimilar`, state, `contentBBox`, ownership, geometry status, repair status, local paste-back status, and visual-effect flags such as `includesShadow`, `includesGradient`, `includesGlow`, or `includesEmbeddedIcon`.
- `screen-map.json`: every screen, page size, source image, major regions, native-simple rebuild targets, component references, shared asset references, page-local asset references, component-state asset references, `assetUsages[]`, native/vector mappings, exceptions, usage-level `targetPlacement`, `layerOrder`, ownership/overlay rules, known risks, and any `active-best-effort` assets that the consumer must preserve as risks.
- `page-asset-audit.json`: per-screen inventory of all visual elements and package-required components, including visible page-local assets, hidden-but-required component coverage, component-skin assets, native-simple targets, vector icons, dynamic-content exceptions, missing items, repair attempts, and extraction status.
- `generation-log.md`: prompts used, reference images used, accepted/rejected variants, and style decisions.
- `qa-checklist.md`: inventory checks, visual consistency checks, transparency checks, and handoff notes.

For repaired or best-effort assets, include `repairAttempts`, `repairSource`, `selectedAttempt`, `ratioError` when relevant, `localPastebackComparison`, and `bestEffortReason`.

Read `references/manifest-schema.md` before writing or validating manifests.

## Strong Package Check

For complete UI packages, run a deterministic package check before final handoff. The check must verify `package-config.json` when present, screen dimensions, foundation board dimensions defined by config/manifests, `screen-map.json`, `asset-map.json`, `page-asset-audit.json`, referenced file existence, manifest dimensions matching real image files, alpha channels for transparent assets, and empty `missingAssets` lists. If the bundled `scripts/validate_package.py` exists, run it against the package root and fix failures before calling the package complete.

The deterministic check is necessary but not sufficient: also generate visual asset contact sheets for shared assets and for every page-local folder, then run local paste-back QA for active assets used by screens. If `scripts/pasteback_qa.py` exists and `screen-map.assetUsages[]` is available, use it to generate local comparison crops for review. Treat empty alpha, text-contaminated crops, card-background-only crops, wrong crop boundaries, neighboring-asset contamination, semantic mismatches, ratio conflicts, local paste-back mismatches, and accidental UI slices as failed QA. Repair the bad asset with the Repair-First Pipeline, or mark it native/vector in the audit when that is the correct representation. Do not call a package complete if any active page-local asset lacks visual inspection metadata and either paste-back metadata or an explicit best-effort record.

For transparent padding, a measured deficit of `<= 1px` may be recorded as `acceptedPaddingTolerancePx: 1` and treated as a warning when the asset has no visible clipping, no missing shadow/glow, and no edge damage. A deficit greater than `1px`, or any visible clipping, must route to repair/regeneration or an explicit accepted exception.

## QA Gate

Before handing off to `ai2figma-struct`:

- Check that every screen image has a matching screen-map entry.
- Check that every visible non-text visual on a screen and every package-required component appears in asset-map, component-state mappings, approved-shared references, or is explicitly recorded as native-simple/vector/dynamic-content/not-visible-on-this-screen. Complex visuals must not be recorded as native-simple.
- Check that foundation boards match the approved reference style instead of creating a new visual identity.
- Check that bottom tabs, nav bars, buttons, cards, and icon style are consistent across screens and approved references.
- Check that transparent assets have clean alpha or clean chroma-key-removal output with no background pollution, no matte-colored fringe, no eaten same-color subject areas, and recorded matte-selection metadata for chroma-key assets.
- Check every page-local contact sheet against filenames and intended use before active manifest promotion.
- Check that active assets pass geometry acceptance and local paste-back QA, or are explicitly marked `active-best-effort` after three repair attempts.
- Check that no active asset comes from a full-screen UI screenshot except approved avatar/photo/example-thumbnail bitmap content.
- Check that no page asset requirement was satisfied by a visually similar asset from another page or folder unless it is explicitly marked `approved-shared` and referenced by the current screen manifest.
- Check that every reusable or package-required component with states has a state matrix based on the actual item count and required states, including navigation item states and state-specific button/tag/card/chip skins even when the component is package-required but hidden on the current screen.
- Check that names are stable and development-friendly.

Read `references/transparent-asset-checklist.md` when transparent cutouts are required.
Read `references/figma-handoff.md` before telling another agent or skill to rebuild in Figma.

## Relationship To ai2figma-struct

`ai2psd-struct` produces structured image-generation packages. `ai2figma-struct` consumes them.

When both are used:

1. Use this skill to generate or organize UI images, foundation boards, transparent assets, repair records, and maps.
2. Repair missing or invalid page assets in this skill first whenever possible, because same-generation working sources usually match style better than later ad hoc generation.
3. Then use `ai2figma-struct` to place clean references, rebuild foundation libraries when provided, consume `ownership` and placement metadata, and assemble editable screens.
4. The manifest should indicate consumer-ready QA status, preferably in `qaStatus`: `approved`, `repaired-approved`, `missing-repaired`, `active-best-effort`, `needs-regeneration`, or `rejected`. Keep placement scope separately as `scope`.
5. If a manifest asset causes visible drift in Figma, `ai2figma-struct` may repair it locally, but the preferred upstream fix is to update the package asset and manifest so future rebuilds inherit the correction.

## Reference Map

- `references/output-contract.md`: expected folder/package structure, size negotiation, and naming rules.
- `references/style-and-asset-lock.md`: approved-style inheritance, asset-sheet crop discipline, and contact-sheet promotion gates.
- `references/prompt-patterns.md`: prompt recipes for UI screens, foundation boards, and transparent assets.
- `references/manifest-schema.md`: asset-map and screen-map structure.
- `references/transparent-asset-checklist.md`: alpha/crop/boundary validation.
- `references/figma-handoff.md`: handoff rules for ai2figma-struct.
- `scripts/validate_package.py`: deterministic strong check for complete packages when available.
- `scripts/pasteback_qa.py`: generate local paste-back comparison crops from `screen-map.assetUsages[]`; it does not auto-approve assets.



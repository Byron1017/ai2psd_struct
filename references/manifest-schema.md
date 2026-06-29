# Manifest Schema

Use JSON manifests so `ai2figma-struct` can consume the package without guessing.

## package-config.json

Record the negotiated project contract before generation or validation:

```json
{
  "version": "newui_Vx",
  "platform": "mobile-app",
  "logicalScreenSize": { "width": 750, "height": 1631 },
  "scale": 2,
  "targetScreenSize": { "width": 1500, "height": 3262 },
  "foundationBoardSize": { "width": 3072, "height": 2048 },
  "assetSheetSize": { "width": 3072, "height": 2048 },
  "deliveryMode": "figma-rebuild",
  "handoffPurpose": "program-development",
  "generateFoundationBoards": true,
  "generateSharedAssets": true,
  "generatePageLocalAssets": true,
  "resourcePackageMode": "synchronized-full",
  "pixelExactAssetMode": true,
  "pageLocalRedundantAssets": true,
  "noSimilarAssetSubstitution": true,
  "perPageRequiredComponentRedundancy": true,
  "requiredComponentRegistry": [
    {
      "componentId": "component.nav.primary",
      "type": "bottom-tab",
      "required": true,
      "itemCount": null,
      "requiredStates": ["selected", "unselected"],
      "coverage": "visible-page-local",
      "approvedReferenceScreens": []
    }
  ],
  "intakeQuestionsResolved": true,
  "styleAuthority": "approved-reference",
  "approvedReferenceSet": ["path/to/approved-home.png", "path/to/approved-logo.png"],
  "styleDriftPolicy": "reject-unless-user-approved",
  "notes": "Example values only; use the project-negotiated contract."
}
```

If a value is unknown, omit it or set it to `null`; validators should warn rather than inventing a fixed size. For `figma-rebuild` or `development-handoff`, `generatePageLocalAssets` means every final screen receives a page-local asset audit and any page-specific complex visual is generated as a clean transparent asset; it is not a per-page optional switch.

When `pixelExactAssetMode` is true, every screen first receives a complete redundant page-local asset set, `pageLocalRedundantAssets` must be true, and visually similar assets from other pages must not satisfy current-page requirements unless `noSimilarAssetSubstitution` is false by explicit user choice.

For final handoff packages, `styleAuthority` is required. Use `approved-reference` only when approved source material is available and list it in `approvedReferenceSet`; use `new-exploration` only when the user wants a fresh direction.

## asset-map.json

```json
{
  "version": "newui_Vx",
  "source": "imagegen",
  "targetScreenSize": { "width": 1500, "height": 3262 },
  "assets": [
    {
      "id": "asset.page.P01.hero-bg.vx",
      "filename": "03-transparent-assets/page-local/P01/P01-hero-bg@2x.png",
      "category": "hero-background",
      "status": "approved",
      "qaStatus": "approved",
      "scope": "page-local",
      "role": "hero-bg",
      "handoffPurpose": "program-development",
      "assetGranularity": "atomic-visual-background",
      "developmentUsable": true,
      "requiredForPixelMatch": true,
      "doNotReplaceWithSimilar": true,
      "state": "default",
      "targetScreen": "P01",
      "targetRegion": "home.hero",
      "contentBBox": { "x": 32, "y": 32, "width": 1340, "height": 812 },
      "nativeOverlayText": true,
      "includesShadow": true,
      "includesGradient": true,
      "includesGlow": true,
      "includesEmbeddedIcon": false,
      "intendedUse": ["hero background atmosphere"],
      "dimensions": { "width": 1404, "height": 876 },
      "alpha": true,
      "source": {
        "type": "generated-synchronized-asset",
        "promptRef": "generation-log.md#p01-hero-bg"
      },
      "crop": {
        "sourceImage": null,
        "roi": null,
        "padding": "preserve visual shadow and glow",
        "notes": "generated with the screen; not a screenshot crop"
      },
      "validation": {
        "alphaChecked": true,
        "edgeChecked": true,
        "backgroundPollution": false,
        "alphaMethod": "chroma-key",
        "matteColor": "#FF00FF",
        "candidateMatteScores": {
          "#00FF00": 4,
          "#FF00FF": 0,
          "#0066FF": 2,
          "#FFFF00": 3,
          "#FF0000": 2,
          "#00FFFF": 3
        },
        "matteConflictScore": 0,
        "matteRisk": "low",
        "matteSelectionReason": "Asset contains mint/green UI colors, so magenta creates the least edge conflict.",
        "transparentPadding": {
          "left": 32,
          "top": 32,
          "right": 32,
          "bottom": 32,
          "requiredHorizontal": 24,
          "requiredVertical": 24,
          "rule": "3d-shadow-glow: max(24px @2x, 10% alpha-bbox long edge)",
          "passed": true
        },
        "shadowProfileRef": "02-screens/P01-home.png#hero",
        "shadowHandling": "baked-in",
        "shadowQuality": "matches-reference",
        "visualInspectionPassed": true,
        "semanticMatch": true,
        "approved": true,
        "contactSheet": "05-contact-sheets/page-local/P01-assets-contact-sheet.png"
      }
    }
  ]
}
```

QA statuses:

- `approved`: accepted on the first successful QA pass.
- `repaired-approved`: failed at least once, then passed after repair.
- `missing-repaired`: originally missing, then generated/extracted and accepted.
- `active-best-effort`: still imperfect after the retry limit, but selected as the closest atomic/native result.
- `needs-regeneration`: known inadequate and not yet repaired.
- `rejected`: must not be used for reconstruction.

Scope and reuse labels:

- `promoted`: approved reusable asset.
- `approved-shared`: exact repeated asset promoted after QA; may be reused only when the current screen explicitly references the same `assetId`.
- `candidate`: useful but not yet validated globally.
- `page-local`: use only for one screen/region; must be stored under `03-transparent-assets/page-local/Pxx/` and referenced by that screen.

Prefer `qaStatus` for the QA decision and `scope` for labels such as `page-local`, `candidate`, `promoted`, or `approved-shared`. If `status` is used, do not use it ambiguously; either set `status` to the QA status and `scope` to the reuse scope, or document the legacy format clearly.

Categories:

- `logo`, `brand-asset`, `subject-render`, `hero-background`, `button-skin`, `tag-skin`, `tab-container`, `tab-icon-state`, `card-skin`, `wallpaper-thumbnail`, `sound-waveform`, `decoration`, `empty-state`, `photo`, `page-local`, `component-state`, `icon-candidate`.

Active assets for `figma-rebuild` or `development-handoff` must be development-usable atomic units. Record `handoffPurpose: "program-development"`, `assetGranularity` such as `atomic-icon`, `atomic-state-icon`, `atomic-visual-skin`, `atomic-decoration`, `atomic-subject`, `atomic-thumbnail`, `atomic-background-art`, or `atomic-shadow`, and `developmentUsable: true`. Avoid over-modeling; the important rule is that the file can be used directly by a developer or Figma rebuilder without cutting it again.

Active assets must not use `source.type: "full-screen-screenshot-crop"` unless the asset is approved avatar/photo/example-thumbnail bitmap content. Active assets also must not be large UI-region slices, whole cards, whole lists, whole tab bars, whole hero/app-shell regions, modal bodies, or mixed text/control bitmaps. For all other visuals, use `generated-synchronized-asset`, `generated-transparent`, `generated-asset-sheet`, `extracted-from-asset-sheet`, or native/vector rebuild records. In pixel-exact mode, assets with `requiredForPixelMatch: true` must include target screen/region, visual-effect flags, ownership, `contentBBox`, and `doNotReplaceWithSimilar: true`.

Do not store shared-asset placement as a single global truth in `asset-map.json`. `asset-map.json` describes the reusable file; `screen-map.json.screens[].assetUsages[]` describes where and how that file is used on each screen. A legacy single-use `asset-map.assets[].targetPlacement` may be present for backward compatibility, but it does not replace screen-level `assetUsages[]` for final handoff packages.

For any active transparent asset, record measured `transparentPadding` in either `asset-map.json.assets[].validation` or `asset-quality-audit.json.assets[]`. For chroma-key assets, also record `alphaMethod: chroma-key`, `matteColor`, `candidateMatteScores`, `matteConflictScore`, `matteRisk`, and `matteSelectionReason`. Do not use black, white, gray, off-white, or near-black matte colors. For assets that actually include `includesShadow`, `includesGlow`, reflection, complex soft-edge effects, or separated shadow layers, also record `shadowProfileRef`, `shadowHandling`, and `shadowQuality`. Do not require these shadow fields for clean no-shadow assets; optional `shadowHandling: none` is enough if the no-shadow decision needs to be explicit. `shadowQuality` should be `matches-reference` only after contact-sheet inspection against the approved UI reference.

## screen-map.json

```json
{
  "version": "newui_Vx",
  "targetScreenSize": { "width": 1500, "height": 3262 },
  "screens": [
    {
      "id": "P01",
      "name": "Home",
      "filename": "02-screens/P01-home.png",
      "figmaFrameName": "UI Vx / P01 Home",
      "foundationRefs": {
        "visualSpec": "01-foundation/visual-spec/VISUAL-SPEC-vx.png",
        "componentLibrary": "01-foundation/component-library/COMPONENT-LIBRARY-vx.png",
        "assetLibrary": "01-foundation/asset-library/ASSET-LIBRARY-vx.png"
      },
      "regions": [
        {
          "id": "home.hero",
          "type": "native-simple+page-local-assets",
          "nativeTargets": ["title", "subtitle"],
          "componentRefs": ["component.top-nav.default"],
          "assetRefs": ["asset.page.P01.hero-bg.vx", "asset.page.P01.primary-button-skin.vx"],
          "componentStateAssets": ["asset.page.P01.tab-home-active.vx", "asset.page.P01.tab-test-inactive.vx"],
          "pageLocalAssets": ["asset.page.P01.hero-bg.vx", "asset.page.P01.primary-button-skin.vx"],
          "placementRules": "Use listed assets at exact placement before native text overlays; do not replace with similar shared assets.",
          "notes": "Hero background and button skin are page-local assets; title/subtitle may remain native overlay text."
        }
      ],
      "assetUsages": [
        {
          "assetId": "asset.page.P01.hero-bg.vx",
          "targetPlacement": { "x": 24, "y": 156, "width": 702, "height": 438 },
          "layerOrder": 10,
          "ownership": "asset-with-native-text",
          "alignBy": "contentBBox",
          "placementConfidence": "measured",
          "localPastebackStatus": "passed",
          "localPastebackComparison": "99-working-sources/pasteback-qa/P01/P01-hero-bg-comparison.png"
        },
        {
          "assetId": "asset.page.P01.primary-button-skin.vx",
          "targetPlacement": { "x": 48, "y": 524, "width": 260, "height": 72 },
          "layerOrder": 30,
          "ownership": "asset-with-native-text",
          "alignBy": "contentBBox",
          "placementConfidence": "measured",
          "localPastebackStatus": "passed"
        }
      ],
      "knownRisks": ["hero asset scale", "bottom tab active state"]
    }
  ]
}
```

Rules:

- `assetUsages[]` is required for every active visible asset in `figma-rebuild`, `development-handoff`, source-file rebuild, or pixel-exact mode.
- Each usage must include `assetId`, `targetPlacement`, `layerOrder`, `ownership`, and `alignBy`.
- Use `alignBy: "contentBBox"` for transparent PNGs with padding. Figma reconstruction must align the visible content bounds, not the full PNG canvas.
- Use `placementConfidence: "measured"` when measured from the reference; use `"estimated"` only when exact measurement is not possible and record the risk.
- `localPastebackStatus` must be `passed` before an asset can be `approved`, `repaired-approved`, or `missing-repaired`. If paste-back remains imperfect after the repair limit, keep the asset as `active-best-effort` and record `bestEffortReason` plus the remaining defect.

## page-asset-audit.json

Use this file to prevent the common failure where only the foundation library is extracted and page-specific assets are missed.

```json
{
  "version": "newui_Vx",
  "screens": [
    {
      "screenId": "P04",
      "screenFile": "02-screens/P04-upload-photo.png",
      "nativeSimpleElements": ["top nav text", "text labels", "simple dividers"],
      "componentNativeSimpleElements": ["component.top-nav.structure"],
      "componentSkinAssets": ["asset.page.P04.primary-button-skin.vx", "asset.page.P04.bottom-tab-home-active.vx"],
      "componentStateAssets": ["asset.page.P04.tab-home-active.vx", "asset.page.P04.tab-test-inactive.vx"],
      "sharedAssets": [],
      "pageLocalAssets": [
        {
          "id": "asset.page.P04.guide-cat-back.vx",
          "filename": "03-transparent-assets/page-local/P04/P04-guide-cat-back@2x.png",
          "source": "page-local asset sheet",
          "status": "approved",
          "qaStatus": "approved",
          "scope": "page-local",
          "doNotReplaceWithSimilar": true
        }
      ],
      "vectorIcons": ["back arrow", "chevron"],
      "dynamicContent": ["runtime user avatar if applicable"],
      "packageRequiredComponents": [
        {
          "componentId": "component.nav.primary",
          "type": "bottom-tab",
          "visibleOnThisScreen": false,
          "itemCount": null,
          "requiredStates": ["selected", "unselected"],
          "coverage": "hidden-approved-global",
          "approvedSourceRef": "02-screens/P01-home.png",
          "assetRefs": ["asset.component.nav-container.vx", "asset.component.nav-home-selected.vx", "asset.component.nav-home-unselected.vx"]
        }
      ],
      "notVisibleRequiredComponents": [
        {
          "componentId": "component.nav.primary",
          "reason": "The current screen intentionally hides this app-shell component, but coverage remains required elsewhere in the package.",
          "approvedSourceRef": "02-screens/P01-home.png"
        }
      ],
      "missingAssets": [],
      "exceptions": []
    }
  ]
}
```

Rules:

- Create one audit entry for every screen, including screens that only use native-simple elements. Each entry must also audit package-required components from `requiredComponentRegistry`, even if they are hidden on the current screen.
- `missingAssets` must be empty before completion unless explicitly accepted. Package-required components must use one of these coverage values only: `visible-page-local`, `visible-approved-shared`, `hidden-approved-global`, `notVisibleOnThisScreen`, or `native-only`.
- Package-required components must have page-local coverage, approved shared/component-state coverage, or, when page-local redundancy is not required, an explicit `notVisibleOnThisScreen` record with an approved source reference. When approved component-state assets exist, include them in `assetRefs` even if the component is hidden on the current screen.
- When `perPageRequiredComponentRedundancy` is true, `notVisibleOnThisScreen` only explains placement. It does not satisfy asset coverage by itself; the same audit entry must still include page-local or component-state asset references for the required component.
- If an icon is rebuilt as vector/native, list it in `vectorIcons` so it is not mistaken for an omitted asset.
- In pixel-exact mode, list buttons, tag pills, navigation item states, card skins, hero backgrounds, and section title icons as `componentSkinAssets`, `componentStateAssets`, or `pageLocalAssets` when they include gradient, glow, shadow, embedded icon, or complex styling. For navigation/stateful components, include a state matrix with the actual item count and required states; do not assume a fixed number of tabs or items.
- Do not satisfy `pageLocalAssets` or `componentSkinAssets` with similar assets from another page. Reuse only explicitly referenced `approved-shared` assets.

## generation-log.md

Record final prompts, reference images, style-lock decisions, selected/rejected variants, manual edits, extraction notes, and unresolved risks for Figma rebuild.

## qa-checklist.md

Record pass/fail for package completeness, screen dimensions, foundation consistency, asset inventory completeness, transparent edge quality, naming stability, and handoff readiness.

## asset-quality-audit.json

Use this file to prevent visually invalid assets from reaching Figma rebuild.

```json
{
  "version": "newui_Vx",
  "policy": "strict-page-local-clean-assets",
  "summary": {
    "pageLocalAssetsReviewed": 106,
    "kept": 85,
    "rejected": 21,
    "missingDedicatedAssets": 14
  },
  "assets": [
    {
      "id": "asset.page.P08.style-realistic.vx",
      "filename": "03-transparent-assets/page-local/P08/P08-style-realistic@2x.png",
      "result": "rejected-not-for-figma-source",
      "visualInspectionPassed": false,
      "semanticMatch": false,
      "contactSheet": "05-contact-sheets/page-local/P08-assets-contact-sheet.png",
      "transparentPadding": {
        "left": 0,
        "top": 18,
        "right": 3,
        "bottom": 24,
        "requiredHorizontal": 24,
        "requiredVertical": 24,
        "passed": false
      },
      "shadowProfileRef": "02-screens/P08-reference.png#style-thumbnail",
      "shadowHandling": "baked-in",
      "shadowQuality": "fails-reference-match",
      "reason": "screenshot crop contains UI label/card context; regenerate as clean thumbnail"
    }
  ]
}
```

Rejected assets may remain in `asset-map.json` with `status: rejected` for traceability, but they must not be active references in `screen-map.json` or `page-asset-audit.json`. Active page-local assets require visual QA metadata. Chroma-key assets also require matte-selection metadata and must pass edge-fringe/despill review. Assets without these fields are not ready for Figma rebuild.

For transparent padding, `acceptedPaddingTolerancePx: 1` may be used only when the measured deficit is no more than 1px on any side and visual inspection shows no clipped subject, shadow, glow, or antialias edge. Larger deficits require repair/regeneration or an explicit accepted exception.

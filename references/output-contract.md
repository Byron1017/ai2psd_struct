# Output Contract

Use this contract when the user wants UI image generation that will later become editable Figma source.

## Required Package Shape

```text
pic/ui/<version>/
  01-foundation/
    visual-spec/
    component-library/
    asset-library/
  02-screens/
  03-transparent-assets/
    shared-approved/
    component-states/
    icons/
    brand-assets/
    subjects/
    decorations/
    thumbnails/
    waveforms/
    page-local/
      P01/
      P02/
      ...
  04-manifest/
    package-config.json
    asset-map.json
    screen-map.json
    page-asset-audit.json
    generation-log.md
    qa-checklist.md
    asset-quality-audit.json
  05-contact-sheets/
    shared-assets-contact-sheet.png
    page-local/
      P01-assets-contact-sheet.png
      P02-assets-contact-sheet.png
      ...
```

Do not create foundation folders as empty theater. If clean foundation boards exist, treat them as source material for Figma reconstruction. If approved references exist, foundation boards must inherit from those references instead of inventing a new visual system.

## Naming

Use stable, sortable names:

- Screens: `P01-home.png`, `P02-upload-photo.png`, `P03-profile.png`
- Visual spec: `VISUAL-SPEC-v<version>.png`
- Component library: `COMPONENT-LIBRARY-v<version>.png`
- Asset library: `ASSET-LIBRARY-v<version>.png`
- Shared-approved assets: `<category>-<role>-<variant>@2x.png`
- Page-local assets: `P<page>-<region>-<role>@2x.png`
- Component-state assets: `P<page>-<component>-<item>-<state>@2x.png` or `P<page>-<component>-<state>@2x.png` when the component has no item dimension, unless promoted to shared-approved

Keep names in English slug form even when UI text is Chinese.

## Size Contract

Dimensions are negotiated per project, then recorded in `04-manifest/package-config.json`. Do not use fixed mobile, mini-app, tablet, or desktop dimensions unless confirmed.

Ask or infer these values before generation:

| Field | Meaning | Example only |
| --- | --- | --- |
| `platform` | Target surface | `mini-app`, `mobile-app`, `desktop-web` |
| `logicalScreenSize` | Design-space canvas | `{ "width": 750, "height": 1631 }` |
| `scale` | Delivery multiplier | `2` for `@2x` |
| `targetScreenSize` | Actual generated screen pixels | `{ "width": 1500, "height": 3262 }` |
| `foundationBoardSize` | Visual/component/asset board pixels | `{ "width": 3072, "height": 2048 }` only when confirmed |
| `deliveryMode` | Rough exploration or final Figma/development handoff | `figma-rebuild` |
| `handoffPurpose` | Final package purpose | `program-development` for development handoff |
| `generatePageLocalAssets` | Every final screen gets a complete per-screen asset pass | Must be `true` for Figma reconstruction/development handoff |
| `resourcePackageMode` | Whether assets are generated synchronously with each final image | `synchronized-full`, `rough-no-assets`, or `user-declined-assets` |
| `pixelExactAssetMode` | Every visually complex element needs a generated asset for reconstruction | `true` when the user asks for 100% restoration or no missing assets |
| `pageLocalRedundantAssets` | Every screen gets its own complete asset set before shared promotion | `true` in pixel-exact mode |
| `noSimilarAssetSubstitution` | Visually similar assets from other folders are forbidden as replacements | `true` in pixel-exact mode |
| `requiredComponentRegistry` | Package-level common/app-shell components that need coverage even when hidden on a page | list bottom tabs/navs/common skins/stateful components when applicable |
| `perPageRequiredComponentRedundancy` | Whether every page must carry page-local copies of required component assets | `true` when the user wants self-contained per-page reconstruction |

## File Expectations

Screen references:

- Exact negotiated target screen size, derived from logical size and scale.
- No external screenshots or canvas contamination.
- Full UI visible; no cropped status bar, bottom tab, or edge content.

Foundation boards:

- Clean board image, not a collage of inconsistent screen leftovers.
- Visible labels for token/component/asset names.
- Examples should match the screen style exactly.

Transparent assets and component-skin assets:

- PNG or WebP with alpha when possible.
- Active image assets must be atomic development units: a single icon/state, decoration, generated subject, thumbnail/photo, background art without editable controls, visual skin/state, shadow/glow, or similar standalone unit. Do not create active assets that a developer would need to cut again.
- Include or separate shadow/glow according to the approved UI reference shadow profile when that effect is part of a 3D, skeuomorphic, game-like, cute, or gradient visual. Do not apply a generic shadow style.
- If generated through chroma key, store only the final alpha PNG in the package unless the user asks for source-key images too.
- Include measured transparent safety padding but no stray background or matte pixels. Padding must be measured from the alpha bounding box to the PNG canvas edge and must satisfy the asset-class minimum defined in `references/transparent-asset-checklist.md`. Chroma-key assets must record the selected matte color, candidate scores, conflict score, risk, and selection reason.

Manifests:

- Must list every final screen and every reusable/page-local/component-state image asset.
- Must record `handoffPurpose`, `assetGranularity`, and `developmentUsable` for active image assets in final Figma/development handoff packages.
- Must keep QA status separate from reuse scope: use `qaStatus` for `approved`, `repaired-approved`, `missing-repaired`, `active-best-effort`, `needs-regeneration`, or `rejected`; use `scope` for `page-local`, `candidate`, `promoted`, or `approved-shared`.
- Must identify native-simple elements, component-skin assets, page-local assets required for pixel match, vector icons, and dynamic-content exceptions.
- Must include `screen-map.json.screens[].assetUsages[]` with target placement, layering, ownership, and `alignBy: "contentBBox"` for every active visible asset required for pixel match.
- Must include contact-sheet evidence for shared assets and every page-local asset folder before assets become active references.
- One-image-one-asset-package evidence is required for every final image unless the user explicitly chose rough exploration or no resource package.

## Per-Screen Asset Package Requirement

For multi-screen UI generation intended for Figma reconstruction or development handoff, every final screen needs a matching complete page-local asset pass. In pixel-exact mode this pass is intentionally redundant: each screen gets its own full asset set before any asset is promoted to shared-approved.

For each screen `Pxx`:

```text
03-transparent-assets/page-local/Pxx/
  Pxx-<region>-<asset-name>@2x.png
```

Examples:

- `P01-hero-bg@2x.png`
- `P01-hero-primary-button-skin@2x.png`
- `P01-hot-tag-night-skin@2x.png`
- `P01-nav-home-active@2x.png` or `P01-bottom-tab-home-active@2x.png`
- `P10-sound-card-waveform@2x.png`

Do not treat the foundation asset library as complete coverage for all screens. A screen with no page-local complex visuals still needs an audit entry proving that everything is native-simple, approved-shared, vector, dynamic content, or explicitly not visible on that screen. Do not use similar assets from other pages as proof of coverage. For navigation/stateful components, record the actual item count and required states; never assume a fixed number of tabs or items. If a package-level required component exists, every screen audit must either include its page-local/shared asset coverage or explicitly mark it `notVisibleOnThisScreen` with a valid approved source reference.

In pixel-exact page-local redundancy mode, page-local coverage is required for every component listed in `requiredComponentRegistry` unless the manifest explicitly records an accepted exception. Hidden common/app-shell components are still audited; hiding a component on the current screen does not remove it from package coverage. `notVisibleOnThisScreen` may explain placement, but it must not be used as the only proof of asset coverage when `perPageRequiredComponentRedundancy` is true.

Each screen must be represented in `page-asset-audit.json` with:

- `screenId`
- `screenFile`
- `nativeSimpleElements`
- `componentNativeSimpleElements`
- `componentSkinAssets`
- `componentStateAssets`
- `sharedAssets`
- `pageLocalAssets`
- `vectorIcons`
- `dynamicContent`
- `missingAssets`
- `packageRequiredComponents`
- `notVisibleRequiredComponents`
- `exceptions`

`missingAssets` must be empty before the package is called complete, unless the user explicitly accepts the exceptions. Every active page-local asset must also have `visualInspectionPassed: true`, `semanticMatch: true`, and a `contactSheet` path in `asset-quality-audit.json`.

## Strong Check Requirement

Before final handoff, run the package validator if available. A package fails strong check when:

- final handoff mode has no explicit `styleAuthority` of `approved-reference` or `new-exploration`;
- `approved-reference` mode has no non-empty `approvedReferenceSet` or no `styleDriftPolicy: reject-unless-user-approved`;
- any pixel-exact package lacks `pixelExactAssetMode`, `pageLocalRedundantAssets`, or `noSimilarAssetSubstitution` in `package-config.json`;
- any screen in `screen-map.json` is missing;
- any screen lacks a `page-asset-audit.json` entry;
- any audit entry has non-empty `missingAssets` without an accepted exception;
- any package-required component lacks asset coverage, an approved-shared reference, or, when sharing is allowed, an explicit `notVisibleOnThisScreen` entry;
- any package-required component uses a coverage value outside `visible-page-local`, `visible-approved-shared`, `hidden-approved-global`, `notVisibleOnThisScreen`, or `native-only`;
- any `perPageRequiredComponentRedundancy` package uses `notVisibleOnThisScreen` as the only coverage for a package-required component;
- any visually complex button, tab, chip, card skin, hero background, section icon, or decorative mark is marked native-simple without an explicit accepted exception;
- any `pageLocalAssets.filename`, `componentSkinAssets.filename`, or `componentStateAssets.filename` does not exist on disk;
- any page-local PNG has no alpha channel unless it is an intentional rectangular bitmap thumbnail/photo;
- any active transparent asset fails the measured transparent safety padding rule without an accepted exception;
- any active transparent asset misses the measured padding rule by no more than 1px without either `acceptedPaddingTolerancePx: 1` or an accepted exception;
- any active asset lacks development-handoff metadata in a final package: `handoffPurpose: "program-development"`, atomic `assetGranularity`, and `developmentUsable: true`;
- any active visible asset used by a screen lacks `screen-map.assetUsages[]` placement metadata, local paste-back status, or a best-effort defect record;
- any active asset is a large UI-region slice, whole card/list/tab/hero/app-shell image, modal body, or mixed text/control bitmap;
- any active asset that actually includes shadow, glow, reflection, complex soft-edge effects, or a separated shadow layer lacks `shadowProfileRef`, `shadowHandling`, or `shadowQuality` metadata; clean no-shadow assets do not need these fields;
- any generated screen has dimensions that differ from the configured delivery dimensions;
- any active page-local asset lacks visual inspection metadata;
- any page-local contact sheet is missing;
- any inspected asset shows neighboring asset contamination, unintended UI pollution, or semantic mismatch;
- any inspected asset shows clipped subject pixels, clipped shadow/glow, matte-colored fringe, eaten same-color subject pixels, or a shadow/glow profile that does not match the approved UI reference;
- any active asset is sourced from a full-screen UI screenshot and is not approved avatar/photo/example-thumbnail bitmap content;
- any page asset requirement is satisfied by a visually similar asset from another page without explicit `approved-shared` status and current-screen manifest reference.

## Asset Quality Audit

For multi-screen packages, create `04-manifest/asset-quality-audit.json` after generating the asset contact sheet. It must identify every page-local asset as one of:

- `approved-clean-or-acceptable-thumbnail`: safe for Figma rebuild as bitmap content.
- `approved-pixel-skin`: safe for Figma rebuild as a visual skin or component-state asset.
- `rejected-not-for-figma-source`: exists only for traceability; must not be referenced by screen-map or page-asset-audit active assets.
- `needs-dedicated-generation`: generate as a standalone transparent asset before final Figma handoff.

Full-screen UI screenshot crops default to rejected/reference-only. They may become active only for approved avatar/photo/example-thumbnail bitmap content that satisfies the screenshot-crop exception in `SKILL.md`.

Large UI-region slices are not a best-effort fallback. If an atomic asset cannot pass after the retry limit, keep the closest atomic/native result, record the defect, and continue; do not activate a whole-card, whole-list, whole-tab, whole-hero, or mixed UI screenshot to hide the problem.

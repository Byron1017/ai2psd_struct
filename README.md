# ai2psd-struct

`ai2psd-struct` is a Codex skill for generating structured UI design-image packages that can later be rebuilt into editable Figma source.

It is designed for workflows where a UI image is not enough. The skill produces synchronized screen references, foundation boards, transparent atomic assets, page-local resources, component-state assets, manifests, QA records, and handoff metadata so downstream tools such as `ai2figma-struct` can reconstruct screens without guessing, substituting similar assets, or relying on large flattened screenshot slices.

## What It Does

`ai2psd-struct` helps Codex create development-usable UI source packages:

- UI screen reference images
- Visual spec, component library, and asset library boards
- Shared transparent assets
- Complete per-screen page-local assets
- Component-state assets for navigation, tabs, buttons, chips, cards, badges, and other repeated UI states
- Asset contact sheets for visual QA
- Mapping manifests for Figma reconstruction
- Repair logs and known-defect records
- Handoff notes for `ai2figma-struct`

The priority order is:

1. Development-usable assets and structure
2. Editable Figma source reconstruction
3. Pixel-level visual closeness

Pixel matching is treated as a QA target, not a reason to flatten the interface into bitmap chunks.

## When To Use It

Use this skill when you want Codex to generate or organize UI images that must later become editable design source, especially when the request includes:

- Figma reconstruction
- Source-file rebuild
- Pixel-level restoration
- Development handoff
- Complete asset packages
- Atomic transparent assets
- Page-local resources
- Visual QA and mapping manifests

For quick mood exploration or one-off concept images, the full resource package can be skipped if the user explicitly does not need reconstruction assets.

## Pipeline

```text
Design brief
-> Style lock / visual tokens
-> Foundation boards
-> UI screen references
-> Transparent assets and cutouts
-> Mapping manifests
-> QA inventory
-> Handoff to ai2figma-struct
```

The skill is usually used before `ai2figma-struct`:

1. `ai2psd-struct` generates the structured image package.
2. `ai2figma-struct` consumes that package to rebuild editable Figma layers.

## Output Structure

For project-bound work, the skill expects or produces a package shaped like this:

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

Important manifest files:

- `package-config.json`: platform, canvas size, delivery scale, board size, delivery mode, and package policy
- `asset-map.json`: asset identity, dimensions, alpha status, source, ownership, content bounds, QA status, repair status, and visual-effect flags
- `screen-map.json`: screen inventory, native rebuild targets, asset usages, placements, ownership, layer order, and known risks
- `page-asset-audit.json`: per-screen inventory of visible assets and package-required components
- `asset-quality-audit.json`: visual inspection results, repair attempts, contact sheets, paste-back QA, and best-effort defects
- `generation-log.md`: prompts, references, accepted/rejected variants, and style decisions
- `qa-checklist.md`: final package checks and handoff notes

## Core Rules

- Generate design references and reconstruction assets together.
- Lock the visual style before creating batches of screens.
- Do not let each screen invent its own icons, tab bars, cards, subject style, or brand assets.
- Prefer atomic assets over large screenshot slices.
- Do not use whole cards, whole tab bars, whole lists, modal bodies, or mixed text/control regions as active development assets.
- Treat complex buttons, tabs, chips, badges, cards, navigation items, icons, shadows, glow, glass, texture, and 3D visuals as assets unless they are clearly simple native UI.
- Use page-local assets first in pixel-exact mode; promote shared assets only after QA.
- Record quality separately from scope: `qaStatus` should describe approval state, while `scope` should describe placement such as `page-local` or `approved-shared`.
- Repair failed assets before handoff. If repair fails after the retry limit, keep the closest development-usable atomic result and mark it `active-best-effort`.

## QA Status Values

Use these values consistently in manifests and audits:

- `approved`: accepted on the first successful QA pass
- `repaired-approved`: failed at least once, then passed after repair
- `missing-repaired`: originally missing, then generated or extracted and accepted
- `active-best-effort`: still imperfect after retry limit, but selected so the workflow can continue
- `needs-regeneration`: known to be inadequate and not yet repaired
- `rejected`: must not be used for reconstruction

Do not mark `active-best-effort` assets as `approved`.

## Transparent Asset Rules

Transparent assets must be development-usable atomic units. They should have:

- Clean alpha or clean chroma-key removal
- No matte-colored fringe
- No eaten subject edges
- No card/background pollution
- No neighboring UI contamination
- Enough transparent safety padding
- Measured `contentBBox`
- Manifest placement metadata when used on a screen
- Contact-sheet QA
- Local paste-back QA in Figma-rebuild or development-handoff mode

When chroma-key removal is needed, choose the matte color per asset. Do not default to green screen.

## Installation

### Manual Codex Skill Install

Clone this repository into your Codex skills directory:

```bash
git clone https://github.com/<owner>/ai2psd-struct.git ~/.codex/skills/ai2psd-struct
```

On Windows PowerShell:

```powershell
git clone https://github.com/<owner>/ai2psd-struct.git "$env:USERPROFILE\.codex\skills\ai2psd-struct"
```

Restart Codex after installing or updating the skill.

### Install From npm

Codex skills are loaded from the Codex skills directory, not directly from `node_modules`. An npm package therefore needs an installer script that copies this skill into:

```text
~/.codex/skills/ai2psd-struct
```

Recommended user command after publishing:

```bash
npm install -g @<scope>/ai2psd-struct
```

The package should run a `postinstall` script, or expose a CLI command, that installs the skill files into the Codex skills directory.

## npm Publishing Checklist

To make this repository installable through npm:

1. Add a `package.json`.
2. Add an installer script, for example `bin/install.js`.
3. Include `SKILL.md`, `references/`, `scripts/`, and `agents/` in the published package.
4. Test the package locally with `npm pack`.
5. Install the packed `.tgz` file globally and confirm the skill appears under `~/.codex/skills/ai2psd-struct`.
6. Publish to npm with `npm publish --access public`.
7. Add the npm install command to this README.

Example `package.json`:

```json
{
  "name": "@<scope>/ai2psd-struct",
  "version": "0.1.0",
  "description": "Codex skill for generating structured UI design-image packages for editable Figma reconstruction.",
  "license": "MIT",
  "type": "module",
  "files": [
    "SKILL.md",
    "references",
    "scripts",
    "agents",
    "bin"
  ],
  "bin": {
    "ai2psd-struct-skill": "./bin/install.js"
  },
  "scripts": {
    "postinstall": "node ./bin/install.js --postinstall"
  },
  "keywords": [
    "codex",
    "codex-skill",
    "figma",
    "ui-design",
    "design-handoff",
    "ai2figma"
  ]
}
```

Example install behavior:

```text
package install location
-> copy SKILL.md
-> copy references/
-> copy scripts/
-> copy agents/
-> ~/.codex/skills/ai2psd-struct
```

## Local npm Test Flow

From the repository root:

```bash
npm pack
npm install -g ./<generated-package-name>.tgz
```

Then confirm the skill exists:

```bash
ls ~/.codex/skills/ai2psd-struct
```

On Windows PowerShell:

```powershell
Get-ChildItem "$env:USERPROFILE\.codex\skills\ai2psd-struct"
```

## Suggested Prompt

```text
Use ai2psd-struct to generate a development-handoff UI package for this product.
Target platform: mobile app.
Canvas: 390x844 @2x.
Delivery mode: figma-rebuild.
Generate foundation boards, screen references, shared transparent assets, page-local assets, manifests, QA audits, and handoff notes for ai2figma-struct.
```

## Relationship To ai2figma-struct

`ai2psd-struct` produces the structured package. `ai2figma-struct` consumes it.

The package should be complete enough that `ai2figma-struct` can rebuild native structure, place atomic assets using manifest metadata, preserve known risks, and avoid substituting similar-looking assets.

## License

Add your license here, for example MIT.

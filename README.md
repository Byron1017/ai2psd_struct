# ai2psd-struct

`ai2psd-struct` is an agent-agnostic skill for generating structured UI design-image packages that can later be rebuilt into editable Figma source.

It is designed for AI agents that need to create more than a flat UI mockup. The skill defines a production workflow for synchronized screen references, foundation boards, transparent atomic assets, page-local resources, component-state assets, manifests, QA records, repair logs, and handoff metadata.

Downstream reconstruction tools, including `ai2figma-struct`, can consume these packages to rebuild editable Figma layers without guessing, substituting similar assets, inventing inconsistent components, or relying on large flattened screenshot slices.

## What It Does

`ai2psd-struct` helps AI agents create development-usable UI source packages:

- UI screen reference images
- Visual spec, component library, and asset library boards
- Shared transparent assets
- Complete per-screen page-local assets
- Component-state assets for navigation, tabs, buttons, chips, cards, badges, and other repeated UI states
- Asset contact sheets for visual QA
- Mapping manifests for editable design reconstruction
- Repair logs and known-defect records
- Handoff notes for downstream Figma reconstruction

The priority order is:

1. Development-usable assets and structure
2. Editable Figma source reconstruction
3. Pixel-level visual closeness

Pixel matching is treated as a QA target, not a reason to flatten the interface into bitmap chunks.

## Who Can Use It

This repository is not tied to one AI agent runtime.

Any agent, IDE assistant, automation runner, or design-generation workflow can use this skill if it can read the package files and follow the workflow contract.

Typical hosts include:

- Codex-style skill runtimes
- Claude-style project or skill folders
- Cursor or IDE agent rule/workflow folders
- Custom AI-agent systems
- Internal design automation pipelines
- MCP-like agent toolchains

The skill is intentionally portable. The installer may copy the package into a specific agent's skill directory, but the workflow itself is agent-neutral.

## When To Use It

Use this skill when an AI agent needs to generate or organize UI images that must later become editable design source, especially when the request includes:

- Figma reconstruction
- Source-file rebuild
- Pixel-level restoration
- Development handoff
- Complete asset packages
- Atomic transparent assets
- Page-local resources
- Component-state coverage
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
-> Handoff to ai2figma-struct or another reconstruction workflow
```

The skill is commonly used before `ai2figma-struct`:

1. `ai2psd-struct` generates the structured image package.
2. `ai2figma-struct` consumes that package to rebuild editable Figma layers.

Other reconstruction workflows can also consume the package if they follow the same manifest and asset contracts.

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

### Install From npm

After the package is published, install it globally:

```bash
npm install -g @<scope>/ai2psd-struct
```

This package should expose a CLI command:

```bash
ai2psd-struct
```

Because different AI agents store skills in different locations, the npm package should not assume one fixed runtime. Instead, use an explicit install command:

```bash
ai2psd-struct install --target codex
ai2psd-struct install --target claude
ai2psd-struct install --target cursor
ai2psd-struct install --path ./skills/ai2psd-struct
```

Recommended behavior:

```text
npm package
-> contains SKILL.md
-> contains references/
-> contains scripts/
-> contains agents/
-> installer copies or links files into the selected agent skill directory
```

The `--path` option should always be supported so users can install the skill into any custom agent runtime.

### Manual Install

You can also clone this repository into any agent-readable skills directory:

```bash
git clone https://github.com/<owner>/ai2psd-struct.git ./skills/ai2psd-struct
```

For Codex-compatible local skill folders, one possible install path is:

```bash
git clone https://github.com/<owner>/ai2psd-struct.git ~/.codex/skills/ai2psd-struct
```

On Windows PowerShell:

```powershell
git clone https://github.com/<owner>/ai2psd-struct.git "$env:USERPROFILE\.codex\skills\ai2psd-struct"
```

Restart or reload your agent runtime after installing or updating the skill.

## npm Publishing Checklist

To make this repository installable through npm:

1. Add a `package.json`.
2. Add a CLI installer script, for example `bin/ai2psd-struct.js`.
3. Support explicit install targets such as `--target codex` and `--path <directory>`.
4. Include `SKILL.md`, `references/`, `scripts/`, and `agents/` in the published package.
5. Test the package locally with `npm pack`.
6. Install the packed `.tgz` file globally and confirm the installer can copy files into a custom skill directory.
7. Publish to npm with `npm publish --access public`.
8. Add the final npm package name to this README.

Recommended `package.json`:

```json
{
  "name": "@<scope>/ai2psd-struct",
  "version": "0.1.0",
  "description": "Agent-agnostic skill for generating structured UI design-image packages for editable Figma reconstruction.",
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
    "ai2psd-struct": "./bin/ai2psd-struct.js"
  },
  "keywords": [
    "ai-agent",
    "agent-skill",
    "figma",
    "ui-design",
    "design-handoff",
    "ai2figma",
    "structured-assets"
  ]
}
```

Avoid default `postinstall` writes into a specific agent directory. Explicit installation is safer and more portable:

```bash
ai2psd-struct install --target codex
ai2psd-struct install --path ~/.some-agent/skills/ai2psd-struct
```

## Suggested CLI Behavior

The npm CLI can be simple:

```text
ai2psd-struct install --target codex
ai2psd-struct install --target claude
ai2psd-struct install --target cursor
ai2psd-struct install --path <directory>
ai2psd-struct doctor
ai2psd-struct info
```

Suggested command meanings:

- `install --target <name>`: install into a known agent skill directory
- `install --path <directory>`: install into a custom directory
- `doctor`: check whether required files exist after installation
- `info`: print package version, included files, and supported install targets

## Local npm Test Flow

From the repository root:

```bash
npm pack
npm install -g ./<generated-package-name>.tgz
```

Then test installation into a temporary directory:

```bash
ai2psd-struct install --path ./tmp-skills/ai2psd-struct
ai2psd-struct doctor --path ./tmp-skills/ai2psd-struct
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

The package should be complete enough that `ai2figma-struct` or another compatible reconstruction workflow can rebuild native structure, place atomic assets using manifest metadata, preserve known risks, and avoid substituting similar-looking assets.

## Repository Contents

```text
SKILL.md
references/
scripts/
agents/
```

- `SKILL.md`: main workflow instructions and gates
- `references/`: detailed contracts, prompt patterns, manifest schema, transparent asset checks, and handoff guidance
- `scripts/`: validation and local paste-back QA helpers
- `agents/`: optional agent-specific metadata or adapter files

## License

Add your license here, for example MIT.

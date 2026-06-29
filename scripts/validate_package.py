#!/usr/bin/env python3
"""Validate an ai2psd-struct UI package."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def image_size(path: Path) -> tuple[int, int] | None:
    if Image is None:
        return None
    try:
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def read_size(obj: dict[str, Any] | None, key: str) -> tuple[int, int] | None:
    if not isinstance(obj, dict):
        return None
    value = obj.get(key)
    if not isinstance(value, dict):
        return None
    width = int(value.get("width", 0) or 0)
    height = int(value.get("height", 0) or 0)
    if width > 0 and height > 0:
        return (width, height)
    return None


def read_scale(package_config: dict[str, Any]) -> float:
    try:
        scale = float(package_config.get("scale", 2) or 2)
    except (TypeError, ValueError):
        scale = 2.0
    return scale if scale > 0 else 2.0


def required_transparent_padding(asset: dict[str, Any], bbox: tuple[int, int, int, int], scale: float) -> tuple[int, int, str]:
    left, top, right, bottom = bbox
    alpha_width = max(1, right - left)
    alpha_height = max(1, bottom - top)
    long_edge = max(alpha_width, alpha_height)
    scale_factor = scale / 2.0
    category = str(asset.get("category", "")).lower()
    role = str(asset.get("role", "")).lower()
    has_shadow = bool(asset.get("includesShadow") or asset.get("includesGlow"))
    wide_skin_categories = {"button-skin", "card-skin", "tab-container", "tag-skin", "chip-skin", "nav-container"}
    simple_icon_categories = {"tab-icon-state", "icon-candidate", "vector-icon"}
    complex_categories = {
        "subject-render",
        "hero-background",
        "brand-asset",
        "decoration",
        "empty-state",
        "illustration",
        "mascot",
        "photo-cutout",
    }

    if category in wide_skin_categories or "skin" in category:
        required_x = max(round(24 * scale_factor), round(alpha_width * 0.04))
        vertical_constant = 24 if has_shadow else 12
        vertical_ratio = 0.06 if has_shadow else 0.04
        required_y = max(round(vertical_constant * scale_factor), round(alpha_height * vertical_ratio))
        return required_x, required_y, "wide-ui-skin"

    if has_shadow or category in complex_categories or any(token in role for token in ["3d", "mascot", "illustration", "shadow", "glow"]):
        required = max(round(24 * scale_factor), round(long_edge * 0.10))
        return required, required, "3d-shadow-glow"

    if category in simple_icon_categories or "icon" in category:
        required = max(round(12 * scale_factor), round(long_edge * 0.08))
        return required, required, "simple-icon"

    required = max(round(12 * scale_factor), round(long_edge * 0.08))
    return required, required, "default-transparent"


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def is_active_asset(asset: dict[str, Any]) -> bool:
    status = str(asset.get("status", "")).lower()
    qa_status = str(asset.get("qaStatus", "") or status).lower()
    return status not in {"rejected", "reference-only"} and qa_status not in {"rejected", "reference-only", "needs-regeneration"}


def is_thumbnail_like(asset: dict[str, Any]) -> bool:
    text = " ".join(
        str(asset.get(key, "")).lower()
        for key in ("category", "role", "id", "filename")
    )
    return any(token in text for token in ("avatar", "photo", "thumbnail", "preview", "wallpaper"))


def has_invalid_region_slice_hint(asset: dict[str, Any]) -> bool:
    text = " ".join(
        str(asset.get(key, "")).lower()
        for key in ("category", "role", "assetGranularity", "id", "filename")
    )
    invalid_tokens = (
        "ui-region",
        "region-slice",
        "screen-slice",
        "full-screen",
        "whole-card",
        "whole-list",
        "whole-tab",
        "whole-hero",
        "app-shell",
        "mixed-ui",
        "mixed-text-control",
        "modal-body",
    )
    return any(token in text for token in invalid_tokens)


def read_box(obj: dict[str, Any] | None) -> tuple[float, float, float, float] | None:
    if not isinstance(obj, dict):
        return None
    try:
        x = float(obj.get("x", 0))
        y = float(obj.get("y", 0))
        width = float(obj.get("width", 0))
        height = float(obj.get("height", 0))
    except (TypeError, ValueError):
        return None
    if width <= 0 or height <= 0:
        return None
    return (x, y, width, height)


def asset_content_bbox(asset: dict[str, Any]) -> tuple[float, float, float, float] | None:
    bbox = read_box(asset.get("contentBBox"))
    if bbox:
        return bbox
    validation = asset.get("validation") if isinstance(asset.get("validation"), dict) else {}
    return read_box(validation.get("contentBBox"))


def usage_list(screen: dict[str, Any]) -> list[dict[str, Any]]:
    usages = screen.get("assetUsages") or []
    if isinstance(usages, list):
        return [usage for usage in usages if isinstance(usage, dict)]
    return []


def usage_local_pasteback_status(usage: dict[str, Any]) -> str:
    return str(usage.get("localPastebackStatus", "") or usage.get("pastebackStatus", "")).lower()


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_package.py <package-root>")
        return 2
    root = Path(sys.argv[1])
    errors: list[str] = []
    warnings: list[str] = []

    manifest_root = root / "04-manifest"
    package_config_path = manifest_root / "package-config.json"
    screen_map_path = manifest_root / "screen-map.json"
    asset_map_path = manifest_root / "asset-map.json"
    audit_path = manifest_root / "page-asset-audit.json"
    quality_path = manifest_root / "asset-quality-audit.json"

    for required in [screen_map_path, asset_map_path, audit_path, quality_path]:
        if not required.exists():
            errors.append(f"missing manifest: {rel(required, root)}")

    if errors:
        print("\n".join(errors))
        return 1

    package_config = load_json(package_config_path) if package_config_path.exists() else {}
    screen_map = load_json(screen_map_path)
    asset_map = load_json(asset_map_path)
    audit = load_json(audit_path)
    quality = load_json(quality_path)

    if not package_config_path.exists():
        warnings.append("missing package-config.json; falling back to manifest sizes and skipping unknown configured size checks")

    target_size = read_size(package_config, "targetScreenSize") or read_size(screen_map, "targetScreenSize")
    foundation_size = read_size(package_config, "foundationBoardSize") or read_size(screen_map, "foundationBoardSize")
    delivery_scale = read_scale(package_config)
    generate_foundation = package_config.get("generateFoundationBoards", None)
    generate_page_local = package_config.get("generatePageLocalAssets", True)
    delivery_mode = str(package_config.get("deliveryMode", "")).lower()
    final_delivery = delivery_mode in {"figma-rebuild", "development-handoff", "figma-rebuild/development-handoff"}
    pixel_exact = bool(package_config.get("pixelExactAssetMode"))
    page_local_redundant = bool(package_config.get("pageLocalRedundantAssets"))
    no_similar_substitution = bool(package_config.get("noSimilarAssetSubstitution"))
    per_page_required_redundancy = bool(package_config.get("perPageRequiredComponentRedundancy"))
    required_registry_raw = package_config.get("requiredComponentRegistry", [])
    if not isinstance(required_registry_raw, list):
        errors.append("package-config requiredComponentRegistry must be a list")
        required_registry_raw = []
    required_component_ids = [
        str(component.get("componentId"))
        for component in required_registry_raw
        if isinstance(component, dict) and component.get("componentId")
    ]
    strict_visual_qa = package_config.get("strictVisualQa")
    if strict_visual_qa is None:
        strict_visual_qa = final_delivery

    style_authority = str(package_config.get("styleAuthority", "")).lower()
    if final_delivery:
        if style_authority not in {"approved-reference", "new-exploration"}:
            errors.append("package-config styleAuthority must be approved-reference or new-exploration for final handoff packages")
        if style_authority == "approved-reference":
            approved_refs = package_config.get("approvedReferenceSet") or []
            if not isinstance(approved_refs, list) or not approved_refs:
                errors.append("approved-reference mode requires non-empty approvedReferenceSet in package-config.json")
            if package_config.get("styleDriftPolicy") != "reject-unless-user-approved":
                errors.append("approved-reference mode requires styleDriftPolicy=reject-unless-user-approved")
        if "requiredComponentRegistry" not in package_config:
            errors.append("final handoff packages must include requiredComponentRegistry in package-config.json; use an empty list only when no common/stateful components are required")
        if pixel_exact:
            if not page_local_redundant:
                errors.append("pixelExactAssetMode requires pageLocalRedundantAssets=true")
            if not no_similar_substitution:
                errors.append("pixelExactAssetMode requires noSimilarAssetSubstitution=true unless the user explicitly accepted similar-asset substitution")

    if target_size is None:
        warnings.append("targetScreenSize is not configured; screen dimension checks are skipped")
    if foundation_size is None:
        warnings.append("foundationBoardSize is not configured; foundation board dimension checks are skipped")

    foundation_refs = {
        "visual-spec": root / "01-foundation" / "visual-spec",
        "component-library": root / "01-foundation" / "component-library",
        "asset-library": root / "01-foundation" / "asset-library",
    }
    for label, folder in foundation_refs.items():
        if not folder.exists():
            if generate_foundation is True:
                errors.append(f"foundation folder missing: {rel(folder, root)}")
            else:
                warnings.append(f"foundation folder missing: {rel(folder, root)}")
            continue
        finals = [p for p in folder.glob("*.png") if "source" not in p.stem.lower() and "draft" not in p.stem.lower()]
        if not finals:
            if generate_foundation is False:
                warnings.append(f"foundation final PNG missing: {rel(folder, root)}")
            else:
                errors.append(f"foundation final PNG missing: {rel(folder, root)}")
            continue
        for fpath in finals:
            size = image_size(fpath)
            if size and foundation_size and size != foundation_size:
                errors.append(f"foundation wrong size {size}, expected {foundation_size}: {rel(fpath, root)}")

    audit_by_id = {s.get("screenId"): s for s in audit.get("screens", [])}
    screen_ids = [s.get("id") for s in screen_map.get("screens", [])]
    asset_files = set()
    quality_by_id = {a.get("id"): a for a in quality.get("assets", [])}
    asset_by_id = {a.get("id"): a for a in asset_map.get("assets", []) if a.get("id")}
    asset_usage_by_id: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    allowed_coverage_values = {
        "visible-page-local",
        "visible-approved-shared",
        "hidden-approved-global",
        "notVisibleOnThisScreen",
        "native-only",
    }

    for screen in screen_map.get("screens", []):
        sid = str(screen.get("id", "") or "")
        raw_usages = screen.get("assetUsages")
        if final_delivery and raw_usages is not None and not isinstance(raw_usages, list):
            errors.append(f"screen assetUsages must be a list when present: {sid}")
        for usage in usage_list(screen):
            asset_id = usage.get("assetId")
            if not asset_id:
                errors.append(f"screen assetUsage missing assetId: {sid}")
                continue
            asset_usage_by_id.setdefault(str(asset_id), []).append((sid, usage))
            asset = asset_by_id.get(asset_id)
            if asset is None:
                errors.append(f"screen assetUsage assetId not in asset-map: {sid}: {asset_id}")
                continue
            if str(asset.get("qaStatus", "")).lower() == "rejected" or str(asset.get("status", "")).lower() == "rejected":
                errors.append(f"screen assetUsage references rejected asset: {sid}: {asset_id}")
            placement = read_box(usage.get("targetPlacement"))
            if final_delivery and placement is None:
                errors.append(f"screen assetUsage missing valid targetPlacement: {sid}: {asset_id}")
            if final_delivery and usage.get("layerOrder") is None:
                errors.append(f"screen assetUsage missing layerOrder: {sid}: {asset_id}")
            ownership = usage.get("ownership")
            if final_delivery and ownership not in {"asset-only", "asset-with-native-text", "native-with-asset-icon", "native-only"}:
                errors.append(f"screen assetUsage has invalid or missing ownership: {sid}: {asset_id}: {ownership}")
            align_by = usage.get("alignBy")
            if final_delivery and asset.get("alpha") is True and align_by != "contentBBox":
                errors.append(f"transparent assetUsage must use alignBy=contentBBox: {sid}: {asset_id}: {align_by}")
            bbox = asset_content_bbox(asset)
            if final_delivery and bbox is None:
                errors.append(f"screen assetUsage asset missing contentBBox: {sid}: {asset_id}")
            if placement and bbox:
                _, _, bbox_width, bbox_height = bbox
                _, _, target_width, target_height = placement
                if bbox_width > 0 and bbox_height > 0 and target_width > 0 and target_height > 0:
                    content_ratio = bbox_width / bbox_height
                    target_ratio = target_width / target_height
                    ratio_error = abs(content_ratio - target_ratio) / target_ratio
                    category = str(asset.get("category", "")).lower()
                    role = str(asset.get("role", "")).lower()
                    tolerance = 0.03 if category in {"hero-background"} or "hero" in role or "background" in role else 0.02
                    if ratio_error > tolerance:
                        qa_status = str(asset.get("qaStatus", "") or asset.get("status", "")).lower()
                        message = (
                            f"screen assetUsage aspect ratio mismatch: {sid}: {asset_id}: "
                            f"ratioError={ratio_error:.4f}, tolerance={tolerance}"
                        )
                        if qa_status == "active-best-effort":
                            warnings.append(message + " (active-best-effort)")
                        else:
                            errors.append(message)
            status = usage_local_pasteback_status(usage)
            qa_status = str(asset.get("qaStatus", "") or asset.get("status", "")).lower()
            if final_delivery and qa_status in {"approved", "repaired-approved", "missing-repaired"}:
                if status != "passed":
                    errors.append(f"approved assetUsage missing localPastebackStatus=passed: {sid}: {asset_id}: {status or 'missing'}")

    for asset in asset_map.get("assets", []):
        filename = asset.get("filename")
        if not filename:
            errors.append(f"asset missing filename: {asset.get('id')}")
            continue
        path = root / filename
        active = is_active_asset(asset)
        if final_delivery and active:
            qa_status = str(asset.get("qaStatus", "") or asset.get("status", "")).lower()
            scope = str(asset.get("scope", "")).lower()
            if not qa_status or qa_status in {"page-local", "candidate", "promoted", "approved-shared"}:
                errors.append(f"active asset missing QA status; use qaStatus separately from scope: {asset.get('id')}: status={asset.get('status')}, scope={scope or 'missing'}")
            if asset.get("handoffPurpose") != "program-development":
                errors.append(f"active asset missing handoffPurpose=program-development: {asset.get('id')}")
            granularity = str(asset.get("assetGranularity", "")).lower()
            if not granularity.startswith("atomic"):
                errors.append(f"active asset missing atomic assetGranularity: {asset.get('id')}: {granularity or 'missing'}")
            if asset.get("developmentUsable") is not True:
                errors.append(f"active asset missing developmentUsable=true: {asset.get('id')}")
            if has_invalid_region_slice_hint(asset):
                errors.append(f"active asset appears to be an invalid large UI-region slice: {asset.get('id')}")
            source_type = str(asset.get("source", {}).get("type", "")).lower()
            if source_type in {"full-screen-screenshot-crop", "screen-crop-alpha"} and not is_thumbnail_like(asset):
                errors.append(f"active asset uses screenshot crop source but is not thumbnail/photo content: {asset.get('id')}: {source_type}")
        if not path.exists():
            errors.append(f"asset file missing: {filename}")
        else:
            asset_files.add(filename.replace("\\", "/"))
            if Image is not None:
                try:
                    with Image.open(path) as im:
                        actual_size = im.size
                        mode = im.mode
                        alpha_empty = im.getchannel("A").getbbox() is None if mode == "RGBA" else False
                    declared = asset.get("dimensions") or {}
                    declared_size = (int(declared.get("width", 0) or 0), int(declared.get("height", 0) or 0))
                    if declared_size != (0, 0) and declared_size != actual_size:
                        errors.append(f"asset manifest dimensions {declared_size} do not match file {actual_size}: {filename}")
                    if asset.get("alpha") is True:
                        if mode != "RGBA":
                            errors.append(f"asset alpha true but file is {mode}: {filename}")
                        elif alpha_empty:
                            errors.append(f"asset alpha channel fully empty: {filename}")
                    if str(asset.get("id", "")).startswith("asset.page.") and target_size and actual_size == target_size:
                        errors.append(f"page-local asset is full screen size; likely invalid UI crop: {filename}")
                    if str(asset.get("id", "")).startswith("asset.page.") and (actual_size[0] < 8 or actual_size[1] < 8):
                        errors.append(f"page-local asset too small to be useful: {filename}: {actual_size}")
                    if str(asset.get("id", "")).startswith("asset.page.") and asset.get("alpha") is True and mode == "RGBA":
                        bbox = im.getchannel("A").getbbox()
                        if bbox is not None:
                            left, top, right, bottom = bbox
                            required_x, required_y, padding_rule = required_transparent_padding(asset, bbox, delivery_scale)
                            padding = {
                                "left": left,
                                "top": top,
                                "right": actual_size[0] - right,
                                "bottom": actual_size[1] - bottom,
                            }
                            accepted_exception = bool(asset.get("validation", {}).get("acceptedTransparentPaddingException"))
                            if (
                                padding["left"] < required_x
                                or padding["right"] < required_x
                                or padding["top"] < required_y
                                or padding["bottom"] < required_y
                            ):
                                deficits = [
                                    max(0, required_x - padding["left"]),
                                    max(0, required_x - padding["right"]),
                                    max(0, required_y - padding["top"]),
                                    max(0, required_y - padding["bottom"]),
                                ]
                                max_deficit = max(deficits)
                                message = (
                                    f"page-local asset transparent padding too small: {filename}: "
                                    f"padding={padding}, requiredX={required_x}, requiredY={required_y}, "
                                    f"rule={padding_rule}, bbox={bbox}, size={actual_size}"
                                )
                                if accepted_exception:
                                    warnings.append(message + " (accepted exception)")
                                elif max_deficit <= 1:
                                    warnings.append(message + " (<=1px tolerance)")
                                else:
                                    errors.append(message)
                except Exception as exc:
                    errors.append(f"cannot open asset: {filename}: {exc}")

    for asset in asset_map.get("assets", []):
        aid = asset.get("id")
        if not aid or not str(aid).startswith("asset.page."):
            continue
        qa_status = str(asset.get("qaStatus", "") or asset.get("status", "")).lower()
        best_effort = qa_status == "active-best-effort"
        best_effort_reason = asset.get("bestEffortReason") or asset.get("validation", {}).get("bestEffortReason")
        if final_delivery and asset.get("requiredForPixelMatch") is True and not asset_usage_by_id.get(aid):
            if best_effort:
                warnings.append(f"active-best-effort page-local asset lacks screen-map assetUsages record: {aid}")
            else:
                errors.append(f"active page-local asset lacks screen-map assetUsages record: {aid}")
        q = quality_by_id.get(aid)
        if q is None:
            errors.append(f"page-local asset missing asset-quality-audit entry: {aid}")
            continue
        best_effort_reason = best_effort_reason or q.get("bestEffortReason")
        result = q.get("result")
        if (asset.get("status") == "rejected" or asset.get("qaStatus") == "rejected") and result != "rejected-not-for-figma-source":
            errors.append(f"rejected asset has inconsistent quality result: {aid}: {result}")
        if asset.get("source", {}).get("type") == "screen-crop-alpha" and asset.get("status") != "rejected":
            if result != "approved-clean-or-acceptable-thumbnail":
                errors.append(f"active screen-crop-alpha asset lacks strict approval: {aid}: {result}")
        if strict_visual_qa and asset.get("status") != "rejected":
            allowed_results = {"approved-clean-or-acceptable-thumbnail", "approved-pixel-skin"}
            if best_effort:
                allowed_results.add("active-best-effort")
                if not best_effort_reason:
                    errors.append(f"active-best-effort asset lacks bestEffortReason: {aid}")
            if result not in allowed_results:
                message = f"active page-local asset is not approved by quality audit: {aid}: {result}"
                if best_effort:
                    warnings.append(message + " (kept as active-best-effort)")
                else:
                    errors.append(message)
            if q.get("visualInspectionPassed") is not True:
                message = f"active page-local asset lacks visualInspectionPassed=true: {aid}"
                if best_effort:
                    warnings.append(message + " (active-best-effort)")
                else:
                    errors.append(message)
            if q.get("semanticMatch") is not True:
                message = f"active page-local asset lacks semanticMatch=true: {aid}"
                if best_effort:
                    warnings.append(message + " (active-best-effort)")
                else:
                    errors.append(message)
            asset_validation = asset.get("validation") if isinstance(asset.get("validation"), dict) else {}
            pasteback_statuses = {
                str(status).lower()
                for status in [
                    q.get("localPastebackStatus"),
                    asset_validation.get("localPastebackStatus"),
                    asset.get("localPastebackStatus"),
                ]
                if status
            }
            pasteback_statuses.update(
                usage_local_pasteback_status(usage)
                for _, usage in asset_usage_by_id.get(aid, [])
                if usage_local_pasteback_status(usage)
            )
            approved_like = qa_status in {"approved", "repaired-approved", "missing-repaired"}
            if final_delivery and approved_like and "passed" not in pasteback_statuses:
                message = f"approved page-local asset lacks localPastebackStatus=passed: {aid}: {sorted(pasteback_statuses) or 'missing'}"
                if best_effort:
                    warnings.append(message + " (active-best-effort)")
                else:
                    errors.append(message)
            alpha_method = q.get("alphaMethod") or asset_validation.get("alphaMethod")
            matte_color = q.get("matteColor") or asset_validation.get("matteColor")
            if asset.get("alpha") is True and not alpha_method:
                errors.append(f"active page-local alpha asset lacks alphaMethod metadata: {aid}")
            if alpha_method == "chroma-key":
                forbidden_mattes = {"#000000", "#000", "#ffffff", "#fff", "white", "black", "gray", "grey"}
                if not matte_color:
                    errors.append(f"chroma-key asset missing matteColor: {aid}")
                elif str(matte_color).strip().lower() in forbidden_mattes:
                    errors.append(f"chroma-key asset uses forbidden black/white/gray matteColor: {aid}: {matte_color}")
                candidate_scores = q.get("candidateMatteScores") or asset_validation.get("candidateMatteScores")
                matte_score = q.get("matteConflictScore", asset_validation.get("matteConflictScore"))
                matte_risk = q.get("matteRisk") or asset_validation.get("matteRisk")
                matte_reason = q.get("matteSelectionReason") or asset_validation.get("matteSelectionReason")
                if not isinstance(candidate_scores, dict) or not candidate_scores:
                    errors.append(f"chroma-key asset missing candidateMatteScores: {aid}")
                if matte_score is None:
                    errors.append(f"chroma-key asset missing matteConflictScore: {aid}")
                if matte_risk not in {"low", "medium", "high"}:
                    errors.append(f"chroma-key asset has invalid or missing matteRisk: {aid}: {matte_risk}")
                if not matte_reason:
                    errors.append(f"chroma-key asset missing matteSelectionReason: {aid}")
            quality_padding = q.get("transparentPadding") if isinstance(q.get("transparentPadding"), dict) else None
            asset_padding = asset_validation.get("transparentPadding") if isinstance(asset_validation.get("transparentPadding"), dict) else None
            if not quality_padding and not asset_padding:
                errors.append(f"active page-local asset lacks measured transparentPadding metadata: {aid}")
            shadow_handling = q.get("shadowHandling") or asset_validation.get("shadowHandling")
            shadow_profile_ref = q.get("shadowProfileRef") or asset_validation.get("shadowProfileRef")
            shadow_quality = q.get("shadowQuality") or asset_validation.get("shadowQuality")
            shadow_relevant = bool(
                asset.get("includesShadow")
                or asset.get("includesGlow")
                or asset.get("includesReflection")
                or asset.get("includesSoftEdgeEffect")
                or shadow_profile_ref
                or shadow_quality
                or shadow_handling in {"baked-in", "separated-shadow", "native-figma-effect"}
            )
            if shadow_relevant:
                if not shadow_profile_ref:
                    errors.append(f"shadow/glow asset missing shadowProfileRef: {aid}")
                if shadow_handling not in {"baked-in", "separated-shadow", "none", "native-figma-effect"}:
                    errors.append(f"shadow/glow asset has invalid or missing shadowHandling: {aid}: {shadow_handling}")
                if shadow_quality != "matches-reference":
                    message = f"shadow/glow asset shadowQuality must be matches-reference: {aid}: {shadow_quality}"
                    if best_effort:
                        warnings.append(message + " (active-best-effort)")
                    else:
                        errors.append(message)
            elif shadow_handling and shadow_handling != "none":
                errors.append(f"non-shadow asset has inconsistent shadowHandling: {aid}: {shadow_handling}")
            contact_sheet = q.get("contactSheet")
            if not contact_sheet:
                errors.append(f"active page-local asset missing contactSheet: {aid}")
            elif not (root / str(contact_sheet)).exists():
                errors.append(f"active page-local asset contactSheet file missing: {aid}: {contact_sheet}")

    extra_audit_ids = sorted(set(audit_by_id) - set(screen_ids))
    if extra_audit_ids:
        errors.append(f"page-asset-audit has entries not in screen-map: {extra_audit_ids}")

    page_local_root = root / "03-transparent-assets" / "page-local"
    page_contact_root = root / "05-contact-sheets" / "page-local"

    for screen in screen_map.get("screens", []):
        sid = screen.get("id")
        filename = screen.get("filename")
        if not sid:
            errors.append("screen missing id")
            continue
        if sid not in audit_by_id:
            errors.append(f"screen missing page-asset-audit entry: {sid}")
        page_dir = page_local_root / str(sid)
        if generate_page_local and not page_dir.exists():
            errors.append(f"missing page-local directory for screen: {sid}")
        page_contact = page_contact_root / f"{sid}-assets-contact-sheet.png"
        if strict_visual_qa and generate_page_local and not page_contact.exists():
            errors.append(f"missing page-local contact sheet for screen: {sid}: {rel(page_contact, root)}")
        if filename:
            path = root / filename
            if not path.exists():
                errors.append(f"screen file missing: {filename}")
            elif Image is not None and target_size:
                size = image_size(path)
                if size != target_size:
                    errors.append(f"screen wrong size {size}, expected {target_size}: {filename}")
        else:
            errors.append(f"screen missing filename: {sid}")

    screen_page_local_refs = {}
    for screen in screen_map.get("screens", []):
        sid = screen.get("id")
        refs = []
        for region in screen.get("regions", []) or []:
            refs.extend(region.get("pageLocalAssets") or [])
        screen_page_local_refs[sid] = sorted(set(refs))

    asset_ids = {a.get("id") for a in asset_map.get("assets", [])}
    rejected_asset_ids = {
        a.get("id")
        for a in asset_map.get("assets", [])
        if str(a.get("status", "")).lower() == "rejected" or str(a.get("qaStatus", "")).lower() == "rejected"
    }

    for sid, entry in audit_by_id.items():
        missing = entry.get("missingAssets") or []
        exceptions = entry.get("exceptions") or []
        if missing and not exceptions:
            errors.append(f"audit has unresolved missingAssets: {sid}: {missing}")
        package_components = entry.get("packageRequiredComponents") or []
        if required_component_ids and not isinstance(package_components, list):
            errors.append(f"audit packageRequiredComponents must be a list: {sid}")
            package_components = []
        component_by_id = {
            str(component.get("componentId")): component
            for component in package_components
            if isinstance(component, dict) and component.get("componentId")
        }
        not_visible_components = entry.get("notVisibleRequiredComponents") or []
        not_visible_by_id = {
            str(component.get("componentId")): component
            for component in not_visible_components
            if isinstance(component, dict) and component.get("componentId")
        }
        for component_id in required_component_ids:
            component = component_by_id.get(component_id)
            not_visible = not_visible_by_id.get(component_id)
            if component is None:
                errors.append(f"audit missing packageRequiredComponents coverage: {sid}: {component_id}")
                continue
            coverage = str(component.get("coverage", ""))
            if coverage not in allowed_coverage_values:
                errors.append(
                    f"package-required component has invalid coverage value: {sid}: {component_id}: "
                    f"{coverage or 'missing'}; allowed={sorted(allowed_coverage_values)}"
                )
            asset_refs = component.get("assetRefs") or component.get("pageLocalAssetRefs") or component.get("componentStateAssetRefs") or []
            if isinstance(asset_refs, str):
                asset_refs = [asset_refs]
            if not isinstance(asset_refs, list):
                errors.append(f"package-required component assetRefs must be a list: {sid}: {component_id}")
                asset_refs = []
            if per_page_required_redundancy and not asset_refs:
                errors.append(f"per-page required component lacks page-local/component-state assetRefs: {sid}: {component_id}")
            if coverage == "notVisibleOnThisScreen" and per_page_required_redundancy and not asset_refs:
                errors.append(f"notVisibleOnThisScreen cannot be the only coverage in per-page redundancy mode: {sid}: {component_id}")
            if not asset_refs and coverage not in {"notVisibleOnThisScreen", "native-only"}:
                errors.append(f"package-required component lacks asset coverage or explicit not-visible/shared coverage: {sid}: {component_id}")
            if coverage in {"notVisibleOnThisScreen", "hidden-approved-global"} and not component.get("approvedSourceRef") and not (not_visible and not_visible.get("approvedSourceRef")):
                errors.append(f"notVisibleOnThisScreen component missing approvedSourceRef: {sid}: {component_id}")
            for ref in asset_refs:
                if ref not in asset_ids:
                    errors.append(f"package-required component assetRef not in asset-map: {sid}: {component_id}: {ref}")
                if ref in rejected_asset_ids:
                    errors.append(f"package-required component references rejected asset: {sid}: {component_id}: {ref}")
        audit_refs = []
        for item in entry.get("pageLocalAssets") or []:
            if isinstance(item, dict) and item.get("id"):
                audit_refs.append(item.get("id"))
                if item.get("id") not in asset_ids:
                    errors.append(f"audit pageLocalAsset id not in asset-map: {sid}: {item.get('id')}")
                if item.get("id") in rejected_asset_ids:
                    errors.append(f"audit references rejected pageLocalAsset: {sid}: {item.get('id')}")
            filename = item.get("filename") if isinstance(item, dict) else item
            if not filename:
                errors.append(f"audit pageLocalAsset missing filename: {sid}")
                continue
            path = root / filename
            if not path.exists():
                errors.append(f"audit pageLocalAsset file missing: {sid}: {filename}")
            if filename.replace("\\", "/") not in asset_files:
                errors.append(f"audit pageLocalAsset not in asset-map: {sid}: {filename}")
        screen_refs = screen_page_local_refs.get(sid, [])
        for ref in screen_refs:
            if ref in rejected_asset_ids:
                errors.append(f"screen-map references rejected pageLocalAsset: {sid}: {ref}")
        if sorted(audit_refs) != screen_refs:
            errors.append(f"screen-map/page-asset-audit pageLocalAssets mismatch: {sid}: screen={screen_refs} audit={sorted(audit_refs)}")

    print(f"screens: {len(screen_map.get('screens', []))}")
    print(f"assets: {len(asset_map.get('assets', []))}")
    print(f"audit screens: {len(audit_by_id)}")
    if package_config:
        print(f"platform: {package_config.get('platform', 'unspecified')}")
        print(f"targetScreenSize: {target_size or 'unspecified'}")
    if warnings:
        print("WARNINGS:")
        print("\n".join(warnings))
    if errors:
        print("ERRORS:")
        print("\n".join(errors))
        return 1
    print("Package is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


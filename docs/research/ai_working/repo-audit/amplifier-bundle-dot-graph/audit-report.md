# Repository Audit Report: microsoft/amplifier-bundle-dot-graph

**Audit Date**: 2026-03-13
**Repository URL**: https://github.com/microsoft/amplifier-bundle-dot-graph

## Summary

| Check | Status | Severity |
|-------|--------|----------|
| Listed in MODULES.md | Not Listed | recommendation |
| CODE_OF_CONDUCT.md | Missing | error |
| SECURITY.md | Missing | error |
| SUPPORT.md | Missing | error |
| LICENSE | Missing | error |
| README Contributing | Missing (no README) | error |
| README Trademarks | Missing (no README) | error |
| GitHub Issues | Disabled | pass |

**Overall Status**: ❌ CRITICAL
- Critical issues (errors): 6
- Warnings: 0
- Recommendations: 1

## Detailed Findings

### 1. MODULES.md Listing — 💡 Recommendation

The repository `amplifier-bundle-dot-graph` is **not listed** in the central `MODULES.md` file. While not a blocking issue, adding it improves discoverability across the organization and ensures the module is tracked alongside other Amplifier bundles.

### 2. Boilerplate Files — ❌ 4 Errors

All four required Microsoft open-source boilerplate files are **missing** from the repository:

| File | Status | Detail |
|------|--------|--------|
| `CODE_OF_CONDUCT.md` | ❌ Missing | Required for all Microsoft public repositories. Must link to the Microsoft Open Source Code of Conduct. |
| `SECURITY.md` | ❌ Missing | Required for all Microsoft public repositories. Must contain the standard Microsoft security reporting policy. |
| `SUPPORT.md` | ❌ Missing | Required for all Microsoft public repositories. Must describe how to get support for the project. |
| `LICENSE` | ❌ Missing | Required for all repositories. Must contain the project's license (typically MIT for Microsoft OSS). |

These are standard compliance requirements for any repository under the `microsoft` GitHub organization.

### 3. README.md — ❌ 2 Errors

The `README.md` file is **entirely missing** from the repository. This means:

- **Contributing section**: Missing — README must include the standard Microsoft contributing text directing contributors to the `CONTRIBUTING.md` or the project's contribution guidelines.
- **Trademarks section**: Missing — README must include the verbatim Microsoft trademarks notice as required by Microsoft open-source policy.

A missing README also impacts developer experience: new contributors and users have no entry point to understand the project's purpose, setup, or usage.

### 4. GitHub Issues — ✅ Pass

GitHub Issues are **disabled** on this repository. This is the recommended configuration for non-main/satellite repositories within the Amplifier project, where issues should be centralized in the primary repository.

## Repository Activity

- **Open PRs**: 0
- **Recent commits (7d)**: 2
- **Last push**: 2026-03-14T05:10:25Z

The repository shows active development with 2 commits in the last 7 days and no outstanding pull requests.

## Remediation Steps

The following steps are ordered by priority to bring this repository into compliance:

### Step 1: Add LICENSE file (Critical)

Create a `LICENSE` file at the repository root with the appropriate license text. For most Microsoft open-source projects, this is the MIT License:

```
MIT License

Copyright (c) Microsoft Corporation.

Permission is hereby granted, free of charge, to any person obtaining a copy
...
```

### Step 2: Add SECURITY.md (Critical)

Create `SECURITY.md` with the standard Microsoft security policy. Use the [Microsoft boilerplate template](https://github.com/microsoft/.github/blob/main/SECURITY.md) verbatim.

### Step 3: Add CODE_OF_CONDUCT.md (Critical)

Create `CODE_OF_CONDUCT.md` linking to the Microsoft Open Source Code of Conduct. Use the [standard template](https://github.com/microsoft/.github/blob/main/CODE_OF_CONDUCT.md).

### Step 4: Add SUPPORT.md (Critical)

Create `SUPPORT.md` describing how users can get help. Use the [standard template](https://github.com/microsoft/.github/blob/main/SUPPORT.md) as a starting point.

### Step 5: Create README.md with required sections (Critical)

Create a `README.md` that includes at minimum:

1. **Project description** — what `amplifier-bundle-dot-graph` is and does (DOT graph bundle for the Amplifier project)
2. **Contributing section** — verbatim Microsoft contributing text
3. **Trademarks section** — verbatim Microsoft trademarks notice:

   > This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.

### Step 6: Add to MODULES.md (Recommended)

Add an entry for `amplifier-bundle-dot-graph` to the central `MODULES.md` file in the main Amplifier repository to improve discoverability.

---
*Generated by Amplifier repo-audit recipe v1.2.0*

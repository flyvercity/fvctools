# fvctools README Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current minimal README.md with a comprehensive, professional guide to the fvctools suite.

**Architecture:** A single, high-quality Markdown file that covers everything from basic usage to developer contribution.

**Tech Stack:** GitHub-Flavored Markdown.

---

### Task 1: Setup and Overview Section

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write Header and Project Overview**
  Include the project title, Flyvercity context, and basic badges.

- [ ] **Step 2: Write Installation Section**
  Detail both `uv` (for developers) and PowerShell (for Windows users) installation paths.

- [ ] **Step 3: Commit**
```bash
git add README.md
git commit -m "docs: add overview and installation to README"
```

### Task 2: Core Toolsets Guide

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Document `fvc df`**
  Explain conversion, validation, and correlation with examples.

- [ ] **Step 2: Document `fvc calc` and `fvc render`**
  Explain geoid/terrain lookups and interactive map generation.

- [ ] **Step 3: Document `fvc shell`**
  Detail the PowerShell integration and object-oriented usage.

- [ ] **Step 4: Commit**
```bash
git add README.md
git commit -m "docs: add core toolsets guide to README"
```

### Task 3: Data Format and Formats Table

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Document the FVC Data Format**
  Explain JSON-Lines and show a `METADATA` + `FLIGHTLOG` example.

- [ ] **Step 2: Create Supported Formats Table**
  List all modules from `src/fvc/tools/df/xformats/` in a clean Markdown table.

- [ ] **Step 3: Commit**
```bash
git add README.md
git commit -m "docs: add data format info and supported formats table to README"
```

### Task 4: Development and Final Polish

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add Contributing and Development Section**
  Include instructions for adding new formats, running tests (`pytest`), and linting (`ruff`).

- [ ] **Step 2: Final Verification**
  Check all paths, command examples, and Markdown rendering.

- [ ] **Step 3: Commit**
```bash
git add README.md
git commit -m "docs: complete README overhaul with development section"
```

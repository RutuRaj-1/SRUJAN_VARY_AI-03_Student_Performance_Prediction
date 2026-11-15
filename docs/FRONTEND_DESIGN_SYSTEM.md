# MASTERY — Frontend Design System Specification

**Project:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Theme:** Structured Brutalism + Editorial Academic Intelligence  

---

## 1. Visual Identity & Design Philosophy

MASTERY's visual architecture balances **authoritative academic rigor** with **structured brutalist containers**.

Key principles:
1. **Light-First & Document-Oriented:** Clean white and light-neutral surfaces (`#F7FAF9`, `#FFFFFF`) ensuring high readability for academic transcripts, mastery radars, and risk factors.
2. **Deep Teal & Mint Identity:** Deep Teal (`#237277`, `#123E40`) for headings, primary controls, and active borders; soft mint (`#D9F0EE`, `#EEF8F7`) for highlighted sections.
3. **Structured Brutalist Geometry:**
   - Visible 1px borders (`#DCE6E2`, `#BDCEC8`).
   - Crisp, restrained corner radii (2px to 6px; no oversized 24px+ floating pills).
   - Solid, reliable data grids with clear section boundaries.
4. **Restrained Semantics:** Semantic colors (green, amber, red) are applied strictly for validated academic signals, never for generic decoration.

---

## 2. Design Tokens

### 2.1 Color Tokens
```css
:root {
  /* Surfaces */
  --background: #F7FAF9;
  --surface: #FFFFFF;
  --surface-subtle: #EEF8F7;
  --surface-muted: #EFF5F3;

  /* Brand Teal Palette */
  --brand-primary: #237277;
  --brand-deep: #123E40;
  --brand-dark: #18575A;
  --brand-accent: #2D8E92;
  --brand-mint: #D9F0EE;

  /* Typography */
  --text-primary: #172825;
  --text-secondary: #40524E;
  --text-muted: #687A75;

  /* Borders */
  --border: #DCE6E2;
  --border-strong: #BDCEC8;

  /* Semantics */
  --success: #169C73;
  --success-soft: #E8F7F1;
  --warning: #D89B22;
  --warning-soft: #FFF6DF;
  --danger: #D96559;
  --danger-soft: #FDECEA;
  --info: #2563EB;
  --info-soft: #EAF2FF;
}
```

### 2.2 Corner Radius Scale
```css
:root {
  --radius-xs: 2px;
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
}
```

---

## 3. UI Component Standards

- **Buttons:**
  - *Primary:* Background `#237277`, text white, `rounded-[4px]`, hover `#18575A`, subtle shadow.
  - *Secondary:* Background `#EEF8F7`, text `#123E40`, border 1px `#BDCEC8`.
  - *Outline:* Background white, border 1px `#BDCEC8`, hover `bg-slate-50`.
- **Containers & Cards:**
  - Background `#FFFFFF`, border 1px `#DCE6E2`, `rounded-[6px]`, padding 20px–24px.
  - Top headers with 1px border-b separator.
- **Data Tables:**
  - Header row in `#EEF8F7` with uppercase 11px font.
  - Alternating subtle row hover in `#F7FAF9`.
  - Tabular numerals (`font-variant-numeric: tabular-nums`) for marks and percentages.

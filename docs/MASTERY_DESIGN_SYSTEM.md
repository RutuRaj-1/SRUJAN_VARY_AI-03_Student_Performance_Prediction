# MASTERY Design System Specification
## Structured Brutalism + Minimal Teal Academic Intelligence

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Version:** 1.0 (Phase 11 Transformation)  
**Target:** React 18, Tailwind CSS, Lucide Icons  

---

## 1. Design Philosophy

MASTERY's visual identity embodies **Serious Academic Intelligence + Structured Brutalism + Restrained Teal Aesthetics**.

Unlike consumer SaaS or generic dashboard templates, an institutional academic intelligence platform must convey trustworthiness, provenance, precision, and clarity. It communicates critical decisions affecting students' academic trajectories and career opportunities.

### Core Principles
1. **Light-First & White-First Surfaces:** Clear, distraction-free backgrounds that prioritize data legibility and document-like readability over dark-mode novelty.
2. **Restrained Brand Accent (Deep Teal & Mint):** Distinctive, authoritative teal (`#237277` and `#123E40`) combined with soft mint (`#D9F0EE`) highlights.
3. **Structured Brutalist Containers:** Visible 1px borders, crisp rectangular sections, minimal corner rounding (2px–8px), and rigorous grid alignment. No blurry gradients, floating glassmorphism, or oversized pill buttons.
4. **Data Density with Visual Hierarchy:** Clear distinctions between primary metrics, metadata, provenance tags, and explanatory notes using tabular numerals and font-weight contrast.
5. **Ethical & Semantic Restraint:** Semantic colors (green, amber, red) are reserved strictly for validated status and risk signals, never used decoratively.

---

## 2. Design Tokens

### 2.1 Color Palette
```css
:root {
  /* Surfaces & Backgrounds */
  --background: #F7FAF9;
  --surface: #FFFFFF;
  --surface-subtle: #EEF8F7;
  --surface-muted: #EFF5F3;

  /* Brand Palette (Deep Teal & Mint) */
  --brand-primary: #237277;
  --brand-deep: #123E40;
  --brand-dark: #18575A;
  --brand-accent: #2D8E92;
  --brand-mint: #D9F0EE;

  /* Typography Colors */
  --text-primary: #172825;
  --text-secondary: #40524E;
  --text-muted: #687A75;

  /* Structural Borders */
  --border: #DCE6E2;
  --border-strong: #BDCEC8;

  /* Semantic Feedback & Status */
  --success: #169C73;
  --success-soft: #E8F7F1;

  --warning: #D89B22;
  --warning-soft: #FFF6DF;

  --danger: #D96559;
  --danger-soft: #FDECEA;

  --info: #2563EB;
  --info-soft: #EAF2FF;

  --ai: #7457C8;
  --ai-soft: #F2EEFF;
}
```

### 2.2 Border Radius Scale (Structured Brutalism)
```css
:root {
  --radius-xs: 2px;
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
}
```
*Rule:* Avoid rounded radii greater than 8px for containers, cards, and modal dialogs. Use crisp 4px–6px radius for buttons and form elements.

### 2.3 Typography Scale
- **Display Hero:** 48px–56px, bold (font-weight 700), tracking -0.025em.
- **Section Heading:** 24px–30px, semibold (font-weight 600), tracking -0.02em.
- **Card/Widget Title:** 16px–18px, semibold (font-weight 600).
- **Body Text:** 14px–15px, regular (font-weight 400), line-height 1.5.
- **Subtext & Metadata:** 12px–13px, medium (font-weight 500).
- **Metric Figures:** Monospace or tabular numerals (`font-variant-numeric: tabular-nums`).

---

## 3. UI Component Specifications

### 3.1 Containers & Cards
- **Background:** White (`#FFFFFF`).
- **Border:** 1px solid `var(--border)` (`#DCE6E2`).
- **Radius:** `rounded-md` (6px) or `rounded-sm` (4px).
- **Shadow:** Minimal subtle drop shadow (`shadow-sm`) or none.
- **Header:** Bottom border dividing title bar from content area.

### 3.2 Badges & Status Indicators
- Status badges use muted background fills with high-contrast foreground text and 1px borders:
  - *Success (Mastered / Verified / Low Risk):* `bg-emerald-50 text-emerald-800 border-emerald-200`
  - *Warning (Progressing / Pending / Moderate Risk):* `bg-amber-50 text-amber-800 border-amber-200`
  - *Danger (Needs Attention / Critical Risk / Gaps):* `bg-rose-50 text-rose-800 border-rose-200`
  - *Info (Enrolled / Standard Status):* `bg-blue-50 text-blue-800 border-blue-200`
  - *Insufficient Evidence:* `bg-slate-100 text-slate-700 border-slate-300 font-mono`

### 3.3 Buttons & Actions
- **Primary Action:** Background `var(--brand-primary)` (`#237277`), hover `#18575A`, text white, `rounded-md`, border-none.
- **Secondary Action:** Background white, border 1px solid `var(--border-strong)` (`#BDCEC8`), hover `bg-surface-subtle`, text `var(--text-primary)`.
- **Destructive Action:** Background `var(--danger)` (`#D96559`), hover `#b54d42`, text white.

### 3.4 Data Tables
- Header row: `bg-surface-subtle` (`#EEF8F7`), uppercase 11px text, font-weight 600, border-b 1px `var(--border)`.
- Cell rows: border-b 1px `var(--border)`, hover `bg-surface-muted`, font size 13px.

---

## 4. Demo Data Safety Disclaimer Banners
When the platform operates in Synthetic Demo Mode, all headers and analytical panels must render a persistent banner:
> **DEMO DATA — SYNTHETIC / NOT REAL STUDENT RECORDS**  
> *Active Scenario: [Scenario Name] — Evidence isolated in frontend memory.*

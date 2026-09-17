# Phase 4 — UI Design System & Component Guidelines

## India Weather Forecasting & Intelligence System

---

### 1. Design Philosophy

The UI design system for the India Weather Forecasting & Intelligence System delivers an executive-grade, high-density scientific experience. Rather than looking like a generic template or student project, the interface combines:
* **Glassmorphism & Depth**: Multi-layered backdrop blurs and subtle translucent borders.
* **Curated HSL Color Palettes**: Handcrafted color tokens engineered for high contrast in both dark and light modes.
* **Restrained Motion**: Subtle 150–250ms transitions that communicate state without inducing cognitive fatigue.
* **Information Density**: Clean data hierarchy optimized for meteorologists, data scientists, and operational analysts.

---

### 2. Design Tokens (`tokens.css`)

#### 2.1 Color Architecture (Dark & Light Theme)

All colors are defined using HSL variables to allow programmatic alpha blending and dynamic contrast adjustment.

| Semantic Token | Dark Mode (Default) | Light Mode | Application |
| :--- | :--- | :--- | :--- |
| `--bg-canvas` | `hsl(222, 47%, 7%)` | `hsl(210, 40%, 98%)` | Main application background |
| `--bg-surface` | `hsl(222, 40%, 11%)` | `hsl(0, 0%, 100%)` | Content cards, sidebars, modal containers |
| `--bg-surface-elevated` | `hsl(222, 35%, 15%)` | `hsl(210, 30%, 95%)` | Dropdowns, tooltips, hover highlights |
| `--border-subtle` | `hsla(220, 20%, 30%, 0.4)` | `hsla(220, 20%, 80%, 0.6)` | Card dividers, table borders |
| `--text-primary` | `hsl(210, 40%, 98%)` | `hsl(222, 47%, 12%)` | Primary headings, prominent metrics |
| `--text-secondary` | `hsl(215, 20%, 65%)` | `hsl(215, 16%, 47%)` | Supporting captions, table column headers |
| `--text-tertiary` | `hsl(215, 15%, 45%)` | `hsl(215, 12%, 60%)` | Metadata, breadcrumbs, timestamp labels |
| `--accent-primary` | `hsl(210, 100%, 56%)` | `hsl(210, 100%, 50%)` | Primary buttons, active nav, temperature curves |
| `--accent-teal` | `hsl(175, 84%, 48%)` | `hsl(175, 84%, 38%)` | Rainfall bars, radar overlays, confidence badges |
| `--status-success` | `hsl(142, 71%, 45%)` | `hsl(142, 76%, 36%)` | Positive trends, model production candidate badges |
| `--status-warning` | `hsl(38, 92%, 50%)` | `hsl(38, 92%, 44%)` | Weather alerts, preview warning banners |
| `--status-danger` | `hsl(0, 84%, 60%)` | `hsl(0, 84%, 50%)` | Heavy rainfall warnings, critical residual errors |

#### 2.2 Typography Scale

Using system font stacks (`system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`):
* `--font-2xs`: `0.75rem` (12px) — Badges, sparkline labels, footnote citations
* `--font-xs`: `0.8125rem` (13px) — Table cells, secondary status descriptions
* `--font-sm`: `0.875rem` (14px) — Body text, dropdown options, navigation links
* `--font-base`: `1rem` (16px) — Card titles, primary form inputs
* `--font-lg`: `1.125rem` (18px) — Section headers, prominent metric subtitles
* `--font-xl`: `1.25rem` (20px) — Page sub-headers, widget titles
* `--font-2xl`: `1.5rem` (24px) — Modal titles, major section headings
* `--font-3xl`: `1.875rem` (30px) — Hero stat callouts
* `--font-4xl`: `2.25rem` (36px) — Primary KPI metric values

#### 2.3 Spacing & Radius Scale
* Spacing: Multiples of 4px (`--space-1: 4px`, `--space-2: 8px`, `--space-4: 16px`, `--space-6: 24px`, `--space-8: 32px`).
* Radius:
  - `--radius-sm`: `6px` (Tags, buttons, inputs)
  - `--radius-md`: `10px` (Cards, dropdowns, table wrappers)
  - `--radius-lg`: `16px` (Modals, preview banners)
  - `--radius-full`: `9999px` (Pills, circular indicators)

#### 2.4 Elevation & Shadows
* `--shadow-sm`: `0 1px 2px rgba(0,0,0,0.08)`
* `--shadow-md`: `0 4px 12px rgba(0,0,0,0.15)`
* `--shadow-lg`: `0 8px 24px rgba(0,0,0,0.25)`

---

### 3. Motion System & Accessibility Standards

#### 3.1 Timing & Curves
* `--transition-fast`: `150ms ease-in-out` (Buttons, nav hovers, badge toggles)
* `--transition-normal`: `250ms ease-in-out` (Card elevation, modal enter/exit, drawer toggle)

#### 3.2 `prefers-reduced-motion` Enforcement
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

#### 3.3 Accessibility (WCAG 2.1 AA Compliance)
* **Contrast Ratios**: All primary text maintains a minimum contrast ratio of 7.1:1 against surface backgrounds; secondary text exceeds 4.5:1.
* **Keyboard Navigation**: Focus outlines are explicitly styled with `outline: 2px solid var(--accent-primary)` and `outline-offset: 2px`.
* **Screen Reader Semantics**: Proper `<nav>`, `<header>`, `<main>`, `aria-expanded`, and `aria-label` tags on interactive controls.

---

### 4. Component Standards

1. **Cards (`.card`)**: Translucent background (`hsla(222, 40%, 11%, 0.8)`), backdrop blur (`12px`), 1px subtle border, rounded corners.
2. **KPI Metric Card (`MetricCard`)**: Bold typography, trend badge with direction arrow, subtitle context, and optional interactive click action.
3. **Buttons (`.btn`, `.btn-primary`, `.btn-secondary`)**: Tactile hover brightness, disabled state styling, flex centered layout.
4. **Data Tables (`DataExplorerTable`)**: Sticky column headers, alternating hover states, right-aligned numbers, monospaced dates, and row expansion triggers.
5. **Interactive Charts**: Responsive SVG containers (`viewBox="0 0 800 280"`), high-contrast axes, gridlines with low opacity, and hover tooltips.

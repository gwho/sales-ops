# UI Tokens

Use Tailwind CSS 3.4 with project tokens. Components must not use hardcoded hex values or raw Tailwind color classes such as `bg-blue-600`, `text-slate-500`, or `border-red-200`.

Define tokens in the Tailwind config and map them to CSS variables in `app/globals.css`.

## Color Tokens

```css
:root {
  --background: 210 40% 98%;
  --surface: 0 0% 100%;
  --surface-muted: 210 40% 96%;
  --surface-subtle: 214 32% 94%;

  --border: 214 32% 91%;
  --border-strong: 215 20% 82%;

  --text-primary: 222 47% 11%;
  --text-secondary: 215 16% 47%;
  --text-muted: 215 20% 65%;
  --text-on-accent: 0 0% 100%;

  --accent: 221 83% 53%;
  --accent-hover: 224 76% 48%;
  --accent-subtle: 214 100% 97%;

  --success: 160 84% 39%;
  --success-subtle: 152 81% 96%;

  --warning: 38 92% 50%;
  --warning-subtle: 48 100% 96%;

  --danger: 0 84% 60%;
  --danger-subtle: 0 86% 97%;

  --info: 199 89% 48%;
  --info-subtle: 204 100% 97%;
}
```

Expected Tailwind names:

```text
bg-background
bg-surface
bg-surface-muted
border-border
text-text-primary
text-text-secondary
text-text-muted
bg-accent
text-text-on-accent
bg-success-subtle
text-success
bg-warning-subtle
text-warning
bg-danger-subtle
text-danger
```

## Typography

Use Inter via `next/font/google`.

| Element | Class pattern |
| --- | --- |
| Page title | `text-2xl font-semibold text-text-primary` |
| Section title | `text-base font-semibold text-text-primary` |
| Card value | `text-2xl font-semibold text-text-primary` |
| Body text | `text-sm text-text-primary` |
| Secondary text | `text-sm text-text-secondary` |
| Muted helper | `text-xs text-text-muted` |
| Table header | `text-xs font-medium uppercase tracking-wide text-text-secondary` |

## Spacing

| Token | Usage |
| --- | --- |
| `gap-2` | Inline badge and icon gaps |
| `gap-3` | Tight control groups |
| `gap-4` | Card internals |
| `gap-6` | Page sections |
| `p-4` | Compact cards |
| `p-6` | Primary dashboard cards |
| `px-3 py-2` | Inputs |
| `px-4 py-2` | Buttons |

## Radius and Shadow

| Element | Pattern |
| --- | --- |
| Cards | `rounded-xl border border-border bg-surface shadow-sm` |
| Buttons | `rounded-md` |
| Inputs | `rounded-md border border-border` |
| Badges | `rounded-full` |
| Tables | `rounded-xl border border-border overflow-hidden` |

## Status Colors

| Status type | Tokens |
| --- | --- |
| Success | `bg-success-subtle text-success` |
| Warning | `bg-warning-subtle text-warning` |
| Danger | `bg-danger-subtle text-danger` |
| Info | `bg-info-subtle text-info` |
| Neutral | `bg-surface-muted text-text-secondary` |

Status labels must include text. Do not rely on color alone.

## Chart Colors

Use token-derived CSS variables in chart config:

- Primary series: `hsl(var(--accent))`
- Success series: `hsl(var(--success))`
- Warning series: `hsl(var(--warning))`
- Danger series: `hsl(var(--danger))`
- Neutral/grid: `hsl(var(--border))`

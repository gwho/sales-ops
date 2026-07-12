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

  --surface-inverse: 222 47% 11%;
  --surface-inverse-hover: 222 39% 20%;
  --text-on-inverse: 0 0% 100%;
  --text-on-inverse-muted: 215 20% 65%;

  --overlay: 222 47% 11%;
}
```

## Overlay (Mobile Nav/Shell Responsiveness)

A single scrim token for dimming the page behind a fixed-position panel. Reuses `--surface-inverse`'s HSL triple so it stays inside the same palette rather than introducing a new hue; applied at reduced opacity via Tailwind's opacity modifier, never at full strength.

| Token | Class | Usage |
| --- | --- | --- |
| `--overlay` | `bg-overlay/50` | Mobile navigation drawer backdrop (`AppShell`), dimming the page while the drawer is open |

Scoped to drawer/modal backdrops only — do not use `bg-overlay` for anything else without a new token-change decision.

## Inverse Surface (Phase 10.2)

A small dark-navy-on-light-text token family, added for the sidebar and one dedicated button variant only — not a dark mode. Reuses `--text-primary`'s navy hue/lightness as a fill (`--surface-inverse`) and `--text-on-accent`'s white (`--text-on-inverse`), so the dark surface stays inside the same palette rather than introducing a new hue.

| Token | Class | Usage |
| --- | --- | --- |
| `--surface-inverse` | `bg-surface-inverse` | `SidebarNav` background, `Button` `dark` variant background |
| `--surface-inverse-hover` | `bg-surface-inverse-hover` | `SidebarNav` inactive-link hover, `Button` `dark` variant hover |
| `--text-on-inverse` | `text-text-on-inverse` | `SidebarNav` active/hover link text, `Button` `dark` variant text |
| `--text-on-inverse-muted` | `text-text-on-inverse-muted` | `SidebarNav` brand label and inactive link text |

Do not use these tokens outside `SidebarNav` and the `Button` `dark` variant without a new token-change decision — the rest of the app stays on the light `surface`/`background` tokens.

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

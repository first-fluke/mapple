# Globe CRM — Design System Specification

## Design Direction: Terrazzo (Warm Professional)

A personal CRM for B2C individuals managing their human networks. The visual language is warm, organic, and editorial — explicitly anti-AI-slop. Every surface, spacing decision, and typographic choice earns its place.

---

## 1. Visual Theme & Atmosphere

Globe CRM feels like a well-worn leather notebook that also ships a world-class keyboard shortcut system. Think Bear notes app's warmth and approachability fused with Linear's data density and intentionality. No cold blues. No sterile whites. No aggressive drop shadows.

Surfaces read like cream paper and warm stone — organic, tactile, slightly aged in the best way. Coral punctuates the interface with energy: a primary action color that signals human warmth rather than corporate urgency. Charcoal typography sits heavy and confident on cream backgrounds, never stark-black-on-white.

The atmosphere is that of a well-designed independent bookshop: curated, human-scaled, every object placed with purpose. Data-dense views (contact lists, activity feeds) breathe through generous micro-spacing and muted secondary text. Empty states feel intentional, not forgotten.

Motion is restrained: subtle fade and translate on entrance, 150ms color transitions on interaction. Nothing bounces. Nothing spins gratuitously. The interface acknowledges gestures quietly and confirms actions without fanfare.

Dark mode is warm dark — burnt earth tones, not cold midnight blue. The page background is stone-950, not black; elevated surfaces use Charcoal (#292524), preserving the warm material feel even in low-light environments.

---

## 2. Color Palette & Roles

Every color carries a defined semantic role. Decorative color use without a functional justification is not permitted.

### Light Mode

| Name | Hex | Role |
|---|---|---|
| Charcoal | `#292524` | Primary text, headings, strong emphasis |
| Warm Stone | `#78716c` | Secondary text, placeholders, metadata |
| Soft Stone | `#a8a29e` | Disabled text, tertiary content |
| Coral | `#f97316` | CTAs, active indicators, primary actions |
| Cream | `#fffbf5` | Page background, canvas |
| Warm White | `#faf8f5` | Card backgrounds, elevated surfaces |
| Sand | `#e7e5e4` | Borders, dividers, subtle separators |
| Light Sand | `#f5f5f4` | Muted backgrounds, hover states |
| Ember Red | `#dc2626` | Error states, destructive actions |
| Forest Green | `#16a34a` | Success states, confirmations |
| Deep Amber | `#d97706` | Warning states |

### Dark Mode (Warm Dark — not cold blue-black)

| Name | Hex | Role |
|---|---|---|
| Cream | `#faf8f5` | Primary text on dark surfaces |
| Warm Stone | `#a8a29e` | Secondary text |
| Charcoal | `#292524` | Elevated surfaces, cards |
| Dark Earth | `#1c1917` | Page background (stone-950) |
| Burnt Coral | `#ea580c` | CTAs — slightly deeper for dark background contrast |
| Stone Border | `#44403c` | Warm dark borders |
| Muted Background | `#292524` | Hover states on dark |

### Chart / Data Visualization

5 consistent colors for both light and dark modes. Do not substitute or reorder these for charts within the same view.

| Slot | Name | Hex |
|---|---|---|
| Chart 1 | Coral | `#f97316` |
| Chart 2 | Teal | `#0d9488` |
| Chart 3 | Amber | `#d97706` |
| Chart 4 | Indigo | `#6366f1` |
| Chart 5 | Rose | `#e11d48` |

---

## 3. Typography Rules

### Typefaces

- **Primary**: Geist Sans (`--font-geist-sans`), fallback: `system-ui, -apple-system, sans-serif`
- **Monospace**: Geist Mono (`--font-geist-mono`), fallback: `ui-monospace, monospace`

### Weights

| Weight | Use |
|---|---|
| 400 | Body text, long-form content |
| 500 | Labels, emphasis, UI elements |
| 600 | Subheadings, section labels |
| 700 | Headings, page titles |

### Size Scale

Use `clamp()` for fluid sizing where viewport responsiveness is needed. These are the base values:

| Token | Rem | Pixels |
|---|---|---|
| xs | 0.75rem | 12px |
| sm | 0.875rem | 14px |
| base | 1rem | 16px — minimum body size on mobile |
| lg | 1.125rem | 18px |
| xl | 1.25rem | 20px |
| 2xl | 1.5rem | 24px |
| 3xl | 1.875rem | 30px |
| 4xl | 2.25rem | 36px |

### Rhythm & Spacing

- **Line-height**: 1.5 for body text, 1.2 for headings
- **Letter-spacing**: -0.02em for headings (tighten for editorial feel), normal (0) for body text

---

## 4. Component Stylings

Dimensions are expressed as design intentions. Section 6 contains the corresponding utility class translations.

### Buttons

- **Primary (Default)**: Height 36px, horizontal padding 16px, Coral (#f97316) background, Charcoal (#292524) text, 10px border radius. Transitions on background and border: 150ms ease-out. Note: Charcoal text on Coral meets WCAG AA (5.4:1); white text does not (2.8:1).
- **Secondary**: Light Sand (#f5f5f4) background, Charcoal (#292524) text, Sand (#e7e5e4) border, same radius and padding as primary.
- **Ghost**: Transparent background, Charcoal (#292524) text. Hover reveals Light Sand (#f5f5f4) background. No visible border at rest.
- **Destructive**: Ember Red (#dc2626) at 10% opacity background, Ember Red (#dc2626) text. Used for irreversible actions only.
- All button variants share the same 150ms ease-out transition on background-color and border-color.

### Cards

- Background: Warm White (#faf8f5)
- Border: Sand (#e7e5e4), 1px
- Border radius: 14px
- Padding: 24px
- Shadow: `0 1px 2px rgba(41, 37, 36, 0.05)` — barely perceptible elevation, warmth preserved
- **No nested cards.** A card inside a card is not permitted at any nesting level.

### Inputs

- Height: 40px
- Border: Sand (#e7e5e4), 1px
- Border radius: 10px
- Background: Cream (#fffbf5)
- **Focus state**: 2px ring at Coral (#f97316) with 20% opacity, border color shifts to Coral (#f97316)
- **Error state**: Border color Ember Red (#dc2626), ring at Ember Red (#dc2626) with 20% opacity

### Navigation

- **Sidebar (desktop)**: Warm White (#faf8f5) background, Sand (#e7e5e4) right border
- **Mobile**: Bottom tab bar, fixed height 56px, same Warm White background and top Sand border

---

## 5. Layout Principles

### Spacing Grid

- **Base unit**: 8px. All spacing values are multiples of 8px.
- **Micro-adjustments**: 4px is permitted only for fine-tuning within components (icon gaps, label padding). It is not a layout spacing unit.

### Breakpoints

| Name | Width |
|---|---|
| sm | 640px |
| md | 768px |
| lg | 1024px |
| xl | 1280px |
| 2xl | 1536px |

### Content Constraints

- **Maximum content width**: 1280px (7xl)
- **Page padding**: 16px on mobile, 24px on tablet, 32px on desktop

### Vertical Rhythm

- **Between major sections**: 48px
- **Within a section**: 24px

### Responsive Strategy

Mobile-first. Layouts begin as single-column stacks and enhance to multi-column grids at medium breakpoints and above. Never build desktop-first and hide for mobile.

### Touch Targets

All interactive elements must meet a minimum 44x44pt tap target on mobile viewports. This applies to icon buttons, navigation items, list row actions, and checkboxes.

---

## 6. Design System Notes for Code Generation

Quick-reference mapping from design intention to utility class implementation. These tokens are the authoritative translation layer between design decisions (sections 1–5) and code output.

```
- "Warm surface"       → bg-stone-50 or bg-[#faf8f5]
- "Cream canvas"       → bg-[#fffbf5]
- "Subtle border"      → border-stone-300
- "Coral action"       → bg-orange-500 hover:bg-orange-600
- "Warm shadow"        → shadow-sm with stone-800/5
- "Relaxed radius"     → rounded-xl (14px) for cards, rounded-lg (10px) for inputs/buttons
- "Data label"         → text-sm font-medium text-stone-500
- "Section heading"    → text-2xl font-bold tracking-tight text-stone-800
- "Micro interaction"  → transition-colors duration-150 ease-out
- "Spring entrance"    → duration-300 ease-out (not bounce)
```

### Additional Mappings

```
- "Primary text"       → text-stone-900 (maps to Charcoal #292524)
- "Secondary text"     → text-stone-500 (maps to Warm Stone #78716c)
- "Disabled text"      → text-stone-400 (maps to Soft Stone #a8a29e)
- "Card container"     → bg-[#faf8f5] border border-stone-200 rounded-xl p-6
- "Input base"         → h-10 rounded-lg border border-stone-200 bg-[#fffbf5]
- "Input focus"        → focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500
- "Input error"        → border-red-600 ring-2 ring-red-600/20
- "Button primary"     → h-9 px-4 rounded-lg bg-orange-500 text-stone-900 hover:bg-orange-600
- "Button secondary"   → h-9 px-4 rounded-lg bg-stone-100 text-stone-900 border border-stone-200
- "Button ghost"       → h-9 px-4 rounded-lg hover:bg-stone-100
- "Button destructive" → h-9 px-4 rounded-lg bg-red-600/10 text-red-600
- "Sidebar nav"        → bg-[#faf8f5] border-r border-stone-200
- "Mobile bottom nav"  → h-14 bg-[#faf8f5] border-t border-stone-200
- "Error color"        → text-red-600 (Ember Red #dc2626)
- "Success color"      → text-green-600 (Forest Green #16a34a)
- "Warning color"      → text-amber-600 (Deep Amber #d97706)
- "Dark page bg"       → dark:bg-stone-950 (Dark Earth #1c1917)
- "Dark card"          → dark:bg-stone-800 (Charcoal #292524)
- "Dark border"        → dark:border-stone-700 (Stone Border #44403c)
- "Dark coral"         → dark:bg-orange-600 (Burnt Coral #ea580c)
```

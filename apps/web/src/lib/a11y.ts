/**
 * Accessibility constants and utilities for WCAG compliance.
 */

/**
 * Relationship types with distinct visual patterns (WCAG 1.4.1).
 * Each type uses a unique dash pattern + color so information is not
 * conveyed by color alone.
 */
export const RELATIONSHIP_STYLES = {
  family: {
    label: 'Family',
    dashArray: 'none',
    color: 'var(--color-relationship-family, #2563eb)',
    description: 'Solid line',
  },
  friend: {
    label: 'Friend',
    dashArray: '10 5',
    color: 'var(--color-relationship-friend, #16a34a)',
    description: 'Dashed line',
  },
  business: {
    label: 'Business',
    dashArray: '2 4',
    color: 'var(--color-relationship-business, #9333ea)',
    description: 'Dotted line',
  },
  acquaintance: {
    label: 'Acquaintance',
    dashArray: '10 5 2 5',
    color: 'var(--color-relationship-acquaintance, #ea580c)',
    description: 'Dash-dot line',
  },
} as const;

export type RelationshipType = keyof typeof RELATIONSHIP_STYLES;

/** Minimum touch target size in pixels (48dp per WCAG 2.5.5 / Material guidelines). */
export const MIN_TOUCH_TARGET = 48;

/**
 * Keyboard event handler for elements that should be activatable via Enter/Space.
 * Use on non-button interactive elements to ensure keyboard accessibility.
 */
export function handleKeyboardActivate(callback: () => void): (e: React.KeyboardEvent) => void {
  return (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      callback();
    }
  };
}

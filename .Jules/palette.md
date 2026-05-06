## 2024-05-17 - Keyboard Accessibility for Custom Dropzones
**Learning:** Custom file dropzones built with `div` elements often lack inherent keyboard interactivity and focus visibility in Vue/HTML.
**Action:** Always add `role="button"`, `tabindex="0"`, appropriate `aria-label`, and keyboard event handlers (`@keydown.enter`, `@keydown.space.prevent`) to custom dropzones to ensure they are accessible via keyboard navigation. Include `:focus-visible` styles to indicate focus state.

## 2024-05-17 - Accessibility for Icon-only Buttons
**Learning:** Icon-only buttons lack descriptive text, making them difficult to understand for screen reader users and those navigating by keyboard if focus styles are inadequate.
**Action:** Ensure icon-only buttons always have a descriptive `aria-label` attribute and clear `:focus-visible` styling (like outlines or underline) to indicate interaction capability and focus.
## 2026-05-06 - Accessibility for Icon-only Close Buttons
**Learning:** In Vue applications utilizing internationalization, icon-only buttons like '×' should leverage localized text for screen readers rather than hardcoded English strings. Additionally, ensuring package managers aren't mixed (avoiding `npm install` when `pnpm` is strictly used) prevents lockfile conflicts.
**Action:** Consistently apply `:aria-label="$t('common.close')"` to generic close buttons across the component library to ensure standardized, localized accessibility while strictly adhering to the `pnpm` boundary.

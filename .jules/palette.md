## 2024-05-17 - Keyboard Accessibility for Custom Dropzones
**Learning:** Custom file dropzones built with `div` elements often lack inherent keyboard interactivity and focus visibility in Vue/HTML.
**Action:** Always add `role="button"`, `tabindex="0"`, appropriate `aria-label`, and keyboard event handlers (`@keydown.enter`, `@keydown.space.prevent`) to custom dropzones to ensure they are accessible via keyboard navigation. Include `:focus-visible` styles to indicate focus state.

## 2024-05-17 - Accessibility for Icon-only Buttons
**Learning:** Icon-only buttons lack descriptive text, making them difficult to understand for screen reader users and those navigating by keyboard if focus styles are inadequate.
**Action:** Ensure icon-only buttons always have a descriptive `aria-label` attribute and clear `:focus-visible` styling (like outlines or underline) to indicate interaction capability and focus.

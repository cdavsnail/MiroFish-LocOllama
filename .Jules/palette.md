## 2024-05-17 - Keyboard Accessibility for Custom Dropzones
**Learning:** Custom file dropzones built with `div` elements often lack inherent keyboard interactivity and focus visibility in Vue/HTML.
**Action:** Always add `role="button"`, `tabindex="0"`, appropriate `aria-label`, and keyboard event handlers (`@keydown.enter`, `@keydown.space.prevent`) to custom dropzones to ensure they are accessible via keyboard navigation. Include `:focus-visible` styles to indicate focus state.

## 2024-05-17 - Accessibility for Icon-only Buttons
**Learning:** Icon-only buttons lack descriptive text, making them difficult to understand for screen reader users and those navigating by keyboard if focus styles are inadequate.
**Action:** Ensure icon-only buttons always have a descriptive `aria-label` attribute and clear `:focus-visible` styling (like outlines or underline) to indicate interaction capability and focus.

## 2024-05-18 - Accessibility for Close Dialog Buttons
**Learning:** Dialog close buttons ('×') scattered across multiple Vue components lacked accessible descriptions for screen readers, while other buttons like 'Remove file' in Home.vue had proper ARIA labels.
**Action:** Consistent implementation of `aria-label` attributes on icon-only close buttons using existing Vue i18n variables (e.g. `:aria-label="$t('common.close')"`) is necessary to ensure consistent screen reader support across application dialogs.

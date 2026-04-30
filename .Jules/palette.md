## 2024-05-17 - Keyboard Accessibility for Custom Dropzones
**Learning:** Custom file dropzones built with `div` elements often lack inherent keyboard interactivity and focus visibility in Vue/HTML.
**Action:** Always add `role="button"`, `tabindex="0"`, appropriate `aria-label`, and keyboard event handlers (`@keydown.enter`, `@keydown.space.prevent`) to custom dropzones to ensure they are accessible via keyboard navigation. Include `:focus-visible` styles to indicate focus state.

## 2024-05-17 - Accessibility for Icon-only Buttons
**Learning:** Icon-only buttons lack descriptive text, making them difficult to understand for screen reader users and those navigating by keyboard if focus styles are inadequate.
**Action:** Ensure icon-only buttons always have a descriptive `aria-label` attribute and clear `:focus-visible` styling (like outlines or underline) to indicate interaction capability and focus.
## 2024-05-10 - Icon-only buttons Accessibility
**Learning:** Found several icon-only close buttons (represented by '×') across components (Step1GraphBuild, Step2EnvSetup, GraphPanel, HistoryDatabase) that were lacking `aria-label`s, rendering them inaccessible to screen readers.
**Action:** Always verify icon-only buttons have an `aria-label`. Use the established Vue i18n framework (e.g. `:aria-label="$t('common.close')"`) for consistent and localized accessibility. When executing Python Playwright scripts and generating screenshots for local frontend verification, always delete the script and image artifacts before committing to avoid repository pollution.

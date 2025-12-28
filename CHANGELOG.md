# Changelog: Fix/Tween-Easing-Bugs

This branch corrects several minor but critical bugs in the animation tweening and easing engine.

## [fix/tween-easing-bugs]

### Fixed
- **Typo in Easing Function**: Corrected a typo in the easing function map within `Tween.cpp`. The function `easeonoutquintic` was renamed to the correct `easeinoutquintic`.
- **Backward Compatibility**: An alias for the misspelled `easeonoutquintic` was added to ensure that any existing layouts relying on the incorrect name will not break.
- **Division-by-Zero Guards**: Added safety checks (`if (d == 0) return b;`) to the Sine, Exponential, and Circular easing functions. This prevents potential crashes or undefined behavior if an animation is ever given a duration of zero.

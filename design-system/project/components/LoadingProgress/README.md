# LoadingProgress

Shows where asset loading is: download, prepare, ready. Sits bottom-left over the ringed-sky loading art.

**Consumer provides:** current stage, bytes loaded and total when known, and an error with a retry handler.

- Determinate bar only when the total is known; otherwise use `is-indeterminate` and name the step instead of a percentage. Never invent progress.
- Show units ("412 / 768 MB"), `tabular-nums`.
- On failure keep the reached progress visible, say what stopped and why, and offer "Retry download".
- Reduced motion replaces the indeterminate sweep with a static dimmed bar.

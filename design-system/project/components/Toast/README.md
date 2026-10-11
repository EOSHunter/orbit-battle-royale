# Toast

Brief, non-blocking feedback about something that just happened. Appears bottom-center in menus, top-center under the compass in a match.

**Consumer provides:** tone (success, warning, danger), a sentence that names the thing, and an optional single action.

- Every tone carries an icon and words; success and danger are close in lightness so color alone never encodes status.
- Errors say what failed and offer the fix as the action ("Retry").
- Auto-dismiss after 4s unless it carries an action. One at a time; newer replaces older.

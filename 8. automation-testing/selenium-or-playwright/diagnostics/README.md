# Diagnostics

Scripts used to find the root cause of failing Selenium tests. Run from `8. automation-testing/selenium-or-playwright` with the
stack up (backend in test mode, frontend running, preferably the production build).

| Script | Question it answers | Finding |
|---|---|---|
| `diag_checkout_selenium.py` | Why does `/checkout` never show the form? | `GET /auth/me` returned 401 (test-mode token expiry against the real clock), so `RoleGuard` redirected to `/login` (DEF-003) |
| `diag_token_cleared_on_navigation.py` | Why is the user logged out right after `login_as()`? | Navigating while `/auth/me` is in flight made `AuthProvider` clear the token: lost in 7 of 12 iterations before the fix, 0 of 12 after (DEF-008) |
| `diag_search_stale_response.py` | Why does the search test intermittently not reach the empty state? | One request per keystroke, last response wins: stale list in 37 of 40 loads before the fix, 0 of 40 after (DEF-007) |
| `diag_wishlist_race.py` | Why does the wishlist test intermittently find an empty wishlist? | Item saved in 7 of 8 runs without waiting and 8 of 8 when waiting for the filled heart. It cannot tell DEF-006 from DEF-008 (see DEF-006) |

The Playwright scripts mentioned in the first version of the Execution Log (`diag_m8_users.js`,
`diag_m9_wishlist.js`) were kept only in a session scratchpad and are not in the repository. Their
cross-checks are superseded by the scripts above.

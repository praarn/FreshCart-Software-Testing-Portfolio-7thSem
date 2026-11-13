**Defect ID:** DEF-006
**Title:** Clicking a wishlist heart before the session is restored redirects a logged-in user to /login
**Reported by:** QA (Selenium re-run, `test_add_product_to_wishlist`)
**Date found:** 2026-11-14
**Found via:** The test failed intermittently (1 of 86 in the production-build run, passing when run alone). The
cause was isolated by waiting for the logged-in navbar before clicking.
**Module:** M9 Wishlist (frontend, catalog page)
**Rule ID(s) affected:** R9.1
**Severity:** Low (window of a few hundred milliseconds after page load)
**Priority:** P3
**Environment:** Next.js production build, headless Chrome 157

## Summary

On `/`, the product grid and heart buttons render as soon as products load. The session is restored
asynchronously (`GET /auth/me`), and until it returns `useAuth().user` is `null`. `toggleWishlist` treats
`!user` as "guest" and calls `router.push("/login")`. A logged-in user who clicks a heart in that window is sent
to the login page and the item is not saved.

## Steps to reproduce

1. Log in, then reload `/` (token in `localStorage`).
2. Click a heart as soon as the grid appears, before `GET /api/auth/me` completes.

## Expected result

The item is added (or the click is ignored until the session is known).

## Actual result

Redirect to `/login`; nothing added. In the Selenium test the heart never filled (`TimeoutException` on
`wait_wishlisted`), and before the test was changed the missing item produced a timeout on `wishlist-grid`.

## Root cause

`app/page.tsx` reads only `user` from `useAuth()` and ignores `loading`.

## Fix

Read `loading` as `authLoading` and add it to the button's `disabled` condition. The test now waits for the
logged-in navbar (`nav-logout-button`) before clicking, and for the heart to fill before navigating away.

## Status

Fixed (verified by the full Selenium run recorded in `03_Test_Execution/`).

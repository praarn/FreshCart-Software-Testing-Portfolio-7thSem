# Frontend — how it's put together

Next.js App Router + React 19 + TypeScript + Tailwind CSS v4. Every page talks to the
FastAPI backend over plain `fetch` — there's no server-side data fetching, no server
actions, nothing Next-specific about the data layer. This file explains the structure;
for routes/access and the look-and-feel decisions, see the root
[`explanation.md`](../explanation.md) and [`../docs/REQUIREMENTS.md`](../docs/REQUIREMENTS.md).

## Folder structure

```
app/
  layout.tsx           Root layout: fonts, AuthProvider, Navbar, Footer, BottomNav
  globals.css           Tailwind import + design tokens (@theme: accent-*, ink)
  page.tsx               /          catalog (banners, categories, offers, search/sort/paginate)
  login/, register/      /login, /register
  product/[id]/           /product/:id   detail + reviews + wishlist toggle
  cart/, checkout/        /cart, /checkout
  orders/, orders/[id]/   /orders, /orders/:id  (order detail has the live WebSocket)
  wishlist/                /wishlist
  admin/                   /admin/**  (layout.tsx holds the admin sub-nav + RoleGuard)
  delivery/                /delivery

components/
  Navbar.tsx      Header: logo, global search (syncs to / via ?search=), nav links, auth state
  Footer.tsx      Site footer
  BottomNav.tsx   Mobile-only fixed bottom nav, role-aware (sm:hidden)
  RoleGuard.tsx   Wraps a page, redirects to /login if unauthenticated, shows a denial
                  message if the user's role isn't in the allowed list
  icons.tsx       Small monoline SVG icon set (no emoji — see "Design system" below)

lib/
  api.ts      Typed fetch wrapper: attaches the JWT, parses the backend's error shape
              into ApiError, exposes api.get/post/put/patch/delete
  auth.tsx    AuthProvider/useAuth — holds the current user, login/register/logout,
              persists the token in localStorage
  types.ts    TypeScript interfaces mirroring the backend's Pydantic schemas
  format.ts   money(), formatDateTime(), statusBadgeClasses() (per-order-status color)
```

## How a page talks to the backend

Every interactive page is a client component (`"use client"`) that calls `api.get/post/...`
from `lib/api.ts` directly in `useEffect`/event handlers — there's no shared data-fetching
library, no cache, just plain `useState` + `fetch`. `lib/api.ts` centralizes exactly three
things: attaching `Authorization: Bearer <token>` from `localStorage`, parsing the backend's
`{status, error, message, field_errors}` shape into a typed `ApiError`, and returning
`undefined` for `204 No Content` responses. `errorMessage(err)` and `fieldErrorMap(err)`
(also in `lib/api.ts`) turn a caught `ApiError` into, respectively, a one-line message for a
toast/banner and a `{field: message}` map for inline form errors.

`NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_WS_URL` (see `.env.example`) point at the backend; being
`NEXT_PUBLIC_*`, they're baked in at build time, which is why the Docker build accepts them
as build args (see `Dockerfile`).

## Auth and route protection

`lib/auth.tsx` wraps the whole app in `AuthProvider` (mounted in `app/layout.tsx`). On load
it reads the token from `localStorage` and calls `GET /auth/me` to populate `user`; `login`/
`register` store the new token and re-fetch `/auth/me`; `logout` calls `POST /auth/logout`
(revokes the token server-side) and clears local state.

Pages that require a role wrap their content in `<RoleGuard roles={[...]}>`
(`components/RoleGuard.tsx`): it shows a loading state while auth resolves, redirects to
`/login` if there's no user, and shows an inline "no access" message if the user's role isn't
allowed — it does not do a server-side redirect, since there's no server-rendered data here.
`app/admin/layout.tsx` applies one `RoleGuard` around the whole `/admin/**` tree plus the
admin sub-nav, so individual admin pages don't each need their own guard.

## Design system

Colors are Tailwind v4 theme tokens defined in `app/globals.css` (`@theme inline { ... }`):
an `accent-*` gold scale (every shade light enough that dark text reads on it — filled accent
buttons always use `text-gray-900`, never `text-white`) and a flat `ink` near-black used for
the logo mark, the footer, and outline buttons. There's no `brand-*`/emerald scale anymore —
an earlier pass used one, but it was replaced to match a quick-commerce reference the project
owner liked, then deliberately desaturated/flattened afterwards (pill buttons → `rounded-md`,
card shadows dropped) because the first pass read as too playful for a professional app.
Status/active/toggle badges intentionally keep `rounded-full` — that's a normal pattern for
short indicators, just not for buttons or cards.

Icons are hand-written inline SVGs in `components/icons.tsx` (`LogoMark`, `SearchIcon`,
`CartIcon`, `HeartIcon`, `HomeIcon`, `BoxIcon`, `DashboardIcon`, `TruckIcon`, `UserIcon`) —
deliberately not emoji, which render inconsistently across platforms. The ★ rating glyph is
a plain Unicode character, not emoji, and is kept as-is (it's a universal, non-cartoonish
convention for ratings).

## Testability

Every interactive element (inputs, buttons, links, table rows, error messages) carries a
matching `id` and `data-testid`, generally following `<page-or-component>-<element>[-<id>]`
(e.g. `add-to-cart-button-${productId}`, `checkout-submit-button`, `admin-order-row-${id}`).
Field-level validation errors use a testid ending in `-error`. This is what the student's
Selenium test suite (under `Test_Automation/`) is expected to target — don't rename these
without checking whether tests depend on them.

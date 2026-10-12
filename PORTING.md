# React Rewrite — Porting Guide

## Framework: Next.js (App Router)

**UPDATE:** The target is **Next.js with the App Router**, not plain Vite React.
Port components as **plain React client components** (function components + hooks).
Do NOT use Next.js server components, `fetch` caching, or SSR features — the app behaves
like the original SPA (auth lives in localStorage, data via react-query).

- **Routing:** Next.js file-based routing in `app/` (the parent wires this at integration).
  **Do NOT create `*Routes.tsx` files.** Instead, list your route mapping
  (`URL path → component file`) in your final report, mirroring the Angular routing modules.
- **Env:** backend URL is `process.env.NEXT_PUBLIC_BACKEND_URL` (default `http://localhost:3030/`).
  Never use `import.meta.env`.
- Everything is a client component: the parent adds `'use client'` wrappers. Your components
  just use hooks normally (`useState`, `useQuery`, `useTranslation`, `useAuth`).
- For navigation use `next/link` (`<Link href="...">`) and `next/navigation` (`useRouter`, `useParams`)
  instead of react-router-dom.

## Source and target

- **Reference (Angular, READ ONLY):** `~/workspace/fi-ksi/web-frontend-angular`
  - Current checkout branch `feat/discussion-resolved-ui` = main + PR #133 (discussion resolved badge).
  - PR #131 (tasks graph barycenter): branch `perf/tasks-graph-minimize-edge-crossings`.
  - PR #132 (admin exec user filter): ref `xhyai/pr132` (fetched from the fork).
  - Base for everything else: `main` (= origin/main at #130).
- **Target (React, WRITE HERE):** `~/workspace/fi-ksi/react-rewrite`

## Already built (do not rebuild)

| Piece | Location |
|---|---|
| Typed fetch API client (71 endpoints + `authorizeForm`) | `src/api/client.ts` |
| OpenAPI types (`components['schemas']['X']`) | `src/api/schema.d.ts` |
| Auth (login/logout/session/BroadcastChannel/auto-refresh) | `src/auth/AuthContext.tsx` → `useAuth()` gives `{ user, isLoggedIn, login, logout, refreshUser }` |
| i18n (cs.json bundled) | `src/i18n.ts` → `useTranslation()` → `t('key')` |
| Routes (Czech, production) | `src/routes.ts` → `ROUTES` |
| Global styles (Bootstrap 4 + KSI theme) | `src/styles/global.scss`, `src/styles/{theme,vars,colors,mixins}.scss` |
| Scoped localStorage | `src/utils/storage.ts` (`storageGet/set/delete(scope, key, ...)`, prefix `KSI/`) |
| Backend URL | `process.env.NEXT_PUBLIC_BACKEND_URL`, default `http://localhost:3030/` |

## Conventions

- React 18, TypeScript `strict`, function components + hooks. No classes for UI.
- **Data fetching:** `@tanstack/react-query` — `useQuery({ queryKey: [...], queryFn: () => apiCall(...) })`.
  This replaces RxJS services and `shareReplay`.
- **Routing:** `next/link` (`<Link href>`) and `next/navigation` (`useRouter`, `useParams`, `usePathname`).
  Route paths use `ROUTES` constants. Do NOT create `*Routes.tsx` files — report your
  route mapping (URL path → component) instead; the parent wires `app/`.
- **i18n:** `const { t } = useTranslation();` then `t('discussion.thread.title')`. All user strings via cs.json keys (same keys as Angular).
- **Styling:** Bootstrap 4 utility classes + component-scoped SCSS: `MyComponent.tsx` imports `./MyComponent.scss`. You may copy relevant rules from the Angular `*.component.scss` and convert (`:host` → root class).
- **API:** `import { tasksGetAll } from '../../api/client'` (relative depth as needed). Types: `import type { components } from '../../api/schema'; type S = components['schemas'];` then `S['Task']`.
- **Auth state:** `const { user, isLoggedIn } = useAuth();`. `user.role` is `'admin' | 'org' | ...` — check the schema `UserRole`.
- **Forms:** controlled components with `useState`. No form library.
- **Modals:** local `useState<boolean>` per modal + Bootstrap `.modal` markup with `show`/`d-block`, or a tiny shared `Modal` component you create in `src/components/shared/Modal.tsx`. Do not port `ModalService`.
- **Guards:** admin/org-only pages redirect to `/403` when the role check fails
  (e.g. `const router = useRouter(); useEffect(() => { if (!allowed) router.replace('/403'); }, ...)`),
  mirroring Angular route guards.
- **Tests:** colocate `*.test.ts` / `*.test.tsx`, run with `vitest run`. Test pure logic (utils, graph layout, formatters) and key component rendering. jsdom is configured.
- **No new npm dependencies** without asking the parent first. Reuse what is installed (react, react-router-dom, @tanstack/react-query, i18next, bootstrap, @uiw/react-codemirror, highlight.js, mathjax).
- **Do NOT edit** `app/`, `src/api/*`, `src/auth/*`, `src/i18n.ts`, `src/routes.ts`.
  The parent owns the Next.js `app/` router wiring.
- Code comments: factual descriptions only, never issue/PR numbers.
- Commit nothing. Just write files.

## Layout

```
src/components/<module>/<ComponentName>.tsx (+ .scss, +.test.tsx)
src/components/shared/...        # shared UI (Spinner, Modal, ...)
src/hooks/...                    # shared hooks (port of services)
src/utils/...                    # pure utils (port of src/app/util + pipes)
```

## Must-include changes ("tie zmeny")

1. **#131 tasks graph:** port `minimizeEdgeCrossings` (barycenter/Sugiyama sweeps) from
   `perf/tasks-graph-minimize-edge-crossings` (`src/app/services/tasks/tasks.service.ts`) as a pure
   TS util + unit tests, and use it in the tasks graph component exactly like
   `tasks-graph.component.ts` does on that branch.
2. **#132 admin exec:** port `page-admin-exec` from ref `xhyai/pr132` — user typeahead with
   `resolveUserId()` (typed text that wasn't picked from the dropdown → `userNotSelected`
   validation error, cs.json keys `admin.exec.user.notSelected` etc.), users list cached
   (react-query cache replaces `shareReplay(1)`).
3. **#133 discussion:** port from branch `feat/discussion-resolved-ui` — "✓ Vyřešeno" badge on
   resolved posts + org-only "Vyřešit / Znovu otevřít" toggle calling `postsResolve`/`postsUnresolve`.

## Practical notes

- Angular templates: `*ngIf` → conditional render, `*ngFor` → `.map`, `| translate` → `t()`,
  `| async` → react-query data, `[(ngModel)]` → controlled state.
- `environment.backend` → `process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3030/'`.
- Static assets live under `/assets/...` (public dir), e.g. `/assets/img/icon.svg`.
- Keep behavior parity over pixel perfection, but keep the KSI look (theme variables, Bootstrap).
- If an Angular piece is genuinely dead code (unused route/component), skip it and note it in your final report.
- MathJax/CodeMirror/Quill usages: check how the Angular component uses them; for CodeMirror use
  `@uiw/react-codemirror`; for math keep dynamic MathJax typesetting; for Quill (rich text) you may
  use a plain `<textarea>` only if the Angular usage is display-only — otherwise ask the parent.

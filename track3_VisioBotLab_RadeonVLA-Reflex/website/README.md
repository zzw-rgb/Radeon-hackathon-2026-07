# RadeonVLA-Reflex showcase site

Static, bilingual project site for the Track 3 submission. It uses Vite and native
TypeScript with no runtime framework, analytics, remote fonts, or CDN dependencies.
Node.js 20.19 or newer is required.

## Run locally

```bash
npm install
npm run dev
```

Open the URL printed by Vite. English is the default language; the header toggle stores
the visitor's choice locally.

## Validate and build

```bash
npm run check
npm run preview -- --host 127.0.0.1
```

The production build is written to `dist/`. `vite.config.ts` uses a relative asset base,
so the same build can be hosted at a repository subpath such as GitHub Pages.

## Updating content

All bilingual copy, verified metrics, task rows, and external URLs live in
`src/content.ts`. Keep these rules when final evidence arrives:

- only publish numbers present in immutable evaluation artifacts;
- replace `Pending` only after held-out evaluation passes;
- distinguish a target (for example 1,000 demonstrations) from a completed result;
- update Dataset Card, Model Card, technical report, and this site from the same run;
- keep the simulation-only limitation visible.

The project-owned hero concept is bundled from
`src/assets/radeonvla-reflex-hero.png`. Keep the software and simulation credits in
`../THIRD_PARTY_NOTICES.md` when editing the footer.

## Adding the final video

The current video area is deliberately a `Pending` panel. When the three demo runs pass:

1. export a 3+ minute narrated H.264 MP4 with `yuv420p` and fast-start;
2. create a lightweight WebP poster and WebVTT captions;
3. host the large MP4 outside the contest Git repository;
4. add a native `<video controls preload="metadata">` element with poster, captions,
   and a direct-download fallback;
5. test playback without autoplay in current Chromium, Firefox, and Safari.

Do not reuse the stitched AV1 dataset videos as the public demo: they are training data,
large, and not universally browser-compatible.

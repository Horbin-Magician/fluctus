# Repository Guidelines

## Project Structure & Module Organization
`front-end/` contains the Nuxt 3 client: `components/` for reusable SFCs, `pages/` for routes, `composables/` for shared state, `server/api/` for edge handlers, and `assets/` vs `public/` for processed vs static files. `back-end/` houses the Flask service; `www/` wires the app + blueprints, `tools/dbControllers/` encapsulates persistence logic, `datas/` stores generated secrets, and `application.py` is the entry point. Run `./dev.sh` to boot both tiers together.

## Build, Test, and Development Commands
- `cd front-end && yarn install` — install client dependencies.
- `cd front-end && yarn dev` — start Nuxt on http://localhost:3000.
- `cd front-end && yarn build && yarn preview` — produce and verify the production bundle.
- `cd back-end && uv sync` — install Flask dependencies.
- `cd back-end && uv run python application.py` — serve the API at http://127.0.0.1:5000.
- `./dev.sh` — concurrently launch both services; Ctrl+C stops everything.

## Coding Style & Naming Conventions
Use two-space indentation for Vue/TS files and four spaces for Python. Keep components/composables PascalCase (`MapContainer.vue`, `TravelDbController.py`), while files in `pages/` follow kebab-case to track the URL. Favor `<script setup lang="ts">`, hoist shared helpers into `utils/` or `composables/`, and keep network calls in `server/api`. Run `npx eslint . --ext .ts,.vue --max-warnings=0` before pushing; Python modules should remain import-safe to keep the Flask factory testable.

## Testing Guidelines
Back-end configs expose `TestingConfig`, so add pytest suites under `back-end/tests/` and run them with `uv run pytest`. Front-end behavior should be guarded with Vitest or Nuxt test-utils specs under `front-end/tests/`, colocated with their owning `pages/` or `components/`. Name tests after the behavior under test, keep fixtures deterministic by mocking network/map calls, and target 80% statement coverage on any new controller or composable.

## Commit & Pull Request Guidelines
Commits follow Conventional Commits (`feat:`, `fix:`, `refactor:`) as seen in the log; keep subjects under 70 characters and add body context when needed. Every PR must include a summary, linked issue or ticket, screenshots/GIFs for UI-facing work, API/contract notes for server changes, and a short list of commands/tests executed. Tag reviewers for each layer affected and wait for lint/tests to pass before requesting merge.

## Configuration & Security Notes
`back-end/datas/secret_key` is generated automatically—exclude the file from commits and never embed credentials in source. Export `FLASK_DEBUG=false` plus the proper CORS origin for staging/production. Nuxt runtime secrets belong in `.env.local` and must be surfaced through `runtimeConfig` rather than hard-coded constants.

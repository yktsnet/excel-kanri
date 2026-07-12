[🇯🇵 日本語](design-decisions.md) | [🇬🇧 English](design-decisions.en.md)

# Design Decisions

The full text of excel-kanri's design decisions. Each entry records not just "what was chosen" but "why." For the essentials only, see [README's Design Decisions](../README.en.md#design-decisions).

## Operating environment and development environment

* **Production / operations target environment**: a VPS or on-premise Linux server
* **Local development environment**: Windows + WSL2 (referencing the WSL2 filesystem directly from the Windows machine)

Editing and saving files on the WSL2 filesystem (`\\wsl.localhost\...`) directly from Windows Explorer or Excel correctly propagates `inotify` events to the WSL Linux-side kernel. This makes it possible to test file-watching triggered by Windows-side operations without standing up an extra file-sharing server (such as Samba). In production, a shared directory such as Samba or WebDAV is set up on the on-premise Linux or VPS host, and employee PCs edit and save the resident-list master Excel directly through that shared folder.

## File-processing and Web UI design

* **Document generation flow (Route A)**:
  1. An employee submits the document type and required fields from the web app's input form.
  2. FastAPI records it in SQLite, and `openpyxl` fills the values into a template Excel to produce a `.xlsx`.
  3. An HTTP request to the Gotenberg container converts it to `.pdf`, saved in `generated/`.
* **Shared-folder watching flow (Route B)**:
  1. An employee places or saves an Excel file into `shared/`.
  2. The server side (Python `watchdog`) detects the change (`IN_CLOSE_WRITE`).
  3. An HTTP request to the Gotenberg container auto-updates the `.pdf` (overwritten in place).
* **Role of the Web UI**: it covers three roles — input (Route A), viewing (Route A + B), and search (Route A only). **No Excel download button is provided** (the web side offers read-only PDF viewing and printing only).

Rendering Excel pixel-perfectly in a browser requires heavyweight middleware such as LibreOffice Online, whereas a PDF renders instantly and accurately with native browser PDF rendering. In Route A, SQLite is the single source of truth for the data, which prevents the generated Excel from being downloaded from the web and manually edited out of sync. Route B's Excel files are directly editable from Windows, so a web download is unnecessary there too.

## Web application tech stack

The priority was self-hosting ease through a unified Python runtime: putting FastAPI in the same runtime as `watchdog` and `openpyxl` makes a `pip install`-only setup possible. React's build assets are served statically by FastAPI, so production needs no separate web server such as Nginx or a reverse proxy for Gotenberg. PDF conversion via Gotenberg delegates to a dedicated conversion container over HTTP instead of installing LibreOffice directly on the app server, eliminating `subprocess` management and keeping the app code simple. shadcn/ui was chosen because it copies components into the repo for free customization, and it ships the business-app staples (Table, Form, Dialog).

See the [README's Tech Stack](../README.en.md#tech-stack) table for the reasoning behind each layer.

## Natural-language interface

* **LLM**: Gemini API
* **Approach**: extend horizontally from the "Text-to-SQL" mechanism already working in a separate project. To keep it generally usable as OSS, the API key is loaded simply from an environment variable.

This has been deferred from the MVP (see "Search MVP scope" below for why).

## Authentication and authorization design

* **Auth method**: JWT (access token)
* **Roles**:
  * `viewer`: file listing, PDF preview/print, and search only
  * `editor`: everything `viewer` can do, plus document creation via Route A (`POST /api/generate`)
* **User management**: managed in a SQLite `users` table (added to the existing DB). No admin role is provided; users are added via seed data or environment variables.
* **Demo mode** (`DEMO_MODE=true`): the login page shows `viewer` / `editor` tabs with demo credentials pre-filled, and sample data (documents and users) is pre-seeded at startup.
* **Normal mode** (`DEMO_MODE=false`): only a plain email + password login screen is shown. Roles are tied to the account.

Since user management is fully handled by seed data at deploy time, an admin UI is omitted to keep complexity down. Being able to bring up a demo environment instantly with a single `DEMO_MODE=true` variable lowers the barrier to evaluation and adoption when publishing as OSS.

## What this repo actually is — separating the toolkit from the applied example

This repo's true identity is "a toolkit that retrofits web input, PDF viewing, and search onto an existing Excel workflow," with property management positioned as merely the first applied example. Three layers: `packages/` (generic modules, no domain vocabulary) → `app/` (assembled from FastAPI + React) → `examples/mansion/` (templates, mappings, seed data).  Domain-specific artifacts live only in `examples/`; a client's actual templates and real data are never included in the repo (fictional forms only).

The property-management vocabulary exists only inside template Excel files, YAML mappings, and form definitions — the machinery (filling, watching, converting, searching, viewing) turned out to be entirely domain-free. Future client projects and OSS users in other industries want exactly this machinery, so the boundary was expressed in the structure from the start. `packages/` has a one-way dependency (it never imports `app`), and external dependencies (Gotenberg, paths, time) are injected as arguments. This means that even a future extraction into a registry package would cost little more than moving directories.

## Distribution model — clone reference (no registry publication)

The whole repo is published as "a reference implementation you clone and use." No PyPI package is published. Users clone it and swap `examples/` for their own forms and mappings.

Registry publication carries ongoing costs — versioning, backward compatibility, English documentation. The cost of generalization is paid only once real users appear. Language and registry are dependent variables determined by the runtime; there is no decision to "standardize on npm / pip." This repo sits on top of the Python ecosystem (openpyxl / watchdog / FastAPI), so it's Python, and since it's not the kind of code that gets bundled into a user's own build, no registry is needed.

## Demo approach — no hosted URL, VHS + one-shot launch

No permanent hosted demo URL is provided. Each module's demo is a VHS `.tape` bundled in the repo, generating a GIF. For the whole app, launching with `DEMO_MODE=true` via a single `docker compose up` is the MVP's completion criterion.

Given the distribution model is a clone reference, the demo audience is developers (and future me), not end users. VHS + README is the right delivery mechanism, and bundling the `.tape` makes the demo itself reproducible and maintainable. A hosted URL would require a resident Gotenberg container + VPS and abuse mitigation for the generation API, and Route B (folder watching) can't be experienced by a visitor anyway. Being able to stand it up locally with one command secures evaluability, and if a hosted URL is ever needed (an interview, a portfolio listing), `DEMO_MODE` can simply be carried over to a VPS at that point.

## Search MVP scope — up to FTS5, Gemini is post-MVP

The MVP includes keyword search (SQLite FTS5) and a search UI. Natural-language search (Gemini Text-to-SQL) is post-MVP.

The problem being solved — the effort of digging up past contracts — is solved by keyword search. SQLite recording is already done by the generation feature, so the incremental cost of an FTS5 table and a search bar is small. LLM integration is a bonus, not a differentiator, and requiring an API key raises the barrier for demos and evaluation. Because it can be bolted on top of FTS5, there's no decoupling cost.

## Setup instructions of record — venv / npm (Nix is optional)

The canonical setup steps in the README and docs are `python -m venv` + `pip install -r requirements.txt` + `npm install`. `shell.nix` is maintained as an optional shortcut for Nix users.

The majority of the intended users (developers who clone the repo) are outside the Nix ecosystem, and Nix-first instructions would be a barrier to entry. `shell.nix` functions only as an entry point to line up the dev machine's toolchain (python313 / node22), and is not assumed by the day-to-day dev loop or the documentation.

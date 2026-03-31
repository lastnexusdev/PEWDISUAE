# CoreJunkie Desktop (Electron)

Switched from the FastAPI web MVP to an Electron desktop app starter.

## What it does
- Register and login users locally.
- Create products (name, category, size/unit).
- Add per-user inventory entries:
  - purchased date,
  - opened date,
  - cadence + amount per use,
  - automatic expected run-out date.
- Persist all data locally in a JSON file under Electron `userData`.

## Run
```bash
cd electron
npm install
npm start
```

## App structure
- `electron/main.js` — Electron main process, IPC handlers, business logic.
- `electron/store.js` — local JSON datastore.
- `electron/preload.js` — secure IPC bridge.
- `electron/renderer/index.html` — desktop UI.
- `electron/renderer/app.js` — renderer interactions and state handling.

## Notes
- This desktop app no longer depends on `corejunkie.com/app` routing because it runs locally as a desktop app.
- If you still want optional cloud sync later, we can add a remote API connector while keeping this Electron UI.

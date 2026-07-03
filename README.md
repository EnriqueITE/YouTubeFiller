# YouTube Filler

![YouTube Filler header](assets/github-header.svg)

YouTube Filler is a lightweight Chrome and Brave extension that adds a native-looking control to the YouTube player. It lets the video fill the browser tab viewport with a centered `cover` crop while keeping browser tabs, the address bar and window controls visible.

The extension only runs on normal YouTube watch pages at `youtube.com/watch` and `www.youtube.com/watch`. It does not activate on Shorts, search, the YouTube home page or embedded players.

## Features

- Adds a YouTube-style button next to the fullscreen control.
- Fills the current browser tab without entering real browser fullscreen.
- Uses a centered `object-fit: cover` crop to reduce black bars.
- Keeps YouTube playback controls available.
- Hides distracting page panels while fill mode is active.
- Works with YouTube single-page navigation between videos.
- Includes a configurable in-page shortcut.
- Supports English (US) by default and Spanish (Spain) inside the extension UI for `es-*` browser locales.

## Shortcuts

- In-page shortcut: `º` by default, intended for Spanish keyboards where the key is to the left of `1`.
- Native browser command: `Alt+Shift+V` by default.
- Exit shortcut: `Escape` while YouTube Filler is active and the browser is not in real fullscreen.

The in-page shortcut only works when the YouTube tab has focus. To use a shortcut from other apps, configure the native browser command as Global in `chrome://extensions/shortcuts` or `brave://extensions/shortcuts`.

## Install Locally

1. Download or clone this repository.
2. Open `chrome://extensions` or `brave://extensions`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the project folder.
6. Open a normal YouTube video at `https://www.youtube.com/watch?...` or `https://youtube.com/watch?...`.

After changing files, reload the extension from `chrome://extensions` or `brave://extensions`.

## Build a Store Package

This extension has no build step and no external dependencies. To package it manually, zip the extension files while excluding git metadata and local temporary files.

A PowerShell helper is included:

```powershell
./scripts/package.ps1
```

The package will be created in `dist/`.

## Permissions

- `storage`: saves the custom shortcut preference.
- `activeTab`: lets the native browser command send the toggle message to the active YouTube tab.
- `https://www.youtube.com/*` and `https://youtube.com/*`: inject the button and styles on YouTube pages, with a runtime guard so the feature only activates on normal `/watch` pages.

## Privacy

YouTube Filler does not collect analytics, does not track browsing history, does not sell data and does not send video information to any external server. Settings are stored with Chrome's extension storage so your shortcut preference can sync through the browser if sync is enabled.

See [PRIVACY.md](PRIVACY.md) for the full privacy policy.

## Support

Issues and feature requests are handled through GitHub Issues. A small support link is also shown in the extension popup: [Buy me a coffee](https://buymeacoffee.com/enriqueite).

## License

This project is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE).

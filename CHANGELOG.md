# Changelog

## 0.4.9 - 2026-07-03

- Split the popup shortcut help into shorter, clearer lines.

## 0.4.8 - 2026-07-03

- Clarified that the default in-page shortcut is intended for Spanish keyboards and can be changed for other layouts.

## 0.4.7 - 2026-07-03

- Refreshed YouTube layout after exiting cover mode to prevent shifted player placement.
- Added a project NOTICE file and included license notices in store packages.

## 0.4.6 - 2026-07-03

- Kept public author/contact/support details while removing local machine paths from packaged output.
- Updated the Chrome Web Store package script to include only runtime extension files.
- Added GPL-3.0-only copyright notices to source files.
- Removed the Chrome Web Store listing draft from the public source tree.

## 0.4.5 - 2026-07-03

- Made content script startup resilient to invalidated extension contexts during reloads.
- Added safer fallbacks around extension APIs and page scheduling.

## 0.4.4 - 2026-07-03

- Hardened startup checks around the document root element.
- Fixed the popup fallback text for the default `º` shortcut.
- Kept YouTube host access limited to HTTPS on `youtube.com` and `www.youtube.com`.

## 0.4.3 - 2026-07-03

- Updated public GitHub documentation to English (US) only.
- Added explicit support for normal watch pages on both `youtube.com` and `www.youtube.com`.
- Updated the popup to use the current extension icon asset.

## 0.4.0 - 2026-07-03

- Renamed the public extension branding to YouTube Filler.
- Added English and Spanish documentation for GitHub and Chrome Web Store preparation.
- Added privacy, support and store listing drafts.
- Added a GitHub header asset.
- Kept the default in-page shortcut as `º` and the native browser command as `Alt+Shift+V`.

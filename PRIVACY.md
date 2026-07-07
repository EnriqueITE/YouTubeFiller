# Privacy Policy

Effective date: 2026-07-03

YouTube Filler is designed to run locally in your browser and avoid collecting personal data.

## Data Collection

The extension does not collect, store, sell, transmit or share personal information.

It does not collect:

- YouTube account information.
- Video titles, URLs, watch history or recommendations.
- Search queries.
- Analytics or telemetry.
- IP addresses or device identifiers.

## Local Browser Storage

YouTube Filler stores only one user preference: the custom in-page shortcut. This is saved with `chrome.storage.sync`, which means Chrome or Brave may sync it through your browser account if browser sync is enabled.

The extension developer does not receive this setting.

## Network Requests

YouTube Filler does not make network requests to external servers during normal use. It only modifies the local YouTube page while you are watching a normal YouTube video. The popup includes an optional external support link. Opening that link is a user-initiated action and leaves the extension.

## Permissions

- `storage`: saves the custom shortcut preference.
- `activeTab`: lets the native browser command send the toggle message to the active YouTube tab.
- `https://www.youtube.com/*` and `https://youtube.com/*`: inject the button and styles on YouTube pages, with a runtime guard so the feature only activates on normal `/watch` pages.

## Contact

For privacy questions, contact hello@enriqueite.com.

## Changes

Privacy policy updates will be published in this repository.

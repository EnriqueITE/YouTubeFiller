(() => {
  const ACTIVE_CLASS = "yt-window-cover-active";
  const BUTTON_ID = "yt-window-cover-button";
  const PLAYER_CLASS = "yt-window-cover-player";
  const VIDEO_CLASS = "yt-window-cover-video";
  const TOGGLE_MESSAGE = "TOGGLE_YT_WINDOW_COVER";
  const STORAGE_KEY = "customShortcut";
  const DEFAULT_CUSTOM_SHORTCUT = "\u00ba";

  let syncQueued = false;
  let customShortcut = DEFAULT_CUSTOM_SHORTCUT;

  function text(messageName, fallback, substitutions) {
    if (typeof chrome === "undefined" || !chrome.i18n || !chrome.i18n.getMessage) {
      return fallback;
    }

    return chrome.i18n.getMessage(messageName, substitutions) || fallback;
  }

  function isWatchPage() {
    return ["www.youtube.com", "youtube.com"].includes(window.location.hostname) && window.location.pathname === "/watch";
  }

  function isActive() {
    return document.documentElement.classList.contains(ACTIVE_CLASS);
  }

  function getPlayer() {
    return document.querySelector("#movie_player.html5-video-player")
      || document.querySelector("#movie_player")
      || document.querySelector(".html5-video-player");
  }

  function getVideo() {
    const player = getPlayer();
    return (player && player.querySelector("video.html5-main-video"))
      || document.querySelector("video.html5-main-video");
  }

  function getControls() {
    const player = getPlayer();
    return (player && player.querySelector(".ytp-right-controls"))
      || document.querySelector(".ytp-right-controls");
  }

  function getShortcutLabel() {
    return customShortcut || DEFAULT_CUSTOM_SHORTCUT;
  }

  function setButtonState(active) {
    const button = document.getElementById(BUTTON_ID);

    if (!button) {
      return;
    }

    const label = active
      ? text("buttonRestore", "Restore YouTube")
      : text("buttonFill", "Fill window");
    const title = `${label} (${getShortcutLabel()})`;

    button.setAttribute("aria-label", title);
    button.setAttribute("aria-pressed", String(active));
    button.title = title;
  }

  function markActiveElements() {
    const player = getPlayer();
    const video = getVideo();

    if (player) {
      player.classList.add(PLAYER_CLASS);
    }

    if (video) {
      video.classList.add(VIDEO_CLASS);
    }
  }

  function unmarkActiveElements() {
    document.querySelectorAll(`.${PLAYER_CLASS}`).forEach((node) => {
      node.classList.remove(PLAYER_CLASS);
    });

    document.querySelectorAll(`.${VIDEO_CLASS}`).forEach((node) => {
      node.classList.remove(VIDEO_CLASS);
    });
  }

  function enableCoverMode() {
    if (!isWatchPage()) {
      return false;
    }

    const player = getPlayer();
    const video = getVideo();

    if (!player || !video) {
      return false;
    }

    markActiveElements();
    document.documentElement.classList.add(ACTIVE_CLASS);
    setButtonState(true);
    return true;
  }

  function disableCoverMode() {
    document.documentElement.classList.remove(ACTIVE_CLASS);
    unmarkActiveElements();
    setButtonState(false);
  }

  function toggleCoverMode() {
    if (isActive()) {
      disableCoverMode();
      return false;
    }

    return enableCoverMode();
  }

  function createButton() {
    const button = document.createElement("button");
    button.id = BUTTON_ID;
    button.type = "button";
    button.className = "ytp-button yt-window-cover-button";
    button.setAttribute("aria-pressed", "false");
    button.innerHTML = [
      '<svg class="yt-window-cover-glyph" viewBox="0 0 36 36" aria-hidden="true" focusable="false">',
      '<g class="yt-window-cover-icon" transform="translate(18 18)">',
      '<path d="M-3 -3L-10.5 -10.5"></path>',
      '<path d="M-10.5 -10.5H-5.2"></path>',
      '<path d="M-10.5 -10.5v5.3"></path>',
      '<path d="M3 -3L10.5 -10.5"></path>',
      '<path d="M10.5 -10.5H5.2"></path>',
      '<path d="M10.5 -10.5v5.3"></path>',
      '<path d="M-3 3L-10.5 10.5"></path>',
      '<path d="M-10.5 10.5H-5.2"></path>',
      '<path d="M-10.5 10.5V5.2"></path>',
      '<path d="M3 3L10.5 10.5"></path>',
      '<path d="M10.5 10.5H5.2"></path>',
      '<path d="M10.5 10.5V5.2"></path>',
      '</g>',
      "</svg>"
    ].join("");

    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      toggleCoverMode();
    });

    setButtonState(false);
    return button;
  }

  function removeButton() {
    const button = document.getElementById(BUTTON_ID);

    if (button) {
      button.remove();
    }
  }

  function getDirectChildForSelector(parent, selector) {
    return Array.from(parent.children).find((child) => {
      return child.matches(selector) || Boolean(child.querySelector(selector));
    }) || null;
  }

  function placeButtonInControls(controls, button, referenceNode) {
    if (referenceNode && referenceNode.parentNode === controls) {
      if (button.parentElement === controls && button.nextElementSibling === referenceNode) {
        return;
      }

      try {
        controls.insertBefore(button, referenceNode);
        return;
      } catch (_error) {
        // YouTube can rebuild controls between lookup and insertion. Retry on the next sync.
        window.setTimeout(queueSync, 100);
        return;
      }
    }

    if (button.parentElement !== controls) {
      try {
        controls.appendChild(button);
      } catch (_error) {
        window.setTimeout(queueSync, 100);
      }
    }
  }

  function ensureButton() {
    if (!isWatchPage()) {
      removeButton();
      return;
    }

    const controls = getControls();

    if (!controls) {
      return;
    }

    const fullscreenControl = getDirectChildForSelector(controls, ".ytp-fullscreen-button");
    let button = document.getElementById(BUTTON_ID);

    if (!button) {
      button = createButton();
    }

    placeButtonInControls(controls, button, fullscreenControl);
    setButtonState(isActive());
  }

  function syncWithPage() {
    if (!isWatchPage()) {
      disableCoverMode();
      removeButton();
      return;
    }

    ensureButton();

    if (isActive()) {
      markActiveElements();
    }
  }

  function queueSync() {
    if (syncQueued) {
      return;
    }

    syncQueued = true;
    window.requestAnimationFrame(() => {
      syncQueued = false;
      syncWithPage();
    });
  }

  function isTypingTarget(target) {
    if (!target || target === document.body || target === document.documentElement) {
      return false;
    }

    const element = target instanceof Element ? target : target.parentElement;

    return Boolean(element && element.closest('input, textarea, select, [contenteditable=""], [contenteditable="true"], ytd-searchbox'));
  }

  function normalizeKey(key) {
    if (!key) {
      return "";
    }

    if (key === " ") {
      return "Space";
    }

    if (key.length === 1) {
      return key.toUpperCase();
    }

    const aliases = {
      ArrowUp: "Up",
      ArrowDown: "Down",
      ArrowLeft: "Left",
      ArrowRight: "Right",
      Esc: "Escape"
    };

    return aliases[key] || key;
  }

  function shortcutFromEvent(event) {
    const key = normalizeKey(event.key);

    if (!key || ["Control", "Shift", "Alt", "Meta"].includes(key)) {
      return "";
    }

    const parts = [];

    if (event.ctrlKey) {
      parts.push("Ctrl");
    }

    if (event.altKey) {
      parts.push("Alt");
    }

    if (event.shiftKey) {
      parts.push("Shift");
    }

    if (event.metaKey) {
      parts.push("Meta");
    }

    parts.push(key);
    return parts.join("+");
  }

  function isShortcutMatch(event) {
    if (customShortcut === DEFAULT_CUSTOM_SHORTCUT && event.code === "Backquote" && !event.ctrlKey && !event.altKey && !event.shiftKey && !event.metaKey) {
      return true;
    }

    return shortcutFromEvent(event) === customShortcut;
  }

  function handleKeydown(event) {
    if (event.key === "Escape" && isActive() && !document.fullscreenElement) {
      disableCoverMode();
      event.preventDefault();
      event.stopPropagation();
      return;
    }

    if (!customShortcut || event.repeat || isTypingTarget(event.target)) {
      return;
    }

    if (!isShortcutMatch(event)) {
      return;
    }

    toggleCoverMode();
    event.preventDefault();
    event.stopPropagation();
  }

  function loadSettings() {
    if (typeof chrome === "undefined" || !chrome.storage || !chrome.storage.sync) {
      return;
    }

    chrome.storage.sync.get({ [STORAGE_KEY]: DEFAULT_CUSTOM_SHORTCUT }, (items) => {
      customShortcut = String(items[STORAGE_KEY] || DEFAULT_CUSTOM_SHORTCUT);
      setButtonState(isActive());
    });

    chrome.storage.onChanged.addListener((changes, areaName) => {
      if (areaName !== "sync" || !changes[STORAGE_KEY]) {
        return;
      }

      customShortcut = String(changes[STORAGE_KEY].newValue || DEFAULT_CUSTOM_SHORTCUT);
      setButtonState(isActive());
    });
  }

  if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.onMessage) {
    chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
      if (!message || message.type !== TOGGLE_MESSAGE) {
        return false;
      }

      const active = toggleCoverMode();
      sendResponse({ active, handled: isWatchPage() });
      return false;
    });
  }

  loadSettings();

  document.addEventListener("keydown", handleKeydown, true);
  document.addEventListener("yt-navigate-finish", queueSync);
  document.addEventListener("yt-page-data-updated", queueSync);
  window.addEventListener("popstate", queueSync);
  window.addEventListener("pageshow", queueSync);

  const observerTarget = document.documentElement || document.body;
  const observer = new MutationObserver(queueSync);

  if (observerTarget) {
    observer.observe(observerTarget, { childList: true, subtree: true });
  }

  syncWithPage();
  window.setTimeout(queueSync, 500);
  window.setTimeout(queueSync, 1500);
  window.setTimeout(queueSync, 3000);
})();
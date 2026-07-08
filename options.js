/*
 * YouTube Filler
 * Copyright (C) 2026 Enrique Serrano Aparicio
 *
 * This program comes with ABSOLUTELY NO WARRANTY.
 * This is free software, and you are welcome to redistribute it
 * under certain conditions; see LICENSE for details.
 *
 * SPDX-License-Identifier: GPL-3.0-only
 */
const STORAGE_KEY = "customShortcut";
const SHORTCUT_UPDATED_MESSAGE = "YT_WINDOW_COVER_SHORTCUT_UPDATED";
const DEFAULT_CUSTOM_SHORTCUT = "\u00ba";
const DEFAULT_SHORTCUT_DEFINITION = {
  label: DEFAULT_CUSTOM_SHORTCUT,
  key: DEFAULT_CUSTOM_SHORTCUT,
  code: "Backquote",
  ctrlKey: false,
  altKey: false,
  shiftKey: false,
  metaKey: false
};
const MODIFIER_KEYS = ["Control", "Shift", "Alt", "Meta"];
const RESERVED_SHORTCUTS = new Set([
  "Ctrl+L",
  "Ctrl+N",
  "Ctrl+R",
  "Ctrl+T",
  "Ctrl+W",
  "Ctrl+Shift+N",
  "Ctrl+Shift+T",
  "Alt+Left",
  "Alt+Right",
  "Alt+F4",
  "Meta+L",
  "Meta+N",
  "Meta+R",
  "Meta+T",
  "Meta+W"
]);

const display = document.getElementById("shortcut-display");
const recordButton = document.getElementById("record-shortcut");
const clearButton = document.getElementById("clear-shortcut");
const status = document.getElementById("status");

let recording = false;

function text(messageName, fallback, substitutions) {
  if (typeof chrome === "undefined" || !chrome.i18n || !chrome.i18n.getMessage) {
    return fallback;
  }

  return chrome.i18n.getMessage(messageName, substitutions) || fallback;
}

function applyTranslations() {
  const uiLanguage = chrome.i18n.getUILanguage ? chrome.i18n.getUILanguage() : "en";

  document.documentElement.lang = uiLanguage.toLowerCase().startsWith("es") ? "es-ES" : "en";
  document.title = text("optionsTitle", "YouTube Filler");

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const messageName = node.getAttribute("data-i18n");
    node.textContent = text(messageName, node.textContent);
  });
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

  if (!key || MODIFIER_KEYS.includes(key)) {
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

function shortcutDefinitionFromEvent(event) {
  const label = shortcutFromEvent(event);

  if (!label) {
    return null;
  }

  return {
    label,
    key: event.key || "",
    code: event.code || "",
    ctrlKey: Boolean(event.ctrlKey),
    altKey: Boolean(event.altKey),
    shiftKey: Boolean(event.shiftKey),
    metaKey: Boolean(event.metaKey)
  };
}

function shortcutLabel(shortcut) {
  if (!shortcut) {
    return DEFAULT_CUSTOM_SHORTCUT;
  }

  if (typeof shortcut === "string") {
    return shortcut || DEFAULT_CUSTOM_SHORTCUT;
  }

  if (typeof shortcut === "object" && typeof shortcut.label === "string" && shortcut.label) {
    return shortcut.label;
  }

  return DEFAULT_CUSTOM_SHORTCUT;
}

function warningForShortcut(shortcut) {
  const label = shortcutLabel(shortcut);

  if (RESERVED_SHORTCUTS.has(label)) {
    return text("statusUnreliable", "Saved: $1. This shortcut may be reserved by the browser.", [label]);
  }

  return "";
}

function showShortcut(shortcut) {
  display.value = shortcutLabel(shortcut);
}

function setStatus(message) {
  status.textContent = message;
}

function setRecording(value) {
  recording = value;
  recordButton.classList.toggle("recording", recording);
  recordButton.textContent = recording
    ? text("recordingButton", "Press keys")
    : text("recordButton", "Record");
  setStatus(recording ? text("statusWaiting", "Waiting for keys...") : "");
}

function notifyShortcutUpdated(shortcut) {
  try {
    if (typeof chrome === "undefined" || !chrome.runtime || !chrome.runtime.sendMessage) {
      return;
    }

    chrome.runtime.sendMessage({
      type: SHORTCUT_UPDATED_MESSAGE,
      shortcut
    }, () => {
      void chrome.runtime.lastError;
    });
  } catch (_error) {
    // Storage remains the source of truth if direct tab notification is unavailable.
  }
}

function saveShortcut(shortcut, reset) {
  chrome.storage.sync.set({ [STORAGE_KEY]: shortcut }, () => {
    showShortcut(shortcut);
    const warning = warningForShortcut(shortcut);
    setStatus(reset
      ? text("statusCleared", "Shortcut reset to default.")
      : warning || text("statusSaved", "Saved: $1", [shortcutLabel(shortcut)]));
    notifyShortcutUpdated(shortcut);
  });
}

applyTranslations();

chrome.storage.sync.get({ [STORAGE_KEY]: DEFAULT_SHORTCUT_DEFINITION }, (items) => {
  showShortcut(items[STORAGE_KEY] || DEFAULT_SHORTCUT_DEFINITION);
});

recordButton.addEventListener("click", () => {
  setRecording(true);
  display.focus();
});

clearButton.addEventListener("click", () => {
  setRecording(false);
  saveShortcut(DEFAULT_SHORTCUT_DEFINITION, true);
});

document.addEventListener("keydown", (event) => {
  if (!recording) {
    return;
  }

  event.preventDefault();
  event.stopPropagation();

  if (event.key === "Escape") {
    setRecording(false);
    setStatus(text("statusCancelled", "Recording cancelled."));
    return;
  }

  const shortcut = shortcutDefinitionFromEvent(event);

  if (!shortcut) {
    setStatus(text("statusInvalid", "Press a normal key or a combination with Ctrl, Alt or Shift."));
    return;
  }

  setRecording(false);
  saveShortcut(shortcut);
}, true);
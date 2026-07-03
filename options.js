const STORAGE_KEY = "customShortcut";
const DEFAULT_CUSTOM_SHORTCUT = "\u00ba";

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

function showShortcut(shortcut) {
  display.value = shortcut || DEFAULT_CUSTOM_SHORTCUT;
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

function saveShortcut(shortcut) {
  chrome.storage.sync.set({ [STORAGE_KEY]: shortcut }, () => {
    showShortcut(shortcut);
    setStatus(shortcut
      ? text("statusSaved", "Saved: $1", [shortcut])
      : text("statusCleared", "Shortcut reset to default."));
  });
}

applyTranslations();

chrome.storage.sync.get({ [STORAGE_KEY]: DEFAULT_CUSTOM_SHORTCUT }, (items) => {
  showShortcut(String(items[STORAGE_KEY] || DEFAULT_CUSTOM_SHORTCUT));
});

recordButton.addEventListener("click", () => {
  setRecording(true);
  display.focus();
});

clearButton.addEventListener("click", () => {
  setRecording(false);
  saveShortcut(DEFAULT_CUSTOM_SHORTCUT);
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

  const shortcut = shortcutFromEvent(event);

  if (!shortcut) {
    setStatus(text("statusInvalid", "Press a normal key or a combination with Ctrl, Alt or Shift."));
    return;
  }

  setRecording(false);
  saveShortcut(shortcut);
}, true);
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
const TOGGLE_MESSAGE = "TOGGLE_YT_WINDOW_COVER";
const SHORTCUT_UPDATED_MESSAGE = "YT_WINDOW_COVER_SHORTCUT_UPDATED";

function sendTabMessage(tab, message) {
  if (!tab || typeof tab.id !== "number") {
    return;
  }

  chrome.tabs.sendMessage(tab.id, message, () => {
    // Reading lastError prevents expected noise when the active tab is not YouTube.
    void chrome.runtime.lastError;
  });
}

function sendToggleMessage(tab) {
  sendTabMessage(tab, { type: TOGGLE_MESSAGE });
}

function queryActiveTab(queryInfo, callback) {
  chrome.tabs.query(queryInfo, (tabs) => {
    callback(tabs && tabs[0]);
  });
}

function sendMessageToActiveTab(message) {
  queryActiveTab({ active: true, lastFocusedWindow: true }, (tab) => {
    if (tab) {
      sendTabMessage(tab, message);
      return;
    }

    queryActiveTab({ active: true, currentWindow: true }, (fallbackTab) => {
      sendTabMessage(fallbackTab, message);
    });
  });
}

chrome.runtime.onMessage.addListener((message) => {
  if (!message || message.type !== SHORTCUT_UPDATED_MESSAGE) {
    return false;
  }

  sendMessageToActiveTab({
    type: SHORTCUT_UPDATED_MESSAGE,
    shortcut: message.shortcut
  });
  return false;
});

chrome.commands.onCommand.addListener((command) => {
  if (command !== "toggle-cover-window") {
    return;
  }

  queryActiveTab({ active: true, lastFocusedWindow: true }, (tab) => {
    if (tab) {
      sendToggleMessage(tab);
      return;
    }

    queryActiveTab({ active: true, currentWindow: true }, sendToggleMessage);
  });
});
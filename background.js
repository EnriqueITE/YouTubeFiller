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
function sendToggleMessage(tab) {
  if (!tab || typeof tab.id !== "number") {
    return;
  }

  chrome.tabs.sendMessage(tab.id, { type: "TOGGLE_YT_WINDOW_COVER" }, () => {
    // Reading lastError prevents expected noise when the active tab is not YouTube.
    void chrome.runtime.lastError;
  });
}

function queryActiveTab(queryInfo, callback) {
  chrome.tabs.query(queryInfo, (tabs) => {
    callback(tabs && tabs[0]);
  });
}

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
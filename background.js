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
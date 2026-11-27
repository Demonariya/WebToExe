(() => {
  "use strict";

  const NAME_B64 = "__APP_NAME_BASE64__";
  const ICON_B64 = "__APP_ICON_BASE64__";
  const SHOW_MINIMIZE = __SHOW_MINIMIZE__;
  const SHOW_MAXIMIZE = __SHOW_MAXIMIZE__;
  const BAR_HEIGHT = 36;
  const BAR_ID = "webtoexe-custom-titlebar";
  const STYLE_ID = "webtoexe-custom-titlebar-style";
  const tauriWindow = window.__TAURI__ && window.__TAURI__.window;

  if (!tauriWindow || !tauriWindow.getCurrentWindow || !document.body || document.getElementById(BAR_ID)) return;

  const appWindow = tauriWindow.getCurrentWindow();
  const appName = new TextDecoder().decode(Uint8Array.from(atob(NAME_B64), (character) => character.charCodeAt(0)));
  const iconUrl = "data:image/png;base64," + ICON_B64;

  const maximizeIcon = '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3.25" y="3.25" width="9.5" height="9.5" rx="1" fill="none" stroke="currentColor" stroke-width="1.15"/></svg>';
  const restoreIcon = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5.25 5.25V3.8c0-.58.47-1.05 1.05-1.05h5.9c.58 0 1.05.47 1.05 1.05v5.9c0 .58-.47 1.05-1.05 1.05h-1.45" fill="none" stroke="currentColor" stroke-width="1.15"/><rect x="2.75" y="5.25" width="7.5" height="7.5" rx="1" fill="none" stroke="currentColor" stroke-width="1.15"/></svg>';
  const minimizeIcon = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8h9" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>';
  const closeIcon = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m4.25 4.25 7.5 7.5m0-7.5-7.5 7.5" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>';

  const style = document.createElement("style");
  style.id = STYLE_ID;
  style.textContent = [
    "#" + BAR_ID + "{position:fixed!important;inset:0 0 auto 0!important;z-index:2147483647!important;height:36px!important;min-height:36px!important;display:flex!important;align-items:center!important;justify-content:space-between!important;padding:0 0 0 14px!important;margin:0!important;box-sizing:border-box!important;color:var(--w2e-fg,#f4f4f5)!important;background:var(--w2e-surface,#17191d)!important;border:0!important;border-bottom:1px solid var(--w2e-border,rgba(255,255,255,.07))!important;box-shadow:none!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;font:500 13px/1 'Segoe UI',system-ui,sans-serif!important;letter-spacing:0!important;user-select:none!important;-webkit-user-select:none!important;-webkit-app-region:drag!important;overflow:hidden!important;isolation:isolate!important}",
    "#" + BAR_ID + " *{box-sizing:border-box!important}",
    "#" + BAR_ID + " .w2e-brand{display:flex!important;align-items:center!important;gap:10px!important;min-width:0!important;height:100%!important;flex:1 1 auto!important;padding-right:12px!important;overflow:hidden!important;pointer-events:none!important}",
    "#" + BAR_ID + " .w2e-icon{width:20px!important;height:20px!important;flex:0 0 20px!important;display:block!important;object-fit:contain!important;border-radius:5px!important;background:transparent!important}",
    "#" + BAR_ID + " .w2e-name{overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;color:inherit!important;font:inherit!important;font-weight:550!important;opacity:.98!important}",
    "#" + BAR_ID + " .w2e-controls{display:flex!important;align-items:stretch!important;align-self:stretch!important;flex:0 0 auto!important;height:100%!important;-webkit-app-region:no-drag!important}",
    "#" + BAR_ID + " button{appearance:none!important;-webkit-appearance:none!important;width:46px!important;min-width:46px!important;height:100%!important;min-height:0!important;display:grid!important;place-items:center!important;margin:0!important;padding:0!important;border:0!important;border-radius:0!important;outline:none!important;box-shadow:none!important;background:transparent!important;color:inherit!important;cursor:default!important;-webkit-app-region:no-drag!important;transition:background-color 120ms ease,color 120ms ease!important}",
    "#" + BAR_ID + " button:hover{background:var(--w2e-hover,rgba(255,255,255,.09))!important}",
    "#" + BAR_ID + " button:active{background:var(--w2e-active,rgba(255,255,255,.15))!important}",
    "#" + BAR_ID + " button:focus-visible{outline:1px solid var(--w2e-accent,#6b9de8)!important;outline-offset:-3px!important}",
    "#" + BAR_ID + " button svg{display:block!important;width:16px!important;height:16px!important;pointer-events:none!important}",
    "#" + BAR_ID + " #w2e-close:hover{color:#fff!important;background:#c42b1c!important}",
    "#" + BAR_ID + " #w2e-close:active{background:#a51f14!important}",
    "#" + BAR_ID + " button[hidden]{display:none!important}",
    "@media(prefers-reduced-motion:reduce){#" + BAR_ID + " button{transition:none!important}}"
  ].join("\n");
  document.head.appendChild(style);

  const bar = document.createElement("div");
  bar.id = BAR_ID;
  bar.setAttribute("role", "toolbar");
  bar.setAttribute("aria-label", appName + " window controls");
  bar.innerHTML = '<div class="w2e-brand" data-tauri-drag-region><img class="w2e-icon" alt="" draggable="false"><span class="w2e-name"></span></div><div class="w2e-controls"><button id="w2e-minimize" type="button" aria-label="Minimize" title="Minimize">' + minimizeIcon + '</button><button id="w2e-maximize" type="button" aria-label="Maximize" title="Maximize">' + maximizeIcon + '</button><button id="w2e-close" type="button" aria-label="Close" title="Close">' + closeIcon + "</button></div>";

  const appIcon = bar.querySelector(".w2e-icon");
  appIcon.src = iconUrl;
  appIcon.addEventListener("error", () => {
    appIcon.style.display = "none";
    const fallback = document.createElement("span");
    fallback.textContent = Array.from(appName.trim())[0]?.toUpperCase() || "A";
    fallback.setAttribute("aria-hidden", "true");
    fallback.style.cssText = "width:20px;height:20px;flex:0 0 20px;display:grid;place-items:center;border-radius:5px;background:var(--w2e-hover);color:inherit;font:600 12px/1 'Segoe UI',sans-serif";
    appIcon.parentElement.insertBefore(fallback, appIcon.nextSibling);
  }, { once: true });

  bar.querySelector(".w2e-name").textContent = appName;
  const minimizeButton = bar.querySelector("#w2e-minimize");
  const maximizeButton = bar.querySelector("#w2e-maximize");
  const closeButton = bar.querySelector("#w2e-close");
  minimizeButton.hidden = !SHOW_MINIMIZE;
  maximizeButton.hidden = !SHOW_MAXIMIZE;
  document.body.appendChild(bar);

  const originalPaddingTop = Number.parseFloat(getComputedStyle(document.body).paddingTop) || 0;
  document.body.style.setProperty("padding-top", (originalPaddingTop + BAR_HEIGHT) + "px", "important");
  document.documentElement.style.setProperty("scroll-padding-top", BAR_HEIGHT + "px");

  const fixedHeader = Array.from(document.querySelectorAll("header,[role='banner'],nav")).find((element) => {
    const computed = getComputedStyle(element);
    return computed.position === "fixed" && (Number.parseFloat(computed.top) || 0) <= 1;
  });
  if (fixedHeader) {
    fixedHeader.dataset.webtoexeOriginalTop = fixedHeader.style.top || "";
    fixedHeader.style.setProperty("top", BAR_HEIGHT + "px", "important");
  }

  function parseColor(value) {
    if (!value || value === "transparent") return null;
    const match = value.match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)/i);
    if (match) {
      const alpha = match[4] ? (match[4].endsWith("%") ? Number.parseFloat(match[4]) / 100 : Number.parseFloat(match[4])) : 1;
      if (alpha < 0.15) return null;
      return [Number(match[1]), Number(match[2]), Number(match[3])];
    }
    const hex = value.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
    if (hex) {
      const raw = hex[1].length === 3 ? Array.from(hex[1]).map((part) => part + part).join("") : hex[1];
      return [0, 2, 4].map((index) => Number.parseInt(raw.slice(index, index + 2), 16));
    }
    return null;
  }

  const luminance = (rgb) => {
    const channel = (value) => {
      value /= 255;
      return value <= 0.04045 ? value / 12.92 : Math.pow((value + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2]);
  };
  const contrastRatio = (first, second) => {
    const light = Math.max(luminance(first), luminance(second));
    const dark = Math.min(luminance(first), luminance(second));
    return (light + 0.05) / (dark + 0.05);
  };
  const toRgb = (rgb) => "rgb(" + rgb.map((value) => Math.round(value)).join(", ") + ")";
  const withAlpha = (rgb, alpha) => "rgba(" + rgb.map((value) => Math.round(value)).join(", ") + ", " + alpha + ")";

  function readTheme() {
    const rootStyle = getComputedStyle(document.documentElement);
    const bodyStyle = getComputedStyle(document.body);
    const header = document.querySelector("header,[role='banner'],nav");
    const headerStyle = header ? getComputedStyle(header) : null;
    const themeMeta = document.querySelector('meta[name="theme-color"]')?.content || "";

    // Prefer the document canvas and app root. Navigation can have a different
    // surface from the page itself (as on Instagram), so it is only a fallback.
    const appSurfaceCandidates = Array.from(
      document.querySelectorAll("main,[role='main'],#app,#root,[data-app-root]")
    ).slice(0, 8).map((element) => parseColor(getComputedStyle(element).backgroundColor));
    const surface = [
      parseColor(bodyStyle.backgroundColor),
      parseColor(rootStyle.backgroundColor),
      ...appSurfaceCandidates,
      parseColor(themeMeta),
      headerStyle && parseColor(headerStyle.backgroundColor)
    ].find(Boolean) || [18, 20, 24];

    const textCandidates = [
      parseColor(bodyStyle.color),
      parseColor(rootStyle.color),
      headerStyle && parseColor(headerStyle.color)
    ].filter(Boolean);
    const foreground = textCandidates.find((candidate) => contrastRatio(surface, candidate) >= 4.5)
      || (luminance(surface) > 0.48 ? [26, 27, 30] : [246, 247, 249]);

    let accent = null;
    for (const element of Array.from(document.querySelectorAll("button,[role='button'],a")).slice(0, 80)) {
      const candidate = parseColor(getComputedStyle(element).backgroundColor);
      if (candidate && contrastRatio(surface, candidate) > 1.8) {
        accent = candidate;
        break;
      }
    }
    if (!accent) {
      const firstLink = document.querySelector("a");
      accent = firstLink ? parseColor(getComputedStyle(firstLink).color) : null;
    }
    accent = accent || [100, 149, 237];

    bar.style.setProperty("--w2e-surface", toRgb(surface));
    bar.style.setProperty("--w2e-fg", toRgb(foreground));
    bar.style.setProperty("--w2e-border", withAlpha(foreground, 0.075));
    bar.style.setProperty("--w2e-hover", withAlpha(foreground, 0.09));
    bar.style.setProperty("--w2e-active", withAlpha(foreground, 0.15));
    bar.style.setProperty("--w2e-accent", toRgb(accent));
  }

  let themeFrame = 0;
  function scheduleThemeUpdate() {
    if (themeFrame) cancelAnimationFrame(themeFrame);
    themeFrame = requestAnimationFrame(() => {
      themeFrame = 0;
      readTheme();
    });
  }

  readTheme();
  const themeObserver = new MutationObserver(scheduleThemeUpdate);
  const observedAttributes = ["class", "style", "data-theme", "data-color-scheme"];
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: observedAttributes });
  themeObserver.observe(document.body, { attributes: true, attributeFilter: observedAttributes });

  const themeTargets = [
    document.querySelector("main"),
    document.querySelector("#app"),
    document.querySelector("#root"),
    document.querySelector("[data-app-root]"),
    document.querySelector("header,[role='banner'],nav")
  ].filter((element, index, all) => element && all.indexOf(element) === index);
  for (const target of themeTargets) {
    if (target !== document.body && target !== document.documentElement) {
      themeObserver.observe(target, { attributes: true, attributeFilter: observedAttributes });
    }
  }
  if (document.head) {
    themeObserver.observe(document.head, { subtree: true, childList: true, attributes: true, attributeFilter: ["content"] });
  }

  const colorScheme = window.matchMedia("(prefers-color-scheme: dark)");
  colorScheme.addEventListener?.("change", scheduleThemeUpdate);
  window.addEventListener("resize", scheduleThemeUpdate, { passive: true });
  window.addEventListener("pageshow", scheduleThemeUpdate);
  const themeTimer = window.setInterval(scheduleThemeUpdate, 2500);

  async function updateMaximizeState() {
    if (!SHOW_MAXIMIZE) return;
    try {
      const maximized = await appWindow.isMaximized();
      maximizeButton.innerHTML = maximized ? restoreIcon : maximizeIcon;
      maximizeButton.title = maximized ? "Restore" : "Maximize";
      maximizeButton.setAttribute("aria-label", maximized ? "Restore" : "Maximize");
      maximizeButton.setAttribute("aria-pressed", String(maximized));
    } catch (error) {
      console.warn("WebToExe could not read the window state.", error);
    }
  }

  minimizeButton.addEventListener("click", (event) => {
    event.stopPropagation();
    appWindow.minimize().catch((error) => console.error("Minimize failed.", error));
  });
  maximizeButton.addEventListener("click", (event) => {
    event.stopPropagation();
    appWindow.toggleMaximize().then(updateMaximizeState).catch((error) => console.error("Maximize toggle failed.", error));
  });
  closeButton.addEventListener("click", (event) => {
    event.stopPropagation();
    appWindow.close().catch((error) => console.error("Close failed.", error));
  });

  bar.addEventListener("mousedown", (event) => {
    if (event.button !== 0 || event.target.closest("button")) return;
    if (event.detail === 2) {
      if (SHOW_MAXIMIZE) appWindow.toggleMaximize().then(updateMaximizeState).catch(console.error);
      return;
    }
    appWindow.startDragging().catch((error) => console.error("Window dragging failed.", error));
  });

  if (SHOW_MAXIMIZE) {
    updateMaximizeState();
    window.addEventListener("resize", updateMaximizeState, { passive: true });
  }

  window.addEventListener("pagehide", () => {
    themeObserver.disconnect();
    window.clearInterval(themeTimer);
    colorScheme.removeEventListener?.("change", scheduleThemeUpdate);
  }, { once: true });
})();
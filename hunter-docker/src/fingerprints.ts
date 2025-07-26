import { Page } from "puppeteer";
import { randomFromArray } from "./utils.js";
import UAParser from "ua-parser-js";

/**
 * Apply deep fingerprint spoofing. Stealth plugin handles most, we patch the rest.
 * NOTE: Order matters: call this BEFORE any navigation.
 */
export async function applyFingerprint(
  page: Page,
  opts: {
    language: string;
    timezone: string;
  }
) {
  const { language, timezone } = opts;

  // Random realistic viewport
  const viewports = [
    { width: 1366, height: 768 },
    { width: 1920, height: 1080 },
    { width: 1536, height: 864 },
    { width: 1440, height: 900 },
    { width: 1600, height: 900 },
  ];
  const viewport = randomFromArray(viewports);
  await page.setViewport({ ...viewport, deviceScaleFactor: 1 });

  // User Agent
  const uas = [
    // Keep updated with popular versions
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
  ];
  const ua = randomFromArray(uas);
  await page.setUserAgent(ua);

  // Accept-Language
  await page.setExtraHTTPHeaders({
    "Accept-Language": language,
  });

  await page.emulateTimezone(timezone);

  // @ts-ignore
  const parser = new UAParser(ua);
  const isChrome = parser.getBrowser().name?.toLowerCase().includes("chrome");

  // Patch navigator.plugins, languages, permissions, webrtc, etc.
  await page.evaluateOnNewDocument(
    (data) => {
      // navigator.languages
      Object.defineProperty(navigator, "languages", {
        get: () => data.languages,
      });

      // navigator.language
      Object.defineProperty(navigator, "language", {
        get: () => data.languages[0],
      });

      // navigator.platform
      Object.defineProperty(navigator, "platform", {
        get: () => data.platform,
      });

      // navigator.hardwareConcurrency
      Object.defineProperty(navigator, "hardwareConcurrency", {
        get: () => data.hardwareConcurrency,
      });

      // plugins length
      Object.defineProperty(navigator, "plugins", {
        get: () => data.plugins,
      });

      // deviceMemory
      Object.defineProperty(navigator, "deviceMemory", {
        get: () => data.deviceMemory,
      });

      // WebGL vendor/renderer spoof
      const getParameter = WebGLRenderingContext.prototype.getParameter;
      WebGLRenderingContext.prototype.getParameter = function (param) {
        if (param === 37445) return data.webglVendor; // UNMASKED_VENDOR_WEBGL
        if (param === 37446) return data.webglRenderer; // UNMASKED_RENDERER_WEBGL
        return getParameter.call(this, param);
      };

      // Canvas fingerprinting mitigation
      const toDataURL = HTMLCanvasElement.prototype.toDataURL;
      HTMLCanvasElement.prototype.toDataURL = function (...args) {
        const ctx = this.getContext("2d");
        if (ctx) {
          ctx.fillStyle = "rgba(0,0,0,0.01)";
          ctx.fillRect(0, 0, this.width, this.height);
        }
        return toDataURL.apply(this, args as any);
      };

      // Audio fingerprint patch
      const oldOscillator = OfflineAudioContext.prototype.startRendering;
      OfflineAudioContext.prototype.startRendering = function () {
        const r = oldOscillator.apply(this, arguments as any);
        const clone = this.createOscillator;
        this.createOscillator = function () {
          const o = clone.apply(this, arguments as any);
          o.frequency.value = o.frequency.value + 0.0000001;
          return o;
        };
        return r;
      };

      // Permissions API - always grant notifications
      const originalQuery = (navigator as any).permissions?.query;
      if (originalQuery) {
        (navigator as any).permissions.query = (parameters: any) =>
          parameters.name === "notifications"
            ? Promise.resolve({ state: "denied" })
            : originalQuery(parameters);
      }

      // WebRTC local IP leak patch
      const origCreateOffer = RTCPeerConnection.prototype.createOffer;
      //   @ts-ignore
      RTCPeerConnection.prototype.createOffer = function (...args: any[]) {
        const pc = this;
        pc.addEventListener("icecandidate", (e: any) => {
          if (!e || !e.candidate) return;
          e.candidate.candidate = e.candidate.candidate.replace(
            /((?:\d{1,3}\.){3}\d{1,3})/g,
            "192.168.1.2"
          );
        });
        // @ts-ignore
        return origCreateOffer.apply(pc, args);
      };

      // Touch support
      const touchEvent = () => true;
      try {
        Object.defineProperty(window, "ontouchstart", { get: touchEvent });
      } catch {}
      (window as any).TouchEvent = function () {};

      // Navigator.connection (downlink, rtt) minimal mock
      (navigator as any).connection = {
        downlink: 10,
        rtt: 50,
        effectiveType: "4g",
        saveData: false,
      };
    },
    {
      languages: [language],
      platform: isChrome ? "Win32" : "MacIntel",
      hardwareConcurrency: [4, 8, 12, 16][Math.floor(Math.random() * 4)],
      deviceMemory: [4, 8, 16][Math.floor(Math.random() * 3)],
      plugins: [1, 2, 3, 4, 5].map((i) => ({
        name: `Plugin ${i}`,
        filename: `plugin${i}.dll`,
        description: "Fake plugin",
      })),
      webglVendor: randomFromArray([
        "Intel Inc.",
        "Google Inc.",
        "NVIDIA Corporation",
      ]),
      webglRenderer: randomFromArray([
        "Intel Iris OpenGL Engine",
        "ANGLE (Intel, Intel(R) HD Graphics 630, OpenGL 4.6.0)",
        "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB, OpenGL 4.5.0)",
      ]),
      language,
    }
  );

  // Preload fonts via CSS injection (helps font detection scripts)
  await page.evaluateOnNewDocument(() => {
    const style = document.createElement("style");
    style.innerHTML = `
      @font-face { font-family: 'NotoSans'; src: local('Noto Sans'); }
      body { font-family: 'NotoSans', sans-serif !important; }
    `;
    document.head.appendChild(style);
  });
}


/**
 * Pinchtab OpenClaw Plugin
 *
 * Single-tool design: one `pinchtab` tool with an `action` parameter.
 * Minimal context bloat — one tool definition covers all browser operations.
 */

interface PluginConfig {
  baseUrl?: string;
  token?: string;
  timeout?: number;
}

interface PluginApi {
  config: { plugins?: { entries?: Record&lt;string, { config?: PluginConfig }&gt; } };
  registerTool: (tool: any, opts?: { optional?: boolean }) =&gt; void;
}

function getConfig(api: PluginApi): PluginConfig {
  return api.config?.plugins?.entries?.pinchtab?.config ?? {};
}

async function pinchtabFetch(
  cfg: PluginConfig,
  path: string,
  opts: { method?: string; body?: unknown; rawResponse?: boolean } = {},
): Promise&lt;any&gt; {
  const base = cfg.baseUrl || "http://localhost:9867";
  const url = `${base}${path}`;
  const headers: Record&lt;string, string&gt; = {};

  if (cfg.token) headers["Authorization"] = `Bearer ${cfg.token}`;
  if (opts.body) headers["Content-Type"] = "application/json";

  const controller = new AbortController();
  const timeout = cfg.timeout || 30000;
  const timer = setTimeout(() =&gt; controller.abort(), timeout);

  try {
    const res = await fetch(url, {
      method: opts.method || (opts.body ? "POST" : "GET"),
      headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
      signal: controller.signal,
    });

    if (opts.rawResponse) return res;

    const text = await res.text();
    if (!res.ok) {
      return { error: `${res.status} ${res.statusText}`, body: text };
    }

    try {
      return JSON.parse(text);
    } catch {
      return { text };
    }
  } catch (err: any) {
    if (err?.name === "AbortError") {
      return { error: `Request timed out after ${timeout}ms: ${path}` };
    }
    return {
      error: `Connection failed: ${err?.message || err}. Is Pinchtab running at ${base}?`,
    };
  } finally {
    clearTimeout(timer);
  }
}

function textResult(data: any): any {
  const text =
    typeof data === "string" ? data : data?.text ?? JSON.stringify(data, null, 2);
  return { content: [{ type: "text", text }] };
}

export default function register(api: PluginApi) {
  api.registerTool(
    {
      name: "pinchtab",
      description: `Browser control via Pinchtab. Actions:
- navigate: go to URL (url, tabId?, newTab?, blockImages?, timeout?)
- snapshot: accessibility tree (filter?, format?, selector?, maxTokens?, depth?, diff?, tabId?)
- click/type/press/fill/hover/scroll/select/focus: act on element (ref, text?, key?, value?, scrollY?, waitNav?, tabId?)
- text: extract readable text (mode?, tabId?)
- tabs: list/new/close tabs (tabAction?, url?, tabId?)
- screenshot: JPEG screenshot (quality?, tabId?)
- evaluate: run JS (expression, tabId?)
- pdf: export page as PDF (landscape?, scale?, tabId?)
- health: check connectivity

Token strategy: use "text" for reading (~800 tokens), "snapshot" with filter=interactive&amp;format=compact for interactions (~3,600), diff=true on subsequent snapshots.`,
      parameters: {
        type: "object",
        properties: {
          action: {
            type: "string",
            enum: [
              "navigate",
              "snapshot",
              "click",
              "type",
              "press",
              "fill",
              "hover",
              "scroll",
              "select",
              "focus",
              "text",
              "tabs",
              "screenshot",
              "evaluate",
              "pdf",
              "health",
            ],
            description: "Action to perform",
          },
          url: { type: "string", description: "URL for navigate or new tab" },
          ref: {
            type: "string",
            description: "Element ref from snapshot (e.g. e5)",
          },
          text: { type: "string", description: "Text to type or fill" },
          key: {
            type: "string",
            description: "Key to press (e.g. Enter, Tab, Escape)",
          },
          expression: {
            type: "string",
            description: "JavaScript expression for evaluate",
          },
          selector: {
            type: "string",
            description: "CSS selector for snapshot scope or action target",
          },
          filter: {
            type: "string",
            enum: ["interactive", "all"],
            description: "Snapshot filter: interactive = buttons/links/inputs only",
          },
          format: {
            type: "string",
            enum: ["json", "compact", "text", "yaml"],
            description: "Snapshot format: compact is most token-efficient",
          },
          maxTokens: {
            type: "number",
            description: "Truncate snapshot to ~N tokens",
          },
          depth: { type: "number", description: "Max snapshot tree depth" },
          diff: {
            type: "boolean",
            description: "Snapshot diff: only changes since last snapshot",
          },
          value: { type: "string", description: "Value for select dropdown" },
          scrollY: {
            type: "number",
            description: "Pixels to scroll vertically",
          },
          waitNav: {
            type: "boolean",
            description: "Wait for navigation after action",
          },
          tabId: { type: "string", description: "Target tab ID" },
          tabAction: {
            type: "string",
            enum: ["list", "new", "close"],
            description: "Tab sub-action (default: list)",
          },
        },
        required: ["action"],
      },
      async handler(params: any) {
        const cfg = getConfig(api);
        const action = params.action;

        // --- health ---
        if (action === "health") {
          return textResult(await pinchtabFetch(cfg, "/health"));
        }

        // --- navigate ---
        if (action === "navigate") {
          const body: any = { url: params.url };
          if (params.tabId) body.tabId = params.tabId;
          if (params.newTab) body.newTab = true;
          if (params.blockImages) body.blockImages = true;
          if (params.timeout) body.timeout = params.timeout;
          return textResult(await pinchtabFetch(cfg, "/navigate", { body }));
        }

        // --- snapshot ---
        if (action === "snapshot") {
          const query = new URLSearchParams();
          if (params.filter) query.set("filter", params.filter);
          if (params.format) query.set("format", params.format);
          if (params.selector) query.set("selector", params.selector);
          if (params.maxTokens) query.set("maxTokens", String(params.maxTokens));
          if (params.depth) query.set("depth", String(params.depth));
          if (params.diff) query.set("diff", "true");
          if (params.tabId) query.set("tabId", params.tabId);
          const qs = query.toString();
          return textResult(await pinchtabFetch(cfg, `/snapshot${qs ? `?${qs}` : ""}`));
        }

        // --- text ---
        if (action === "text") {
          const query = new URLSearchParams();
          if (params.tabId) query.set("tabId", params.tabId);
          const qs = query.toString();
          return textResult(await pinchtabFetch(cfg, `/text${qs ? `?${qs}` : ""}`));
        }

        // --- actions (click/type/press/fill/hover/scroll/select/focus) ---
        if (["click", "type", "press", "fill", "hover", "scroll", "select", "focus"].includes(action)) {
          const body: any = { kind: action };
          if (params.ref) body.ref = params.ref;
          if (params.text) body.text = params.text;
          if (params.key) body.key = params.key;
          if (params.value) body.value = params.value;
          if (params.scrollY) body.scrollY = params.scrollY;
          if (params.waitNav) body.waitNav = true;
          if (params.tabId) body.tabId = params.tabId;
          if (params.selector) body.selector = params.selector;
          return textResult(await pinchtabFetch(cfg, "/action", { body }));
        }

        // --- tabs ---
        if (action === "tabs") {
          const tabAction = params.tabAction || "list";
          if (tabAction === "list") {
            return textResult(await pinchtabFetch(cfg, "/tabs"));
          }
          const body: any = { action: tabAction };
          if (params.url) body.url = params.url;
          if (params.tabId) body.tabId = params.tabId;
          return textResult(await pinchtabFetch(cfg, "/tab", { body }));
        }

        // --- screenshot ---
        if (action === "screenshot") {
          const query = new URLSearchParams();
          if (params.tabId) query.set("tabId", params.tabId);
          if (params.quality) query.set("quality", String(params.quality));
          const qs = query.toString();
          try {
            const res = await pinchtabFetch(
              cfg,
              `/screenshot${qs ? `?${qs}` : ""}`,
              { rawResponse: true },
            );
            if (res instanceof Response) {
              if (!res.ok) {
                return textResult({
                  error: `Screenshot failed: ${res.status} ${await res.text()}`,
                });
              }
              const buf = await res.arrayBuffer();
              const b64 = Buffer.from(buf).toString("base64");
              return {
                content: [{ type: "image", data: b64, mimeType: "image/jpeg" }],
              };
            }
            return textResult(res);
          } catch (err: any) {
            return textResult({ error: `Screenshot failed: ${err?.message}` });
          }
        }

        // --- evaluate ---
        if (action === "evaluate") {
          const body: any = { expression: params.expression };
          if (params.tabId) body.tabId = params.tabId;
          return textResult(await pinchtabFetch(cfg, "/evaluate", { body }));
        }

        // --- pdf ---
        if (action === "pdf") {
          const query = new URLSearchParams();
          if (params.tabId) query.set("tabId", params.tabId);
          if (params.landscape) query.set("landscape", "true");
          if (params.scale) query.set("scale", String(params.scale));
          const qs = query.toString();
          return textResult(
            await pinchtabFetch(cfg, `/pdf${qs ? `?${qs}` : ""}`),
          );
        }

        return textResult({ error: `Unknown action: ${action}` });
      },
    },
    { optional: true },
  );
}


# 🌐 Gemini Web2API Gateway (gem2api)

> **Universal multi-protocol bridge connecting Google Gemini Web sessions to OpenAI & Anthropic Claude APIs with Google 4 Series (4 Neon, 4 Hydrogen), multi-account pooling, and 1-click Web UI management.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Compatible](https://img.shields.io/badge/API-OpenAI%20Compatible-green.svg)](#)
[![Anthropic Claude Ready](https://img.shields.io/badge/API-Anthropic%20Claude-purple.svg)](#)
[![Google 4 Series Ready](https://img.shields.io/badge/Model-4%20Neon%20%7C%204%20Hydrogen-blueviolet.svg)](#)
[![MCP Ready](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-orange.svg)](#)

---

## 📌 Overview

**Gemini Web2API Gateway (`gem2api`)** is an open-source multi-protocol bridge that translates your Google Gemini Web session into standardized, drop-in replacement REST APIs for:
1. **OpenAI API** (`/v1/chat/completions`, `/v1/models`)
2. **Anthropic Claude Messages API** (`/v1/messages`, `/claude/v1/messages`)
3. **Gemini Deep Research** (`/gemini/v1beta/interactions`)
4. **Google 4 Series** (`gemini-4-neon`, `gemini-4-hydrogen`, `gemini-4-argon`)
5. **OpenAI Codex Responses** (`/v1/responses`)

Designed specifically for developers, researchers, and agentic workflows, it connects Gemini Web directly to IDE plugins, local developer tools, and autonomous coding assistants like **Claude Code**, **Cline**, **OpenCode**, **Cursor**, and **OpenDevin** without protocol incompatibilities.

---

## 🏛️ Architecture & Workflow

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Developer Clients                             │
│       OpenCode  •  Cline  •  Cursor  •  Claude Code  •  OpenDevin      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Standard OpenAI (/v1) or Claude (/v1/messages)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Gemini Web2API Gateway                          │
│  • Google 4 Series Ticket Header Engine (4 Neon, 4 Hydrogen, 4 Argon)  │
│  • Web UI Dashboard & 1-Click Cookie Importer (Cookie-Editor / Raw)   │
│  • Automatic SNlM0e XSRF Security Token Handshake & Extraction         │
│  • Anthropic Claude Adapter (translates messages, system & thinking)   │
│  • Agent Tool Adapter (formats MCP schemas & parallel tool execution)  │
│  • Deep Research Engine (autonomous multi-stage web-grounded research) │
│  • Hardened Scotty Resumable Upload (multimodal vision + fallback)     │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
┌───────────────────────────────────────┐  ┌─────────────────────────────┐
│     SQLite Session Pool & Router      │  │ Browser Companion Extension │
│  • Multi-Account Rotation & Failover  │  │  • Multi-Profile Sync       │
│  • Cooldown Backoff Tracking          │  │  • Automated Session Refresh│
│  • Account-Specific API Keys          │  │  • Background Worker Keep   │
└───────────────────┬───────────────────┘  └──────────────┬──────────────┘
                    │                                     │
                    └───────────────────┬─────────────────┘
                                        │ HTTPS Session Stream
                                        ▼
                        ┌───────────────────────────────┐
                        │       Google Gemini Web       │
                        │  4 Neon (High / Med / Low)    │
                        │  4 Hydrogen • 3.8 Flash • Pro │
                        │  Deep Research • Web Search   │
                        └───────────────────────────────┘
```

---

## 🚀 Quick Start on Any Device (Termux, Linux, macOS, WSL)

Deploy in seconds with a single command on any device:

### 1. Clone the Repository
```bash
git clone https://github.com/mystxnavadeep/gem2api.git
cd gem2api
```

### 2. Service Management Commands
A universal controller script `./run.sh` (and `./gemini-gateway.sh`) is provided:

| Command | Action |
| :--- | :--- |
| **`./run.sh start`** | Start gateway as background daemon |
| **`./run.sh stop`** | Stop background gateway daemon |
| **`./run.sh restart`** | Restart gateway daemon |
| **`./run.sh status`** | Check process status, active accounts, and health |
| **`./run.sh logs`** | Stream live gateway output logs |
| **`./run.sh run`** | Run in foreground (for debugging) |
| **`./run.sh test`** | Run automated end-to-end test suite |

```bash
./run.sh start
```

### 3. Open the Web Dashboard
Visit **`http://localhost:10012/`** (or `http://<device-ip>:10012` from any browser on your local network).

---

## 🍪 Adding Accounts & Cookies via UI

You can add and manage multiple Google accounts directly from the Web Dashboard without opening config files or inspecting network devtools:

1. Click **`➕ Add Account / User`** on the dashboard.
2. Enter an optional **Account Name** (e.g. `tester`, `work_pro`, `personal`) and choose your **Auth Profile** (`0` for primary Google account, `1` for secondary).
3. Provide your cookies in **ANY** comfortable format:
   - **Browser Extension JSON Export**: Click "Export JSON" in **Cookie-Editor** or **EditThisCookie** and paste it directly (or click "Upload File" to pick `cookies.json`).
   - **Raw Cookie Header**: Paste standard header strings (`__Secure-1PSID=...; __Secure-1PSIDTS=...; SID=...; SAPISID=...;`).
   - **Key-Value JSON**: Paste `{ "__Secure-1PSID": "...", "__Secure-1PSIDTS": "..." }`.
   - **Gateway Sync Payload**: Paste `{ "cookie": "...", "xsrf_token": "..." }`.
4. **Automatic Handshake**: Keep *Auto-Extract & Verify* checked. The gateway will:
   - Calculate Google `SAPISIDHASH` authorization.
   - Handshake with Google Gemini web servers.
   - Automatically extract `SNlM0e` (XSRF security token) and build label `cfb2h`.
   - Capture fresh `__Secure-1PSIDTS` tokens.
   - Generate a unique dedicated API key (`sk-gemini-<account>-...`).
   - Register the account into the load-balanced SQLite pool.
5. Click **`🧪 Test 4 Neon`** next to the newly added account to verify live upstream response and latency!

---

## 📋 Model Directory & Aliases

| Model ID (API Name) | Protocol Target | Reasoning Engine | Recommended For |
| :--- | :--- | :---: | :--- |
| **`gemini-4-neon`** | OpenAI / Claude / Native | 🧠 Extended (High Thinking) | **Complex coding, architecture, deep reasoning** |
| `neon-medium` | OpenAI / Claude / Native | 🧠 Extended (Medium) | Balanced deep thinking |
| `neon-low` | OpenAI / Claude / Native | 🧠 Extended (Low) | Fast structured reasoning |
| **`gemini-4-hydrogen`** | OpenAI / Claude / Native | Standard | Everyday speed and quick tasks |
| `gemini-auto` | OpenAI / Claude / Native | Adaptive | Google automatic model selection |
| `gemini-4-argon` | OpenAI / Claude / Native | Frontier Preview | Experimental Google 4 preview |
| `gemini-3.8-flash` | OpenAI / Claude / Native | Standard | General coding, fast completions |
| `gemini-3.8-flash-thinking` | OpenAI / Claude / Native | 🧠 Extended (`mode: 2`) | Autonomous coding agents, MCP |
| `claude-3-7-sonnet` | Anthropic Claude (`/v1/messages`) | 🧠 Extended | **Claude Code, Cursor, complex agentic workflows** |
| `claude-3-5-sonnet` | Anthropic Claude (`/v1/messages`) | 🧠 Extended | High-accuracy code architecture & refactoring |
| `claude-3-5-haiku` | Anthropic Claude (`/v1/messages`) | Standard (`mode: 6`) | Ultra-fast token streaming, summaries |
| `gemini-deep-research` | Interactions / OpenAI | 🔍 Grounded Research | Multi-source investigation and report synthesis |

---

## 🛠️ Client Configuration

### 1. Claude Code / Terminal Agent
```bash
export ANTHROPIC_BASE_URL="http://localhost:10012"
export ANTHROPIC_API_KEY="sk-gemini-example-key"
export CLAUDE_MODEL="claude-3-7-sonnet"
claude
```

### 2. Cline / Roo Code (VS Code Extension)
- **API Provider**: `Anthropic` or `OpenAI Compatible`
- **Base URL**: `http://localhost:10012` (for Anthropic) or `http://localhost:10012/v1` (for OpenAI)
- **API Key**: Any key or your account-specific key (e.g. `sk-gemini-tester-...`)
- **Model ID**: `gemini-4-neon` or `claude-3-7-sonnet`

### 3. OpenCode / OpenCode Studio
In custom provider settings:
- **Provider**: `OpenAI-Compatible`
- **Base URL**: `http://localhost:10012/v1`
- **API Key**: Enter any key or your account-specific key.
- **Model**: `gemini-4-neon`

### 4. Cursor / Continue.dev
In `.cursorrules` or `continue/config.json`:
```json
{
  "models": [
    {
      "title": "Google 4 Neon",
      "provider": "openai",
      "model": "gemini-4-neon",
      "apiBase": "http://localhost:10012/v1",
      "apiKey": "sk-gemini-example-key"
    },
    {
      "title": "Claude 3.7 Sonnet (via Gemini)",
      "provider": "anthropic",
      "model": "claude-3-7-sonnet",
      "apiBase": "http://localhost:10012",
      "apiKey": "sk-gemini-example-key"
    }
  ]
}
```

---

## 🧪 End-to-End Verification

A comprehensive automated test suite covers all protocols:

```bash
./run.sh test
```

Covers:
- OpenAI `/v1/chat/completions` compatibility
- Anthropic Claude `/v1/messages` non-streaming, streaming, and tool calls
- Token estimation `/v1/messages/count_tokens`
- Scotty resumable upload MIME parsing and image extraction
- Deep Research plan generation and synthesis
- UI Cookie parsing across Cookie-Editor arrays, raw strings, and sync objects
- Multi-account SQLite pool & live upstream session dispatch

---

## ☁️ Cloudflare Edge Worker Deployment

To deploy serverless on Cloudflare's edge network:

1. Navigate to the `cloudflare/` directory:
   ```bash
   cd cloudflare
   ```
2. Configure your secret cookie:
   ```bash
   npx wrangler secret put COOKIE_STRING
   ```
3. Deploy:
   ```bash
   npx wrangler deploy
   ```

See [`cloudflare/README.MD`](cloudflare/README.MD) for full details.

---

## 📄 License

Distributed under the [MIT License](LICENSE).

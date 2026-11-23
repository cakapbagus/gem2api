DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Web2API Gateway Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
</head>
<body class="bg-slate-100 font-sans p-4 md:p-8 text-slate-800">
    <div class="max-w-6xl mx-auto space-y-6">
        
        <!-- Header -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div>
                <div class="flex items-center gap-3">
                    <h1 class="text-2xl md:text-3xl font-extrabold text-blue-600 tracking-tight">Gemini Web2API Gateway</h1>
                    <span class="bg-blue-50 text-blue-700 text-xs font-semibold px-2.5 py-1 rounded-full border border-blue-200">v1.2.0 Universal</span>
                </div>
                <p class="text-sm text-slate-500 mt-1">Universal Multi-Protocol Bridge: OpenAI • Anthropic Claude • Google 4 Series (4 Neon) • Deep Research</p>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="openAddAccountModal()" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2.5 rounded-lg shadow-sm transition-all text-sm">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                    Add Account / User
                </button>
            </div>
        </div>
        
        <!-- Supported Protocols Banner -->
        <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
            <h2 class="text-sm font-bold text-slate-700 uppercase tracking-wider mb-3 flex items-center gap-2">
                <span>🔌</span> Active Protocols & Endpoints
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
                <div class="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
                    <div class="font-bold text-slate-800 text-sm mb-1 font-sans">OpenAI Compatible</div>
                    <div class="text-blue-600 font-semibold">POST /v1/chat/completions</div>
                    <div class="text-slate-500 mt-1 font-sans">Drop-in for Cline, OpenCode, Cursor, Chatbox</div>
                </div>
                <div class="bg-purple-50 p-3.5 rounded-lg border border-purple-200">
                    <div class="font-bold text-purple-900 text-sm mb-1 font-sans">Anthropic Claude</div>
                    <div class="text-purple-600 font-semibold">POST /v1/messages</div>
                    <div class="text-slate-500 mt-1 font-sans">Drop-in for Claude Code, LangChain, Anthropic SDK</div>
                </div>
                <div class="bg-emerald-50 p-3.5 rounded-lg border border-emerald-200">
                    <div class="font-bold text-emerald-900 text-sm mb-1 font-sans">Gemini Deep Research</div>
                    <div class="text-emerald-600 font-semibold">POST /gemini/v1beta/interactions</div>
                    <div class="text-slate-500 mt-1 font-sans">Autonomous web-grounded multi-turn research</div>
                </div>
            </div>
        </div>

        <!-- Master Info & Quick Controls -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col justify-between">
                <div>
                    <h2 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <span>🔑</span> Gateway Credentials
                    </h2>
                    <div class="space-y-2 text-sm">
                        <div class="flex items-center justify-between bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                            <span class="text-slate-600 font-medium">Master API Key:</span>
                            <div class="flex items-center gap-1.5">
                                <code id="master-key" class="font-mono text-xs bg-white px-2 py-1 rounded border border-slate-300 select-all">Loading...</code>
                                <button onclick="copyToClipboard(document.getElementById('master-key').textContent)" class="p-1 hover:bg-slate-200 rounded text-slate-500" title="Copy Key">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>
                                </button>
                            </div>
                        </div>
                        <div class="flex items-center justify-between text-xs text-slate-500 pt-1">
                            <span>Active Accounts in Pool: <strong id="total-accounts" class="text-blue-600 font-bold text-sm">0</strong></span>
                            <span>Auto Load-Balancing: <strong class="text-emerald-600 font-bold">Enabled</strong></span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col justify-between">
                <div>
                    <h2 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <span>⚙️</span> Health & Session Controls
                    </h2>
                    <div class="flex items-center justify-between mb-4">
                        <div>
                            <div class="text-sm font-medium text-slate-700">Incognito Mode</div>
                            <div class="text-xs text-slate-500">Temporary chats (no Google Gemini web history)</div>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" id="incognito-toggle" onchange="toggleIncognito(this.checked)" class="sr-only peer">
                            <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                        </label>
                    </div>
                </div>
                <div class="flex gap-2">
                    <button onclick="runHealthCheck()" class="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 px-3 rounded-lg text-sm transition-colors flex items-center justify-center gap-1.5">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        Verify All Accounts
                    </button>
                    <button onclick="triggerAutoSync()" class="bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium py-2 px-3 rounded-lg text-sm transition-colors border border-slate-300" title="Request sync from browser extension">
                        Sync Extension
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Accounts Table Section -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div class="p-5 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 bg-slate-50/50">
                <div class="flex items-center gap-2">
                    <h2 class="text-lg font-bold text-slate-800">Connected Accounts & Quotas</h2>
                    <span id="account-badge-count" class="bg-blue-100 text-blue-700 text-xs font-semibold px-2.5 py-0.5 rounded-full">0 active</span>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="openAddAccountModal()" class="inline-flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-colors">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                        Add Account
                    </button>
                    <button onclick="loadStats()" class="inline-flex items-center gap-1.5 bg-white hover:bg-slate-100 text-slate-700 text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-300 transition-colors">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                        Refresh
                    </button>
                </div>
            </div>
            
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-slate-200 text-sm text-left">
                    <thead class="bg-slate-50 text-slate-600 font-semibold text-xs uppercase tracking-wider">
                        <tr>
                            <th class="py-3 px-4">Account Name</th>
                            <th class="py-3 px-4">Dedicated API Key</th>
                            <th class="py-3 px-4">Auth Profile</th>
                            <th class="py-3 px-4">Status</th>
                            <th class="py-3 px-4">Cooldown</th>
                            <th class="py-3 px-4">Health Check</th>
                            <th class="py-3 px-4 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="accounts-table" class="divide-y divide-slate-100 text-slate-700 font-normal">
                        <tr><td colspan="7" class="py-6 text-center text-slate-400">Loading accounts...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- API Playground & Connection Test -->
        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div class="flex justify-between items-center mb-4 flex-wrap gap-3">
                <div>
                    <h2 class="text-lg font-bold text-slate-800">API Playground & Live Diagnostics</h2>
                    <p class="text-xs text-slate-500">Test generation upstream across OpenAI, Claude, or Deep Research protocols.</p>
                </div>
                <div class="flex items-center space-x-2 flex-wrap gap-2">
                    <label class="flex items-center space-x-1.5 text-xs text-slate-700 font-medium cursor-pointer bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-300">
                        <input type="checkbox" id="chat-thinking" class="form-checkbox h-3.5 w-3.5 text-blue-600 rounded">
                        <span>🧠 Extended thinking</span>
                    </label>
                    <select id="chat-protocol" class="border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs bg-slate-50 font-medium focus:ring-2 focus:ring-blue-500">
                        <option value="openai">Protocol: OpenAI (/v1/chat/completions)</option>
                        <option value="claude">Protocol: Claude (/v1/messages)</option>
                        <option value="research">Protocol: Deep Research</option>
                    </select>
                    <select id="chat-account" class="border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs bg-slate-50 font-medium focus:ring-2 focus:ring-blue-500">
                        <option value="auto">Auto Load-Balance</option>
                    </select>
                    <select id="chat-model" class="border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs bg-slate-50 font-medium focus:ring-2 focus:ring-blue-500">
                        <optgroup label="Google 4 Series">
                            <option value="gemini-4-neon" selected>4 Neon (Deeper analysis - High)</option>
                            <option value="neon-medium">4 Neon (Deeper analysis - Medium)</option>
                            <option value="neon-low">4 Neon (Deeper analysis - Low)</option>
                            <option value="gemini-4-hydrogen">4 Hydrogen (Everyday help)</option>
                            <option value="gemini-auto">Auto (Adapts to your needs)</option>
                            <option value="gemini-4-argon">4 Argon (Frontier Preview)</option>
                        </optgroup>
                        <optgroup label="Gemini Native">
                            <option value="gemini-3.8-flash">Gemini 3.8 Flash</option>
                            <option value="gemini-3.8-flash-thinking">Gemini 3.8 Flash (Thinking)</option>
                            <option value="gemini-3.5-flash-lite">Gemini 3.5 Flash-Lite</option>
                            <option value="gemini-3.1-pro">Gemini 3.1 Pro</option>
                            <option value="gemini-deep-research">Gemini Deep Research</option>
                        </optgroup>
                        <optgroup label="Claude Drop-in">
                            <option value="claude-3-7-sonnet">Claude 3.7 Sonnet</option>
                            <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                            <option value="claude-3-5-haiku">Claude 3.5 Haiku</option>
                        </optgroup>
                    </select>
                </div>
            </div>
            <div id="chat-history" class="bg-slate-50 border border-slate-200 p-4 rounded-xl h-64 overflow-y-auto mb-4 text-sm flex flex-col space-y-3 custom-scrollbar">
                <div class="text-slate-400 text-center italic text-xs my-auto">Select a model and send a message to test the gateway response...</div>
            </div>
            <div class="flex gap-2">
                <input type="text" id="chat-input" placeholder="Type a message or test prompt..." class="flex-grow border border-slate-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white" onkeypress="if(event.key === 'Enter') sendChatMessage()">
                <button onclick="sendChatMessage()" id="chat-btn" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg text-sm transition-colors">
                    Send
                </button>
            </div>
        </div>
    </div>

    <!-- ─── ADD ACCOUNT MODAL ──────────────────────────────────────────────── -->
    <div id="add-account-modal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-xl w-full p-6 relative max-h-[90vh] overflow-y-auto custom-scrollbar">
            <!-- Modal Header -->
            <div class="flex items-center justify-between pb-4 border-b border-slate-100">
                <div class="flex items-center gap-2">
                    <span class="p-2 bg-blue-50 text-blue-600 rounded-lg">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
                    </span>
                    <div>
                        <h3 class="text-lg font-bold text-slate-800">Add Gemini User Account</h3>
                        <p class="text-xs text-slate-500">Import session cookies in any format. SNlM0e is auto-extracted from Google!</p>
                    </div>
                </div>
                <button onclick="closeAddAccountModal()" class="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>

            <!-- Modal Alert Banner -->
            <div id="modal-alert" class="hidden my-4 p-3 rounded-lg text-xs leading-relaxed font-medium"></div>

            <!-- Form -->
            <div class="space-y-4 pt-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-700 uppercase mb-1">Account Name</label>
                        <input type="text" id="modal-acc-name" placeholder="e.g. tester, work_pro, gemini_pro" class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none">
                        <p class="text-[11px] text-slate-400 mt-1">Leave blank to auto-generate.</p>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-700 uppercase mb-1">Auth Profile (u/X)</label>
                        <input type="number" id="modal-acc-auth-user" value="0" min="0" max="9" class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none">
                        <p class="text-[11px] text-slate-400 mt-1">0 = primary Google account, 1 = 2nd profile.</p>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-700 uppercase mb-1">Custom API Key <span class="text-slate-400 font-normal lowercase">(optional)</span></label>
                    <input type="text" id="modal-acc-api-key" placeholder="sk-gemini-... (leave blank to auto-generate)" class="w-full font-mono border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none">
                </div>

                <!-- Cookie Input Tabs -->
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="block text-xs font-semibold text-slate-700 uppercase">Cookies Input</label>
                        <div class="flex gap-1 text-xs">
                            <button type="button" id="tab-paste-btn" onclick="switchCookieTab('paste')" class="px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 font-medium">Paste Text / JSON</button>
                            <button type="button" id="tab-file-btn" onclick="switchCookieTab('file')" class="px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 hover:bg-slate-200">Upload File</button>
                        </div>
                    </div>

                    <!-- Tab 1: Paste Text/JSON -->
                    <div id="cookie-paste-pane">
                        <textarea id="modal-acc-cookies" rows="6" class="w-full font-mono text-xs border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:outline-none custom-scrollbar" placeholder="Paste cookies in ANY format:
• Cookie-Editor / EditThisCookie JSON Array: [{'name': '__Secure-1PSID', 'value': '...'}, ...]
• Raw Cookie Header: __Secure-1PSID=...; __Secure-1PSIDTS=...; SID=...; SAPISID=...;
• Key-Value JSON: {'__Secure-1PSID': '...', ...}
• Extension Export: {'cookie': '...', 'xsrf_token': '...'}"></textarea>
                    </div>

                    <!-- Tab 2: Upload File -->
                    <div id="cookie-file-pane" class="hidden">
                        <div class="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors cursor-pointer bg-slate-50" onclick="document.getElementById('modal-acc-file').click()">
                            <svg class="w-8 h-8 mx-auto text-slate-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                            <span class="text-sm font-medium text-slate-700">Click to select cookies.json</span>
                            <p class="text-xs text-slate-400 mt-1">Supports JSON cookie exports from any browser extension</p>
                            <input type="file" id="modal-acc-file" accept=".json,.txt" class="hidden" onchange="handleCookieFileUpload(event)">
                        </div>
                        <div id="file-upload-status" class="text-xs text-emerald-600 font-medium mt-2 hidden"></div>
                    </div>
                </div>

                <div class="bg-blue-50/60 p-3 rounded-lg border border-blue-100 flex items-start gap-2.5">
                    <input type="checkbox" id="modal-acc-auto-verify" checked class="mt-0.5 rounded text-blue-600 focus:ring-blue-500">
                    <label for="modal-acc-auto-verify" class="text-xs text-slate-700 leading-snug cursor-pointer">
                        <strong>Auto-Extract & Verify:</strong> Gateway automatically handshakes with Google Gemini, extracts <code>SNlM0e</code> (XSRF security token), captures fresh <code>__Secure-1PSIDTS</code>, and verifies session health.
                    </label>
                </div>

                <!-- Advanced Tokens Accordion -->
                <div>
                    <button type="button" onclick="toggleAdvancedTokens()" class="text-xs text-slate-500 hover:text-slate-800 font-medium flex items-center gap-1">
                        <span id="adv-arrow">▶</span> Manual Token Overrides (Optional)
                    </button>
                    <div id="advanced-tokens-pane" class="hidden mt-2 space-y-2 pl-2 border-l-2 border-slate-200">
                        <div>
                            <label class="block text-[11px] font-semibold text-slate-600">Manual SNlM0e (XSRF Token)</label>
                            <input type="text" id="modal-acc-xsrf" placeholder="Only needed if bypassing auto-extraction" class="w-full border border-slate-300 rounded px-2.5 py-1.5 text-xs font-mono focus:outline-none">
                        </div>
                    </div>
                </div>

                <!-- Footer Buttons -->
                <div class="flex items-center justify-end gap-2 pt-4 border-t border-slate-100">
                    <button type="button" onclick="closeAddAccountModal()" class="px-4 py-2 rounded-lg text-sm text-slate-600 hover:bg-slate-100 font-medium transition-colors">
                        Cancel
                    </button>
                    <button type="button" id="modal-submit-btn" onclick="submitAddAccount()" class="px-5 py-2 rounded-lg text-sm bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-sm transition-all flex items-center gap-2">
                        <span>Connect & Add Account</span>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notification Container -->
    <div id="toast-container" class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none"></div>

    <script>
        function showToast(message, type = "success") {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            const bgClass = type === "success" ? "bg-emerald-600 text-white" : (type === "error" ? "bg-red-600 text-white" : "bg-slate-800 text-white");
            toast.className = `${bgClass} px-4 py-2.5 rounded-lg shadow-lg text-xs font-medium flex items-center gap-2 transition-all duration-300 transform translate-y-2 opacity-0 pointer-events-auto`;
            toast.innerHTML = `<span>${message}</span>`;
            container.appendChild(toast);
            
            requestAnimationFrame(() => {
                toast.classList.remove('translate-y-2', 'opacity-0');
            });
            setTimeout(() => {
                toast.classList.add('opacity-0', 'translate-y-2');
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showToast("Copied to clipboard: " + text.slice(0, 24) + "...", "success");
            }).catch(e => {
                const ta = document.createElement("textarea");
                ta.value = text;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand("copy");
                ta.remove();
                showToast("Copied to clipboard!", "success");
            });
        }

        function openAddAccountModal() {
            document.getElementById('add-account-modal').classList.remove('hidden');
            document.getElementById('modal-alert').classList.add('hidden');
            document.getElementById('modal-acc-cookies').value = '';
            document.getElementById('modal-acc-name').value = '';
            document.getElementById('modal-acc-api-key').value = '';
            document.getElementById('modal-acc-xsrf').value = '';
            document.getElementById('file-upload-status').classList.add('hidden');
            document.getElementById('modal-acc-cookies').focus();
        }

        function closeAddAccountModal() {
            document.getElementById('add-account-modal').classList.add('hidden');
        }

        function switchCookieTab(tab) {
            const pastePane = document.getElementById('cookie-paste-pane');
            const filePane = document.getElementById('cookie-file-pane');
            const pasteBtn = document.getElementById('tab-paste-btn');
            const fileBtn = document.getElementById('tab-file-btn');
            
            if (tab === 'paste') {
                pastePane.classList.remove('hidden');
                filePane.classList.add('hidden');
                pasteBtn.className = "px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 font-medium";
                fileBtn.className = "px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 hover:bg-slate-200";
            } else {
                pastePane.classList.add('hidden');
                filePane.classList.remove('hidden');
                fileBtn.className = "px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 font-medium";
                pasteBtn.className = "px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 hover:bg-slate-200";
            }
        }

        function handleCookieFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                const content = e.target.result;
                document.getElementById('modal-acc-cookies').value = content;
                const statusEl = document.getElementById('file-upload-status');
                statusEl.textContent = `✓ Loaded '${file.name}' (${content.length} bytes)`;
                statusEl.classList.remove('hidden');
                showToast(`Loaded ${file.name}`, "info");
            };
            reader.readAsText(file);
        }

        function toggleAdvancedTokens() {
            const pane = document.getElementById('advanced-tokens-pane');
            const arrow = document.getElementById('adv-arrow');
            if (pane.classList.contains('hidden')) {
                pane.classList.remove('hidden');
                arrow.textContent = '▼';
            } else {
                pane.classList.add('hidden');
                arrow.textContent = '▶';
            }
        }

        async function submitAddAccount() {
            const btn = document.getElementById('modal-submit-btn');
            const alertBox = document.getElementById('modal-alert');
            const cookies = document.getElementById('modal-acc-cookies').value.trim();
            const name = document.getElementById('modal-acc-name').value.trim();
            const auth_user = document.getElementById('modal-acc-auth-user').value.trim() || '0';
            const api_key = document.getElementById('modal-acc-api-key').value.trim();
            const xsrf_token = document.getElementById('modal-acc-xsrf').value.trim();
            const auto_verify = document.getElementById('modal-acc-auto-verify').checked;

            if (!cookies) {
                alertBox.className = "my-4 p-3 rounded-lg text-xs font-medium bg-red-50 text-red-700 border border-red-200 block";
                alertBox.textContent = "Please paste cookies or upload a cookies JSON file.";
                return;
            }

            btn.disabled = true;
            btn.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg> Handshaking with Gemini...`;
            alertBox.className = "my-4 p-3 rounded-lg text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200 block";
            alertBox.textContent = "Connecting to Google Gemini, extracting SNlM0e security token, and validating session...";

            try {
                const res = await fetch('/api/accounts', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        name: name,
                        auth_user: auth_user,
                        api_key: api_key,
                        cookies: cookies,
                        xsrf_token: xsrf_token,
                        auto_verify: auto_verify
                    })
                });

                const data = await res.json();
                if (!res.ok || data.status === "error") {
                    throw new Error(data.error || "Failed to add account");
                }

                alertBox.className = "my-4 p-3 rounded-lg text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200 block";
                alertBox.innerHTML = `<strong>✅ Success!</strong> ${data.message}<br><span class="font-mono mt-1 inline-block">Key: ${data.account.api_key}</span>`;
                showToast(`Account '${data.account.name}' added successfully!`, "success");
                
                await loadStats();
                setTimeout(() => {
                    closeAddAccountModal();
                }, 1400);
            } catch (err) {
                alertBox.className = "my-4 p-3 rounded-lg text-xs font-medium bg-red-50 text-red-700 border border-red-200 block";
                alertBox.innerHTML = `<strong>❌ Error:</strong> ${err.message}`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = `<span>Connect & Add Account</span>`;
            }
        }

        async function testAccount(name) {
            const healthEl = document.getElementById('health-' + name);
            if (healthEl) {
                healthEl.innerHTML = `<span class="inline-flex items-center gap-1 text-blue-600 font-semibold"><svg class="animate-spin h-3.5 w-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg> Testing 4 Neon...</span>`;
            }
            showToast(`Pinging ${name} with 4 Neon...`, "info");

            try {
                const res = await fetch('/api/test-account', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name})
                });
                const data = await res.json();
                if (!res.ok || data.status === "error") {
                    throw new Error(data.error || "Test failed");
                }
                if (healthEl) {
                    healthEl.innerHTML = `<span class="text-emerald-600 font-bold">● Live (${data.latency_ms}ms)</span>`;
                }
                showToast(`✅ ${name}: 4 Neon responded in ${data.latency_ms}ms`, "success");
            } catch (err) {
                if (healthEl) {
                    healthEl.innerHTML = `<span class="text-red-600 font-bold">● Failed</span>`;
                }
                showToast(`❌ ${name} test failed: ${err.message}`, "error");
            }
        }

        async function loadStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                
                document.getElementById('master-key').textContent = data.master_key || "None configured";
                document.getElementById('total-accounts').textContent = data.total_accounts;
                document.getElementById('account-badge-count').textContent = `${data.total_accounts} active`;
                document.getElementById('incognito-toggle').checked = data.temporary_chats;
                
                const tbody = document.getElementById('accounts-table');
                tbody.innerHTML = '';
                
                const accountDropdown = document.getElementById('chat-account');
                const currentSelection = accountDropdown.value;
                accountDropdown.innerHTML = '<option value="auto">Auto Load-Balance</option>';
                
                if (data.accounts.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" class="py-8 text-center text-slate-400">No accounts configured yet. Click <strong>Add Account</strong> above to connect your Gemini session.</td></tr>';
                    return;
                }
                
                data.accounts.forEach(acc => {
                    const option = document.createElement('option');
                    option.value = acc.api_key;
                    option.textContent = `Force: ${acc.name}`;
                    if (currentSelection === acc.api_key) option.selected = true;
                    accountDropdown.appendChild(option);

                    const statusClass = acc.status === "Ready" ? "text-emerald-700 bg-emerald-50 border-emerald-200" : "text-amber-700 bg-amber-50 border-amber-200";
                    const tr = document.createElement('tr');
                    tr.className = "hover:bg-slate-50/80 transition-colors";
                    tr.innerHTML = `
                        <td class="py-3 px-4 font-semibold text-slate-800 flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full ${acc.status === 'Ready' ? 'bg-emerald-500' : 'bg-amber-500'}"></span>
                            ${acc.name}
                        </td>
                        <td class="py-3 px-4">
                            <div class="inline-flex items-center gap-1.5 bg-slate-50 px-2 py-1 rounded border border-slate-200">
                                <span class="font-mono text-xs text-slate-600">${acc.api_key}</span>
                                <button onclick="copyToClipboard('${acc.api_key}')" class="text-slate-400 hover:text-blue-600 transition-colors p-0.5" title="Copy API Key">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>
                                </button>
                            </div>
                        </td>
                        <td class="py-3 px-4 font-mono text-xs text-slate-500"><span class="bg-slate-100 px-1.5 py-0.5 rounded">u/${acc.auth_user || 0}</span></td>
                        <td class="py-3 px-4">
                            <span class="inline-block text-xs font-semibold px-2 py-0.5 rounded-full border ${statusClass}">${acc.status}</span>
                        </td>
                        <td class="py-3 px-4 text-xs text-slate-500">${acc.cooldown_seconds > 0 ? acc.cooldown_seconds + 's' : '-'}</td>
                        <td class="py-3 px-4 text-xs font-medium" id="health-${acc.name}"><span class="text-slate-400">Ready</span></td>
                        <td class="py-3 px-4 text-center">
                            <div class="inline-flex items-center gap-1.5">
                                <button onclick="testAccount('${acc.name}')" class="bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-medium px-2 py-1 rounded border border-blue-200 transition-colors" title="Test with 4 Neon">
                                    Test 4 Neon
                                </button>
                                <button onclick="deleteAccount('${acc.name}')" class="bg-red-50 hover:bg-red-100 text-red-600 text-xs font-medium px-2 py-1 rounded border border-red-200 transition-colors" title="Delete Account">
                                    Delete
                                </button>
                            </div>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (err) {
                console.error(err);
            }
        }

        async function runHealthCheck() {
            showToast("Verifying all sessions upstream with Google...", "info");
            try {
                const res = await fetch('/api/check');
                const results = await res.json();
                results.forEach(r => {
                    const el = document.getElementById('health-' + r.name);
                    if (el) {
                        el.textContent = r.status;
                        el.className = r.valid ? "py-3 px-4 text-xs text-emerald-600 font-bold" : "py-3 px-4 text-xs text-red-600 font-bold";
                    }
                });
                showToast("Health check complete!", "success");
            } catch(e) {
                showToast("Health check failed: " + e, "error");
            }
        }
        
        async function triggerAutoSync() {
            try {
                const res = await fetch('/api/request-sync', { method: 'POST' });
                const data = await res.json();
                showToast(data.message || "Sync requested", "info");
            } catch(e) {
                showToast("Failed to request sync: " + e, "error");
            }
        }
        
        async function toggleIncognito(isEnabled) {
            try {
                const res = await fetch('/api/config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({temporary_chats: isEnabled})
                });
                if (res.ok) {
                    showToast(isEnabled ? "🕵️ Incognito Mode Enabled" : "Incognito Mode Disabled", "info");
                }
            } catch(e) {
                console.error(e);
            }
        }
        
        async function deleteAccount(name) {
            if (!confirm(`Are you sure you want to delete account '${name}'?`)) return;
            try {
                const res = await fetch('/api/accounts?name=' + encodeURIComponent(name), { method: 'DELETE' });
                if (res.ok) {
                    showToast(`Account '${name}' deleted`, "info");
                    loadStats();
                } else {
                    showToast("Failed to delete account", "error");
                }
            } catch (e) {
                console.error(e);
            }
        }

        let chatMessages = [];
        
        async function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const btn = document.getElementById('chat-btn');
            const history = document.getElementById('chat-history');
            const text = input.value.trim();
            const protocol = document.getElementById('chat-protocol').value;
            const selectedModel = document.getElementById('chat-model').value;
            const selectedAccount = document.getElementById('chat-account').value;
            
            if (!text) return;
            
            if (chatMessages.length === 0) history.innerHTML = '';
            
            input.value = '';
            input.disabled = true;
            btn.disabled = true;
            
            chatMessages.push({role: "user", content: text});
            history.innerHTML += `<div class="self-end bg-blue-600 text-white rounded-xl py-2 px-4 max-w-[80%] shadow-sm">${text.replace(/</g, "&lt;")}</div>`;
            history.scrollTop = history.scrollHeight;
            
            const botId = "bot-msg-" + Date.now();
            history.innerHTML += `<div class="self-start bg-slate-200 text-slate-800 rounded-xl py-2 px-4 max-w-[80%] whitespace-pre-wrap shadow-sm text-xs leading-relaxed" id="${botId}">⏳ Connecting via ${protocol.toUpperCase()}...</div>`;
            history.scrollTop = history.scrollHeight;
            const botBubble = document.getElementById(botId);
            
            try {
                const authToken = selectedAccount === "auto" ? "sk-gemini-auto" : selectedAccount;
                let modelToUse = selectedModel;
                if (document.getElementById('chat-thinking')?.checked && !modelToUse.includes("thinking")) {
                    modelToUse += "@think=0";
                }
                
                let endpoint = '/v1/chat/completions';
                let payload = {};
                
                if (protocol === 'claude') {
                    endpoint = '/v1/messages';
                    payload = {
                        model: modelToUse,
                        messages: chatMessages,
                        max_tokens: 4096,
                        stream: false
                    };
                } else if (protocol === 'research') {
                    endpoint = '/gemini/v1beta/interactions';
                    payload = {
                        input: text,
                        model: modelToUse,
                        stream: false
                    };
                } else {
                    payload = {
                        model: modelToUse,
                        messages: chatMessages,
                        stream: false
                    };
                }
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + authToken
                    },
                    body: JSON.stringify(payload)
                });
                
                const resData = await response.json();
                let reply = "";
                
                if (protocol === 'claude') {
                    if (resData.content && Array.isArray(resData.content)) {
                        reply = resData.content.map(b => b.text || (b.thinking ? `[Thinking]: ${b.thinking}` : "")).filter(Boolean).join("\\n");
                    } else if (resData.error) {
                        reply = "Error: " + JSON.stringify(resData.error);
                    }
                } else if (protocol === 'research') {
                    reply = resData.final_report || (resData.outputs && resData.outputs[0]?.text) || JSON.stringify(resData, null, 2);
                } else {
                    reply = resData.choices?.[0]?.message?.content || resData.error?.message || "No response received";
                }
                
                botBubble.textContent = reply;
                chatMessages.push({role: "assistant", content: reply});
            } catch (err) {
                botBubble.textContent = "Error: " + err.message;
            } finally {
                input.disabled = false;
                btn.disabled = false;
                input.focus();
                history.scrollTop = history.scrollHeight;
            }
        }

        window.onload = loadStats;
    </script>
</body>
</html>
"""

const tabKeys = [
  "nav.new_task",
  "nav.auth",
  "nav.queue",
  "nav.pending",
  "nav.providers",
  "nav.settings",
];

const state = {
  lang: "zh-CN",
  messages: {},
  loggedIn: false,
  activeTab: "nav.new_task",
  providers: [],
  authProfiles: [],
};

function t(key) {
  return state.messages[key] || key;
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = new Error("request_failed");
    error.status = response.status;
    throw error;
  }
  return response.json();
}

function render() {
  document.documentElement.lang = state.lang;
  document.getElementById("appTitle").textContent = t("app.title");
  document.getElementById("appSubtitle").textContent = t("app.subtitle");
  document.getElementById("loginTitle").textContent = t("login.title");
  document.getElementById("loginPasswordLabel").textContent = t("login.password");
  document.getElementById("loginBtn").textContent = t("login.submit");
  document.getElementById("lockedText").textContent = t("state.locked");

  const tabs = document.getElementById("tabs");
  tabs.innerHTML = "";
  for (const key of tabKeys) {
    const node = document.createElement("button");
    node.className = `tab${state.activeTab === key ? " active" : ""}`;
    node.textContent = t(key);
    node.addEventListener("click", () => {
      state.activeTab = key;
      render();
    });
    tabs.appendChild(node);
  }

  const loginPanel = document.getElementById("loginPanel");
  const appPanel = document.getElementById("appPanel");
  const logoutBtn = document.getElementById("logoutBtn");
  const generalPanel = document.getElementById("generalPanel");
  const authPanel = document.getElementById("authPanel");
  loginPanel.hidden = state.loggedIn;
  appPanel.hidden = !state.loggedIn;
  logoutBtn.hidden = !state.loggedIn;
  if (state.loggedIn) {
    const authTab = state.activeTab === "nav.auth";
    generalPanel.hidden = authTab;
    authPanel.hidden = !authTab;
  }
  renderAuthList();
}

async function loadI18n(lang) {
  const data = await fetchJson(`/api/i18n?lang=${encodeURIComponent(lang)}`);
  state.lang = data.lang;
  state.messages = data.messages || {};
  document.getElementById("langSelect").value = state.lang;
  render();
}

async function refreshSession() {
  const data = await fetchJson("/api/session");
  state.loggedIn = Boolean(data.loggedIn);
  render();
}

async function loadProviders() {
  const data = await fetchJson("/api/providers");
  state.providers = data.items || [];
  const providerSelect = document.getElementById("authProvider");
  providerSelect.innerHTML = "";
  for (const p of state.providers) {
    const node = document.createElement("option");
    node.value = p.providerKey;
    node.textContent = `${p.displayName} (${p.providerKey})`;
    providerSelect.appendChild(node);
  }
}

function renderAuthList() {
  const list = document.getElementById("authList");
  if (!list) return;
  list.innerHTML = "";
  for (const item of state.authProfiles) {
    const node = document.createElement("li");
    node.className = "auth-item";
    const left = document.createElement("div");
    const title = document.createElement("div");
    title.textContent = `${item.displayName} [${item.providerKey}]`;
    const meta = document.createElement("div");
    meta.className = "auth-item-meta";
    meta.textContent = `mode=${item.authMode}, status=${item.status}, token=${item.token || "(none)"}, cookie=${item.cookie || "(none)"}`;
    left.appendChild(title);
    left.appendChild(meta);

    const actions = document.createElement("div");
    const validateBtn = document.createElement("button");
    validateBtn.className = "ghost";
    validateBtn.textContent = "Validate";
    validateBtn.addEventListener("click", () => validateAuth(item.profileId));
    const deleteBtn = document.createElement("button");
    deleteBtn.className = "ghost";
    deleteBtn.textContent = "Delete";
    deleteBtn.addEventListener("click", () => deleteAuth(item.profileId));
    actions.appendChild(validateBtn);
    actions.appendChild(deleteBtn);

    node.appendChild(left);
    node.appendChild(actions);
    list.appendChild(node);
  }
}

async function loadAuthProfiles() {
  if (!state.loggedIn) return;
  const data = await fetchJson("/api/auth/profiles");
  state.authProfiles = data.items || [];
  renderAuthList();
}

async function saveAuth() {
  const providerKey = document.getElementById("authProvider").value;
  const authMode = document.getElementById("authMode").value;
  const displayName = document.getElementById("authDisplayName").value.trim() || providerKey;
  const token = document.getElementById("authToken").value.trim();
  const cookie = document.getElementById("authCookie").value.trim();
  await fetchJson("/api/auth/profiles", {
    method: "POST",
    body: JSON.stringify({ providerKey, authMode, displayName, token, cookie, extra: {} }),
  });
  document.getElementById("authToken").value = "";
  document.getElementById("authCookie").value = "";
  await loadAuthProfiles();
}

async function validateAuth(profileId) {
  await fetchJson(`/api/auth/profiles/${profileId}/validate`, { method: "POST" });
  await loadAuthProfiles();
}

async function deleteAuth(profileId) {
  await fetchJson(`/api/auth/profiles/${profileId}`, { method: "DELETE" });
  await loadAuthProfiles();
}

async function onLogin() {
  const input = document.getElementById("passwordInput");
  const errorNode = document.getElementById("loginError");
  errorNode.hidden = true;
  try {
    await fetchJson("/api/login", {
      method: "POST",
      body: JSON.stringify({ password: input.value }),
    });
    input.value = "";
    await refreshSession();
  } catch (error) {
    if (error.status === 401) {
      errorNode.hidden = false;
      errorNode.textContent = t("login.failed");
      return;
    }
    throw error;
  }
}

async function onLogout() {
  await fetchJson("/api/logout", { method: "POST" });
  await refreshSession();
}

async function bootstrap() {
  const langSelect = document.getElementById("langSelect");
  langSelect.addEventListener("change", async () => {
    await loadI18n(langSelect.value);
  });
  document.getElementById("loginBtn").addEventListener("click", onLogin);
  document.getElementById("logoutBtn").addEventListener("click", onLogout);
  document.getElementById("authSaveBtn").addEventListener("click", saveAuth);
  document.getElementById("authReloadBtn").addEventListener("click", loadAuthProfiles);
  await loadI18n("zh-CN");
  await loadProviders();
  await refreshSession();
  await loadAuthProfiles();
}

bootstrap().catch((error) => {
  console.error(error);
});

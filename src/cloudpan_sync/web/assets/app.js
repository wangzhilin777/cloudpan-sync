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
    const node = document.createElement("span");
    node.className = "tab";
    node.textContent = t(key);
    tabs.appendChild(node);
  }

  const loginPanel = document.getElementById("loginPanel");
  const appPanel = document.getElementById("appPanel");
  const logoutBtn = document.getElementById("logoutBtn");
  loginPanel.hidden = state.loggedIn;
  appPanel.hidden = !state.loggedIn;
  logoutBtn.hidden = !state.loggedIn;
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
  await loadI18n("zh-CN");
  await refreshSession();
}

bootstrap().catch((error) => {
  console.error(error);
});

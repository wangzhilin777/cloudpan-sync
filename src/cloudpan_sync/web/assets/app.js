const tabKeys = [
  "nav.new_task",
  "nav.auth",
  "nav.queue",
  "nav.pending",
  "nav.providers",
  "nav.settings",
];
const wizardKeys = [
  "选择来源网盘",
  "选择目标网盘",
  "选择来源文件夹",
  "扫描分析",
  "确认策略",
  "执行任务",
];

const state = {
  lang: "zh-CN",
  messages: {},
  loggedIn: false,
  activeTab: "nav.new_task",
  providers: [],
  authProfiles: [],
  tasks: [],
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
  const queuePanel = document.getElementById("queuePanel");
  loginPanel.hidden = state.loggedIn;
  appPanel.hidden = !state.loggedIn;
  logoutBtn.hidden = !state.loggedIn;
  if (state.loggedIn) {
    const authTab = state.activeTab === "nav.auth";
    const queueTab = state.activeTab === "nav.queue";
    generalPanel.hidden = authTab;
    authPanel.hidden = !authTab;
    queuePanel.hidden = !queueTab;
    if (!authTab && !queueTab) {
      generalPanel.hidden = false;
    }
  }
  renderAuthList();
  renderTaskList();
  renderWizardSteps();
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
  const modalSelect = document.getElementById("authModalProvider");
  if (modalSelect) {
    modalSelect.innerHTML = providerSelect.innerHTML;
  }
}

function renderWizardSteps() {
  const wrap = document.getElementById("wizardSteps");
  if (!wrap) return;
  wrap.innerHTML = "";
  wizardKeys.forEach((label, index) => {
    const step = document.createElement("div");
    const active = state.activeTab === "nav.new_task" && index === 0;
    step.className = `wizard-step${active ? " active" : ""}`;
    step.textContent = `${index + 1}. ${label}`;
    wrap.appendChild(step);
  });
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
  const extraHeader = document.getElementById("authExtraHeader").value.trim();
  const extraDevice = document.getElementById("authExtraDevice").value.trim();
  const extra = {};
  if (extraHeader) extra.header = extraHeader;
  if (extraDevice) extra.deviceId = extraDevice;
  await fetchJson("/api/auth/profiles", {
    method: "POST",
    body: JSON.stringify({ providerKey, authMode, displayName, token, cookie, extra }),
  });
  document.getElementById("authToken").value = "";
  document.getElementById("authCookie").value = "";
  await loadAuthProfiles();
}

function openAuthModal() {
  const modal = document.getElementById("authModal");
  if (modal && typeof modal.showModal === "function") {
    modal.showModal();
  }
}

async function startCaptureGuide() {
  const providerKey = document.getElementById("authModalProvider").value;
  const resultNode = document.getElementById("authCaptureResult");
  const data = await fetchJson("/api/auth/capture/start", {
    method: "POST",
    body: JSON.stringify({ providerKey }),
  });
  resultNode.textContent = JSON.stringify(data, null, 2);
}

async function validateAuth(profileId) {
  await fetchJson(`/api/auth/profiles/${profileId}/validate`, { method: "POST" });
  await loadAuthProfiles();
}

async function deleteAuth(profileId) {
  await fetchJson(`/api/auth/profiles/${profileId}`, { method: "DELETE" });
  await loadAuthProfiles();
}

function renderTaskList() {
  const list = document.getElementById("taskList");
  if (!list) return;
  list.innerHTML = "";
  for (const task of state.tasks) {
    const node = document.createElement("li");
    node.className = "auth-item";
    const left = document.createElement("div");
    const title = document.createElement("div");
    title.textContent = `${task.sourceProvider} -> ${task.targetProvider}`;
    const meta = document.createElement("div");
    meta.className = "auth-item-meta";
    meta.textContent = `state=${task.state}, done=${task.progress.done}/${task.progress.total}, failed=${task.progress.failed}, pending=${task.progress.pendingManual}`;
    left.appendChild(title);
    left.appendChild(meta);

    const actions = document.createElement("div");
    for (const action of ["run", "pause", "resume", "retry"]) {
      const btn = document.createElement("button");
      btn.className = "ghost";
      btn.textContent = action;
      btn.addEventListener("click", () => taskAction(task.taskId, action));
      actions.appendChild(btn);
    }
    node.appendChild(left);
    node.appendChild(actions);
    list.appendChild(node);
  }
}

async function loadTasks() {
  if (!state.loggedIn) return;
  const data = await fetchJson("/api/tasks");
  state.tasks = data.items || [];
  renderTaskList();
}

async function createDemoTask() {
  const body = {
    sourceProvider: "quark",
    targetProvider: "guangya",
    thresholdMB: 200,
    selectedRoots: ["/1", "/2"],
    entries: [
      { path: "/1/11/111/a.bin", size: 100, md5: "e10adc3949ba59abbe56e057f20f883e" },
      { path: "/1/11/112/b.bin", size: 100, md5: "" },
      { path: "/2/21/211/c.bin", size: 1000000000, md5: "" },
    ],
  };
  await fetchJson("/api/tasks", { method: "POST", body: JSON.stringify(body) });
  await loadTasks();
}

async function taskAction(taskId, action) {
  await fetchJson(`/api/tasks/${taskId}/action`, {
    method: "POST",
    body: JSON.stringify({ action }),
  });
  await loadTasks();
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
  document.getElementById("authOpenModalBtn").addEventListener("click", openAuthModal);
  document.getElementById("authStartCaptureBtn").addEventListener("click", startCaptureGuide);
  document.getElementById("taskCreateDemoBtn").addEventListener("click", createDemoTask);
  document.getElementById("taskReloadBtn").addEventListener("click", loadTasks);
  await loadI18n("zh-CN");
  await loadProviders();
  await refreshSession();
  await loadAuthProfiles();
  await loadTasks();
}

bootstrap().catch((error) => {
  console.error(error);
});

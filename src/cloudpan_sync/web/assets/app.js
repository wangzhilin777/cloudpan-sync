const tabKeys = [
  "nav.new_task",
  "nav.auth",
  "nav.queue",
  "nav.pending",
  "nav.providers",
  "nav.settings",
];

const wizardSteps = [
  { title: "wizard.step.1", description: "wizard.desc.1" },
  { title: "wizard.step.2", description: "wizard.desc.2" },
  { title: "wizard.step.3", description: "wizard.desc.3" },
  { title: "wizard.step.4", description: "wizard.desc.4" },
  { title: "wizard.step.5", description: "wizard.desc.5" },
  { title: "wizard.step.6", description: "wizard.desc.6" },
];

const tabPanelIds = {
  "nav.new_task": "newTaskPanel",
  "nav.auth": "authPanel",
  "nav.queue": "queuePanel",
  "nav.pending": "pendingPanel",
  "nav.providers": "providersPanel",
  "nav.settings": "settingsPanel",
};

const state = {
  lang: "zh-CN",
  messages: {},
  loggedIn: false,
  activeTab: "nav.new_task",
  activeWizardStep: 0,
  providers: [],
  providerResearch: [],
  statusMatrix: null,
  auditSummary: null,
  realEvidenceReport: null,
  realEvidenceSummary: null,
  realEvidenceRemediation: null,
  authProfiles: [],
  authEditingProfileId: "",
  liveValidations: [],
  liveValidationMeta: { historyCount: 0, summary: null },
  providerLiveProbes: {},
  providerLiveProbeMeta: { historyCount: 0, summary: null },
  taskRuntimeEvidence: [],
  taskRuntimeEvidenceMeta: { historyCount: 0, summary: null },
  tasks: [],
  taskPlanPreview: null,
};

const liveProbeProviderSet = new Set([
  "guangya",
  "aliyundrive_open",
  "189cloud",
  "baidu_netdisk",
  "123_open",
  "115_open",
  "xunlei",
  "pikpak",
  "quark",
  "uc",
]);

function latestValidationByProfile(profileId) {
  for (let index = state.liveValidations.length - 1; index >= 0; index -= 1) {
    const row = state.liveValidations[index];
    if (row && row.profileId === profileId) {
      return row;
    }
  }
  return null;
}

function realEvidenceByProvider(providerKey) {
  return (state.realEvidenceReport?.items || []).find((item) => item.providerKey === providerKey) || null;
}

function resolvedParentIdForProfile(profile) {
  if (!profile) {
    return "";
  }
  return profile.resolvedParentId || profile.extra?.parentId || "";
}

function resolvedFileIdForProfile(profile) {
  if (!profile) {
    return "";
  }
  return profile.resolvedFileId || profile.extra?.fileId || "";
}

function buildPatchCommandHint(profile) {
  const hasProfileMissing = Array.isArray(profile?.missingFieldHints) && profile.missingFieldHints.length;
  const hasWriteMissing = profile?.writeReady === false;
  if (!profile || (!hasProfileMissing && !hasWriteMissing)) {
    return "";
  }
  const base = `.\\.venv\\Scripts\\python.exe scripts\\patch_auth_profile_extra.py --profile-id ${profile.profileId}`;
  if (profile.providerKey === "guangya") {
    return `${base} --set parentId=YOUR_REAL_PARENT_ID --write --revalidate`;
  }
  if (profile.providerKey === "aliyundrive_open") {
    return `${base} --set domainId=YOUR_DOMAIN_ID --set driveId=YOUR_DRIVE_ID --write --revalidate`;
  }
  if (profile.providerKey === "189cloud") {
    return `.\\.venv\\Scripts\\python.exe scripts\\patch_189cloud_account_auth.py --profile-id ${profile.profileId} --raw-file captured_189_headers.txt --write --revalidate`;
  }
  if (profile.providerKey === "xunlei") {
    return `${base} --set deviceId=YOUR_DEVICE_ID --write --revalidate`;
  }
  if (profile.providerKey === "quark" || profile.providerKey === "uc") {
    return `${base} --set pwdId=YOUR_SHARE_PWD_ID --write --revalidate`;
  }
  return `${base} --set key=value --write --revalidate`;
}

function updateAuthFormMode() {
  const saveBtn = document.getElementById("authSaveBtn");
  const resetBtn = document.getElementById("authResetBtn");
  const editHint = document.getElementById("authEditHint");
  const tokenInput = document.getElementById("authToken");
  const cookieInput = document.getElementById("authCookie");
  if (saveBtn) {
    saveBtn.textContent = state.authEditingProfileId ? "Update Auth" : "Save Auth";
  }
  if (resetBtn) {
    resetBtn.textContent = state.authEditingProfileId ? "Cancel Edit" : "Reset Form";
  }
  if (editHint) {
    if (state.authEditingProfileId) {
      const profile = state.authProfiles.find((item) => item.profileId === state.authEditingProfileId);
      editHint.hidden = false;
      editHint.textContent = `Editing ${profile?.displayName || state.authEditingProfileId}. Leave token/cookie blank to keep existing secrets, then update only the fields you want to change.`;
    } else {
      editHint.hidden = true;
      editHint.textContent = "";
    }
  }
  if (tokenInput) {
    tokenInput.placeholder = state.authEditingProfileId ? "token (leave blank to keep current)" : "token (optional)";
  }
  if (cookieInput) {
    cookieInput.placeholder = state.authEditingProfileId ? "cookie (leave blank to keep current)" : "cookie (optional)";
  }
}

function resetAuthForm() {
  state.authEditingProfileId = "";
  document.getElementById("authDisplayName").value = "";
  document.getElementById("authToken").value = "";
  document.getElementById("authCookie").value = "";
  document.getElementById("authExtraHeader").value = "";
  document.getElementById("authExtraDevice").value = "";
  document.getElementById("authExtraCaptchaToken").value = "";
  document.getElementById("authExtraClientId").value = "";
  document.getElementById("authExtraDid").value = "";
  document.getElementById("authExtraDt").value = "";
  document.getElementById("authExtraParentId").value = "";
  document.getElementById("authExtraPageSize").value = "";
  document.getElementById("authExtraFileId").value = "";
  document.getElementById("authExtraDirName").value = "";
  document.getElementById("authExtraPwdId").value = "";
  document.getElementById("authExtraPasscode").value = "";
  document.getElementById("authExtraDomainId").value = "";
  document.getElementById("authExtraDriveId").value = "";
  document.getElementById("authExtraShareCode").value = "";
  document.getElementById("authExtraAccessCode").value = "";
  document.getElementById("authExtraAccessToken").value = "";
  document.getElementById("authExtraSignature").value = "";
  document.getElementById("authExtraDate").value = "";
  document.getElementById("authExtraPathPrefix").value = "";
  updateAuthFormMode();
}

function fillAuthForm(profile) {
  if (!profile) {
    resetAuthForm();
    return;
  }
  state.authEditingProfileId = profile.profileId || "";
  document.getElementById("authDisplayName").value = profile.displayName || "";
  document.getElementById("authProvider").value = profile.providerKey || "";
  syncAuthModeOptions();
  document.getElementById("authMode").value = profile.authMode || document.getElementById("authMode").value;
  document.getElementById("authToken").value = "";
  document.getElementById("authCookie").value = "";
  document.getElementById("authExtraHeader").value = profile.extra?.header || "";
  document.getElementById("authExtraDevice").value = profile.extra?.deviceId || profile.extra?.["x-device-id"] || "";
  document.getElementById("authExtraCaptchaToken").value = profile.extra?.captchaToken || "";
  document.getElementById("authExtraClientId").value = profile.extra?.clientId || "";
  document.getElementById("authExtraDid").value = profile.extra?.did || "";
  document.getElementById("authExtraDt").value = profile.extra?.dt || "";
  document.getElementById("authExtraParentId").value = resolvedParentIdForProfile(profile) || "";
  document.getElementById("authExtraPageSize").value = profile.extra?.pageSize || "";
  document.getElementById("authExtraFileId").value = resolvedFileIdForProfile(profile) || "";
  document.getElementById("authExtraDirName").value = profile.extra?.dirName || "";
  document.getElementById("authExtraPwdId").value = profile.extra?.pwdId || profile.extra?.sharePwdId || "";
  document.getElementById("authExtraPasscode").value = profile.extra?.passcode || "";
  document.getElementById("authExtraDomainId").value = profile.extra?.domainId || "";
  document.getElementById("authExtraDriveId").value = profile.extra?.driveId || "";
  document.getElementById("authExtraShareCode").value = profile.extra?.shareCode || "";
  document.getElementById("authExtraAccessCode").value = profile.extra?.accessCode || "";
  document.getElementById("authExtraAccessToken").value = profile.extra?.accessToken || profile.extra?.access_token || "";
  document.getElementById("authExtraSignature").value = profile.extra?.signature || profile.extra?.Signature || "";
  document.getElementById("authExtraDate").value = profile.extra?.date || profile.extra?.Date || "";
  document.getElementById("authExtraPathPrefix").value = profile.extra?.pathPrefix || "";
  updateAuthFormMode();
}

function collectAuthPayload() {
  const providerKey = document.getElementById("authProvider").value;
  const authMode = document.getElementById("authMode").value;
  const displayName = document.getElementById("authDisplayName").value.trim() || providerKey;
  const token = document.getElementById("authToken").value.trim();
  const cookie = document.getElementById("authCookie").value.trim();
  const extraHeader = document.getElementById("authExtraHeader").value.trim();
  const extraDevice = document.getElementById("authExtraDevice").value.trim();
  const extraCaptchaToken = document.getElementById("authExtraCaptchaToken").value.trim();
  const extraClientId = document.getElementById("authExtraClientId").value.trim();
  const extraDid = document.getElementById("authExtraDid").value.trim();
  const extraDt = document.getElementById("authExtraDt").value.trim();
  const extraParentId = document.getElementById("authExtraParentId").value.trim();
  const extraPageSize = document.getElementById("authExtraPageSize").value.trim();
  const extraFileId = document.getElementById("authExtraFileId").value.trim();
  const extraDirName = document.getElementById("authExtraDirName").value.trim();
  const extraPwdId = document.getElementById("authExtraPwdId").value.trim();
  const extraPasscode = document.getElementById("authExtraPasscode").value.trim();
  const extraDomainId = document.getElementById("authExtraDomainId").value.trim();
  const extraDriveId = document.getElementById("authExtraDriveId").value.trim();
  const extraShareCode = document.getElementById("authExtraShareCode").value.trim();
  const extraAccessCode = document.getElementById("authExtraAccessCode").value.trim();
  const extraAccessToken = document.getElementById("authExtraAccessToken").value.trim();
  const extraSignature = document.getElementById("authExtraSignature").value.trim();
  const extraDate = document.getElementById("authExtraDate").value.trim();
  const extraPathPrefix = document.getElementById("authExtraPathPrefix").value.trim();
  const extra = {};
  if (extraHeader) {
    extra.header = extraHeader;
  }
  if (extraDevice) {
    extra.deviceId = extraDevice;
  }
  if (extraCaptchaToken) {
    extra.captchaToken = extraCaptchaToken;
  }
  if (extraClientId) {
    extra.clientId = extraClientId;
  }
  if (extraDid) {
    extra.did = extraDid;
  }
  if (extraDt) {
    extra.dt = extraDt;
  }
  if (extraParentId) {
    extra.parentId = extraParentId;
  }
  if (extraPageSize) {
    extra.pageSize = extraPageSize;
  }
  if (extraFileId) {
    extra.fileId = extraFileId;
  }
  if (extraDirName) {
    extra.dirName = extraDirName;
  }
  if (extraPwdId) {
    extra.pwdId = extraPwdId;
  }
  if (extraPasscode) {
    extra.passcode = extraPasscode;
  }
  if (extraDomainId) {
    extra.domainId = extraDomainId;
  }
  if (extraDriveId) {
    extra.driveId = extraDriveId;
  }
  if (extraShareCode) {
    extra.shareCode = extraShareCode;
  }
  if (extraAccessCode) {
    extra.accessCode = extraAccessCode;
  }
  if (extraAccessToken) {
    extra.accessToken = extraAccessToken;
  }
  if (extraSignature) {
    extra.signature = extraSignature;
  }
  if (extraDate) {
    extra.date = extraDate;
  }
  if (extraPathPrefix) {
    extra.pathPrefix = extraPathPrefix;
  }
  return { providerKey, authMode, displayName, token, cookie, extra };
}

function setAuthValidationSummary(data, title = "Latest Auth Result") {
  const box = document.getElementById("authValidationSummary");
  const raw = document.getElementById("authCaptureResult");
  if (!box || !raw) {
    return;
  }
  if (!data) {
    box.hidden = true;
    box.innerHTML = "";
    raw.textContent = "";
    return;
  }

  const row = data.validation || data.item || data;
  const ok = Boolean(row?.ok) || data?.status === "capture_pending";
  box.hidden = false;
  box.className = `auth-validation-summary${ok ? " ok" : " fail"}`;
  box.innerHTML = "";

  const heading = document.createElement("div");
  heading.className = "auth-validation-title";
  heading.textContent = `${title}: ${ok ? "ok" : "needs_fix"}`;
  box.appendChild(heading);

  const summary = document.createElement("div");
  summary.className = "auth-validation-meta";
  summary.textContent = row?.summary || row?.message || row?.error || "no details";
  box.appendChild(summary);

  const meta = document.createElement("div");
  meta.className = "auth-pill-row";
  const pills = [
    `provider=${row?.providerKey || data?.providerKey || "(unknown)"}`,
    `mode=${row?.mode || data?.status || "(unknown)"}`,
    `status=${row?.status ?? "(none)"}`,
  ];
  if (Array.isArray(row?.requiredFieldHints)) {
    row.requiredFieldHints.forEach((item) => pills.push(`need=${item}`));
  } else if (Array.isArray(data?.requiredFieldHints)) {
    data.requiredFieldHints.forEach((item) => pills.push(`need=${item}`));
  }
  pills.forEach((text) => {
    const pill = document.createElement("span");
    pill.className = `auth-pill${ok ? " ok" : " fail"}`;
    pill.textContent = text;
    meta.appendChild(pill);
  });
  box.appendChild(meta);

  raw.textContent = JSON.stringify(data, null, 2);
}

function setAuthEvidenceSummary(evidence, markdown) {
  const box = document.getElementById("authValidationSummary");
  const raw = document.getElementById("authCaptureResult");
  if (!box || !raw) {
    return;
  }
  const summary = evidence?.summary || {};
  const profile = evidence?.profile || {};
  const validation = evidence?.latestValidation || null;
  const probe = evidence?.latestProbe || null;
  box.hidden = false;
  box.className = `auth-validation-summary${summary.validationOk || summary.probeOk ? " ok" : " fail"}`;
  box.innerHTML = "";

  const heading = document.createElement("div");
  heading.className = "auth-validation-title";
  heading.textContent = `Auth Evidence: ${profile.displayName || profile.profileId || "(unknown)"}`;
  box.appendChild(heading);

  const meta = document.createElement("div");
  meta.className = "auth-validation-meta";
  meta.textContent = `profileReady=${Boolean(summary.profileReady)}, writeReady=${Boolean(summary.writeReady)}, validationOk=${Boolean(summary.validationOk)}, probeOk=${Boolean(summary.probeOk)}`;
  box.appendChild(meta);

  const pills = [
    `provider=${profile.providerKey || "(unknown)"}`,
    `resolvedParentId=${summary.resolvedParentId || "(none)"}`,
    `resolvedFileId=${summary.resolvedFileId || "(none)"}`,
    `writeReady=${Boolean(summary.writeReady)}`,
    `validation=${validation ? (validation.ok ? "ok" : "failed") : "none"}`,
    `probe=${probe ? (probe.ok ? "ok" : "failed") : "none"}`,
  ];
  const pillRow = document.createElement("div");
  pillRow.className = "auth-pill-row";
  pills.forEach((text) => {
    const pill = document.createElement("span");
    pill.className = `auth-pill${text.includes("=ok") ? " ok" : ""}${text.includes("=failed") ? " fail" : ""}`;
    pill.textContent = text;
    pillRow.appendChild(pill);
  });
  box.appendChild(pillRow);
  raw.textContent = markdown || JSON.stringify(evidence, null, 2);
}

function setAuthEvidenceBundleSummary(bundle, markdown) {
  const box = document.getElementById("authValidationSummary");
  const raw = document.getElementById("authCaptureResult");
  if (!box || !raw) {
    return;
  }
  const summary = bundle?.summary || {};
  box.hidden = false;
  box.className = `auth-validation-summary${summary.validationOkCount || summary.probeOkCount ? " ok" : " fail"}`;
  box.innerHTML = "";

  const heading = document.createElement("div");
  heading.className = "auth-validation-title";
  heading.textContent = "Auth Evidence Bundle";
  box.appendChild(heading);

  const meta = document.createElement("div");
  meta.className = "auth-validation-meta";
  meta.textContent = `profiles=${summary.profileCount || 0}, ready=${summary.profileReadyCount || 0}, writeReady=${summary.writeReadyCount || 0}, validationOk=${summary.validationOkCount || 0}, probeOk=${summary.probeOkCount || 0}`;
  box.appendChild(meta);

  const pillRow = document.createElement("div");
  pillRow.className = "auth-pill-row";
  [
    `profileCount=${summary.profileCount || 0}`,
    `profileReady=${summary.profileReadyCount || 0}`,
    `writeReady=${summary.writeReadyCount || 0}`,
    `validationOk=${summary.validationOkCount || 0}`,
    `probeOk=${summary.probeOkCount || 0}`,
  ].forEach((text) => {
    const pill = document.createElement("span");
    pill.className = "auth-pill";
    pill.textContent = text;
    pillRow.appendChild(pill);
  });
  box.appendChild(pillRow);
  raw.textContent = markdown || JSON.stringify(bundle, null, 2);
}

function setAuthRemediationSummary(bundle, markdown) {
  const box = document.getElementById("authValidationSummary");
  const raw = document.getElementById("authCaptureResult");
  if (!box || !raw) {
    return;
  }
  const summary = bundle?.summary || {};
  box.hidden = false;
  box.className = `auth-validation-summary${summary.needsFixCount ? " fail" : " ok"}`;
  box.innerHTML = "";

  const heading = document.createElement("div");
  heading.className = "auth-validation-title";
  heading.textContent = "Auth Remediation Guide";
  box.appendChild(heading);

  const meta = document.createElement("div");
  meta.className = "auth-validation-meta";
  meta.textContent = `profiles=${summary.profileCount || 0}, ready=${summary.readyCount || 0}, needsFix=${summary.needsFixCount || 0}, writeReady=${summary.writeReadyCount || 0}, writeNeedsFix=${summary.writeNeedsFixCount || 0}`;
  box.appendChild(meta);

  const pillRow = document.createElement("div");
  pillRow.className = "auth-pill-row";
  [
    `profileCount=${summary.profileCount || 0}`,
    `readyCount=${summary.readyCount || 0}`,
    `needsFixCount=${summary.needsFixCount || 0}`,
    `writeReadyCount=${summary.writeReadyCount || 0}`,
    `writeNeedsFixCount=${summary.writeNeedsFixCount || 0}`,
  ].forEach((text) => {
    const pill = document.createElement("span");
    pill.className = `auth-pill${text.includes("needsFixCount=0") ? " ok" : ""}${text.includes("needsFixCount=") && !text.includes("=0") ? " fail" : ""}`;
    pill.textContent = text;
    pillRow.appendChild(pill);
  });
  box.appendChild(pillRow);
  raw.textContent = markdown || JSON.stringify(bundle, null, 2);
}

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

function hideAllPanels() {
  for (const panelId of Object.values(tabPanelIds)) {
    const node = document.getElementById(panelId);
    if (node) {
      node.hidden = true;
    }
  }
}

function render() {
  document.documentElement.lang = state.lang;
  document.getElementById("appTitle").textContent = t("app.title");
  document.getElementById("appSubtitle").textContent = t("app.subtitle");
  document.getElementById("loginTitle").textContent = t("login.title");
  document.getElementById("loginPasswordLabel").textContent = t("login.password");
  document.getElementById("loginBtn").textContent = t("login.submit");
  document.getElementById("lockedText").textContent = t("state.locked");
  document.getElementById("authTitle").textContent = t("panel.auth.title");
  document.getElementById("authLiveProbeHint").textContent = t("auth.live_probe_needs");
  const authModeHint = document.getElementById("authModeHint");
  if (authModeHint) {
    const selectedProviderKey = document.getElementById("authProvider")?.value || "";
    const selectedProvider = state.providers.find((item) => item.providerKey === selectedProviderKey);
    authModeHint.textContent = `authModes=${(selectedProvider?.authModes || []).join(", ") || "(none)"}`;
  }
  document.getElementById("queueTitle").textContent = t("panel.queue.title");
  document.getElementById("queueSubtitle").textContent = t("panel.queue.subtitle");
  document.getElementById("pendingTitle").textContent = t("panel.pending.title");
  document.getElementById("pendingFoldHint").textContent = t("panel.pending.fold_hint");
  document.getElementById("pendingSubtitle").textContent = t("panel.pending.subtitle");
  document.getElementById("providersTitle").textContent = t("panel.providers.title");
  document.getElementById("providersSubtitle").textContent = t("panel.providers.subtitle");
  document.getElementById("settingsTitle").textContent = t("panel.settings.title");
  document.getElementById("settingsSubtitle").textContent = t("panel.settings.subtitle");
  document.getElementById("newTaskTitle").textContent = t("panel.new_task.title");
  document.getElementById("newTaskSubtitle").textContent = t("panel.new_task.subtitle");
  document.getElementById("wizardSecondaryTitle").textContent = t("panel.new_task.secondary");
  document.getElementById("wizardSummaryTitle").textContent = t("panel.new_task.summary");
  document.getElementById("providersMatrixTitle").textContent = t("providers.matrix");
  document.getElementById("providersResearchTitle").textContent = t("providers.research");
  document.getElementById("providersLiveProbeHint").textContent = t("providers.live_probe_hint");
  document.getElementById("settingsSessionTitle").textContent = t("settings.session");
  document.getElementById("settingsValidationTitle").textContent = t("settings.validation");
  document.getElementById("settingsProviderProbeTitle").textContent = t("settings.provider_probe");
  document.getElementById("settingsProviderStatusTitle").textContent = "Provider Status Matrix";
  document.getElementById("settingsAuditTitle").textContent = t("settings.audit");
  document.getElementById("settingsTip").textContent = t("settings.last_tip");
  updateAuthFormMode();

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
  loginPanel.hidden = state.loggedIn;
  appPanel.hidden = !state.loggedIn;
  logoutBtn.hidden = !state.loggedIn;

  hideAllPanels();
  if (state.loggedIn) {
    const activePanelId = tabPanelIds[state.activeTab] || "newTaskPanel";
    const activePanel = document.getElementById(activePanelId);
    if (activePanel) {
      activePanel.hidden = false;
    }
  }

  renderWizardSteps();
  renderSummaryCards();
  renderAuthList();
  renderTaskList();
  renderTaskPlanPreview();
  renderPendingList();
  renderProviderPanel();
  renderSettingsPanel();
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
  for (const provider of state.providers) {
    const node = document.createElement("option");
    node.value = provider.providerKey;
    node.textContent = `${provider.displayName} (${provider.providerKey})`;
    providerSelect.appendChild(node);
  }
  const modalSelect = document.getElementById("authModalProvider");
  modalSelect.innerHTML = providerSelect.innerHTML;
  const taskSourceProvider = document.getElementById("taskSourceProvider");
  const taskTargetProvider = document.getElementById("taskTargetProvider");
  taskSourceProvider.innerHTML = providerSelect.innerHTML;
  taskTargetProvider.innerHTML = providerSelect.innerHTML;
  if (state.providers.some((provider) => provider.providerKey === "quark")) {
    taskSourceProvider.value = "quark";
  }
  if (state.providers.some((provider) => provider.providerKey === "guangya")) {
    taskTargetProvider.value = "guangya";
  }
  syncAuthModeOptions();
  renderSummaryCards();
}

function syncAuthModeOptions() {
  const providerSelect = document.getElementById("authProvider");
  const authModeSelect = document.getElementById("authMode");
  const authModeHint = document.getElementById("authModeHint");
  if (!providerSelect || !authModeSelect) {
    return;
  }
  const currentValue = authModeSelect.value;
  const provider = state.providers.find((item) => item.providerKey === providerSelect.value);
  const allowedModes = provider?.authModes || ["manual_token", "manual_cookie", "web_login_capture"];
  authModeSelect.innerHTML = "";
  for (const mode of allowedModes) {
    const option = document.createElement("option");
    option.value = mode;
    option.textContent = mode;
    authModeSelect.appendChild(option);
  }
  authModeSelect.value = allowedModes.includes(currentValue) ? currentValue : (allowedModes[0] || "");
  if (authModeHint) {
    authModeHint.textContent = `authModes=${allowedModes.join(", ") || "(none)"}`;
  }
}

function renderSummaryCards() {
  const wrap = document.getElementById("summaryGrid");
  if (!wrap) {
    return;
  }
  const pendingCount = state.tasks.reduce((sum, task) => {
    const value = task?.progress?.pendingManual || 0;
    return sum + value;
  }, 0);
  const cards = [
    { label: t("summary.providers"), value: state.providers.length },
    { label: t("summary.tasks"), value: state.tasks.length },
    { label: t("summary.pending"), value: pendingCount },
    { label: t("summary.auth_profiles"), value: state.authProfiles.length },
  ];
  wrap.innerHTML = "";
  for (const card of cards) {
    const node = document.createElement("div");
    node.className = "summary-card";
    const value = document.createElement("strong");
    value.textContent = String(card.value);
    const label = document.createElement("span");
    label.textContent = card.label;
    node.appendChild(value);
    node.appendChild(label);
    wrap.appendChild(node);
  }
}

function renderWizardSteps() {
  const wrap = document.getElementById("wizardSteps");
  const nav = document.getElementById("wizardSecondaryNav");
  const summaryBody = document.getElementById("wizardSummaryBody");
  if (!wrap || !nav || !summaryBody) {
    return;
  }
  wrap.innerHTML = "";
  nav.innerHTML = "";
  wizardSteps.forEach((step, index) => {
    const active = state.activeWizardStep === index;

    const stepNode = document.createElement("button");
    stepNode.type = "button";
    stepNode.className = `wizard-step${active ? " active" : ""}`;
    stepNode.textContent = `${index + 1}. ${t(step.title)}`;
    stepNode.addEventListener("click", () => {
      state.activeWizardStep = index;
      renderWizardSteps();
    });
    wrap.appendChild(stepNode);

    const navNode = document.createElement("button");
    navNode.type = "button";
    navNode.className = `secondary-link${active ? " active" : ""}`;
    navNode.textContent = t(step.title);
    navNode.addEventListener("click", () => {
      state.activeWizardStep = index;
      renderWizardSteps();
    });
    nav.appendChild(navNode);
  });
  summaryBody.textContent = t(wizardSteps[state.activeWizardStep].description);
}

function renderAuthList() {
  const list = document.getElementById("authList");
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
    const stack = document.createElement("div");
    stack.className = "auth-item-stack";
    stack.appendChild(meta);
    if (Array.isArray(item.missingFieldHints) && item.missingFieldHints.length) {
      const readinessNote = document.createElement("div");
      readinessNote.className = "auth-item-note";
      readinessNote.textContent = `profile_ready=${item.profileReady}, missing=${item.missingFieldHints.join(" | ")}`;
      stack.appendChild(readinessNote);
      const patchHint = buildPatchCommandHint(item);
      if (patchHint) {
        const patchNote = document.createElement("div");
        patchNote.className = "auth-item-note";
        patchNote.textContent = `patch_hint=${patchHint}`;
        stack.appendChild(patchNote);
      }
    } else if (resolvedParentIdForProfile(item) || resolvedFileIdForProfile(item)) {
      const resolvedNote = document.createElement("div");
      resolvedNote.className = "auth-item-note";
      resolvedNote.textContent = `resolvedParentId=${resolvedParentIdForProfile(item) || "(none)"}, resolvedFileId=${resolvedFileIdForProfile(item) || "(none)"}`;
      stack.appendChild(resolvedNote);
    }
    if (item.writeReady === false) {
      const writeNote = document.createElement("div");
      writeNote.className = "auth-item-note";
      const writeMissing = Array.isArray(item.writeMissingFieldHints) && item.writeMissingFieldHints.length
        ? item.writeMissingFieldHints.join(" | ")
        : "(none)";
      writeNote.textContent = `write_ready=${item.writeReady}, write_missing=${writeMissing}`;
      stack.appendChild(writeNote);
      if (item.writeBlockerNote) {
        const writeBlockerNote = document.createElement("div");
        writeBlockerNote.className = "auth-item-note";
        writeBlockerNote.textContent = `write_blocker=${item.writeBlockerNote}`;
        stack.appendChild(writeBlockerNote);
      }
    }
    const latestValidation = latestValidationByProfile(item.profileId);
    if (latestValidation) {
      const validationNote = document.createElement("div");
      validationNote.className = "auth-item-note";
      validationNote.textContent = `validation: ok=${latestValidation.ok}, mode=${latestValidation.mode || "(unknown)"}, status=${latestValidation.status || 0}, summary=${latestValidation.summary || latestValidation.error || "(none)"}, risk=${latestValidation.riskHint || "(none)"}`;
      stack.appendChild(validationNote);
    }
    const latestProbe = state.providerLiveProbes[item.profileId];
    if (latestProbe) {
      const probeNote = document.createElement("div");
      probeNote.className = "auth-item-note";
      probeNote.textContent = `probe: ok=${latestProbe.ok}, mode=${latestProbe.mode || "(unknown)"}, checks=${(latestProbe.checks || []).length}, summary=${latestProbe.summary || "(none)"}`;
      stack.appendChild(probeNote);
    }
    left.appendChild(title);
    left.appendChild(stack);

    const actions = document.createElement("div");
    actions.className = "row-actions";
    const validateBtn = document.createElement("button");
    validateBtn.className = "ghost";
    validateBtn.textContent = "Validate";
    validateBtn.addEventListener("click", () => validateAuth(item.profileId));
    const editBtn = document.createElement("button");
    editBtn.className = "ghost";
    editBtn.textContent = "Edit";
    editBtn.addEventListener("click", () => fillAuthForm(item));
    const evidenceBtn = document.createElement("button");
    evidenceBtn.className = "ghost";
    evidenceBtn.textContent = "Refresh Evidence";
    evidenceBtn.addEventListener("click", () => showAuthEvidence(item));
    if (liveProbeProviderSet.has(item.providerKey)) {
      const probeBtn = document.createElement("button");
      probeBtn.className = "ghost";
      probeBtn.textContent = t("auth.live_probe");
      probeBtn.addEventListener("click", () => probeProviderLive(item));
      actions.appendChild(probeBtn);
    }
    const deleteBtn = document.createElement("button");
    deleteBtn.className = "ghost";
    deleteBtn.textContent = "Delete";
    deleteBtn.addEventListener("click", () => deleteAuth(item.profileId));
    actions.appendChild(editBtn);
    actions.appendChild(evidenceBtn);
    actions.appendChild(validateBtn);
    actions.appendChild(deleteBtn);

    node.appendChild(left);
    node.appendChild(actions);
    list.appendChild(node);
  }
}

async function loadAuthProfiles() {
  if (!state.loggedIn) {
    return;
  }
  const data = await fetchJson("/api/auth/profiles");
  state.authProfiles = data.items || [];
  renderTaskProfileOptions();
  render();
}

function renderTaskProfileOptions() {
  const select = document.getElementById("taskTargetProfile");
  const parentInput = document.getElementById("taskTargetParentId");
  const targetProvider = document.getElementById("taskTargetProvider")?.value || "";
  if (!select) {
    return;
  }
  const currentValue = select.value;
  const filteredProfiles = state.authProfiles.filter((profile) => !targetProvider || profile.providerKey === targetProvider);
  select.innerHTML = "";
  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = targetProvider ? `(no targetProfileId for ${targetProvider})` : "(no targetProfileId)";
  select.appendChild(empty);
  for (const profile of filteredProfiles) {
    const node = document.createElement("option");
    node.value = profile.profileId;
    node.textContent = `${profile.displayName} [${profile.providerKey}]`;
    select.appendChild(node);
  }
  if (currentValue && filteredProfiles.some((profile) => profile.profileId === currentValue)) {
    select.value = currentValue;
    syncTaskTargetParentFromProfile();
    return;
  }
  const preferred = filteredProfiles[0] || null;
  if (preferred) {
    select.value = preferred.profileId;
    if (parentInput && !parentInput.value.trim()) {
      parentInput.value = resolvedParentIdForProfile(preferred);
    }
    return;
  }
  if (parentInput) {
    parentInput.value = "";
  }
}

function syncTaskTargetParentFromProfile() {
  const select = document.getElementById("taskTargetProfile");
  const parentInput = document.getElementById("taskTargetParentId");
  if (!select || !parentInput) {
    return;
  }
  const profile = state.authProfiles.find((item) => item.profileId === select.value);
  if (!profile) {
    return;
  }
  parentInput.value = resolvedParentIdForProfile(profile);
}

function onTaskTargetProviderChange() {
  state.taskPlanPreview = null;
  setTaskCreateGuard("");
  resetTaskPlanAck();
  renderTaskProfileOptions();
  renderTaskPlanPreview();
}

function selectedTaskTargetProfile() {
  const profileId = document.getElementById("taskTargetProfile")?.value || "";
  if (!profileId) {
    return null;
  }
  return state.authProfiles.find((item) => item.profileId === profileId) || null;
}

function setTaskCreateGuard(message) {
  const box = document.getElementById("taskCreateGuard");
  if (!box) {
    return;
  }
  if (!message) {
    box.hidden = true;
    box.textContent = "";
    return;
  }
  box.hidden = false;
  box.textContent = message;
}

function resetTaskPlanAck() {
  const ack = document.getElementById("taskPlanPreviewAck");
  if (ack) {
    ack.checked = false;
  }
}

function taskActionsForState(task) {
  const allowed = task?.summary?.allowedActions;
  if (Array.isArray(allowed) && allowed.length) {
    return allowed;
  }
  return ["retry"];
}

function appendTaskStatusPill(container, label, className = "") {
  const pill = document.createElement("span");
  pill.className = `task-status-pill${className ? ` ${className}` : ""}`;
  pill.textContent = label;
  container.appendChild(pill);
}

function appendTaskGuardPill(container, label, className = "") {
  const pill = document.createElement("span");
  pill.className = `task-guard-pill${className ? ` ${className}` : ""}`;
  pill.textContent = label;
  container.appendChild(pill);
}

async function loadProviderResearch() {
  if (!state.loggedIn) {
    return;
  }
  const data = await fetchJson("/api/providers/research");
  state.providerResearch = data.items || [];
  renderProviderPanel();
}

async function loadStatusMatrix() {
  if (!state.loggedIn) {
    return;
  }
  const data = await fetchJson("/api/providers/status_matrix");
  state.statusMatrix = data;
  renderProviderPanel();
  renderSettingsPanel();
}

async function loadAuditSummary() {
  if (!state.loggedIn) {
    return;
  }
  const data = await fetchJson("/api/plan/audit");
  state.auditSummary = data.summary || null;
  renderSettingsPanel();
}

async function loadRealEvidenceSummary() {
  if (!state.loggedIn) {
    return;
  }
  const data = await fetchJson("/api/real_evidence");
  state.realEvidenceReport = data;
  state.realEvidenceSummary = data.summary || null;
  renderProviderPanel();
  renderSettingsPanel();
}

async function loadRealEvidenceRemediationSummary() {
  if (!state.loggedIn) {
    return;
  }
  const data = await fetchJson("/api/real_evidence_remediation_bundle");
  state.realEvidenceRemediation = data;
  renderSettingsPanel();
}

async function loadLiveValidations() {
  if (!state.loggedIn) {
    return;
  }
  const data = await fetchJson("/api/auth/live_validations");
  state.liveValidations = data.latestItems || data.items || [];
  state.liveValidationMeta = {
    historyCount: (data.items || []).length,
    summary: data.summary || null,
  };
  renderSettingsPanel();
}

async function loadProviderLiveProbeResults() {
  if (!state.loggedIn) {
    return;
  }
  const data = await fetchJson("/api/providers/live_probe_results");
  const next = {};
  for (const item of data.latestItems || data.items || []) {
    if (item && item.profileId) {
      next[item.profileId] = item;
    }
  }
  state.providerLiveProbes = next;
  state.providerLiveProbeMeta = {
    historyCount: (data.items || []).length,
    summary: data.summary || null,
  };
  renderProviderPanel();
  renderSettingsPanel();
}

async function loadTaskRuntimeEvidence() {
  if (!state.loggedIn) {
    return;
  }
  const data = await fetchJson("/api/task_runtime_evidence");
  state.taskRuntimeEvidence = data.latestItems || data.items || [];
  state.taskRuntimeEvidenceMeta = {
    historyCount: (data.items || []).length,
    summary: data.summary || null,
  };
  renderSettingsPanel();
}

async function saveAuth() {
  const payload = collectAuthPayload();
  const editingId = state.authEditingProfileId;
  const data = await fetchJson(editingId ? `/api/auth/profiles/${editingId}` : "/api/auth/profiles", {
    method: editingId ? "PUT" : "POST",
    body: JSON.stringify(payload),
  });
  setAuthValidationSummary(data, "Saved Auth Validation");
  resetAuthForm();
  await Promise.all([loadAuthProfiles(), loadLiveValidations(), loadStatusMatrix()]);
}

function openAuthModal() {
  const modal = document.getElementById("authModal");
  if (modal && typeof modal.showModal === "function") {
    modal.showModal();
  }
}

async function startCaptureGuide() {
  const providerKey = document.getElementById("authModalProvider").value;
  const data = await fetchJson("/api/auth/capture/start", {
    method: "POST",
    body: JSON.stringify({ providerKey }),
  });
  setAuthValidationSummary(data, "Capture Guide");
}

async function validateAuth(profileId) {
  const data = await fetchJson(`/api/auth/profiles/${profileId}/validate`, { method: "POST" });
  setAuthValidationSummary(data, "Manual Validate");
  await Promise.all([loadAuthProfiles(), loadLiveValidations(), loadStatusMatrix()]);
}

async function showAuthEvidence(profile) {
  const extra = profile?.extra || {};
  const data = await fetchJson(`/api/auth/profiles/${profile.profileId}/refresh_evidence`, {
    method: "POST",
    body: JSON.stringify({
      pageSize: Number(extra.pageSize || 100) || 100,
      dirName: extra.dirName || "",
    }),
  });
  setAuthEvidenceSummary(data?.evidence || {}, data?.markdown || "");
  await Promise.all([loadAuthProfiles(), loadLiveValidations(), loadProviderLiveProbeResults(), loadStatusMatrix()]);
}

async function showAuthEvidenceBundle() {
  const data = await fetchJson("/api/auth/refresh_evidence_bundle", {
    method: "POST",
    body: JSON.stringify({ pageSize: 100, dirName: "" }),
  });
  setAuthEvidenceBundleSummary(data?.bundle || {}, data?.markdown || "");
  await Promise.all([loadAuthProfiles(), loadLiveValidations(), loadProviderLiveProbeResults(), loadStatusMatrix()]);
}

async function showAuthRemediationGuide() {
  const [bundleData, markdownData] = await Promise.all([
    fetchJson("/api/auth/remediation_bundle"),
    fetchJson("/api/auth/remediation_bundle_markdown"),
  ]);
  setAuthRemediationSummary(bundleData || {}, markdownData?.markdown || "");
  await Promise.all([loadAuthProfiles(), loadLiveValidations(), loadProviderLiveProbeResults(), loadStatusMatrix()]);
}

async function deleteAuth(profileId) {
  await fetchJson(`/api/auth/profiles/${profileId}`, { method: "DELETE" });
  delete state.providerLiveProbes[profileId];
  await Promise.all([loadAuthProfiles(), loadLiveValidations(), loadProviderLiveProbeResults(), loadStatusMatrix()]);
}

function onAuthReset() {
  resetAuthForm();
}

async function probeProviderLive(profile) {
  const extra = profile.extra || {};
  const payload = {
    profileId: profile.profileId,
    parentId: resolvedParentIdForProfile(profile),
    fileId: resolvedFileIdForProfile(profile),
    pageSize: Number(extra.pageSize || 100) || 100,
    dirName: extra.dirName || "",
  };
  const data = await fetchJson("/api/providers/live_probe_profile", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  state.providerLiveProbes[profile.profileId] = data.item || null;
  setAuthValidationSummary(data.item || data, "Live Probe");
  await Promise.all([loadProviderLiveProbeResults(), loadStatusMatrix()]);
}

function renderTaskList() {
  const list = document.getElementById("taskList");
  list.innerHTML = "";
  for (const task of state.tasks) {
    const summary = task.summary || {};
    const node = document.createElement("li");
    node.className = "auth-item";
    const left = document.createElement("div");
    const title = document.createElement("div");
    title.textContent = `${task.sourceProvider} -> ${task.targetProvider}`;
    const meta = document.createElement("div");
    meta.className = "task-status-row";
    appendTaskStatusPill(meta, `state=${summary.state || task.state}`, String(summary.state || task.state || ""));
    appendTaskStatusPill(meta, `done=${task.progress.done}/${task.progress.total}`);
    appendTaskStatusPill(meta, `failed=${task.progress.failed}`);
    appendTaskStatusPill(meta, `pending=${task.progress.pendingManual}`);
    appendTaskStatusPill(meta, `live=${summary.liveSuccessCount || task.progress.liveSuccess || 0}`);
    appendTaskStatusPill(meta, `liveFailed=${summary.liveFailedCount || task.progress.liveFailed || 0}`);
    appendTaskStatusPill(meta, `probe=${summary.probeOnlyCount || task.progress.probeOnly || 0}`);
    appendTaskStatusPill(meta, `candidate=${summary.candidateOnlyCount || task.progress.candidateOnly || 0}`);
    if (summary.completionKind) {
      appendTaskStatusPill(meta, `completion=${summary.completionKind}`);
    }
    const detail = document.createElement("div");
    detail.className = "auth-item-meta";
    const guard = task.guard || {};
    const targetProfile = guard.targetProfile || {};
    const targetProfileText = targetProfile.displayName || task.targetProfileId || "(none)";
    const profileReadyText = Object.prototype.hasOwnProperty.call(targetProfile, "profileReady")
      ? String(targetProfile.profileReady !== false)
      : "(unknown)";
    const writeReadyText = Object.prototype.hasOwnProperty.call(targetProfile, "writeReady")
      ? String(targetProfile.writeReady !== false)
      : "(unknown)";
    detail.textContent = `targetProfile=${targetProfileText}, targetProfileId=${task.targetProfileId || "(none)"}, targetParentId=${task.targetParentId || "(none)"}, conflictPolicy=${task.conflictPolicy || "auto_rename_new"}, profileReady=${profileReadyText}, writeReady=${writeReadyText}`;
    left.appendChild(title);
    left.appendChild(meta);
    left.appendChild(detail);
    const blockingReasons = guard.blockingReasons || [];
    const warningReasons = guard.warningReasons || [];
    const guardRow = document.createElement("div");
    guardRow.className = "task-guard-row";
    if (summary.hardBlocked || guard.hardBlocked) {
      appendTaskGuardPill(guardRow, "guard=hard_blocked", "blocking");
    }
    if ((summary.blockingCount || blockingReasons.length) > 0) {
      appendTaskGuardPill(guardRow, `blocking=${summary.blockingCount || blockingReasons.length}`, "blocking");
    }
    if ((summary.warningCount || warningReasons.length) > 0) {
      appendTaskGuardPill(guardRow, `warnings=${summary.warningCount || warningReasons.length}`, "warning");
    }
    if (summary.riskReason) {
      appendTaskGuardPill(guardRow, `risk=${summary.riskReason}`, "warning");
    }
    if (summary.awaitingAcknowledgement) {
      appendTaskGuardPill(guardRow, "awaitingAcknowledgement=true", "ack");
    }
    if (summary.riskPaused) {
      appendTaskGuardPill(guardRow, "riskPaused=true", "warning");
    }
    if (targetProfile.profileReady === false) {
      appendTaskGuardPill(guardRow, "targetProfileReady=false", "warning");
    }
    if (targetProfile.writeReady === false) {
      appendTaskGuardPill(guardRow, "targetWriteReady=false", "blocking");
    }
    const requiresAck = summary.requiresAcknowledgement || guard.requiresAcknowledgement || {};
    const acknowledged = summary.acknowledged || guard.acknowledged || {};
    if (requiresAck?.pendingManual || requiresAck?.downloadUpload) {
      const ackFlags = [];
      if (requiresAck?.pendingManual) {
        ackFlags.push(`pendingManual:${Boolean(acknowledged?.pendingManual) ? "ok" : "need_ack"}`);
      }
      if (requiresAck?.downloadUpload) {
        ackFlags.push(`downloadUpload:${Boolean(acknowledged?.downloadUpload) ? "ok" : "need_ack"}`);
      }
      appendTaskGuardPill(guardRow, `ack=${ackFlags.join(",")}`, "ack");
    }
    if (guardRow.childNodes.length) {
      left.appendChild(guardRow);
    }
    if (blockingReasons.length || warningReasons.length) {
      const guardMeta = document.createElement("div");
      guardMeta.className = "auth-item-meta";
      guardMeta.textContent = `blocking=${blockingReasons.join(" | ") || "(none)"}, warnings=${warningReasons.join(" | ") || "(none)"}`;
      left.appendChild(guardMeta);
    }
    if (targetProfile.profileReady === false || targetProfile.writeReady === false) {
      const targetProfileMeta = document.createElement("div");
      targetProfileMeta.className = "auth-item-meta";
      targetProfileMeta.textContent = `targetProfileMissing=${(targetProfile.missingFieldHints || []).join(" | ") || "(none)"}, targetWriteMissing=${(targetProfile.writeMissingFieldHints || []).join(" | ") || "(none)"}${targetProfile.writeBlockerNote ? `, writeBlocker=${targetProfile.writeBlockerNote}` : ""}`;
      left.appendChild(targetProfileMeta);
    }
    const lastActionError = summary.lastActionError || task.lastActionError || {};
    if (lastActionError.action || lastActionError.reason) {
      const errorRow = document.createElement("div");
      errorRow.className = "task-guard-row";
      appendTaskGuardPill(
        errorRow,
        `lastActionError=${lastActionError.action || "(unknown)"}`,
        "error"
      );
      left.appendChild(errorRow);
      const errorMeta = document.createElement("div");
      errorMeta.className = "task-action-error";
      errorMeta.textContent = `${lastActionError.reason || "(no reason)"}${lastActionError.at ? ` @ ${lastActionError.at}` : ""}`;
      left.appendChild(errorMeta);
    }

    const resultRows = task.latestResults || task.results || [];
    if (resultRows.length) {
      const latest = resultRows
        .slice(0, 3)
        .map((row) => {
          const executionText = row.executionMode ? ` [${row.executionMode}]` : "";
          const modeText = row.liveAttempt ? ` (${row.liveAttempt.mode})` : "";
          const riskText = row.liveAttempt?.riskHint ? ` - ${row.liveAttempt.riskHint}` : "";
          const authText = row.liveAttempt?.requiredAuth?.length
            ? `, requiredAuth=${row.liveAttempt.requiredAuth.join("/")}`
            : "";
          const errorText = row.liveAttempt?.error
            ? `, error=${row.liveAttempt.error}`
            : "";
          const noteText = row.note
            ? `, note=${row.note}`
            : "";
          const verifyText = row.liveAttempt?.verifyMode
            ? `, verify=${row.liveAttempt.verifyOk ? "ok" : "pending"}:${row.liveAttempt.verifyMode}`
            : "";
          const verifyNoteText = row.liveAttempt?.verifyNote
            ? `, verifyNote=${row.liveAttempt.verifyNote}`
            : "";
          const conflictText = row.liveAttempt?.conflictAction
            ? `, conflict=${row.liveAttempt.conflictAction}:${row.liveAttempt.resolvedTargetName || "(same)"}`
            : "";
          const conflictSupportText = row.conflictSupportStatus
            ? `, conflictSupport=${row.conflictSupportStatus}`
            : "";
          return `${row.path}: ${row.status}${executionText}${modeText}${verifyText}${verifyNoteText}${conflictText}${conflictSupportText}${authText}${errorText}${noteText}${riskText}`;
        })
        .join(" | ");
      const resultMeta = document.createElement("div");
      resultMeta.className = "auth-item-meta";
      resultMeta.textContent = latest;
      left.appendChild(resultMeta);
    }

    const actions = document.createElement("div");
    actions.className = "row-actions";
    for (const action of taskActionsForState(task)) {
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

function renderPendingList() {
  const list = document.getElementById("pendingList");
  const summaryMeta = document.getElementById("pendingSummaryMeta");
  const details = document.getElementById("pendingDetails");
  list.innerHTML = "";
  const rows = [];
  for (const task of state.tasks) {
    const items = task?.pendingItems || task?.plan?.pendingItems || [];
    const taskSummary = task?.summary || {};
    for (const item of items) {
      rows.push({
        taskId: task.taskId,
        taskState: taskSummary.state || task.state || "",
        taskRiskReason: taskSummary.riskReason || "",
        targetProvider: task.targetProvider,
        path: item.path,
        size: item.size,
        reason: item.reason,
        conflictPolicy: item.conflictPolicy || "auto_rename_new",
        availableFastInputs: item.availableFastInputs || [],
        missingFastInputs: item.missingFastInputs || [],
        conflictSupportStatus: item.conflictSupportStatus || "",
        conflictNote: item.conflictNote || "",
      });
    }
  }
  if (summaryMeta) {
    summaryMeta.textContent = `tasks=${state.tasks.length}, pending=${rows.length}`;
  }
  if (details) {
    details.open = rows.length > 0;
  }
  if (!rows.length) {
    const empty = document.createElement("li");
    empty.className = "empty-card";
    empty.textContent = t("pending.empty");
    list.appendChild(empty);
    return;
  }
  for (const row of rows) {
    const node = document.createElement("li");
    node.className = "auth-item";
    const left = document.createElement("div");
    const title = document.createElement("div");
    title.textContent = `${row.path} -> ${row.targetProvider}`;
    const meta = document.createElement("div");
    meta.className = "auth-item-meta";
    meta.textContent = `task=${row.taskId}, state=${row.taskState || "(unknown)"}, risk=${row.taskRiskReason || "(none)"}, size=${row.size}, conflictPolicy=${row.conflictPolicy || "auto_rename_new"}, available=${row.availableFastInputs.join(",") || "(none)"}, missing=${row.missingFastInputs.join(",") || "(none)"}`;
    const detail = document.createElement("div");
    detail.className = "auth-item-meta";
    const conflictSupportText = row.conflictSupportStatus ? `, conflictSupport=${row.conflictSupportStatus}` : "";
    const conflictNoteText = row.conflictNote ? `, conflictNote=${row.conflictNote}` : "";
    detail.textContent = `${row.reason}${conflictSupportText}${conflictNoteText}`;
    left.appendChild(title);
    left.appendChild(meta);
    left.appendChild(detail);
    node.appendChild(left);
    list.appendChild(node);
  }
}

function renderTaskPlanPreview() {
  const panel = document.getElementById("taskPlanPreviewPanel");
  const meta = document.getElementById("taskPlanPreviewMeta");
  const summaryWrap = document.getElementById("taskPlanPreviewSummary");
  const risk = document.getElementById("taskPlanPreviewRisk");
  const ackWrap = document.getElementById("taskPlanPreviewAckWrap");
  const list = document.getElementById("taskPlanPreviewList");
  if (!panel || !meta || !summaryWrap || !risk || !ackWrap || !list) {
    return;
  }
  summaryWrap.innerHTML = "";
  list.innerHTML = "";
  const plan = state.taskPlanPreview;
  if (!plan) {
    panel.hidden = true;
    meta.textContent = "";
    risk.hidden = true;
    risk.textContent = "";
    ackWrap.hidden = true;
    return;
  }
  panel.hidden = false;
  const counts = plan?.summary?.strategyCounts || {};
  const targetProfile = selectedTaskTargetProfile();
  const targetProfileText = targetProfile
    ? `, targetProfile=${targetProfile.displayName || targetProfile.profileId}, profileReady=${targetProfile.profileReady !== false}, writeReady=${targetProfile.writeReady !== false}`
    : ", targetProfile=(none)";
  meta.textContent = `source=${plan.sourceProvider || "(unknown)"} -> target=${plan.targetProvider || "(unknown)"}, thresholdMB=${plan.thresholdMB || 0}, conflictPolicy=${plan.conflictPolicy || "auto_rename_new"}${targetProfileText}`;
  [
    { label: "total", value: plan?.summary?.total || 0 },
    { label: "fast_upload", value: counts.fast_upload || 0 },
    { label: "download_upload", value: counts.download_upload || 0 },
    { label: "pending_manual", value: counts.pending_manual || 0 },
  ].forEach((card) => {
    const node = document.createElement("div");
    node.className = "summary-card compact";
    const value = document.createElement("strong");
    value.textContent = String(card.value);
    const label = document.createElement("span");
    label.textContent = card.label;
    node.appendChild(value);
    node.appendChild(label);
    summaryWrap.appendChild(node);
  });

  const riskLines = [];
  if (!targetProfile) {
    riskLines.push("targetProfile missing: No saved target auth profile is selected. Create or select a target profile before you expect live write behavior.");
  } else {
    if (targetProfile.profileReady === false) {
      riskLines.push(`targetProfile not ready: ${targetProfile.displayName || targetProfile.profileId} is still missing required auth fields: ${(targetProfile.missingFieldHints || []).join(" | ") || "(unknown)"}`);
    }
    if (targetProfile.writeReady === false) {
      riskLines.push(`targetProfile not write-ready: ${targetProfile.displayName || targetProfile.profileId} cannot safely write yet: ${(targetProfile.writeMissingFieldHints || []).join(" | ") || "(unknown)"}${targetProfile.writeBlockerNote ? ` | ${targetProfile.writeBlockerNote}` : ""}`);
    }
  }
  if ((counts.pending_manual || 0) > 0) {
    riskLines.push(`pending_manual=${counts.pending_manual}: Some files still need manual confirmation. Usually this means required fast-upload fingerprints are missing and the fallback threshold is too small or disabled.`);
  }
  if ((counts.download_upload || 0) > 0) {
    riskLines.push(`download_upload=${counts.download_upload}: These files will fall back to download-then-upload. If this is not what you want, add more fingerprints or lower the target scope before creating the task.`);
  }
  const firstUnsupported = (plan.items || []).find((item) => item.conflictSupportStatus === "unsupported");
  if (firstUnsupported) {
    riskLines.push(`conflict unsupported: ${firstUnsupported.path} is using ${plan.conflictPolicy || "auto_rename_new"} on a target path that is not currently guaranteed. Review the provider note before running.`);
  }
  risk.hidden = riskLines.length === 0;
  risk.textContent = riskLines.join("\n");
  ackWrap.hidden = !((counts.pending_manual || 0) > 0 || (counts.download_upload || 0) > 0);

  for (const item of plan.items || []) {
    const node = document.createElement("li");
    node.className = "auth-item";
    const left = document.createElement("div");
    left.className = "task-plan-preview-list-meta";
    const title = document.createElement("div");
    title.textContent = `${item.path}: ${item.strategy}`;
    const metaLine = document.createElement("div");
    metaLine.className = "auth-item-meta";
    metaLine.textContent = `available=${(item.availableFastInputs || []).join(",") || "(none)"}, missing=${(item.missingFastInputs || []).join(",") || "(none)"}, conflictSupport=${item.conflictSupportStatus || "unknown"}`;
    const reasonLine = document.createElement("div");
    reasonLine.className = "auth-item-meta";
    reasonLine.textContent = `${item.reason || ""}${item.conflictNote ? ` | ${item.conflictNote}` : ""}`;
    const fingerprint = item.normalizedFingerprints || {};
    const fingerprintCode = document.createElement("div");
    fingerprintCode.className = "task-plan-preview-code";
    fingerprintCode.textContent = [
      `md5=${fingerprint.md5 || "(none)"}`,
      `sha1=${fingerprint.sha1 || "(none)"}`,
      `sha256=${fingerprint.sha256 || "(none)"}`,
      `crc64=${fingerprint.crc64 || "(none)"}`,
      `gcid=${fingerprint.gcid || "(none)"}`,
      `etag=${fingerprint.etag || "(none)"}`,
      `pickcode=${fingerprint.pickcode || "(none)"}`,
      `blockListMd5=${(fingerprint.blockListMd5 || []).join(",") || "(none)"}`,
    ].join("\n");
    left.appendChild(title);
    left.appendChild(metaLine);
    left.appendChild(reasonLine);
    left.appendChild(fingerprintCode);
    node.appendChild(left);
    list.appendChild(node);
  }
}

async function loadTasks() {
  if (!state.loggedIn) {
    return;
  }
  const data = await fetchJson("/api/tasks");
  state.tasks = data.listItems || data.items || [];
  render();
}

async function createDemoTask() {
  const preferredProfile = state.authProfiles.find((profile) => profile.providerKey === "guangya");
  const body = {
    sourceProvider: "quark",
    targetProvider: "guangya",
    targetProfileId: preferredProfile?.profileId || "",
    targetParentId: resolvedParentIdForProfile(preferredProfile),
    thresholdMB: 200,
    conflictPolicy: "auto_rename_new",
    selectedRoots: ["/1", "/2"],
    entries: [
      { path: "/1/11/111/a.bin", size: 100, md5: "e10adc3949ba59abbe56e057f20f883e" },
      { path: "/1/11/112/b.bin", size: 100, md5: "" },
      { path: "/2/21/211/c.bin", size: 1000000000, md5: "" },
    ],
  };
  await fetchJson("/api/tasks", { method: "POST", body: JSON.stringify(body) });
  state.taskPlanPreview = null;
  await loadTasks();
}

function collectTaskFormPayload() {
  const sourceProvider = document.getElementById("taskSourceProvider").value;
  const targetProvider = document.getElementById("taskTargetProvider").value;
  const targetProfileId = document.getElementById("taskTargetProfile").value;
  const targetParentId = document.getElementById("taskTargetParentId").value.trim();
  const sourcePath = document.getElementById("taskSourcePath").value.trim() || "/demo.bin";
  const localPath = document.getElementById("taskLocalPath").value.trim();
  const md5 = document.getElementById("taskMd5").value.trim();
  const sizeRaw = document.getElementById("taskSize").value.trim();
  const thresholdRaw = document.getElementById("taskThresholdMB").value.trim();
  const conflictPolicy = document.getElementById("taskConflictPolicy").value;
  const ackChecked = Boolean(document.getElementById("taskPlanPreviewAck")?.checked);
  return {
    sourceProvider,
    targetProvider,
    targetProfileId,
    targetParentId,
    thresholdMB: Number(thresholdRaw || 0) || 0,
    conflictPolicy,
    acknowledgePendingManual: ackChecked,
    acknowledgeDownloadUpload: ackChecked,
    selectedRoots: [sourcePath],
    entries: [
      {
        path: sourcePath,
        size: Number(sizeRaw || 0) || 0,
        md5,
        localPath,
      },
    ],
  };
}

async function previewTaskPlan() {
  setTaskCreateGuard("");
  resetTaskPlanAck();
  const plan = await fetchTaskPlanPreview();
  state.taskPlanPreview = plan;
  renderTaskPlanPreview();
}

async function fetchTaskPlanPreview() {
  const body = collectTaskFormPayload();
  return fetchJson("/api/plan/mock", {
    method: "POST",
    body: JSON.stringify({
      sourceProvider: body.sourceProvider,
      targetProvider: body.targetProvider,
      thresholdMB: body.thresholdMB,
      conflictPolicy: body.conflictPolicy,
      selectedRoots: body.selectedRoots,
      entries: body.entries,
    }),
  });
}

async function createTaskFromForm() {
  setTaskCreateGuard("");
  const plan = await fetchTaskPlanPreview();
  state.taskPlanPreview = plan;
  renderTaskPlanPreview();
  const counts = plan?.summary?.strategyCounts || {};
  const targetProfile = selectedTaskTargetProfile();
  if (targetProfile && targetProfile.writeReady === false) {
    const message = `Task creation blocked: target profile ${targetProfile.displayName || targetProfile.profileId} is not write-ready yet. ${(targetProfile.writeMissingFieldHints || []).join(" | ") || "(unknown)"}${targetProfile.writeBlockerNote ? ` | ${targetProfile.writeBlockerNote}` : ""}`;
    setTaskCreateGuard(message);
    return;
  }
  const unsupportedItem = (plan.items || []).find((item) => item.conflictSupportStatus === "unsupported");
  if (unsupportedItem) {
    const message = `Task creation blocked: ${unsupportedItem.path} is using ${plan.conflictPolicy || "auto_rename_new"} on a target path that is not currently guaranteed. ${unsupportedItem.conflictNote || "Review the provider note before running."}`;
    setTaskCreateGuard(message);
    return;
  }
  const ack = document.getElementById("taskPlanPreviewAck");
  if (((counts.pending_manual || 0) > 0 || (counts.download_upload || 0) > 0) && !ack?.checked) {
    setTaskCreateGuard("Task creation requires confirmation: this plan still contains pending_manual or download_upload items. Review the preview and tick the acknowledgement checkbox before continuing.");
    return;
  }
  const body = collectTaskFormPayload();
  await fetchJson("/api/tasks", { method: "POST", body: JSON.stringify(body) });
  state.taskPlanPreview = null;
  setTaskCreateGuard("");
  resetTaskPlanAck();
  await loadTasks();
}

async function taskAction(taskId, action) {
  await fetchJson(`/api/tasks/${taskId}/action`, {
    method: "POST",
    body: JSON.stringify({ action }),
  });
  await loadTasks();
}

function renderProviderPanel() {
  const summaryWrap = document.getElementById("providerMatrixSummary");
  const matrixList = document.getElementById("providerMatrixList");
  const researchList = document.getElementById("providerResearchList");
  summaryWrap.innerHTML = "";
  matrixList.innerHTML = "";
  researchList.innerHTML = "";

  if (state.statusMatrix?.summary) {
    const cards = [
      { label: t("summary.providers"), value: state.statusMatrix.summary.providerCount || 0 },
      { label: "authReady", value: state.statusMatrix.summary.authReadyCount || 0 },
      { label: "createDir", value: state.statusMatrix.summary.createDirReadyCount || 0 },
      { label: "fastCheck", value: state.statusMatrix.summary.fastCheckCount || 0 },
      { label: "conflictAware", value: state.statusMatrix.summary.conflictAwareProviderCount || 0 },
      { label: "autoRenameProbeOnly", value: state.statusMatrix.summary.autoRenameProbeOnlyCount || 0 },
      { label: "conflictUnsupported", value: state.statusMatrix.summary.conflictUnsupportedProviderCount || 0 },
      { label: "runtimeBlocked", value: state.statusMatrix.summary.taskRuntimeBlockedEvidenceCount || 0 },
      { label: "runtimeConflictHandled", value: state.statusMatrix.summary.taskRuntimeConflictHandledCount || 0 },
      { label: "runtime", value: state.statusMatrix.summary.taskRuntimeSampleCount || 0 },
    ];
    for (const card of cards) {
      const node = document.createElement("div");
      node.className = "summary-card compact";
      const value = document.createElement("strong");
      value.textContent = String(card.value);
      const label = document.createElement("span");
      label.textContent = card.label;
      node.appendChild(value);
      node.appendChild(label);
      summaryWrap.appendChild(node);
    }
  }

  for (const item of state.statusMatrix?.items || []) {
    const node = document.createElement("li");
    node.className = "auth-item";
    const title = document.createElement("div");
    title.textContent = `${item.displayName} [${item.providerKey}]`;
    const meta = document.createElement("div");
    meta.className = "auth-item-meta";
    meta.textContent = `support=${item.supportStatus}, auth=${item.auth_ready}, list=${item.list_ready}, metadata=${item.metadata_ready}, create_dir=${item.create_dir_ready}, fast_check=${item.fast_check}`;
    const conflict = document.createElement("div");
    conflict.className = "auth-item-meta";
    const policyText = (item.conflictPolicies || []).join(", ") || "(none)";
    conflict.textContent = `conflictPolicies=${policyText}, overwrite=${item.supportsOverwrite}, autoRename=${item.supportsAutoRename}, overwriteBehavior=${item.overwriteBehavior || "not_implemented"}, overwriteSupport=${item.overwrite_support_status || "unknown"}, autoRenameSupport=${item.auto_rename_support_status || "unknown"}`;
    const runtimeTrack = document.createElement("div");
    runtimeTrack.className = "auth-item-meta";
    runtimeTrack.textContent = `task_runtime_track=${item.task_runtime_track || "runtime_planned"}, blocked=${item.task_runtime_blocked || 0}, conflictHandled=${item.task_runtime_conflict_handled || 0}${item.task_runtime_track_note ? `, note=${item.task_runtime_track_note}` : ""}`;
    node.appendChild(title);
    node.appendChild(meta);
    node.appendChild(conflict);
    node.appendChild(runtimeTrack);
    const realEvidence = realEvidenceByProvider(item.providerKey);
    if (realEvidence) {
      const evidenceMeta = document.createElement("div");
      evidenceMeta.className = "auth-item-meta";
      evidenceMeta.textContent = `real_evidence auth=${Boolean(realEvidence.authEvidence?.ok)}, list=${Boolean(realEvidence.listEvidence?.ok)}, metadata=${Boolean(realEvidence.metadataEvidence?.ok)}, create_dir=${Boolean(realEvidence.createDirEvidence?.ok)}, task_runtime=${Boolean(realEvidence.taskRuntimeEvidence?.ok)}(${realEvidence.taskRuntimeEvidence?.successCount || 0}/${realEvidence.taskRuntimeEvidence?.failedCount || 0}, candidate=${realEvidence.taskRuntimeEvidence?.candidateCount || 0}, probe=${realEvidence.taskRuntimeEvidence?.probeCount || 0}, blocked=${realEvidence.taskRuntimeEvidence?.blockedCount || 0}, conflict=${realEvidence.taskRuntimeEvidence?.conflictHandledCount || 0}), fully_verified=${Boolean(realEvidence.fullyVerified)}`;
      node.appendChild(evidenceMeta);
      if ((realEvidence.gaps || []).length) {
        const evidenceGaps = document.createElement("div");
        evidenceGaps.className = "auth-item-meta";
        evidenceGaps.textContent = `real_evidence_gaps=${(realEvidence.gaps || []).join(" | ")}`;
        node.appendChild(evidenceGaps);
      }
    }
    if (item.conflictNotes) {
      const notes = document.createElement("div");
      notes.className = "auth-item-meta";
      notes.textContent = item.conflictNotes;
      node.appendChild(notes);
    }
    matrixList.appendChild(node);
  }

  for (const item of state.providerResearch) {
    const node = document.createElement("li");
    node.className = "auth-item";
    const title = document.createElement("div");
    title.textContent = `${item.displayName} [${item.providerKey}]`;
    const meta = document.createElement("div");
    meta.className = "auth-item-meta";
    meta.textContent = `status=${item.status}, authModes=${(item.authModes || []).join(", ") || "(none)"}`;
    const notes = document.createElement("div");
    notes.className = "auth-item-meta";
    notes.textContent = item.notes || "";
    const realEvidence = realEvidenceByProvider(item.providerKey);
    if (realEvidence) {
      const evidenceMeta = document.createElement("div");
      evidenceMeta.className = "auth-item-meta";
      evidenceMeta.textContent = `real_evidence auth=${Boolean(realEvidence.authEvidence?.ok)}, list=${Boolean(realEvidence.listEvidence?.ok)}, metadata=${Boolean(realEvidence.metadataEvidence?.ok)}, create_dir=${Boolean(realEvidence.createDirEvidence?.ok)}, task_runtime=${Boolean(realEvidence.taskRuntimeEvidence?.ok)}(${realEvidence.taskRuntimeEvidence?.successCount || 0}/${realEvidence.taskRuntimeEvidence?.failedCount || 0}, candidate=${realEvidence.taskRuntimeEvidence?.candidateCount || 0}, probe=${realEvidence.taskRuntimeEvidence?.probeCount || 0}, blocked=${realEvidence.taskRuntimeEvidence?.blockedCount || 0}, conflict=${realEvidence.taskRuntimeEvidence?.conflictHandledCount || 0}), fully_verified=${Boolean(realEvidence.fullyVerified)}`;
      node.appendChild(title);
      node.appendChild(meta);
      node.appendChild(notes);
      node.appendChild(evidenceMeta);
      if ((realEvidence.gaps || []).length) {
        const evidenceGaps = document.createElement("div");
        evidenceGaps.className = "auth-item-meta";
        evidenceGaps.textContent = `real_evidence_gaps=${(realEvidence.gaps || []).join(" | ")}`;
        node.appendChild(evidenceGaps);
      }
      const matchedProfile = state.authProfiles.find((profile) => profile.providerKey === item.providerKey);
      if (matchedProfile && state.providerLiveProbes[matchedProfile.profileId]) {
        const probe = state.providerLiveProbes[matchedProfile.profileId];
        const probeNode = document.createElement("div");
        probeNode.className = "auth-item-meta";
        probeNode.textContent = `live_probe=${probe.mode}, ok=${probe.ok}, checks=${(probe.checks || []).length}`;
        node.appendChild(probeNode);
      }
      researchList.appendChild(node);
      continue;
    }
    const matchedProfile = state.authProfiles.find((profile) => profile.providerKey === item.providerKey);
    if (matchedProfile && state.providerLiveProbes[matchedProfile.profileId]) {
      const probe = state.providerLiveProbes[matchedProfile.profileId];
      const probeNode = document.createElement("div");
      probeNode.className = "auth-item-meta";
      probeNode.textContent = `live_probe=${probe.mode}, ok=${probe.ok}, checks=${(probe.checks || []).length}`;
      node.appendChild(title);
      node.appendChild(meta);
      node.appendChild(notes);
      node.appendChild(probeNode);
      researchList.appendChild(node);
      continue;
    }
    node.appendChild(title);
    node.appendChild(meta);
    node.appendChild(notes);
    researchList.appendChild(node);
  }
}

function renderSettingsPanel() {
  const sessionList = document.getElementById("settingsSessionList");
  const validationList = document.getElementById("settingsValidationList");
  const providerProbeList = document.getElementById("settingsProviderProbeList");
  const providerStatusList = document.getElementById("settingsProviderStatusList");
  const realEvidenceList = document.getElementById("settingsRealEvidenceList");
  const realEvidenceRemediationList = document.getElementById("settingsRealEvidenceRemediationList");
  const taskRuntimeEvidenceList = document.getElementById("settingsTaskRuntimeEvidenceList");
  const auditList = document.getElementById("settingsAuditList");
  sessionList.innerHTML = "";
  validationList.innerHTML = "";
  providerProbeList.innerHTML = "";
  providerStatusList.innerHTML = "";
  realEvidenceList.innerHTML = "";
  realEvidenceRemediationList.innerHTML = "";
  taskRuntimeEvidenceList.innerHTML = "";
  auditList.innerHTML = "";

  const sessionRows = [
    `${t("settings.session")}: ${state.loggedIn ? t("settings.logged_in") : t("settings.logged_out")}`,
    `${t("summary.auth_profiles")}: ${state.authProfiles.length}`,
    `${t("summary.tasks")}: ${state.tasks.length}`,
  ];
  for (const row of sessionRows) {
    const li = document.createElement("li");
    li.textContent = row;
    sessionList.appendChild(li);
  }

  const latestValidationRows = {};
  for (const row of state.liveValidations) {
    if (row && row.profileId) {
      latestValidationRows[row.profileId] = row;
    }
  }
  const latestValidationList = Object.values(latestValidationRows);
  const validationSummary = state.liveValidationMeta?.summary || {};
  const validationRows = [
    `${t("settings.validation")}: history=${state.liveValidationMeta?.historyCount || 0}, latestProfiles=${validationSummary.profileCount || latestValidationList.length}`,
    `latestOk=${validationSummary.okCount || 0}, latestFailed=${validationSummary.failedCount || 0}`,
    `okProfiles=${(validationSummary.okProfiles || []).join("/") || "(none)"}, failedProfiles=${(validationSummary.failedProfiles || []).join("/") || "(none)"}, okProviders=${(validationSummary.okProviderKeys || []).join("/") || "(none)"}, failedProviders=${(validationSummary.failedProviderKeys || []).join("/") || "(none)"}, failedModes=${(validationSummary.failedModes || []).join("/") || "(none)"}`,
  ];
  const latestValidation = latestValidationList[latestValidationList.length - 1];
  if (latestValidation) {
    validationRows.push(
      `latest=${latestValidation.providerKey}, ok=${latestValidation.ok}, status=${latestValidation.status}`
    );
  }
  for (const row of validationRows) {
    const li = document.createElement("li");
    li.textContent = row;
    validationList.appendChild(li);
  }

  const probeRows = Object.values(state.providerLiveProbes || {});
  const probeSummary = state.providerLiveProbeMeta?.summary || {};
  if (!probeRows.length) {
    const li = document.createElement("li");
    li.textContent = "none";
    providerProbeList.appendChild(li);
  } else {
    const summaryLi = document.createElement("li");
    summaryLi.textContent = `history=${state.providerLiveProbeMeta?.historyCount || 0}, latestProfiles=${probeSummary.profileCount || probeRows.length}, latestOk=${probeSummary.okCount || 0}, latestFailed=${probeSummary.failedCount || 0}`;
    providerProbeList.appendChild(summaryLi);
    const profileLi = document.createElement("li");
    profileLi.textContent = `okProfiles=${(probeSummary.okProfiles || []).join("/") || "(none)"}, failedProfiles=${(probeSummary.failedProfiles || []).join("/") || "(none)"}, okProviders=${(probeSummary.okProviderKeys || []).join("/") || "(none)"}, failedProviders=${(probeSummary.failedProviderKeys || []).join("/") || "(none)"}, failedModes=${(probeSummary.failedModes || []).join("/") || "(none)"}, providers=${(probeSummary.providerKeys || []).join("/") || "(none)"}`;
    providerProbeList.appendChild(profileLi);
    for (const probe of probeRows) {
      const li = document.createElement("li");
      li.textContent = `${probe.providerKey || "(unknown)"}: ok=${probe.ok}, mode=${probe.mode}, checks=${(probe.checks || []).length}`;
      providerProbeList.appendChild(li);
    }
  }

  const providerStatusSummary = state.statusMatrix?.summary || {};
  const providerStatusRows = [
    `providers=${providerStatusSummary.providerCount || 0}, authReady=${providerStatusSummary.authReadyCount || 0}, createDir=${providerStatusSummary.createDirReadyCount || 0}, fastCheck=${providerStatusSummary.fastCheckCount || 0}, liveProbeOk=${providerStatusSummary.liveProbeOkCount || 0}`,
    `conflictAware=${providerStatusSummary.conflictAwareProviderCount || 0}, overwriteReady=${providerStatusSummary.overwriteReadyCount || 0}, autoRenameReady=${providerStatusSummary.autoRenameReadyCount || 0}, overwriteDowngrade=${providerStatusSummary.overwriteDowngradeCount || 0}, overwriteSupported=${providerStatusSummary.overwriteSupportedCount || 0}, autoRenameSupported=${providerStatusSummary.autoRenameSupportedCount || 0}`,
    `autoRenameProbeOnly=${providerStatusSummary.autoRenameProbeOnlyCount || 0}, conflictUnsupported=${providerStatusSummary.conflictUnsupportedProviderCount || 0}`,
    `runtimeEvidenceProviders=${providerStatusSummary.taskRuntimeEvidenceProviderCount || 0}, runtimeFailedProviders=${providerStatusSummary.taskRuntimeFailedProviderCount || 0}, runtimeCandidateProviders=${providerStatusSummary.taskRuntimeCandidateEvidenceProviderCount || 0}, runtimeProbeProviders=${providerStatusSummary.taskRuntimeProbeEvidenceProviderCount || 0}, runtime=${providerStatusSummary.taskRuntimeSampleCount || 0}, runtimeSuccess=${providerStatusSummary.taskRuntimeSuccessCount || 0}, runtimeFailed=${providerStatusSummary.taskRuntimeFailedCount || 0}, runtimeCandidate=${providerStatusSummary.taskRuntimeCandidateEvidenceCount || 0}, runtimeProbe=${providerStatusSummary.taskRuntimeProbeEvidenceCount || 0}, runtimeBlockedProviders=${providerStatusSummary.taskRuntimeBlockedProviderCount || 0}, runtimeBlocked=${providerStatusSummary.taskRuntimeBlockedEvidenceCount || 0}, runtimeConflictHandledProviders=${providerStatusSummary.taskRuntimeConflictHandledProviderCount || 0}, runtimeConflictHandled=${providerStatusSummary.taskRuntimeConflictHandledCount || 0}`,
    `runtimeActive=${providerStatusSummary.taskRuntimeActiveCount || 0}, runtimeCandidate=${providerStatusSummary.taskRuntimeCandidateCount || 0}, runtimeTrackBlocked=${providerStatusSummary.taskRuntimeBlockedCount || 0}`,
    `authReadyProviders=${(providerStatusSummary.authReadyProviders || []).join("/") || "(none)"}, createDirProviders=${(providerStatusSummary.createDirReadyProviders || []).join("/") || "(none)"}, fastCheckProviders=${(providerStatusSummary.fastCheckProviders || []).join("/") || "(none)"}, liveProbeOkProviders=${(providerStatusSummary.liveProbeOkProviders || []).join("/") || "(none)"}`,
    `overwriteDowngradeProviders=${(providerStatusSummary.overwriteDowngradeProviders || []).join("/") || "(none)"}, overwriteSupportedProviders=${(providerStatusSummary.overwriteSupportedProviders || []).join("/") || "(none)"}, autoRenameSupportedProviders=${(providerStatusSummary.autoRenameSupportedProviders || []).join("/") || "(none)"}, autoRenameProbeOnlyProviders=${(providerStatusSummary.autoRenameProbeOnlyProviders || []).join("/") || "(none)"}, conflictUnsupportedProviders=${(providerStatusSummary.conflictUnsupportedProviders || []).join("/") || "(none)"}`,
    `runtimeSuccessProviders=${(providerStatusSummary.taskRuntimeSuccessProviders || []).join("/") || "(none)"}, runtimeFailedProvidersList=${(providerStatusSummary.taskRuntimeFailedProviders || []).join("/") || "(none)"}, runtimeCandidateProvidersList=${(providerStatusSummary.taskRuntimeCandidateProviders || []).join("/") || "(none)"}, runtimeProbeProvidersList=${(providerStatusSummary.taskRuntimeProbeProviders || []).join("/") || "(none)"}, runtimeBlockedProvidersList=${(providerStatusSummary.taskRuntimeBlockedProviders || []).join("/") || "(none)"}, runtimeConflictHandledProvidersList=${(providerStatusSummary.taskRuntimeConflictHandledProviders || []).join("/") || "(none)"}`,
  ];
  for (const row of providerStatusRows) {
    const li = document.createElement("li");
    li.textContent = row;
    providerStatusList.appendChild(li);
  }

  const realEvidence = state.realEvidenceSummary || {};
  const realEvidenceRows = [
    `providers=${realEvidence.providerCount || 0}, profilesSaved=${realEvidence.profilesSaved || 0}, latestValidationProfiles=${realEvidence.latestValidationProfileCount || 0}, latestProbeProfiles=${realEvidence.latestProbeProfileCount || 0}`,
    `auth=${realEvidence.authEvidenceProviderCount || 0}, list=${realEvidence.listEvidenceProviderCount || 0}, metadata=${realEvidence.metadataEvidenceProviderCount || 0}`,
    `create_dir=${realEvidence.createDirEvidenceProviderCount || 0}, task_runtime=${realEvidence.taskRuntimeEvidenceProviderCount || 0}, task_runtime_failed=${realEvidence.taskRuntimeFailedProviderCount || 0}, task_runtime_candidate=${realEvidence.taskRuntimeCandidateProviderCount || 0}, task_runtime_probe=${realEvidence.taskRuntimeProbeProviderCount || 0}, fully_verified=${realEvidence.fullyVerifiedProviderCount || 0}`,
    `runtime_samples=${realEvidence.taskRuntimeSampleCount || 0}, runtime_success=${realEvidence.taskRuntimeSuccessCount || 0}, runtime_failed=${realEvidence.taskRuntimeFailedCount || 0}, runtime_candidate=${realEvidence.taskRuntimeCandidateCount || 0}, runtime_probe=${realEvidence.taskRuntimeProbeCount || 0}, runtime_blocked_providers=${realEvidence.taskRuntimeBlockedProviderCount || 0}, runtime_blocked=${realEvidence.taskRuntimeBlockedCount || 0}, runtime_conflict_handled=${realEvidence.taskRuntimeConflictHandledCount || 0}`,
    `authProviders=${(realEvidence.authEvidenceProviders || []).join("/") || "(none)"}, listProviders=${(realEvidence.listEvidenceProviders || []).join("/") || "(none)"}, metadataProviders=${(realEvidence.metadataEvidenceProviders || []).join("/") || "(none)"}, createDirProviders=${(realEvidence.createDirEvidenceProviders || []).join("/") || "(none)"}, fullyVerifiedProviders=${(realEvidence.fullyVerifiedProviders || []).join("/") || "(none)"}`,
    `runtimeSuccessProviders=${(realEvidence.taskRuntimeEvidenceProviders || []).join("/") || "(none)"}, runtimeFailedProvidersList=${(realEvidence.taskRuntimeFailedProviders || []).join("/") || "(none)"}, runtimeCandidateProvidersList=${(realEvidence.taskRuntimeCandidateProviders || []).join("/") || "(none)"}, runtimeProbeProvidersList=${(realEvidence.taskRuntimeProbeProviders || []).join("/") || "(none)"}, runtimeBlockedProvidersList=${(realEvidence.taskRuntimeBlockedProviders || []).join("/") || "(none)"}`,
  ];
  for (const row of realEvidenceRows) {
    const li = document.createElement("li");
    li.textContent = row;
    realEvidenceList.appendChild(li);
  }

  const remediationSummary = state.realEvidenceRemediation?.summary || {};
  const remediationItems = state.realEvidenceRemediation?.items || [];
  const remediationRows = [
    `providers=${remediationSummary.providerCount || 0}, noProfiles=${remediationSummary.providersWithNoProfiles || 0}, createCommands=${remediationSummary.providersWithCreateCommand || 0}, bootstrapCommands=${remediationSummary.providersWithBootstrapCommand || 0}, patchCommands=${remediationSummary.providersWithPatchCommand || 0}, patchProbeCommands=${remediationSummary.providersWithPatchProbeCommand || 0}, recreateProbeCommands=${remediationSummary.providersWithRecreateProbeCommand || 0}, refreshEvidenceCommands=${remediationSummary.providersWithRefreshEvidenceCommand || 0}, postRefreshRuntimeCommands=${remediationSummary.providersWithPostRefreshRuntimeCommand || 0}, runtimeProbeCommands=${remediationSummary.providersWithRuntimeProbeCommand || 0}, liveUploadCommands=${remediationSummary.providersWithLiveUploadCommand || 0}, fastCandidateCommands=${remediationSummary.providersWithFastCandidateCommand || 0}, runtimeSuccessCommands=${remediationSummary.providersWithRuntimeSuccessCommand || 0}, postBootstrapRuntimeCommands=${remediationSummary.providersWithPostBootstrapRuntimeCommand || 0}, primaryCommands=${remediationSummary.providersWithPrimaryCommand || 0}, overwriteVariantCommands=${remediationSummary.providersWithOverwriteVariantCommand || 0}, conflictPolicyNotes=${remediationSummary.providersWithConflictPolicyNote || 0}, declaredConflictPolicies=${remediationSummary.providersWithDeclaredConflictPolicies || 0}, directOverwrite=${remediationSummary.providersWithProviderManagedOverwrite || 0}, overwriteDowngrade=${remediationSummary.providersWithOverwriteDowngrade || 0}, conflictUnsupported=${remediationSummary.providersWithConflictUnsupported || 0}, blockedOnly=${remediationSummary.providersBlockedOnly || 0}, candidateOnly=${remediationSummary.providersCandidateOnly || 0}, probeOnly=${remediationSummary.providersProbeOnly || 0}`,
    `needAuth=${remediationSummary.providersNeedingAuthEvidence || 0}, needList=${remediationSummary.providersNeedingListEvidence || 0}, needMetadata=${remediationSummary.providersNeedingMetadataEvidence || 0}, needCreateDir=${remediationSummary.providersNeedingCreateDirEvidence || 0}, needRuntime=${remediationSummary.providersNeedingRuntimeSuccess || 0}`,
    `noProfilesProviders=${(remediationSummary.providersWithNoProfilesList || []).join("/") || "(none)"}, needAuthProviders=${(remediationSummary.providersNeedingAuthEvidenceList || []).join("/") || "(none)"}, needRuntimeProviders=${(remediationSummary.providersNeedingRuntimeSuccessList || []).join("/") || "(none)"}, recreateProbeProviders=${(remediationSummary.providersWithRecreateProbeCommandList || []).join("/") || "(none)"}, primaryCommandProviders=${(remediationSummary.providersWithPrimaryCommandList || []).join("/") || "(none)"}, overwriteVariantProviders=${(remediationSummary.providersWithOverwriteVariantCommandList || []).join("/") || "(none)"}`,
    `blockedOnlyProviders=${(remediationSummary.providersBlockedOnlyList || []).join("/") || "(none)"}, candidateOnlyProviders=${(remediationSummary.providersCandidateOnlyList || []).join("/") || "(none)"}, probeOnlyProviders=${(remediationSummary.providersProbeOnlyList || []).join("/") || "(none)"}`,
  ];
  for (const row of remediationRows) {
    const li = document.createElement("li");
    li.textContent = row;
    realEvidenceRemediationList.appendChild(li);
  }
  for (const item of remediationItems.filter((row) => row.nextStep).slice(0, 3)) {
    const li = document.createElement("li");
    const authModes = (item.recommendedAuthModes || []).join("/") || "(none)";
    const loginUrl = item.webLoginUrl || item.officialDocsUrl || "";
    const fieldHints = (item.requiredFieldHints || []).slice(0, 2).join(" | ");
    const placeholderSecretHints = (item.placeholderSecretFieldHints || []).join("/") || "";
    li.textContent = `${item.providerKey || "(unknown)"}: profiles=${item.profileCount || 0}, authModes=${authModes}, nextStep=${item.nextStep}, blockedOnly=${Boolean(item.runtimeBlockedOnly)}, candidateOnly=${Boolean(item.runtimeCandidateOnly)}, probeOnly=${Boolean(item.runtimeProbeOnly)}, needsSecretRefresh=${Boolean(item.needsSecretRefresh)}, conflictDeclared=${(item.declaredConflictPolicies || []).join("/") || "(none)"}, overwriteSupport=${item.overwriteSupportStatus || "unknown"}, autoRenameSupport=${item.autoRenameSupportStatus || "unknown"}, overwriteBehavior=${item.overwriteBehavior || "unknown"}${loginUrl ? `, login=${loginUrl}` : ""}${fieldHints ? `, hints=${fieldHints}` : ""}${placeholderSecretHints ? `, placeholderSecretHints=${placeholderSecretHints}` : ""}${item.providerConflictNotes ? `, providerConflictNotes=${item.providerConflictNotes}` : ""}${item.recommendedPrimaryCommand ? `, primary=${item.recommendedPrimaryCommand}` : ""}${item.recommendedPrimaryCommandLabel ? `, primaryLabel=${item.recommendedPrimaryCommandLabel}` : ""}${item.recommendedCreateCommand ? `, create=${item.recommendedCreateCommand}` : ""}${item.recommendedBootstrapCommand ? `, bootstrap=${item.recommendedBootstrapCommand}` : ""}${item.recommendedPatchCommand ? `, patch=${item.recommendedPatchCommand}` : ""}${item.recommendedPatchProbeCommand ? `, patchProbe=${item.recommendedPatchProbeCommand}` : ""}${item.recommendedRecreateProbeCommand ? `, recreateProbe=${item.recommendedRecreateProbeCommand}` : ""}${item.recommendedRefreshEvidenceCommand ? `, refresh=${item.recommendedRefreshEvidenceCommand}` : ""}${item.recommendedPostRefreshRuntimeCommand ? `, postRefreshRuntime=${item.recommendedPostRefreshRuntimeCommand}` : ""}${item.recommendedRuntimeProbeCommand ? `, runtime=${item.recommendedRuntimeProbeCommand}` : ""}${item.recommendedLiveUploadCommand ? `, liveUpload=${item.recommendedLiveUploadCommand}` : ""}${item.recommendedFastCandidateCommand ? `, fastCandidate=${item.recommendedFastCandidateCommand}` : ""}${item.recommendedRuntimeSuccessCommand ? `, runtimeSuccess=${item.recommendedRuntimeSuccessCommand}` : ""}${item.recommendedPostBootstrapRuntimeCommand ? `, postBootstrapRuntime=${item.recommendedPostBootstrapRuntimeCommand}` : ""}${item.recommendedOverwriteVariantCommand ? `, overwriteVariant=${item.recommendedOverwriteVariantCommand}` : ""}${item.conflictPolicyNote ? `, conflictPolicyNote=${item.conflictPolicyNote}` : ""}`;
    realEvidenceRemediationList.appendChild(li);
  }

  const runtimeEvidenceSummary = state.taskRuntimeEvidenceMeta?.summary || {};
  const runtimeEvidenceRows = [
    `history=${state.taskRuntimeEvidenceMeta?.historyCount || 0}, latestSamples=${runtimeEvidenceSummary.sampleCount || 0}`,
    `providers=${runtimeEvidenceSummary.providerCount || 0}, profiles=${runtimeEvidenceSummary.profileCount || 0}, successProviders=${runtimeEvidenceSummary.successProviderCount || 0}, failedProviders=${runtimeEvidenceSummary.failedProviderCount || 0}, candidateProviders=${runtimeEvidenceSummary.candidateProviderCount || 0}, probeProviders=${runtimeEvidenceSummary.probeProviderCount || 0}, blockedProviders=${runtimeEvidenceSummary.blockedProviderCount || 0}, success=${runtimeEvidenceSummary.successCount || 0}, failed=${runtimeEvidenceSummary.failedCount || 0}, candidate=${runtimeEvidenceSummary.candidateCount || 0}, probe=${runtimeEvidenceSummary.probeCount || 0}, blocked=${runtimeEvidenceSummary.blockedCount || 0}, verifyOk=${runtimeEvidenceSummary.verifyOkCount || 0}`,
    `conflictHandledProviders=${runtimeEvidenceSummary.conflictHandledProviderCount || 0}, conflictHandled=${runtimeEvidenceSummary.conflictHandledCount || 0}`,
    `successProfiles=${(runtimeEvidenceSummary.successProfiles || []).join("/") || "(none)"}, failedProfiles=${(runtimeEvidenceSummary.failedProfiles || []).join("/") || "(none)"}, candidateProfiles=${(runtimeEvidenceSummary.candidateProfiles || []).join("/") || "(none)"}, probeProfiles=${(runtimeEvidenceSummary.probeProfiles || []).join("/") || "(none)"}, blockedProfiles=${(runtimeEvidenceSummary.blockedProfiles || []).join("/") || "(none)"}, conflictHandledProfiles=${(runtimeEvidenceSummary.conflictHandledProfiles || []).join("/") || "(none)"}`,
  ];
  for (const row of runtimeEvidenceRows) {
    const li = document.createElement("li");
    li.textContent = row;
    taskRuntimeEvidenceList.appendChild(li);
  }
  for (const item of (state.taskRuntimeEvidence || []).slice(0, 3)) {
    const li = document.createElement("li");
    li.textContent = `${item.providerKey || "(unknown)"}: path=${item.path || "(unknown)"}, mode=${item.mode || ""}, executionMode=${item.executionMode || ""}, success=${Boolean(item.success)}, candidateOnly=${Boolean(item.candidateOnly)}, probeOnly=${Boolean(item.probeOnly)}, verifyOk=${Boolean(item.verifyOk)}, verifyMode=${item.verifyMode || "(none)"}, conflict=${item.conflictAction || "(none)"}, resolvedTargetName=${item.resolvedTargetName || "(none)"}, riskHint=${item.riskHint || "(none)"}, requiredAuth=${(item.requiredAuth || []).join("/") || "(none)"}, error=${item.error || "(none)"}`;
    taskRuntimeEvidenceList.appendChild(li);
  }

  const audit = state.auditSummary || {};
  const auditRows = [
    `done=${audit.done || 0}`,
    `partial=${audit.partial || 0}`,
    `todo=${audit.todo || 0}`,
    `featureCompletionPercent=${audit.featureCompletionPercent || 0}`,
    `strictCompletionPercent=${audit.strictCompletionPercent || 0}`,
    `providerCount=${audit.providerCount || 0}`,
    `researchCount=${audit.researchCount || 0}`,
  ];
  for (const row of auditRows) {
    const li = document.createElement("li");
    li.textContent = row;
    auditList.appendChild(li);
  }
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
    await refreshProtectedData();
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
  state.authProfiles = [];
  state.liveValidations = [];
  state.liveValidationMeta = { historyCount: 0, summary: null };
  state.providerLiveProbes = {};
  state.providerLiveProbeMeta = { historyCount: 0, summary: null };
  state.realEvidenceReport = null;
  state.realEvidenceSummary = null;
  state.realEvidenceRemediation = null;
  state.taskRuntimeEvidence = [];
  state.taskRuntimeEvidenceMeta = { historyCount: 0, summary: null };
  state.providerResearch = [];
  state.statusMatrix = null;
  state.auditSummary = null;
  state.tasks = [];
  await refreshSession();
}

async function refreshProtectedData() {
  if (!state.loggedIn) {
    render();
    return;
  }
  await Promise.all([
    loadAuthProfiles(),
    loadProviderResearch(),
    loadStatusMatrix(),
    loadTasks(),
    loadLiveValidations(),
    loadProviderLiveProbeResults(),
    loadRealEvidenceSummary(),
    loadRealEvidenceRemediationSummary(),
    loadTaskRuntimeEvidence(),
    loadAuditSummary(),
  ]);
}

async function bootstrap() {
  const langSelect = document.getElementById("langSelect");
  langSelect.addEventListener("change", async () => {
    await loadI18n(langSelect.value);
  });
  document.getElementById("loginBtn").addEventListener("click", onLogin);
  document.getElementById("logoutBtn").addEventListener("click", onLogout);
  document.getElementById("authSaveBtn").addEventListener("click", saveAuth);
  document.getElementById("authResetBtn").addEventListener("click", onAuthReset);
  document.getElementById("authReloadBtn").addEventListener("click", loadAuthProfiles);
  document.getElementById("authOpenModalBtn").addEventListener("click", openAuthModal);
  document.getElementById("authBundleBtn").addEventListener("click", showAuthEvidenceBundle);
  document.getElementById("authRemediationBtn").addEventListener("click", showAuthRemediationGuide);
  document.getElementById("authStartCaptureBtn").addEventListener("click", startCaptureGuide);
  document.getElementById("authProvider").addEventListener("change", () => {
    syncAuthModeOptions();
    render();
  });
  document.getElementById("taskTargetProvider").addEventListener("change", onTaskTargetProviderChange);
  document.getElementById("taskTargetProfile").addEventListener("change", syncTaskTargetParentFromProfile);
  document.getElementById("taskPreviewBtn").addEventListener("click", previewTaskPlan);
  document.getElementById("taskCreateBtn").addEventListener("click", createTaskFromForm);
  document.getElementById("taskCreateDemoBtn").addEventListener("click", createDemoTask);
  document.getElementById("taskReloadBtn").addEventListener("click", loadTasks);
  await loadI18n("zh-CN");
  await loadProviders();
  await refreshSession();
  await refreshProtectedData();
}

bootstrap().catch((error) => {
  console.error(error);
});

from __future__ import annotations

MESSAGES = {
    "zh-CN": {
        "app.title": "CloudPan Sync",
        "app.subtitle": "常用网盘互传控制台",
        "login.title": "管理员登录",
        "login.password": "管理密码",
        "login.submit": "登录",
        "login.failed": "密码错误，请重试。",
        "nav.new_task": "新建任务",
        "nav.auth": "授权管理",
        "nav.queue": "传输队列",
        "nav.pending": "待处理",
        "nav.providers": "网盘能力",
        "nav.settings": "设置",
        "state.locked": "请先登录后使用完整功能。",
    },
    "en-US": {
        "app.title": "CloudPan Sync",
        "app.subtitle": "Transfer console between mainstream providers",
        "login.title": "Admin Login",
        "login.password": "Admin Password",
        "login.submit": "Sign In",
        "login.failed": "Invalid password. Please try again.",
        "nav.new_task": "New Task",
        "nav.auth": "Auth",
        "nav.queue": "Queue",
        "nav.pending": "Pending",
        "nav.providers": "Providers",
        "nav.settings": "Settings",
        "state.locked": "Please login to unlock full features.",
    },
}


def messages_for(lang: str) -> dict[str, str]:
    return MESSAGES.get(lang, MESSAGES["zh-CN"])

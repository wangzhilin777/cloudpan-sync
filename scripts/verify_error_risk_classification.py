from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloudpan_sync.aliyun_open_upload_live import _classify_upload_issue as classify_aliyun_upload_issue
from cloudpan_sync.guangya_live import _classify_guangya_live_issue
from cloudpan_sync.guangya_upload_live import _classify_upload_issue as classify_guangya_upload_issue


def main() -> None:
    guangya_live_auth = _classify_guangya_live_issue(401, "http_error:401")
    guangya_live_risk = _classify_guangya_live_issue(403, "http_error:403")
    guangya_live_rate = _classify_guangya_live_issue(429, "http_error:429")
    guangya_live_network = _classify_guangya_live_issue(0, "url_error:timeout")
    guangya_live_api_change = _classify_guangya_live_issue(200, "invalid_json")
    guangya_live_unexpected = _classify_guangya_live_issue(0, "unexpected:boom")

    guangya_upload_auth = classify_guangya_upload_issue(401, "http_error:401")
    guangya_upload_risk = classify_guangya_upload_issue(403, "http_error:403")
    guangya_upload_rate = classify_guangya_upload_issue(429, "http_error:429")
    guangya_upload_input = classify_guangya_upload_issue(0, "local_md5_mismatch")

    aliyun_upload_auth = classify_aliyun_upload_issue(401, "http_error:401")
    aliyun_upload_risk = classify_aliyun_upload_issue(403, "http_error:403")
    aliyun_upload_conflict = classify_aliyun_upload_issue(409, "http_error:409")
    aliyun_upload_rate = classify_aliyun_upload_issue(429, "http_error:429")
    aliyun_upload_provider = classify_aliyun_upload_issue(500, "http_error:500")

    print(
        json.dumps(
            {
                "guangyaLiveClassifiesAuthFailure": (
                    guangya_live_auth[0] == "auth"
                    and "授权很可能失效" in guangya_live_auth[1]
                ),
                "guangyaLiveClassifiesRiskFailure": (
                    guangya_live_risk[0] == "risk"
                    and "命中风控" in guangya_live_risk[1]
                ),
                "guangyaLiveClassifiesRateLimit": (
                    guangya_live_rate[0] == "rate_limit"
                    and "降并发" in guangya_live_rate[1]
                ),
                "guangyaLiveClassifiesNetworkFailure": (
                    guangya_live_network[0] == "network"
                    and "检查网络或代理" in guangya_live_network[1]
                ),
                "guangyaLiveClassifiesApiChange": (
                    guangya_live_api_change[0] == "api_change"
                    and "接口结构变化" in guangya_live_api_change[1]
                ),
                "guangyaLiveClassifiesUnexpectedFailure": (
                    guangya_live_unexpected[0] == "unexpected"
                    and "错误文本继续排查" in guangya_live_unexpected[1]
                ),
                "guangyaUploadClassifiesAuthRiskRateAndInput": (
                    guangya_upload_auth[0] == "auth"
                    and guangya_upload_risk[0] == "risk"
                    and guangya_upload_rate[0] == "rate_limit"
                    and guangya_upload_input[0] == "input"
                    and "MD5" in guangya_upload_input[1]
                ),
                "aliyunUploadClassifiesAuthRiskConflictRateAndProvider": (
                    aliyun_upload_auth[0] == "auth"
                    and aliyun_upload_risk[0] == "risk"
                    and aliyun_upload_conflict[0] == "conflict"
                    and "auto_rename_new" in aliyun_upload_conflict[1]
                    and aliyun_upload_rate[0] == "rate_limit"
                    and aliyun_upload_provider[0] == "provider"
                ),
                "errorRiskClassificationFlowMatchesExpectedKinds": (
                    guangya_live_auth[0] == "auth"
                    and "授权很可能失效" in guangya_live_auth[1]
                    and guangya_live_risk[0] == "risk"
                    and "命中风控" in guangya_live_risk[1]
                    and guangya_live_rate[0] == "rate_limit"
                    and "降并发" in guangya_live_rate[1]
                    and guangya_live_network[0] == "network"
                    and "检查网络或代理" in guangya_live_network[1]
                    and guangya_live_api_change[0] == "api_change"
                    and "接口结构变化" in guangya_live_api_change[1]
                    and guangya_live_unexpected[0] == "unexpected"
                    and "错误文本继续排查" in guangya_live_unexpected[1]
                    and guangya_upload_auth[0] == "auth"
                    and guangya_upload_risk[0] == "risk"
                    and guangya_upload_rate[0] == "rate_limit"
                    and guangya_upload_input[0] == "input"
                    and "MD5" in guangya_upload_input[1]
                    and aliyun_upload_auth[0] == "auth"
                    and aliyun_upload_risk[0] == "risk"
                    and aliyun_upload_conflict[0] == "conflict"
                    and "auto_rename_new" in aliyun_upload_conflict[1]
                    and aliyun_upload_rate[0] == "rate_limit"
                    and aliyun_upload_provider[0] == "provider"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

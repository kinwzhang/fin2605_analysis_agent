import httpx
import pytest

from src.config import get_api_key

MINIMAX_BASE_URL = "https://api.minimax.chat/v1"
KIMI_BASE_URL = "https://api.moonshot.cn/v1"


@pytest.fixture(scope="module")
def minimax_api_key() -> str:
    try:
        return get_api_key("minimax")
    except ValueError:
        pytest.skip("MINIMAX_API_KEY not configured")


@pytest.fixture(scope="module")
def kimi_api_key() -> str:
    try:
        return get_api_key("kimi")
    except ValueError:
        pytest.skip("KIMI_API_KEY not configured")


class TestKimiAPI:
    def test_list_models(self, kimi_api_key: str) -> None:
        url = f"{KIMI_BASE_URL}/models"
        headers = {"Authorization": f"Bearer {kimi_api_key}"}

        resp = httpx.get(url, headers=headers, timeout=15)
        assert resp.status_code == 200, f"Got {resp.status_code}: {resp.text}"

        data = resp.json()
        models = [m["id"] for m in data.get("data", [])]
        print(f"
Kimi models ({len(models)}): {models}")

    def test_chat_completion(self, kimi_api_key: str) -> None:
        url = f"{KIMI_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {kimi_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "moonshot-v1-8k",
            "messages": [
                {"role": "user", "content": "Reply with just the word "hello""},
            ],
        }

        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        assert resp.status_code == 200

        data = resp.json()
        print(f"
Response keys: {list(data.keys())}")
        print(f"Content: {data['choices'][0]['message']['content']}")


class TestMiniMaxAPI:
    def test_chat_completion(self, minimax_api_key: str) -> None:
        url = f"{MINIMAX_BASE_URL}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {minimax_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "MiniMax-M2.7",
            "messages": [
                {"role": "user", "content": "Reply with just the word "hello""},
            ],
        }

        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        assert resp.status_code == 200

        data = resp.json()
        print(f"
Response keys: {list(data.keys())}")
        print(f"Content: {data['choices'][0]['message']['content']}")

    def test_list_models_not_available(self, minimax_api_key: str) -> None:
        url = f"{MINIMAX_BASE_URL}/models"
        headers = {"Authorization": f"Bearer {minimax_api_key}"}

        resp = httpx.get(url, headers=headers, timeout=10)
        print(f"
MiniMax /v1/models → {resp.status_code}")
        assert resp.status_code == 404, "MiniMax has no list models API"

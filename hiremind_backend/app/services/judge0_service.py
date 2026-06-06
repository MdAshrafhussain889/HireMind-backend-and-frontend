"""
Judge0 code execution service.

Runs candidate code against assessment test cases and returns aggregated
pass/fail metadata for persistence and AI evaluation.
"""

import logging
from urllib.parse import urlparse

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

LANGUAGE_IDS = {
    "python": 71,
    "python3": 71,
    "java": 62,
    "cpp": 54,
    "c++": 54,
    "c": 50,
    "js": 63,
    "javascript": 63,
    "sql": 82,
}

STATUS_VERDICTS = {
    1: "IN_QUEUE",
    2: "PROCESSING",
    3: "ACCEPTED",
    4: "WRONG_ANSWER",
    5: "TIME_LIMIT_EXCEEDED",
    6: "COMPILATION_ERROR",
    7: "RUNTIME_ERROR",
    8: "RUNTIME_ERROR",
    9: "RUNTIME_ERROR",
    10: "RUNTIME_ERROR",
    11: "RUNTIME_ERROR",
    12: "RUNTIME_ERROR",
    13: "INTERNAL_ERROR",
    14: "EXEC_FORMAT_ERROR",
}


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    parsed = urlparse(settings.judge0_api_url)

    if "rapidapi" in parsed.netloc:
        if not settings.judge0_api_key:
            raise RuntimeError(
                "JUDGE0_API_KEY is required for RapidAPI Judge0. "
                "For free local execution, run: docker compose -f docker-compose.judge0.yml up -d "
                "and set JUDGE0_API_URL=http://127.0.0.1:2358 with JUDGE0_API_KEY empty."
            )
        headers.update({
            "X-RapidAPI-Key": settings.judge0_api_key,
            "X-RapidAPI-Host": parsed.netloc,
        })
    elif settings.judge0_api_key:
        headers["Authorization"] = f"Bearer {settings.judge0_api_key}"

    return headers


def _normalize_output(value: str | None) -> str:
    return (value or "").replace("\r\n", "\n").strip()


def _case_input(test_case: dict) -> str:
    return str(test_case.get("stdin", test_case.get("input", "")))


def _case_expected(test_case: dict) -> str:
    return str(test_case.get("expected_output", test_case.get("output", "")))


def _status_verdict(result: dict) -> str:
    status = result.get("status") or {}
    status_id = status.get("id")
    if status_id in STATUS_VERDICTS:
        return STATUS_VERDICTS[status_id]
    description = status.get("description")
    if description:
        return description.upper().replace(" ", "_")
    return "UNKNOWN"


def _submit_case(
    client: httpx.Client,
    code: str,
    language_id: int,
    stdin: str,
) -> dict:
    url = f"{settings.judge0_api_url.rstrip('/')}/submissions"
    response = client.post(
        url,
        params={"base64_encoded": "false", "wait": "true"},
        json={
            "source_code": code,
            "language_id": language_id,
            "stdin": stdin,
            "cpu_time_limit": 5,
            "memory_limit": 262144,
        },
    )
    response.raise_for_status()
    return response.json()


def run_against_test_cases(
    code: str,
    language: str,
    test_cases: list,
) -> dict:
    """
    Execute code against every test case using Judge0.

    Test cases accept either {input, expected_output} or {stdin, output}.
    """
    language_key = language.lower().strip()
    language_id = LANGUAGE_IDS.get(language_key)
    if not language_id:
        raise ValueError(f"Unsupported language: {language}")

    if not test_cases:
        raise ValueError("At least one test case is required for code execution")

    passed_cases = 0
    failed_cases = []
    total_runtime_ms = 0.0
    max_memory_kb = 0.0
    tokens = []
    overall_verdict = "ACCEPTED"

    logger.info("Judge0 execution started: language=%s cases=%s", language_key, len(test_cases))

    try:
        with httpx.Client(headers=_headers(), timeout=60.0) as client:
            for index, test_case in enumerate(test_cases, start=1):
                stdin = _case_input(test_case)
                expected = _case_expected(test_case)
                result = _submit_case(client, code, language_id, stdin)

                token = result.get("token")
                if token:
                    tokens.append(token)

                runtime_ms = float(result.get("time") or 0) * 1000
                memory_kb = float(result.get("memory") or 0)
                total_runtime_ms += runtime_ms
                max_memory_kb = max(max_memory_kb, memory_kb)

                actual = result.get("stdout") or ""
                case_verdict = _status_verdict(result)
                output_matches = _normalize_output(actual) == _normalize_output(expected)

                if case_verdict == "ACCEPTED" and output_matches:
                    passed_cases += 1
                    continue

                if case_verdict == "ACCEPTED":
                    case_verdict = "WRONG_ANSWER"

                if overall_verdict == "ACCEPTED" or (
                    overall_verdict == "WRONG_ANSWER" and case_verdict != "WRONG_ANSWER"
                ):
                    overall_verdict = case_verdict

                failed_cases.append({
                    "case": index,
                    "input": stdin,
                    "expected_output": expected,
                    "actual_output": actual,
                    "verdict": case_verdict,
                    "stderr": result.get("stderr"),
                    "compile_output": result.get("compile_output"),
                })

    except httpx.HTTPStatusError as e:
        detail = e.response.text[:500] if e.response is not None else str(e)
        raise RuntimeError(f"Judge0 returned HTTP {e.response.status_code}: {detail}") from e
    except httpx.RequestError as e:
        raise RuntimeError(f"Judge0 request failed: {str(e)}") from e

    return {
        "passed_cases": passed_cases,
        "total_cases": len(test_cases),
        "verdict": overall_verdict,
        "runtime_ms": total_runtime_ms,
        "memory_kb": max_memory_kb,
        "failed_cases": failed_cases,
        "token": tokens[-1] if tokens else None,
    }


def supported_languages():
    return list(LANGUAGE_IDS.keys())

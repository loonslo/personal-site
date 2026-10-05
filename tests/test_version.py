"""The build records which commit produced it, so a live site can be traced to its source."""

from __future__ import annotations

import json

import pytest

import build

ENV_NAMES = ("GIT_SHA", "VERCEL_GIT_COMMIT_SHA", "GITHUB_SHA", "BUILD_TIME")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def built_version(tmp_path) -> dict:
    out = build.build(out=tmp_path / "dist")
    return json.loads((out / "version.json").read_text(encoding="utf-8"))


def test_version_json_carries_the_injected_commit_and_time(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_SHA", "abc1234")
    monkeypatch.setenv("BUILD_TIME", "2026-10-05T00:00:00Z")
    assert built_version(tmp_path) == {
        "service": "personal-site",
        "git_sha": "abc1234",
        "build_time": "2026-10-05T00:00:00Z",
    }


def test_the_explicit_variable_wins_over_the_platform_ones(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_SHA", "explicit")
    monkeypatch.setenv("VERCEL_GIT_COMMIT_SHA", "vercel")
    monkeypatch.setenv("GITHUB_SHA", "github")
    assert built_version(tmp_path)["git_sha"] == "explicit"


@pytest.mark.parametrize(("name", "expected"), [("VERCEL_GIT_COMMIT_SHA", "vercel-sha"), ("GITHUB_SHA", "github-sha")])
def test_platform_variables_are_used_when_nothing_explicit_is_set(tmp_path, monkeypatch, name, expected):
    monkeypatch.setenv(name, expected)
    assert built_version(tmp_path)["git_sha"] == expected


def test_a_local_build_says_unknown_instead_of_guessing(tmp_path):
    info = built_version(tmp_path)
    assert info == {"service": "personal-site", "git_sha": "unknown"}

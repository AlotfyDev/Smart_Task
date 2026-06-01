"""Tests for smart_task.config module."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from smart_task.config import (
    DEFAULT_DB_PATH,
    VERIFICATION_PREFIXES,
    SmartTaskConfig,
    load_config,
)


class TestVerificationPrefixes:
    def test_contains_all_expected_keys(self):
        assert set(VERIFICATION_PREFIXES.keys()) == {"SHELL", "PATH", "BDD", "SMOKE", "MANUAL", "MIXED"}

    def test_values_are_strings(self):
        for key, val in VERIFICATION_PREFIXES.items():
            assert isinstance(val, str), f"{key} value is not a string"


class TestDefaultDbPath:
    def test_is_path_object(self):
        assert isinstance(DEFAULT_DB_PATH, Path)

    def test_ends_with_tasks_db(self):
        assert DEFAULT_DB_PATH.name == "tasks.db"

    def test_in_home_smart_task_dir(self):
        assert str(DEFAULT_DB_PATH).endswith(".smart_task\\tasks.db") or str(DEFAULT_DB_PATH).endswith(".smart_task/tasks.db")


class TestSmartTaskConfig:
    def test_default_creation(self):
        config = SmartTaskConfig()
        assert isinstance(config.db_path, Path)
        assert set(config.verification_prefixes.keys()) == {"SHELL", "PATH", "BDD", "SMOKE", "MANUAL", "MIXED"}
        assert config.topics_dir_name == "topic_based_microtasks"
        assert config.mappings_file_name == "topic_to_ticket_mappings.json"

    def test_priority_order_all_keys(self):
        config = SmartTaskConfig()
        assert set(config.priority_order.keys()) == {"Critical", "High", "Medium", "Low"}

    def test_priority_order_values(self):
        config = SmartTaskConfig()
        assert config.priority_order["Critical"] == 4
        assert config.priority_order["High"] == 3
        assert config.priority_order["Medium"] == 2
        assert config.priority_order["Low"] == 1

    def test_post_init_converts_string_db_path(self):
        config = SmartTaskConfig()
        config.db_path = "C:\\temp\\test.db"
        config.__post_init__()
        assert isinstance(config.db_path, Path)
        assert str(config.db_path) == "C:\\temp\\test.db"


class TestLoadConfig:
    def test_load_config_default(self):
        config = load_config()
        assert isinstance(config, SmartTaskConfig)

    def test_load_config_uses_env_var(self, monkeypatch):
        test_path = "C:\\test\\custom\\tasks.db"
        monkeypatch.setenv("SMART_TASK_DB_PATH", test_path)
        config = load_config()
        assert str(config.db_path) == test_path

    def test_load_config_default_when_no_env(self, monkeypatch):
        monkeypatch.delenv("SMART_TASK_DB_PATH", raising=False)
        config = load_config()
        assert config.db_path.name == "tasks.db"

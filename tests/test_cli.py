"""Tests for the CLI interface."""

from __future__ import annotations

import os
import sys
from datetime import date

import pytest

from meal_planner.cli import main


@pytest.fixture()
def db_path(tmp_path):
    return str(tmp_path / "cli_test.db")


class TestCLIGenerate:
    def test_generate_default(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16"])
        out = capsys.readouterr().out
        assert "WEEKLY MEAL PLAN" in out
        assert "SHOPPING LIST" in out

    def test_generate_saves_history(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16", "--save"])
        out = capsys.readouterr().out
        assert "saved to history" in out

    def test_generate_low_cost_mode(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16", "--mode", "low-cost"])
        out = capsys.readouterr().out
        assert "WEEKLY MEAL PLAN" in out

    def test_generate_healthy_mode(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16", "--mode", "healthy"])
        out = capsys.readouterr().out
        assert "WEEKLY MEAL PLAN" in out

    def test_generate_high_protein_mode(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16", "--mode", "high-protein"])
        out = capsys.readouterr().out
        assert "WEEKLY MEAL PLAN" in out

    def test_generate_with_adults_and_children(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16", "--adults", "2", "--children", "2"])
        out = capsys.readouterr().out
        assert "4 people" in out

    def test_generate_vegetarian(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16", "--diet", "vegetarian"])
        out = capsys.readouterr().out
        assert "WEEKLY MEAL PLAN" in out

    def test_generate_with_budget(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16", "--budget", "100"])
        out = capsys.readouterr().out
        assert "WEEKLY MEAL PLAN" in out

    def test_generate_with_max_prep_time(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16", "--max-prep-time", "20"])
        out = capsys.readouterr().out
        assert "WEEKLY MEAL PLAN" in out


class TestCLIPantry:
    def test_pantry_list_empty(self, db_path, capsys):
        main(["--db", db_path, "pantry", "list"])
        out = capsys.readouterr().out
        assert "empty" in out.lower()

    def test_pantry_add_and_list(self, db_path, capsys):
        main(["--db", db_path, "pantry", "add", "eggs", "12", "unit"])
        main(["--db", db_path, "pantry", "list"])
        out = capsys.readouterr().out
        assert "eggs" in out

    def test_pantry_remove(self, db_path, capsys):
        main(["--db", db_path, "pantry", "add", "butter", "0.5", "kg"])
        main(["--db", db_path, "pantry", "remove", "butter"])
        out = capsys.readouterr().out
        assert "Removed" in out

    def test_pantry_clear(self, db_path, capsys):
        main(["--db", db_path, "pantry", "add", "salt", "1", "kg"])
        main(["--db", db_path, "pantry", "clear"])
        out = capsys.readouterr().out
        assert "cleared" in out.lower()


class TestCLIHistory:
    def test_history_list_empty(self, db_path, capsys):
        main(["--db", db_path, "history", "list"])
        out = capsys.readouterr().out
        assert "No meal history" in out

    def test_history_after_generate_save(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16", "--save"])
        capsys.readouterr()  # clear generate output
        main(["--db", db_path, "history", "list", "--limit", "30"])
        out = capsys.readouterr().out
        assert "2026-06-16" in out

    def test_history_rate(self, db_path, capsys):
        main(["--db", db_path, "generate", "--week-start", "2026-06-16", "--save"])
        capsys.readouterr()
        main(["--db", db_path, "history", "rate", "1", "--rating", "5", "--feedback", "Great!"])
        out = capsys.readouterr().out
        assert "Updated feedback" in out

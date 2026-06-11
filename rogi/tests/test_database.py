"""Tests for ROGI database layer."""

from __future__ import annotations

import tempfile
from datetime import date

import pytest

from rogi.database.repository import Repository
from rogi.database.models import (
    DigestModel,
    EmailModel,
    FamilyMemberModel,
    FoodPreferenceModel,
    PantryItemModel,
    ShoppingListModel,
)


@pytest.fixture
def repo() -> Repository:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    r = Repository(db_path=db_path)
    r.connect()
    yield r
    r.close()


class TestPantry:
    def test_upsert_and_get(self, repo: Repository) -> None:
        item = PantryItemModel(name="Milk", quantity=2.0, unit="L")
        repo.upsert_pantry_item(item)
        result = repo.get_pantry_item("Milk")
        assert result is not None
        assert result.quantity == 2.0
        assert result.unit == "L"

    def test_upsert_updates_existing(self, repo: Repository) -> None:
        item = PantryItemModel(name="Rice", quantity=1.0, unit="kg")
        repo.upsert_pantry_item(item)
        item2 = PantryItemModel(name="Rice", quantity=3.5, unit="kg")
        repo.upsert_pantry_item(item2)
        result = repo.get_pantry_item("rice")  # case-insensitive
        assert result is not None
        assert result.quantity == 3.5

    def test_delete(self, repo: Repository) -> None:
        item = PantryItemModel(name="Eggs", quantity=6, unit="unit")
        repo.upsert_pantry_item(item)
        repo.delete_pantry_item("Eggs")
        assert repo.get_pantry_item("Eggs") is None

    def test_get_all(self, repo: Repository) -> None:
        repo.upsert_pantry_item(PantryItemModel(name="A", quantity=1, unit="kg"))
        repo.upsert_pantry_item(PantryItemModel(name="B", quantity=2, unit="L"))
        items = repo.get_pantry()
        assert len(items) == 2

    def test_expiring(self, repo: Repository) -> None:
        from datetime import timedelta

        soon = date.today() + timedelta(days=3)
        far = date.today() + timedelta(days=30)
        repo.upsert_pantry_item(PantryItemModel(name="Soon", quantity=1, unit="unit", expiry_date=soon))
        repo.upsert_pantry_item(PantryItemModel(name="Far", quantity=1, unit="unit", expiry_date=far))
        expiring = repo.get_expiring_pantry(days=7)
        names = [e.name for e in expiring]
        assert "Soon" in names
        assert "Far" not in names


class TestEmails:
    def test_upsert_and_get(self, repo: Repository) -> None:
        email = EmailModel(
            message_id="<test@example.com>",
            account="gmail",
            sender="alice@example.com",
            subject="Invoice #123",
            is_invoice=True,
            category="invoice",
        )
        repo.upsert_email(email)
        emails = repo.get_emails(category="invoice")
        assert len(emails) == 1
        assert emails[0].subject == "Invoice #123"

    def test_get_emails_filter_account(self, repo: Repository) -> None:
        repo.upsert_email(EmailModel(message_id="<a>", account="gmail", sender="x", subject="A"))
        repo.upsert_email(EmailModel(message_id="<b>", account="outlook", sender="y", subject="B"))
        gmail_only = repo.get_emails(account="gmail")
        assert all(e.account == "gmail" for e in gmail_only)


class TestShoppingList:
    def test_save_and_retrieve(self, repo: Repository) -> None:
        sl = ShoppingListModel(
            name="Weekly shop",
            items=[{"name": "Milk", "quantity": 2, "unit": "L", "price": 1.5}],
            total_cost=3.0,
        )
        list_id = repo.save_shopping_list(sl)
        assert list_id > 0
        fetched = repo.get_shopping_list(list_id)
        assert fetched is not None
        assert fetched.name == "Weekly shop"
        assert len(fetched.items) == 1

    def test_update_status(self, repo: Repository) -> None:
        sl = ShoppingListModel(name="Test", items=[], total_cost=0)
        list_id = repo.save_shopping_list(sl)
        repo.update_shopping_status(list_id, "confirmed")
        pending = repo.list_shopping_lists(status="pending")
        assert not any(s.id == list_id for s in pending)
        confirmed = repo.list_shopping_lists(status="confirmed")
        assert any(s.id == list_id for s in confirmed)


class TestMemory:
    def test_food_preference(self, repo: Repository) -> None:
        pref = FoodPreferenceModel(preference_type="dislike", item="broccoli", member="child1")
        repo.add_food_preference(pref)
        prefs = repo.get_food_preferences()
        assert any(p.item == "broccoli" for p in prefs)

    def test_family_member(self, repo: Repository) -> None:
        member = FamilyMemberModel(name="Alice", role="adult", age=35)
        repo.upsert_family_member(member)
        family = repo.get_family()
        assert any(m.name == "Alice" for m in family)

    def test_shopping_habit(self, repo: Repository) -> None:
        repo.set_shopping_habit("preferred_supermarket", "Mercadona")
        assert repo.get_shopping_habit("preferred_supermarket") == "Mercadona"
        repo.set_shopping_habit("preferred_supermarket", "Lidl")
        assert repo.get_shopping_habit("preferred_supermarket") == "Lidl"


class TestDigest:
    def test_save_and_get(self, repo: Repository) -> None:
        today = date.today()
        digest = DigestModel(digest_date=today, content="# Test Digest\nContent here.")
        repo.save_digest(digest)
        fetched = repo.get_digest(today)
        assert fetched is not None
        assert "Content here" in fetched.content

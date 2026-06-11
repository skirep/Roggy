"""Email classification and processing agent."""

from __future__ import annotations

import email as _email_lib
import imaplib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..database.models import EmailModel
from ..database.repository import Repository
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

CLASSIFY_SYSTEM = (
    "You are an email classifier. "
    "Given an email subject and body snippet respond with a JSON object with keys: "
    '"category" (one of: invoice, appointment, important, newsletter, other), '
    '"is_invoice" (boolean), '
    '"is_appointment" (boolean), '
    '"is_important" (boolean), '
    '"summary" (one sentence summary). '
    "Respond ONLY with the JSON object, no extra text."
)


class EmailAgent:
    """Reads, classifies, and stores emails from IMAP accounts."""

    def __init__(self, repo: Repository, ollama: OllamaClient) -> None:
        self._repo = repo
        self._ollama = ollama

    # ------------------------------------------------------------------
    # IMAP ingestion
    # ------------------------------------------------------------------

    def fetch_imap(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        account_label: str,
        mailbox: str = "INBOX",
        max_messages: int = 50,
        use_ssl: bool = True,
    ) -> List[EmailModel]:
        """Connect via IMAP, fetch recent messages, return list of EmailModel."""
        logger.info("Connecting to IMAP %s as %s", host, username)
        try:
            imap_cls = imaplib.IMAP4_SSL if use_ssl else imaplib.IMAP4
            conn = imap_cls(host, port)
            conn.login(username, password)
            conn.select(mailbox)
            _, data = conn.search(None, "ALL")
            msg_ids = data[0].split()
            # Take the most recent max_messages
            recent_ids = msg_ids[-max_messages:]
            emails: List[EmailModel] = []
            for msg_id in reversed(recent_ids):
                _, raw = conn.fetch(msg_id, "(RFC822)")
                if not raw or not raw[0]:
                    continue
                raw_bytes = raw[0][1] if isinstance(raw[0], tuple) else raw[0]
                msg = _email_lib.message_from_bytes(raw_bytes)  # type: ignore[arg-type]
                parsed = self._parse_message(msg, account_label)
                emails.append(parsed)
            conn.logout()
            return emails
        except Exception as exc:
            logger.error("IMAP fetch error for %s: %s", account_label, exc)
            return []

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    async def classify(self, email_model: EmailModel) -> EmailModel:
        """Use Ollama to classify a single email and return updated model."""
        prompt = (
            f"Subject: {email_model.subject or ''}\n"
            f"Snippet: {email_model.body_snippet or ''}"
        )
        import json

        try:
            raw = await self._ollama.chat(
                messages=[
                    {"role": "system", "content": CLASSIFY_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            # Strip markdown code blocks if present
            clean = raw.strip().strip("```json").strip("```").strip()
            result: Dict[str, Any] = json.loads(clean)
            email_model.category = result.get("category", "other")
            email_model.is_invoice = bool(result.get("is_invoice", False))
            email_model.is_appointment = bool(result.get("is_appointment", False))
            email_model.is_important = bool(result.get("is_important", False))
            email_model.summary = result.get("summary")
        except Exception as exc:
            logger.warning("Classification failed for email %s: %s", email_model.message_id, exc)
            email_model.category = "other"
        return email_model

    async def process_and_store(self, emails: List[EmailModel]) -> None:
        """Classify each email and persist to database."""
        for em in emails:
            classified = await self.classify(em)
            self._repo.upsert_email(classified)
            logger.debug("Stored email: %s", classified.subject)

    async def generate_daily_summary(self, since: Optional[datetime] = None) -> str:
        """Ask Ollama to summarise today's emails stored in DB."""
        emails = self._repo.get_unread_emails(since=since)
        if not emails:
            return "No emails to summarise."
        bullet_list = "\n".join(
            f"- [{e.category}] From: {e.sender} | {e.subject}"
            for e in emails[:30]
        )
        prompt = (
            f"Here are today's emails:\n{bullet_list}\n\n"
            "Write a concise daily email summary in 3-5 bullet points."
        )
        return await self._ollama.generate(prompt=prompt, temperature=0.3)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_message(self, msg: Any, account_label: str) -> EmailModel:
        subject = msg.get("Subject", "")
        sender = msg.get("From", "")
        date_str = msg.get("Date", "")
        message_id = msg.get("Message-ID", "").strip()

        # Extract plain-text body snippet
        body_snippet = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_snippet = payload.decode("utf-8", errors="replace")[:500]
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body_snippet = payload.decode("utf-8", errors="replace")[:500]

        try:
            from email.utils import parsedate_to_datetime
            received_at: Optional[datetime] = parsedate_to_datetime(date_str)
        except Exception:
            received_at = None

        return EmailModel(
            message_id=message_id,
            account=account_label,
            sender=sender,
            subject=subject,
            body_snippet=body_snippet,
            received_at=received_at,
        )

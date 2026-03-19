"""Tests for audit metadata size limiting (M4).

Covers:
  - Small metadata passes through unchanged.
  - Metadata exactly at MAX_METADATA_BYTES passes (boundary: > not >=).
  - Metadata exceeding MAX_METADATA_BYTES is replaced with {"_truncated": True}.
  - Non-JSON-serializable metadata is replaced with {"_truncated": True}.
  - record_event() stores the truncated sentinel, not the oversized payload.
  - A warning is logged on truncation.
"""
import json
import pytest

from app.services.audit_service import MAX_METADATA_BYTES, _truncate_metadata, record_event
from app.models.audit import AuditEvent, AUDIT_EVENT_CREATED


# ---------------------------------------------------------------------------
# Unit tests for _truncate_metadata
# ---------------------------------------------------------------------------

class TestTruncateMetadata:

    def test_small_metadata_passes_through(self):
        meta = {"steps": 3, "model": "gpt-4o"}
        assert _truncate_metadata(meta) == meta

    def test_empty_metadata_passes_through(self):
        assert _truncate_metadata({}) == {}

    def test_metadata_exactly_at_limit_passes(self):
        # Build a dict whose JSON is exactly MAX_METADATA_BYTES bytes.
        # {"k": "..."} with enough chars to hit the boundary.
        # overhead: '{"k": ""}' = 9 bytes, so value length = MAX - 9
        target = MAX_METADATA_BYTES
        overhead = len(json.dumps({"k": ""}).encode())
        value = "x" * (target - overhead)
        meta = {"k": value}
        assert len(json.dumps(meta).encode()) == target
        result = _truncate_metadata(meta)
        assert result == meta  # not truncated at the boundary

    def test_metadata_one_byte_over_limit_is_truncated(self):
        target = MAX_METADATA_BYTES + 1
        overhead = len(json.dumps({"k": ""}).encode())
        value = "x" * (target - overhead)
        meta = {"k": value}
        assert len(json.dumps(meta).encode()) == target
        result = _truncate_metadata(meta)
        assert result == {"_truncated": True}

    def test_large_metadata_is_truncated(self):
        meta = {"data": "x" * 20_000}
        result = _truncate_metadata(meta)
        assert result == {"_truncated": True}

    def test_non_serializable_metadata_is_replaced(self):
        meta = {"bad": {1, 2, 3}}  # sets are not JSON-serializable
        result = _truncate_metadata(meta)
        assert result == {"_truncated": True}

    def test_original_dict_is_not_mutated(self):
        meta = {"data": "x" * 20_000}
        original_len = len(meta["data"])
        _truncate_metadata(meta)
        assert len(meta["data"]) == original_len  # original unchanged


# ---------------------------------------------------------------------------
# Integration: record_event stores truncated sentinel in DB
# ---------------------------------------------------------------------------

class TestRecordEventMetadataTruncation:

    async def test_oversized_metadata_stored_as_sentinel(self, isolated_db):
        oversized = {"data": "x" * 20_000}
        await record_event(
            run_id="aaaaaaaaaaaaaaaaaaaaaaaa",
            tenant_id="tenant_alpha",
            agent_id="bbbbbbbbbbbbbbbbbbbbbbbb",
            event=AUDIT_EVENT_CREATED,
            metadata=oversized,
        )
        stored = await AuditEvent.find_one(
            AuditEvent.run_id == "aaaaaaaaaaaaaaaaaaaaaaaa"
        )
        assert stored is not None
        assert stored.metadata == {"_truncated": True}

    async def test_normal_metadata_stored_intact(self, isolated_db):
        meta = {"steps": 2}
        await record_event(
            run_id="cccccccccccccccccccccccc",
            tenant_id="tenant_alpha",
            agent_id="dddddddddddddddddddddddd",
            event=AUDIT_EVENT_CREATED,
            metadata=meta,
        )
        stored = await AuditEvent.find_one(
            AuditEvent.run_id == "cccccccccccccccccccccccc"
        )
        assert stored is not None
        assert stored.metadata == meta


# ---------------------------------------------------------------------------
# Warning logged on truncation
# ---------------------------------------------------------------------------

class TestTruncationWarningLogged:

    def test_warning_is_emitted_when_truncated(self, caplog):
        import logging
        oversized = {"data": "x" * 20_000}
        with caplog.at_level(logging.WARNING):
            _truncate_metadata(oversized)
        assert any("truncat" in r.message.lower() for r in caplog.records)

    def test_no_warning_for_normal_metadata(self, caplog):
        import logging
        meta = {"steps": 1}
        with caplog.at_level(logging.WARNING):
            _truncate_metadata(meta)
        assert not any("truncat" in r.message.lower() for r in caplog.records)

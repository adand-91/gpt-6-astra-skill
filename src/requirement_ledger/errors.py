"""Stable public errors and exit codes."""

from __future__ import annotations


class LedgerError(Exception):
    """An expected, user-actionable failure."""

    code = "E_LEDGER"
    exit_code = 2

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UnsafePathError(LedgerError):
    code = "E_UNSAFE_PATH"
    exit_code = 4


class InputChangedError(LedgerError):
    code = "E_INPUT_CHANGED"
    exit_code = 5


class PrivacyBlockError(LedgerError):
    code = "E_PRIVACY_BLOCK"
    exit_code = 3


class SchemaError(LedgerError):
    code = "E_SCHEMA"
    exit_code = 6


class IncompleteEvidenceError(LedgerError):
    code = "E_INCOMPLETE_EVIDENCE"
    exit_code = 7


class ExecutionBlockedError(LedgerError):
    code = "E_EXECUTION_BLOCKED"
    exit_code = 8


class InputLimitError(LedgerError):
    """A bounded input exceeded an explicit product limit."""

    code = "E_INPUT_LIMIT"
    exit_code = 9

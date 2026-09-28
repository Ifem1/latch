# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import json
from dataclasses import dataclass
from datetime import datetime, timezone


GRANT_PROVISIONAL = 1
GRANT_COMMITTED = 2
GRANT_REVERTED = 3
ERR_EXPECTED = "EXPECTED"
MAX_PURPOSE_LEN = 400
MAX_ARM_ATTEMPTS = 8


@allow_storage
@dataclass
class Grant:
    latch_id: u256
    definition_hash: str
    action_hash: str
    beneficiary: Address
    amount: u256
    purpose: str
    state: u8
    staged_at: u256
    finalized_at: u256
    arm_attempts: u8


@gl.contract_interface
class ILatch:
    class View:
        def is_armable(
            self,
            latch_id: u256,
            expected_consumer: Address,
            expected_definition_hash: str,
            expected_action_hash: str,
        ) -> bool: ...

        def get_arm_status(
            self,
            latch_id: u256,
            expected_consumer: Address,
            expected_definition_hash: str,
            expected_action_hash: str,
        ) -> str: ...

    class Write:
        def arm_latch(
            self,
            latch_id: u256,
            expected_definition_hash: str,
            expected_action_hash: str,
        ) -> None: ...

        def acknowledge_terminal(
            self,
            latch_id: u256,
            expected_definition_hash: str,
            expected_action_hash: str,
            applied_state: str,
        ) -> None: ...


class GrantStaged(gl.Event):
    def __init__(self, grant_id: u256, latch_id: u256, /, **blob): ...


class GrantCommitted(gl.Event):
    def __init__(self, grant_id: u256, latch_id: u256, /, **blob): ...


class GrantReverted(gl.Event):
    def __init__(self, grant_id: u256, latch_id: u256, /, **blob): ...


def clean_text(value, limit: int) -> str:
    return " ".join(str(value).strip().split())[:limit]


def message_timestamp() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def normalize_hash(value: str) -> str:
    text = str(value).strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if len(text) != 64:
        raise gl.vm.UserError(f"{ERR_EXPECTED}: hash must be 32 bytes hex")
    for char in text:
        if char not in "0123456789abcdef":
            raise gl.vm.UserError(f"{ERR_EXPECTED}: invalid hash")
    return text


def normalize_address(value: Address) -> Address:
    """Accept SDK Address values and raw bytes used by Direct Mode fixtures."""
    if hasattr(value, "as_bytes"):
        return value
    return Address(value)


def hash_text(text: str) -> str:
    return Keccak256(str(text).encode("utf-8")).hexdigest()


def grant_action_payload(beneficiary: Address, amount: int, purpose: str) -> str:
    return json.dumps(
        {
            "kind": "EXAMPLE_LATCHED_GRANT_V1",
            "beneficiary": str(beneficiary).lower(),
            "amount": int(amount),
            "purpose": purpose,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def grant_state_name(value: int) -> str:
    return {
        GRANT_PROVISIONAL: "PROVISIONAL",
        GRANT_COMMITTED: "COMMITTED",
        GRANT_REVERTED: "REVERTED",
    }.get(int(value), "UNKNOWN")


class ExampleLatchedGrant(gl.Contract):
    """Minimal LATCH consumer proving that provisional value is unusable until commit."""

    latch_contract: Address
    admin: Address
    next_grant_id: u256
    grants: TreeMap[u256, Grant]
    latch_to_grant: TreeMap[u256, u256]
    usable_credits: TreeMap[Address, u256]

    def __init__(self, latch_contract: Address):
        self.latch_contract = normalize_address(latch_contract)
        self.admin = gl.message.sender_address
        self.next_grant_id = u256(1)

    def _only_admin(self) -> None:
        if gl.message.sender_address != self.admin:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: only admin may stage grants")

    def _grant_for_latch(self, latch_id: u256) -> tuple[u256, Grant]:
        grant_id_raw = self.latch_to_grant.get(latch_id)
        grant_id = int(grant_id_raw) if grant_id_raw is not None else 0
        if grant_id <= 0:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: no grant is bound to this latch")
        grant = self.grants.get(u256(grant_id))
        if grant is None:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: bound grant does not exist")
        return u256(grant_id), grant

    def _send_ack(self, grant: Grant, applied_state: str) -> None:
        ILatch(self.latch_contract).emit(on="finalized").acknowledge_terminal(
            grant.latch_id,
            str(grant.definition_hash),
            str(grant.action_hash),
            applied_state,
        )

    @gl.public.view
    def preview_grant_action_hash(
        self,
        beneficiary: Address,
        amount: u256,
        purpose: str,
    ) -> str:
        beneficiary = normalize_address(beneficiary)
        normalized_purpose = clean_text(purpose, MAX_PURPOSE_LEN + 1)
        if len(normalized_purpose) == 0 or len(normalized_purpose) > MAX_PURPOSE_LEN:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: purpose is invalid")
        if int(amount) <= 0:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: amount must be positive")
        return hash_text(grant_action_payload(beneficiary, int(amount), normalized_purpose))

    @gl.public.write
    def stage_grant(
        self,
        latch_id: u256,
        expected_definition_hash: str,
        beneficiary: Address,
        amount: u256,
        purpose: str,
    ) -> u256:
        self._only_admin()
        beneficiary = normalize_address(beneficiary)
        if int(amount) <= 0:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: amount must be positive")
        normalized_purpose = clean_text(purpose, MAX_PURPOSE_LEN + 1)
        if len(normalized_purpose) == 0 or len(normalized_purpose) > MAX_PURPOSE_LEN:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: purpose is invalid")
        definition_hash = normalize_hash(expected_definition_hash)
        action_hash = hash_text(grant_action_payload(beneficiary, int(amount), normalized_purpose))

        existing = self.latch_to_grant.get(latch_id)
        if existing is not None and int(existing) != 0:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: latch already has a staged grant")

        latch = ILatch(self.latch_contract)
        if not latch.view().is_armable(
            latch_id,
            gl.message.contract_address,
            definition_hash,
            action_hash,
        ):
            raise gl.vm.UserError(f"{ERR_EXPECTED}: latch binding is not armable for this exact grant")

        now = message_timestamp()
        grant_id = self.next_grant_id
        self.next_grant_id = u256(int(self.next_grant_id) + 1)
        grant = self.grants.get_or_insert_default(grant_id)
        grant.latch_id = latch_id
        grant.definition_hash = definition_hash
        grant.action_hash = action_hash
        grant.beneficiary = beneficiary
        grant.amount = amount
        grant.purpose = normalized_purpose
        grant.state = u8(GRANT_PROVISIONAL)
        grant.staged_at = u256(now)
        grant.finalized_at = u256(0)
        grant.arm_attempts = u8(1)
        self.latch_to_grant[latch_id] = grant_id

        # The grant is staged locally first. Arming is a finalized child transaction.
        # Until LATCH commits, this amount is NOT included in usable_credits.
        latch.emit(on="finalized").arm_latch(latch_id, definition_hash, action_hash)
        GrantStaged(
            grant_id,
            latch_id,
            definition_hash=definition_hash,
            action_hash=action_hash,
            beneficiary=str(beneficiary),
            amount=amount,
        ).emit()
        return grant_id

    @gl.public.write
    def retry_or_recover_arm(self, latch_id: u256) -> str:
        """Retry a lost arm child, or safely clear a grant for a cancelled latch.

        A terminal latch is never locally changed: its finalized callback remains
        the only authority that can commit or revert the grant.
        """
        self._only_admin()
        grant_id, grant = self._grant_for_latch(latch_id)
        if int(grant.state) == GRANT_REVERTED:
            return "REVERTED"
        if int(grant.state) != GRANT_PROVISIONAL:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: grant is not provisional")

        latch = ILatch(self.latch_contract)
        status = latch.view().get_arm_status(
            latch_id,
            gl.message.contract_address,
            str(grant.definition_hash),
            str(grant.action_hash),
        )
        if status == "CREATED":
            if int(grant.arm_attempts) >= MAX_ARM_ATTEMPTS:
                raise gl.vm.UserError(f"{ERR_EXPECTED}: arm retry limit reached")
            grant.arm_attempts = u8(int(grant.arm_attempts) + 1)
            latch.emit(on="finalized").arm_latch(
                latch_id, str(grant.definition_hash), str(grant.action_hash)
            )
            return "ARM_REQUESTED"
        if status == "ARMED":
            return "ARMED"
        if status == "CANCELLED":
            # Cancellation is final and cannot authorize value. Clear only the
            # unusable provisional record; never send a terminal acknowledgement.
            grant.state = u8(GRANT_REVERTED)
            grant.finalized_at = u256(message_timestamp())
            GrantReverted(
                grant_id, latch_id, beneficiary=str(grant.beneficiary),
                amount=grant.amount, recovery="CANCELLED_LATCH",
            ).emit()
            return "REVERTED"
        if status == "MISMATCH":
            raise gl.vm.UserError(f"{ERR_EXPECTED}: latch binding mismatch")
        raise gl.vm.UserError(f"{ERR_EXPECTED}: terminal latch requires its finalized callback")

    @gl.public.write
    def latch_commit(
        self,
        latch_id: u256,
        definition_hash: str,
        action_hash: str,
    ) -> None:
        if gl.message.sender_address != self.latch_contract:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: only configured LATCH may commit")
        grant_id, grant = self._grant_for_latch(latch_id)
        if normalize_hash(definition_hash) != str(grant.definition_hash):
            raise gl.vm.UserError(f"{ERR_EXPECTED}: definition hash mismatch")
        if normalize_hash(action_hash) != str(grant.action_hash):
            raise gl.vm.UserError(f"{ERR_EXPECTED}: action hash mismatch")

        if int(grant.state) == GRANT_COMMITTED:
            self._send_ack(grant, "COMMITTED")
            return
        if int(grant.state) != GRANT_PROVISIONAL:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: grant is not provisional")

        existing = self.usable_credits.get(grant.beneficiary)
        current = int(existing) if existing is not None else 0
        self.usable_credits[grant.beneficiary] = u256(current + int(grant.amount))
        grant.state = u8(GRANT_COMMITTED)
        grant.finalized_at = u256(message_timestamp())
        GrantCommitted(
            grant_id,
            latch_id,
            beneficiary=str(grant.beneficiary),
            amount=grant.amount,
        ).emit()
        self._send_ack(grant, "COMMITTED")

    @gl.public.write
    def latch_revert(
        self,
        latch_id: u256,
        definition_hash: str,
        action_hash: str,
    ) -> None:
        if gl.message.sender_address != self.latch_contract:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: only configured LATCH may revert")
        grant_id, grant = self._grant_for_latch(latch_id)
        if normalize_hash(definition_hash) != str(grant.definition_hash):
            raise gl.vm.UserError(f"{ERR_EXPECTED}: definition hash mismatch")
        if normalize_hash(action_hash) != str(grant.action_hash):
            raise gl.vm.UserError(f"{ERR_EXPECTED}: action hash mismatch")

        if int(grant.state) == GRANT_REVERTED:
            self._send_ack(grant, "REVERTED")
            return
        if int(grant.state) != GRANT_PROVISIONAL:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: grant is not provisional")

        grant.state = u8(GRANT_REVERTED)
        grant.finalized_at = u256(message_timestamp())
        GrantReverted(
            grant_id,
            latch_id,
            beneficiary=str(grant.beneficiary),
            amount=grant.amount,
        ).emit()
        self._send_ack(grant, "REVERTED")

    @gl.public.view
    def get_grant(self, grant_id: u256) -> dict:
        grant = self.grants.get(grant_id)
        if grant is None:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: grant does not exist")
        return {
            "grant_id": int(grant_id),
            "latch_id": int(grant.latch_id),
            "definition_hash": str(grant.definition_hash),
            "action_hash": str(grant.action_hash),
            "beneficiary": str(grant.beneficiary),
            "amount": int(grant.amount),
            "purpose": str(grant.purpose),
            "state": int(grant.state),
            "state_name": grant_state_name(int(grant.state)),
            "staged_at": int(grant.staged_at),
            "finalized_at": int(grant.finalized_at),
            "arm_attempts": int(grant.arm_attempts),
        }

    @gl.public.view
    def get_usable_credit(self, beneficiary: Address) -> u256:
        beneficiary = normalize_address(beneficiary)
        value = self.usable_credits.get(beneficiary)
        return u256(int(value) if value is not None else 0)

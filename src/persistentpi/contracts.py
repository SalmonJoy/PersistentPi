"""Portable data contracts. Hidden results have no Runner-facing interface."""
from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
from typing import Any

from . import CONTRACT_VERSION


def canonical(value: Any) -> bytes:
    if hasattr(value, '__dataclass_fields__'):
        value = asdict(value)
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('utf-8')


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


class Contract:
    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class Budget(Contract):
    max_attempts: int
    max_model_decisions: int
    max_tool_calls: int
    max_tokens: int
    max_wall_seconds: float
    test_timeout_seconds: float
    max_workspace_bytes: int
    max_output_bytes: int
    max_edit_bytes: int
    contract_version: int = field(default=CONTRACT_VERSION, init=False)

    def __post_init__(self):
        for name, value in self.to_dict().items():
            if name == 'contract_version':
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError('Budget limits must be finite and positive: ' + name)
            if not name.endswith('seconds') and type(value) is not int:
                raise ValueError('Count/byte limits must be integers: ' + name)


@dataclass(frozen=True)
class TaskView(Contract):
    task_id: str
    description: str
    editable_paths: tuple[str, ...]
    readable_paths: tuple[str, ...]
    public_test_id: str
    fixture_version: str
    contract_version: int = field(default=CONTRACT_VERSION, init=False)


@dataclass(frozen=True)
class ActionRequest(Contract):
    tool: str
    arguments: dict
    contract_version: int = field(default=CONTRACT_VERSION, init=False)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict) or set(data) - {'tool', 'arguments', 'contract_version'}:
            raise ValueError('Invalid action contract')
        if data.get('contract_version', CONTRACT_VERSION) != CONTRACT_VERSION:
            raise ValueError('Unsupported action contract version')
        if not isinstance(data.get('tool'), str) or not isinstance(data.get('arguments', {}), dict):
            raise ValueError('Invalid action fields')
        return cls(data['tool'], data.get('arguments', {}))


@dataclass(frozen=True)
class CheckpointRef(Contract):
    hash: str
    parent_hash: str | None = None
    contract_version: int = field(default=CONTRACT_VERSION, init=False)


@dataclass(frozen=True)
class ActionResult(Contract):
    tool: str
    ok: bool
    data: dict = field(default_factory=dict)
    error: str | None = None
    checkpoint: CheckpointRef | None = None
    contract_version: int = field(default=CONTRACT_VERSION, init=False)


@dataclass(frozen=True)
class Observation(Contract):
    step: int
    action: ActionRequest
    result: ActionResult
    contract_version: int = field(default=CONTRACT_VERSION, init=False)


@dataclass(frozen=True)
class DecisionState(Contract):
    remaining_attempts: int
    remaining_decisions: int
    remaining_tool_calls: int
    remaining_tokens: int
    remaining_wall_seconds: float
    contract_version: int = field(default=CONTRACT_VERSION, init=False)


@dataclass(frozen=True)
class PublicFeedback(Contract):
    outcome: str
    verifier_id: str
    verifier_version: str
    duration_seconds: float
    output: str
    output_truncated: bool
    contract_version: int = field(default=CONTRACT_VERSION, init=False)


@dataclass(frozen=True)
class EvaluationResult(Contract):
    split: str
    outcome: str
    score: float | None
    test_id: str
    command: tuple[str, ...]
    duration_seconds: float
    output: str
    output_truncated: bool
    exit_code: int | None
    capabilities: dict
    contract_version: int = field(default=CONTRACT_VERSION, init=False)

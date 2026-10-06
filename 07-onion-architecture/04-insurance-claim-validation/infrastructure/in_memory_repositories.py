"""Implementações em memória dos repositórios (Ring 4 - Infrastructure)."""

from typing import Dict, Optional, List
from domain.model.policy import Policy
from domain.model.claim import Claim
from application.interfaces import IPolicyRepository, IClaimRepository


class InMemoryPolicyRepository(IPolicyRepository):
    """Repositório em memória para persistência de apólices."""
    def __init__(self) -> None:
        self._policies: Dict[str, Policy] = {}

    def get_by_id(self, policy_id: str) -> Optional[Policy]:
        return self._policies.get(policy_id)

    def save(self, policy: Policy) -> None:
        self._policies[policy.policy_id] = policy


class InMemoryClaimRepository(IClaimRepository):
    """Repositório em memória para persistência de sinistros."""
    def __init__(self) -> None:
        self._claims: Dict[str, Claim] = {}

    def get_by_id(self, claim_id: str) -> Optional[Claim]:
        return self._claims.get(claim_id)

    def save(self, claim: Claim) -> None:
        self._claims[claim.claim_id] = claim

    def list_all(self) -> List[Claim]:
        return list(self._claims.values())

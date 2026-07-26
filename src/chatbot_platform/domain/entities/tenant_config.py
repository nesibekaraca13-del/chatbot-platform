from dataclasses import dataclass


@dataclass(frozen=True)
class TenantConfig:
    tenant_id: str
    name: str
    llm_provider: str | None = None

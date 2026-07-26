from pathlib import Path

import yaml

from chatbot_platform.domain.entities.tenant_config import TenantConfig


def load_tenant_config(tenants_dir: Path, tenant_id: str) -> TenantConfig:
    config_path = tenants_dir / tenant_id / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Tenant config bulunamadı: {tenant_id}")

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return TenantConfig(
        tenant_id=tenant_id,
        name=data.get("name", tenant_id),
        llm_provider=data.get("llm_provider"),
    )


def list_tenant_ids(tenants_dir: Path) -> list[str]:
    if not tenants_dir.exists():
        return []
    return sorted(p.name for p in tenants_dir.iterdir() if p.is_dir())

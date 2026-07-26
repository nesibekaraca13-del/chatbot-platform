from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TenantPaths:
    knowledge_dir: Path
    chroma_collection_name: str


def resolve_tenant_paths(tenants_root: Path, tenant_id: str) -> TenantPaths:
    return TenantPaths(
        knowledge_dir=tenants_root / tenant_id / "knowledge",
        chroma_collection_name=f"knowledge_{tenant_id}",
    )

from pathlib import Path

from chatbot_platform.infrastructure.tenants.tenant_paths import resolve_tenant_paths


def test_resolve_tenant_paths_derives_knowledge_dir_and_collection_name() -> None:
    paths = resolve_tenant_paths(Path("/tenants"), "ahmet-mobilya")

    assert paths.knowledge_dir == Path("/tenants/ahmet-mobilya/knowledge")
    assert paths.chroma_collection_name == "knowledge_ahmet-mobilya"


def test_resolve_tenant_paths_differs_per_tenant() -> None:
    paths_a = resolve_tenant_paths(Path("/tenants"), "firma-a")
    paths_b = resolve_tenant_paths(Path("/tenants"), "firma-b")

    assert paths_a.knowledge_dir != paths_b.knowledge_dir
    assert paths_a.chroma_collection_name != paths_b.chroma_collection_name

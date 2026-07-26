from pathlib import Path

from chatbot_platform.application.use_cases.index_knowledge_base import index_knowledge_base
from chatbot_platform.infrastructure.tenants.tenant_paths import resolve_tenant_paths
from chatbot_platform.infrastructure.vector_store.chroma_vector_store import ChromaVectorStore


def _write_about_file(knowledge_dir: Path, heading: str, text: str) -> None:
    knowledge_dir.mkdir(parents=True)
    (knowledge_dir / "about.md").write_text(
        f"---\ncategory: about\nlanguage: tr\nlast_updated: 2026-07-26\n---\n\n"
        f"## {heading}\n\n{text}\n",
        encoding="utf-8",
    )


def test_two_tenants_have_isolated_knowledge_and_vector_stores(tmp_path: Path) -> None:
    tenants_root = tmp_path / "tenants"
    paths_a = resolve_tenant_paths(tenants_root, "firma-a")
    paths_b = resolve_tenant_paths(tenants_root, "firma-b")

    _write_about_file(paths_a.knowledge_dir, "Firma A", "Biz A firmasıyız, kırmızı ürünler satarız.")
    _write_about_file(paths_b.knowledge_dir, "Firma B", "Biz B firmasıyız, mavi ürünler satarız.")

    chroma_dir = tmp_path / "chroma_db"
    store_a = ChromaVectorStore(
        persist_directory=chroma_dir, collection_name=paths_a.chroma_collection_name
    )
    store_b = ChromaVectorStore(
        persist_directory=chroma_dir, collection_name=paths_b.chroma_collection_name
    )

    index_knowledge_base(paths_a.knowledge_dir, store_a)
    index_knowledge_base(paths_b.knowledge_dir, store_b)

    assert store_a.count() == 1
    assert store_b.count() == 1

    results_a = store_a.search("firma hangi renk ürün satıyor", top_k=1)
    results_b = store_b.search("firma hangi renk ürün satıyor", top_k=1)

    assert "A firmasıyız" in results_a[0].text
    assert "B firmasıyız" in results_b[0].text


def test_clearing_one_tenant_does_not_affect_the_other(tmp_path: Path) -> None:
    tenants_root = tmp_path / "tenants"
    paths_a = resolve_tenant_paths(tenants_root, "firma-a")
    paths_b = resolve_tenant_paths(tenants_root, "firma-b")

    _write_about_file(paths_a.knowledge_dir, "Firma A", "A firmasının bilgisi.")
    _write_about_file(paths_b.knowledge_dir, "Firma B", "B firmasının bilgisi.")

    chroma_dir = tmp_path / "chroma_db"
    store_a = ChromaVectorStore(
        persist_directory=chroma_dir, collection_name=paths_a.chroma_collection_name
    )
    store_b = ChromaVectorStore(
        persist_directory=chroma_dir, collection_name=paths_b.chroma_collection_name
    )

    index_knowledge_base(paths_a.knowledge_dir, store_a)
    index_knowledge_base(paths_b.knowledge_dir, store_b)

    store_a.clear()

    assert store_a.count() == 0
    assert store_b.count() == 1

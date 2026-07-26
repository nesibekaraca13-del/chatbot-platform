from pathlib import Path

import pytest

from chatbot_platform.infrastructure.tenants.tenant_config_loader import (
    list_tenant_ids,
    load_tenant_config,
)


def _write_tenant(tenants_dir: Path, tenant_id: str, content: str) -> None:
    tenant_dir = tenants_dir / tenant_id
    tenant_dir.mkdir(parents=True)
    (tenant_dir / "config.yaml").write_text(content, encoding="utf-8")


def test_load_tenant_config_reads_fields(tmp_path: Path) -> None:
    _write_tenant(
        tmp_path,
        "ahmet-mobilya",
        "name: Ahmet Mobilya A.Ş.\nllm_provider: gemini\n",
    )

    config = load_tenant_config(tmp_path, "ahmet-mobilya")

    assert config.tenant_id == "ahmet-mobilya"
    assert config.name == "Ahmet Mobilya A.Ş."
    assert config.llm_provider == "gemini"


def test_load_tenant_config_defaults_name_and_provider(tmp_path: Path) -> None:
    _write_tenant(tmp_path, "bos-firma", "")

    config = load_tenant_config(tmp_path, "bos-firma")

    assert config.name == "bos-firma"
    assert config.llm_provider is None


def test_load_tenant_config_raises_for_missing_tenant(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_tenant_config(tmp_path, "yok-boyle-bir-firma")


def test_list_tenant_ids_returns_sorted_directory_names(tmp_path: Path) -> None:
    _write_tenant(tmp_path, "zebra-firma", "name: Zebra\n")
    _write_tenant(tmp_path, "ahmet-mobilya", "name: Ahmet\n")

    assert list_tenant_ids(tmp_path) == ["ahmet-mobilya", "zebra-firma"]


def test_list_tenant_ids_returns_empty_list_when_dir_missing(tmp_path: Path) -> None:
    missing_dir = tmp_path / "yok"

    assert list_tenant_ids(missing_dir) == []

from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockType

from mcp_certificate_monitor.cert.peer_cert import PeerCert
from mcp_certificate_monitor.store import (
    HostStore,
    add_host,
    load,
    remove_host,
    save,
    update_result,
)


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MockType:
    return mocker.patch("mcp_certificate_monitor.store.logger")


@pytest.fixture
def store_dir(mocker: MockerFixture, tmp_path: Path) -> Path:
    d = tmp_path / "cert-monitor"
    mocker.patch("mcp_certificate_monitor.store.STORE_DIR", d)
    mocker.patch("mcp_certificate_monitor.store.STORE_PATH", d / "hosts.json")
    return d


@pytest.fixture
def mock_fsync(mocker: MockerFixture) -> MockType:
    return mocker.patch("mcp_certificate_monitor.store.os.fsync")


class TestSave:
    def test_creates_directory_if_missing(
        self, store_dir: Path, mock_fsync: MockType, sample_host_store: HostStore
    ) -> None:
        assert not store_dir.exists()
        save(sample_host_store.hosts)
        assert store_dir.exists()

    def test_writes_valid_json(
        self, store_dir: Path, mock_fsync: MockType, sample_host_store: HostStore
    ) -> None:
        save(sample_host_store.hosts)
        written = HostStore.model_validate_json((store_dir / "hosts.json").read_text())
        assert written.hosts == sample_host_store.hosts

    def test_no_temp_files_after_success(
        self, store_dir: Path, mock_fsync: MockType, sample_host_store: HostStore
    ) -> None:
        save(sample_host_store.hosts)
        assert not list(store_dir.glob(".output-json-*.tmp"))

    def test_error_cleans_up_and_reraises(
        self, store_dir: Path, mocker: MockerFixture, sample_host_store: HostStore
    ) -> None:
        mocker.patch(
            "mcp_certificate_monitor.store.os.fsync", side_effect=OSError("disk full")
        )
        with pytest.raises(OSError, match="disk full"):
            save(sample_host_store.hosts)
        assert not list(store_dir.glob(".output-json-*.tmp"))


class TestLoad:
    def test_empty_result_if_path_does_not_exist(self, store_dir: Path) -> None:
        assert not store_dir.exists()
        loaded = load()
        assert loaded == {}

    def test_empty_result_if_file_corrupt(
        self, store_dir: Path, mock_logger: MockType
    ) -> None:
        store_dir.mkdir()
        (store_dir / "hosts.json").write_text("not valid json")
        assert load() == {}
        mock_logger.warning.assert_called_once()

    def test_loads_valid_json(
        self, store_dir: Path, sample_host_store: HostStore
    ) -> None:
        store_dir.mkdir()
        (store_dir / "hosts.json").write_text(sample_host_store.model_dump_json())
        assert load() == sample_host_store.hosts


class TestAddHost:
    def test_raises_if_already_monitored(
        self, store_dir: Path, sample_host_store: HostStore
    ) -> None:
        store_dir.mkdir()
        (store_dir / "hosts.json").write_text(sample_host_store.model_dump_json())
        with pytest.raises(KeyError, match="already monitored"):
            add_host("example.com")

    def test_adds_host(self, store_dir: Path, mock_fsync: MockType) -> None:
        new_host = add_host("www.example.com", 999)

        assert new_host.domain == "www.example.com"
        assert new_host.port == 999

        written = HostStore.model_validate_json((store_dir / "hosts.json").read_text())
        assert written.hosts == {
            "www.example.com": new_host,
        }


class TestRemoveHost:
    def test_raises_if_not_monitored(
        self, store_dir: Path, sample_host_store: HostStore, mock_fsync: MockType
    ) -> None:
        store_dir.mkdir()
        (store_dir / "hosts.json").write_text(sample_host_store.model_dump_json())
        with pytest.raises(KeyError, match="not monitored"):
            remove_host("not-monitored-domain.org")

    def test_removes_host(
        self, store_dir: Path, sample_host_store: HostStore, mock_fsync: MockType
    ) -> None:
        store_dir.mkdir()
        (store_dir / "hosts.json").write_text(sample_host_store.model_dump_json())
        remove_host("example.com")
        written = HostStore.model_validate_json((store_dir / "hosts.json").read_text())
        assert written.hosts == {}


class TestUpdateResult:
    def test_raises_if_not_monitored(
        self,
        store_dir: Path,
        sample_host_store: HostStore,
        sample_peer_cert: PeerCert,
        mock_fsync: MockType,
    ) -> None:
        store_dir.mkdir()
        (store_dir / "hosts.json").write_text(sample_host_store.model_dump_json())
        with pytest.raises(KeyError, match="not monitored"):
            update_result("not-monitored-domain.org", sample_peer_cert)

    def test_updates_result(
        self,
        store_dir: Path,
        sample_host_store: HostStore,
        sample_peer_cert: PeerCert,
        mock_fsync: MockType,
    ):
        store_dir.mkdir()
        (store_dir / "hosts.json").write_text(sample_host_store.model_dump_json())
        update_result("example.com", sample_peer_cert)
        written = HostStore.model_validate_json((store_dir / "hosts.json").read_text())
        assert written.hosts["example.com"].last_result == sample_peer_cert

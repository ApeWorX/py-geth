import contextlib
import os
import shutil
import tempfile

from geth.wrapper import (
    construct_test_chain_kwargs,
    get_max_socket_path_length,
)


@contextlib.contextmanager
def tempdir():
    directory = tempfile.mkdtemp()

    try:
        yield directory
    finally:
        shutil.rmtree(directory)


def test_short_data_directory_paths_use_local_geth_ipc_socket():
    with tempdir() as data_dir:
        expected_path = os.path.abspath(os.path.join(data_dir, "geth.ipc"))
        assert len(expected_path) < get_max_socket_path_length()
        chain_kwargs = construct_test_chain_kwargs(data_dir=data_dir, ipc_disable=False)

        assert chain_kwargs["ipc_path"] == expected_path


def test_long_data_directory_paths_use_tempfile_geth_ipc_socket():
    with tempdir() as temp_directory:
        data_dir = os.path.abspath(temp_directory)
        while len(os.path.join(data_dir, "geth.ipc")) <= get_max_socket_path_length():
            data_dir = os.path.join(data_dir, "long-path-component")

        data_dir_ipc_path = os.path.abspath(os.path.join(data_dir, "geth.ipc"))
        assert len(data_dir_ipc_path) > get_max_socket_path_length()

        chain_kwargs = construct_test_chain_kwargs(data_dir=data_dir, ipc_disable=False)

        assert chain_kwargs["ipc_path"] != data_dir_ipc_path


def test_windows_test_chains_disable_ipc(monkeypatch, tmp_path):
    monkeypatch.setattr("geth.wrapper.sys.platform", "win32")

    chain_kwargs = construct_test_chain_kwargs(data_dir=str(tmp_path))

    assert chain_kwargs["ipc_disable"] is True
    assert "ipc_path" not in chain_kwargs


def test_generated_ports_are_unique(monkeypatch):
    generated_ports = iter(("40000", "40000", "40001", "40001", "40002"))
    monkeypatch.setattr("geth.wrapper.is_port_open", lambda port: False)
    monkeypatch.setattr("geth.wrapper.get_open_port", lambda: next(generated_ports))

    chain_kwargs = construct_test_chain_kwargs()

    assert {
        chain_kwargs["port"],
        chain_kwargs["ws_port"],
        chain_kwargs["rpc_port"],
    } == {"40000", "40001", "40002"}

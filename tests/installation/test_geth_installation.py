import pytest

from geth import install as install_module
from geth.exceptions import (
    PyGethOSError,
    PyGethValueError,
)


@pytest.mark.parametrize(
    "platform,executable_name",
    (("linux", "geth"), ("darwin", "geth"), ("win32", "geth.exe")),
)
def test_installation_paths_use_platform_executable_name(
    monkeypatch, tmp_path, platform, executable_name
):
    monkeypatch.setattr(install_module.sys, "platform", platform)
    monkeypatch.setenv("GETH_BASE_INSTALL_PATH", str(tmp_path))

    assert install_module.get_built_executable_path("v1.17.2").endswith(
        str(
            tmp_path.joinpath(
                "geth-v1.17.2",
                "source",
                "go-ethereum-1.17.2",
                "build",
                "bin",
                executable_name,
            )
        )
    )
    assert install_module.get_executable_path("v1.17.2").endswith(
        str(tmp_path.joinpath("geth-v1.17.2", "bin", executable_name))
    )


def test_go_binary_override(monkeypatch):
    monkeypatch.setenv("GO_BINARY", "/custom/go")

    assert install_module.get_go_executable_path() == "/custom/go"


@pytest.mark.parametrize("platform", ("linux", "win32"))
def test_build_from_source_code(monkeypatch, tmp_path, platform):
    source_path = tmp_path / "source"
    source_path.mkdir()
    executable_name = "geth.exe" if platform == "win32" else "geth"
    built_executable = source_path / "build" / "bin" / executable_name
    executable = tmp_path / "installed" / "bin" / executable_name
    calls = []

    def build_geth(command, **kwargs):
        calls.append((command, kwargs))
        built_executable.parent.mkdir(parents=True)
        built_executable.write_bytes(b"geth")
        return 0

    monkeypatch.setattr(install_module.sys, "platform", platform)
    monkeypatch.setenv("GO_BINARY", "/custom/go")
    monkeypatch.setattr(install_module, "is_go_available", lambda: True)
    monkeypatch.setattr(
        install_module, "get_source_code_path", lambda identifier: str(source_path)
    )
    monkeypatch.setattr(
        install_module,
        "get_built_executable_path",
        lambda identifier: str(built_executable),
    )
    monkeypatch.setattr(
        install_module, "get_executable_path", lambda identifier: str(executable)
    )
    monkeypatch.setattr(install_module, "check_subprocess_call", build_geth)

    install_module.build_from_source_code("v1.17.2")

    assert calls == [
        (
            [
                "/custom/go",
                "run",
                "build/ci.go",
                "install",
                "./cmd/geth",
            ],
            {"message": "Building `geth` binary"},
        )
    ]
    assert executable.read_bytes() == b"geth"
    assert executable.is_symlink() is (platform != "win32")


def test_build_requires_go(monkeypatch):
    monkeypatch.setattr(install_module, "is_go_available", lambda: False)

    with pytest.raises(PyGethOSError, match="`go` runtime was not found"):
        install_module.build_from_source_code("v1.17.2")


def test_install_rejects_unsupported_platform():
    with pytest.raises(PyGethValueError, match="not supported on your platform"):
        install_module.install_geth("v1.17.2", platform="unsupported")


def test_install_rejects_unsupported_version():
    with pytest.raises(PyGethValueError, match="not supported"):
        install_module.install_geth("v0.0.0", platform=install_module.LINUX)

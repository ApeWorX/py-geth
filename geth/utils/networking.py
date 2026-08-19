from collections.abc import (
    Generator,
)
import contextlib
import socket
import time

from geth.exceptions import (
    PyGethValueError,
)

from .timeout import (
    Timeout,
)


def is_port_open(port: int) -> bool:
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", port))
    except OSError:
        return False
    else:
        return True
    finally:
        sock.close()


def get_open_port() -> str:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return str(port)


def _get_p2p_bind_address() -> tuple[socket.AddressFamily, tuple[str, int]]:
    if socket.has_ipv6:
        return socket.AF_INET6, ("::", 0)

    return socket.AF_INET, ("0.0.0.0", 0)


def is_p2p_port_open(port: int) -> bool:
    family, bind_address = _get_p2p_bind_address()
    bind_address = (bind_address[0], port)
    tcp_sock = socket.socket(family, socket.SOCK_STREAM)
    udp_sock = socket.socket(family, socket.SOCK_DGRAM)
    try:
        udp_sock.bind(bind_address)
        tcp_sock.bind(bind_address)
    except OSError:
        return False
    else:
        return True
    finally:
        tcp_sock.close()
        udp_sock.close()


def get_open_p2p_port() -> str:
    family, bind_address = _get_p2p_bind_address()

    while True:
        udp_sock = socket.socket(family, socket.SOCK_DGRAM)
        tcp_sock = socket.socket(family, socket.SOCK_STREAM)
        try:
            udp_sock.bind(bind_address)
            port = udp_sock.getsockname()[1]
            tcp_sock.bind((bind_address[0], port))
        except OSError:
            continue
        else:
            return str(port)
        finally:
            tcp_sock.close()
            udp_sock.close()


@contextlib.contextmanager
def get_ipc_socket(
    ipc_path: str, timeout: float = 0.1
) -> Generator[socket.socket, None, None]:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(ipc_path)
    sock.settimeout(timeout)

    yield sock

    sock.close()


def wait_for_http_connection(port: int, timeout: int = 5) -> None:
    with Timeout(timeout) as _timeout:
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            try:
                s.connect(("127.0.0.1", port))
            except (TimeoutError, ConnectionRefusedError):
                time.sleep(0.1)
                _timeout.check()
                continue
            else:
                break
        else:
            raise PyGethValueError(
                "Unable to establish HTTP connection, "
                f"timed out after {timeout} seconds"
            )

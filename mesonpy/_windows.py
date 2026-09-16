import platform
import sysconfig


def _windows_interpreter_arch() -> str:
    """Return the Windows architecture for which the Python interpreter has been compiled."""
    match sysconfig.get_platform():
        case 'win32':
            return 'x86'
        case 'win-amd64':
            return 'amd64'
        case 'win-arm64':
            return 'arm64'
    raise ValueError


def detect():
    arch = _windows_interpreter_arch()
    nativearch = platform.machine().lower()
    cross = arch != nativearch
    print(f'arch={arch} native={nativearch} cross={cross}')

"""Fail-closed, handle-relative output creation for Windows.

This module deliberately has no import-time dependency on Windows DLLs so the
package remains importable on every supported platform.  On Windows, a caller
supplies an already selected parent directory and one validated leaf name.  A
directory handle is opened without following a reparse point and ``NtCreateFile``
creates the child relative to that handle.

File creation is transactional with respect to content disclosure: the new
handle is first made delete-pending, bytes are written and flushed, the parent
binding is rechecked, and only then is deletion cancelled.  Cleanup is always
handle based.  This module never unlinks or removes a path after a failure.
"""

from __future__ import annotations

import ctypes
import os
from contextlib import contextmanager
from ctypes import wintypes
from pathlib import Path
from typing import Iterator

__all__ = [
    "UnsupportedPlatformError",
    "Win32SafeIOError",
    "create_new_directory",
    "create_new_file",
    "profile_directory",
    "validate_leaf_name",
]


class Win32SafeIOError(OSError):
    """A Windows native safe-I/O operation failed closed."""


class UnsupportedPlatformError(Win32SafeIOError):
    """The Windows-only operation was called on another platform."""


_FORBIDDEN_LEAF_CHARS = frozenset('<>:"/\\|?*')
_RESERVED_BASENAMES = frozenset({"CON", "PRN", "AUX", "NUL", "CLOCK$"})
_RESERVED_PORT_DIGITS = frozenset("123456789¹²³")
_MAX_LEAF_UTF16_UNITS = 255


def validate_leaf_name(leaf: str) -> str:
    """Validate and return a single portable Windows leaf name.

    The function is platform independent so callers can reject unsafe output
    names before dispatch.  It intentionally applies the conservative Win32
    namespace rules even though the eventual create uses an NT relative name.
    In particular, alternate data streams, separators, trailing dot/space
    aliases, control characters, and DOS device names are never accepted.
    """

    if type(leaf) is not str:
        raise TypeError("Windows output leaf must be a string")
    if not leaf or leaf in {".", ".."}:
        raise ValueError("Windows output leaf must be one non-empty name")
    if leaf[-1] in {" ", "."}:
        raise ValueError("Windows output leaf cannot end in a space or dot")
    if any(character in _FORBIDDEN_LEAF_CHARS or ord(character) < 32 for character in leaf):
        raise ValueError("Windows output leaf contains a reserved character")
    try:
        units = len(leaf.encode("utf-16-le", errors="strict")) // 2
    except UnicodeEncodeError as exc:
        raise ValueError("Windows output leaf contains an unpaired surrogate") from exc
    if units > _MAX_LEAF_UTF16_UNITS:
        raise ValueError("Windows output leaf exceeds 255 UTF-16 code units")

    # Device aliases remain reserved before an extension.  Rstrip is
    # intentionally conservative for aliases such as ``CON .txt``.
    basename = leaf.split(".", 1)[0].rstrip(" .").upper()
    if basename in _RESERVED_BASENAMES:
        raise ValueError("Windows output leaf is a reserved DOS device name")
    if (len(basename) == 4 and basename[:3] in {"COM", "LPT"}
            and basename[3] in _RESERVED_PORT_DIGITS):
        raise ValueError("Windows output leaf is a reserved DOS device name")
    return leaf


def _require_windows() -> None:
    if os.name != "nt":
        raise UnsupportedPlatformError("handle-relative creation is available only on Windows")


if os.name == "nt":  # pragma: no cover - declarations are exercised by Windows CI
    import msvcrt

    _NTSTATUS = ctypes.c_long
    _ULONG_PTR = ctypes.c_size_t

    class _UNICODE_STRING(ctypes.Structure):
        _fields_ = [
            ("Length", wintypes.USHORT),
            ("MaximumLength", wintypes.USHORT),
            ("Buffer", wintypes.LPWSTR),
        ]

    class _OBJECT_ATTRIBUTES(ctypes.Structure):
        _fields_ = [
            ("Length", wintypes.ULONG),
            ("RootDirectory", wintypes.HANDLE),
            ("ObjectName", ctypes.POINTER(_UNICODE_STRING)),
            ("Attributes", wintypes.ULONG),
            ("SecurityDescriptor", wintypes.LPVOID),
            ("SecurityQualityOfService", wintypes.LPVOID),
        ]

    class _IO_STATUS_VALUE(ctypes.Union):
        _fields_ = [("Status", _NTSTATUS), ("Pointer", wintypes.LPVOID)]

    class _IO_STATUS_BLOCK(ctypes.Structure):
        _anonymous_ = ("value",)
        _fields_ = [("value", _IO_STATUS_VALUE), ("Information", _ULONG_PTR)]

    class _BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("dwFileAttributes", wintypes.DWORD),
            ("ftCreationTime", wintypes.FILETIME),
            ("ftLastAccessTime", wintypes.FILETIME),
            ("ftLastWriteTime", wintypes.FILETIME),
            ("dwVolumeSerialNumber", wintypes.DWORD),
            ("nFileSizeHigh", wintypes.DWORD),
            ("nFileSizeLow", wintypes.DWORD),
            ("nNumberOfLinks", wintypes.DWORD),
            ("nFileIndexHigh", wintypes.DWORD),
            ("nFileIndexLow", wintypes.DWORD),
        ]

    class _FILE_DISPOSITION_INFO(ctypes.Structure):
        # FILE_DISPOSITION_INFO uses BOOLEAN (one byte), not Win32 BOOL
        # (four bytes).  SetFileInformationByHandle rejects the wrong ABI.
        _fields_ = [("DeleteFile", ctypes.c_ubyte)]

    if ctypes.sizeof(_FILE_DISPOSITION_INFO) != 1:
        raise RuntimeError("unexpected Windows FILE_DISPOSITION_INFO ABI")

    class _GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", ctypes.c_ubyte * 8),
        ]

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
    _advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    _shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    _ole32 = ctypes.WinDLL("ole32", use_last_error=True)

    _kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    ]
    _kernel32.CreateFileW.restype = wintypes.HANDLE
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.CloseHandle.restype = wintypes.BOOL
    _kernel32.GetFileInformationByHandle.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(_BY_HANDLE_FILE_INFORMATION),
    ]
    _kernel32.GetFileInformationByHandle.restype = wintypes.BOOL
    _kernel32.SetFileInformationByHandle.argtypes = [
        wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD,
    ]
    _kernel32.SetFileInformationByHandle.restype = wintypes.BOOL
    _kernel32.WriteFile.argtypes = [
        wintypes.HANDLE, wintypes.LPCVOID, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID,
    ]
    _kernel32.WriteFile.restype = wintypes.BOOL
    _kernel32.FlushFileBuffers.argtypes = [wintypes.HANDLE]
    _kernel32.FlushFileBuffers.restype = wintypes.BOOL
    _kernel32.GetCurrentProcess.argtypes = []
    _kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    _kernel32.DuplicateHandle.argtypes = [
        wintypes.HANDLE, wintypes.HANDLE, wintypes.HANDLE,
        ctypes.POINTER(wintypes.HANDLE), wintypes.DWORD, wintypes.BOOL,
        wintypes.DWORD,
    ]
    _kernel32.DuplicateHandle.restype = wintypes.BOOL

    _ntdll.NtCreateFile.argtypes = [
        ctypes.POINTER(wintypes.HANDLE), wintypes.DWORD,
        ctypes.POINTER(_OBJECT_ATTRIBUTES), ctypes.POINTER(_IO_STATUS_BLOCK),
        wintypes.LPVOID, wintypes.ULONG, wintypes.ULONG, wintypes.ULONG,
        wintypes.ULONG, wintypes.LPVOID, wintypes.ULONG,
    ]
    _ntdll.NtCreateFile.restype = _NTSTATUS
    _ntdll.RtlNtStatusToDosError.argtypes = [_NTSTATUS]
    _ntdll.RtlNtStatusToDosError.restype = wintypes.ULONG

    _advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.LPVOID),
        ctypes.POINTER(wintypes.ULONG),
    ]
    _advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = wintypes.BOOL
    _kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
    _kernel32.LocalFree.restype = wintypes.HLOCAL

    _shell32.SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(_GUID), wintypes.DWORD, wintypes.HANDLE,
        ctypes.POINTER(wintypes.LPWSTR),
    ]
    _shell32.SHGetKnownFolderPath.restype = ctypes.c_long
    _ole32.CoTaskMemFree.argtypes = [wintypes.LPVOID]
    _ole32.CoTaskMemFree.restype = None


_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
_FILE_ATTRIBUTE_DIRECTORY = 0x00000010
_FILE_ATTRIBUTE_NORMAL = 0x00000080
_FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
_FILE_LIST_DIRECTORY = 0x00000001
_FILE_WRITE_DATA = 0x00000002
_FILE_TRAVERSE = 0x00000020
_FILE_READ_ATTRIBUTES = 0x00000080
_FILE_WRITE_ATTRIBUTES = 0x00000100
_DELETE = 0x00010000
_SYNCHRONIZE = 0x00100000
_FILE_SHARE_READ = 0x00000001
_FILE_SHARE_WRITE = 0x00000002
_OPEN_EXISTING = 3
_FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
_FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
_OBJ_CASE_INSENSITIVE = 0x00000040
_FILE_CREATE = 2
_FILE_DIRECTORY_FILE = 0x00000001
_FILE_SYNCHRONOUS_IO_NONALERT = 0x00000020
_FILE_NON_DIRECTORY_FILE = 0x00000040
_FILE_DISPOSITION_INFO_CLASS = 4
_DUPLICATE_SAME_ACCESS = 0x00000002
_FILE_CREATED = 2
_SDDL_REVISION_1 = 1
_SUPPORTED_FILE_MODES = frozenset({0o600, 0o644})


def _winerror(message: str, code: int | None = None) -> Win32SafeIOError:
    if code is None:
        code = ctypes.get_last_error()
    detail = ctypes.FormatError(code).strip() if code else "unknown Windows error"
    error = Win32SafeIOError(code, f"{message}: {detail}")
    error.winerror = code
    return error


def _nt_error(message: str, status: int) -> Win32SafeIOError:
    code = int(_ntdll.RtlNtStatusToDosError(status))
    return _winerror(message, code)


def _close_no_raise(handle: int | None) -> None:
    if handle not in (None, 0, _INVALID_HANDLE_VALUE):
        _kernel32.CloseHandle(handle)


def _extended_path(path: Path) -> str:
    text = os.path.abspath(os.fspath(path))
    if "\x00" in text:
        raise ValueError("Windows parent path contains NUL")
    if text.startswith("\\\\?\\"):
        return text
    if text.startswith("\\\\"):
        return "\\\\?\\UNC\\" + text[2:]
    return "\\\\?\\" + text


def _normalise_parent(parent: Path) -> Path:
    if not isinstance(parent, Path):
        parent = Path(parent)
    if any(part == ".." for part in parent.parts):
        raise ValueError("Windows output parent cannot contain parent traversal")
    return Path(os.path.abspath(os.fspath(parent)))


def _handle_information(handle: int, *, expect_directory: bool) -> tuple[int, int]:
    information = _BY_HANDLE_FILE_INFORMATION()
    if not _kernel32.GetFileInformationByHandle(handle, ctypes.byref(information)):
        raise _winerror("cannot inspect Windows output handle")
    attributes = int(information.dwFileAttributes)
    if attributes & _FILE_ATTRIBUTE_REPARSE_POINT:
        raise Win32SafeIOError("Windows output boundary cannot be a reparse point")
    is_directory = bool(attributes & _FILE_ATTRIBUTE_DIRECTORY)
    if is_directory != expect_directory:
        expected = "directory" if expect_directory else "regular file"
        raise Win32SafeIOError(f"Windows output handle is not a {expected}")
    if not expect_directory and (information.nFileSizeHigh or information.nFileSizeLow):
        raise Win32SafeIOError("new Windows output file was not empty")
    file_index = (int(information.nFileIndexHigh) << 32) | int(information.nFileIndexLow)
    return int(information.dwVolumeSerialNumber), file_index


def _python_handle_identity(handle: int) -> tuple[int, int]:
    process = _kernel32.GetCurrentProcess()
    duplicate = wintypes.HANDLE()
    if not _kernel32.DuplicateHandle(
        process, handle, process, ctypes.byref(duplicate), 0, False,
        _DUPLICATE_SAME_ACCESS,
    ):
        raise _winerror("cannot duplicate Windows output parent for identity checking")
    descriptor: int | None = None
    try:
        descriptor = msvcrt.open_osfhandle(
            int(duplicate.value), os.O_RDONLY | getattr(os, "O_BINARY", 0)
        )
        duplicate = wintypes.HANDLE()
        info = os.fstat(descriptor)
        return info.st_dev, info.st_ino
    except OSError as exc:
        raise Win32SafeIOError(
            "cannot bind Windows output parent to Python file identity"
        ) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        _close_no_raise(duplicate.value)


def _expected_python_identity(value: object) -> tuple[int, int]:
    if (not isinstance(value, tuple) or len(value) != 2
            or any(type(part) is not int for part in value)):
        raise ValueError("expected Windows parent identity must be a pair of integers")
    return value


def _open_parent(
    parent: Path,
    expected_python_identity: tuple[int, int] | None = None,
) -> tuple[int, tuple[int, int]]:
    access = _FILE_LIST_DIRECTORY | _FILE_TRAVERSE | _FILE_READ_ATTRIBUTES | _SYNCHRONIZE
    # Omitting FILE_SHARE_DELETE prevents the selected parent itself from
    # being renamed or deleted while the child transaction is active.
    handle = _kernel32.CreateFileW(
        _extended_path(parent), access, _FILE_SHARE_READ | _FILE_SHARE_WRITE,
        None, _OPEN_EXISTING,
        _FILE_FLAG_BACKUP_SEMANTICS | _FILE_FLAG_OPEN_REPARSE_POINT, None,
    )
    if handle == _INVALID_HANDLE_VALUE:
        raise _winerror("cannot open Windows output parent without following reparse points")
    try:
        native_identity = _handle_information(handle, expect_directory=True)
        if expected_python_identity is not None:
            expected_python_identity = _expected_python_identity(expected_python_identity)
            if _python_handle_identity(handle) != expected_python_identity:
                raise Win32SafeIOError(
                    "Windows output parent changed before its handle could be bound"
                )
        return handle, native_identity
    except BaseException:
        _close_no_raise(handle)
        raise


def _verify_path_parent_identity(
    parent: Path,
    expected_python_identity: tuple[int, int],
) -> None:
    """Reopen the path and compare it in the same identity domain as preflight."""
    verification, _ = _open_parent(parent, expected_python_identity)
    _close_no_raise(verification)


@contextmanager
def _security_descriptor(mode: int) -> Iterator[int]:
    if type(mode) is not int or mode not in _SUPPORTED_FILE_MODES:
        raise ValueError("Windows file mode must be exactly 0o600 or 0o644")
    # A protected DACL avoids silently inheriting broader write access.  The
    # owner, local system and administrators retain full control; 0644 also
    # grants authenticated users read access.  OWNER RIGHTS binds to the owner
    # assigned by the creating token, so no environment-derived username/SID is
    # involved.
    sddl = "D:P(A;;FA;;;SY)(A;;FA;;;BA)(A;;FA;;;OW)"
    if mode == 0o644:
        sddl += "(A;;FR;;;AU)"
    descriptor = wintypes.LPVOID()
    size = wintypes.ULONG()
    if not _advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(
        sddl, _SDDL_REVISION_1, ctypes.byref(descriptor), ctypes.byref(size)
    ):
        raise _winerror("cannot build the Windows output security descriptor")
    try:
        yield int(descriptor.value)
    finally:
        _kernel32.LocalFree(descriptor)


def _relative_create(
    parent_handle: int,
    leaf: str,
    *,
    directory: bool,
    security_descriptor: int,
) -> int:
    name_buffer = ctypes.create_unicode_buffer(leaf)
    byte_length = len(leaf.encode("utf-16-le"))
    name = _UNICODE_STRING(
        Length=byte_length,
        MaximumLength=byte_length + ctypes.sizeof(ctypes.c_wchar),
        Buffer=ctypes.cast(name_buffer, wintypes.LPWSTR),
    )
    attributes = _OBJECT_ATTRIBUTES(
        Length=ctypes.sizeof(_OBJECT_ATTRIBUTES),
        RootDirectory=parent_handle,
        ObjectName=ctypes.pointer(name),
        Attributes=_OBJ_CASE_INSENSITIVE,
        SecurityDescriptor=security_descriptor,
        SecurityQualityOfService=None,
    )
    io_status = _IO_STATUS_BLOCK()
    child = wintypes.HANDLE()
    access = _DELETE | _FILE_READ_ATTRIBUTES | _SYNCHRONIZE
    if not directory:
        access |= _FILE_WRITE_DATA | _FILE_WRITE_ATTRIBUTES
    options = _FILE_SYNCHRONOUS_IO_NONALERT
    options |= _FILE_DIRECTORY_FILE if directory else _FILE_NON_DIRECTORY_FILE
    file_attributes = _FILE_ATTRIBUTE_DIRECTORY if directory else _FILE_ATTRIBUTE_NORMAL
    status = int(_ntdll.NtCreateFile(
        ctypes.byref(child), access, ctypes.byref(attributes), ctypes.byref(io_status),
        None, file_attributes, 0, _FILE_CREATE, options, None, 0,
    ))
    if status < 0:
        raise _nt_error("cannot create Windows output without overwriting", status)
    if int(io_status.Information) != _FILE_CREATED:
        # Do not delete when the kernel did not confirm that this call created
        # the object: the returned handle must not be assumed to be ours.
        _close_no_raise(child.value)
        raise Win32SafeIOError(
            "Windows output create did not report a newly created object"
        )
    try:
        _handle_information(child.value, expect_directory=directory)
    except BaseException:
        # NtCreateFile returned this exact child handle.  Roll it back by
        # handle before closing; never look the name up again by path.
        try:
            _set_delete_pending(child.value, True)
        except OSError:
            pass
        _close_no_raise(child.value)
        raise
    return int(child.value)


def _set_delete_pending(handle: int, delete: bool) -> None:
    disposition = _FILE_DISPOSITION_INFO(1 if delete else 0)
    if not _kernel32.SetFileInformationByHandle(
        handle, _FILE_DISPOSITION_INFO_CLASS, ctypes.byref(disposition),
        ctypes.sizeof(disposition),
    ):
        action = "mark" if delete else "commit"
        raise _winerror(f"cannot {action} Windows output delete disposition")


def _write_all(handle: int, data: bytes) -> None:
    offset = 0
    maximum = 0xFFFFFFFF
    while offset < len(data):
        chunk = data[offset:offset + maximum]
        buffer = ctypes.create_string_buffer(chunk)
        written = wintypes.DWORD()
        if not _kernel32.WriteFile(
            handle, buffer, len(chunk), ctypes.byref(written), None
        ):
            raise _winerror("cannot write Windows output")
        count = int(written.value)
        if count < 1 or count > len(chunk):
            raise Win32SafeIOError("Windows output write made invalid forward progress")
        offset += count
    if not _kernel32.FlushFileBuffers(handle):
        raise _winerror("cannot flush Windows output")


def create_new_file(
    parent: Path,
    leaf: str,
    data: bytes,
    mode: int,
    *,
    expected_parent_identity: tuple[int, int],
) -> Path:
    """Create one new file relative to a locked Windows parent handle.

    Only modes ``0o600`` and ``0o644`` are accepted; both receive a protected
    DACL and the latter additionally grants authenticated users read access.
    Existing names are never replaced.  If an error occurs after delete-pending
    succeeds, closing the child handle performs rollback without a path lookup.
    If marking delete-pending itself fails, the function fails before writing
    any caller bytes and may conservatively leave an empty protected file.
    """

    expected_parent_identity = _expected_python_identity(expected_parent_identity)
    _require_windows()
    validate_leaf_name(leaf)
    if type(data) is not bytes:
        raise TypeError("Windows output data must be bytes")
    parent_path = _normalise_parent(parent)
    parent_handle: int | None = None
    child_handle: int | None = None
    delete_pending = False
    try:
        parent_handle, _ = _open_parent(
            parent_path, expected_parent_identity
        )
        with _security_descriptor(mode) as descriptor:
            child_handle = _relative_create(
                parent_handle, leaf, directory=False, security_descriptor=descriptor
            )
        _set_delete_pending(child_handle, True)
        delete_pending = True
        _write_all(child_handle, data)
        _verify_path_parent_identity(parent_path, expected_parent_identity)
        _set_delete_pending(child_handle, False)
        delete_pending = False
    finally:
        # When delete_pending is true, closing this exact handle is the only
        # rollback action.  Never perform cleanup by path.
        _close_no_raise(child_handle)
        _close_no_raise(parent_handle)
    if delete_pending:  # Defensive: normal exception flow has already escaped.
        raise Win32SafeIOError("Windows output remained delete-pending")
    return parent_path / leaf


def create_new_directory(
    parent: Path,
    leaf: str,
    *,
    expected_parent_identity: tuple[int, int],
) -> Path:
    """Create one private directory relative to a locked Windows parent handle."""

    expected_parent_identity = _expected_python_identity(expected_parent_identity)
    _require_windows()
    validate_leaf_name(leaf)
    parent_path = _normalise_parent(parent)
    parent_handle: int | None = None
    child_handle: int | None = None
    delete_pending = False
    try:
        parent_handle, _ = _open_parent(
            parent_path, expected_parent_identity
        )
        with _security_descriptor(0o600) as descriptor:
            child_handle = _relative_create(
                parent_handle, leaf, directory=True, security_descriptor=descriptor
            )
        _set_delete_pending(child_handle, True)
        delete_pending = True
        _verify_path_parent_identity(parent_path, expected_parent_identity)
        _set_delete_pending(child_handle, False)
        delete_pending = False
    finally:
        _close_no_raise(child_handle)
        _close_no_raise(parent_handle)
    if delete_pending:
        raise Win32SafeIOError("Windows output directory remained delete-pending")
    return parent_path / leaf


def profile_directory() -> Path:
    """Return the current user's Profile known folder without environment lookup."""

    _require_windows()
    # FOLDERID_Profile = {5E6C858F-0E22-4760-9AFE-EA3317B67173}
    folder_id = _GUID(
        0x5E6C858F, 0x0E22, 0x4760,
        (ctypes.c_ubyte * 8)(0x9A, 0xFE, 0xEA, 0x33, 0x17, 0xB6, 0x71, 0x73),
    )
    output = wintypes.LPWSTR()
    result = int(_shell32.SHGetKnownFolderPath(
        ctypes.byref(folder_id), 0, None, ctypes.byref(output)
    ))
    if result < 0:
        # HRESULT_FROM_WIN32 stores the useful code in the low 16 bits.
        code = result & 0xFFFF
        raise _winerror("cannot query the current Windows Profile directory", code)
    try:
        value = output.value
        if not value:
            raise Win32SafeIOError("Windows Profile known folder returned an empty path")
        return Path(value)
    finally:
        _ole32.CoTaskMemFree(output)

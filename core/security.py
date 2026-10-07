from __future__ import annotations

import hashlib
import secrets
import socket
import string
from typing import Dict


# الرموز المستخدمة عند توليد كلمات المرور.
DEFAULT_SYMBOLS = "!@#$%^&*()-_=+[]{}?"


def generate_password(length: int = 20, use_symbols: bool = True) -> str:
    """
    Generate a cryptographically secure random password.

    Args:
        length: Password length. Must be between 8 and 128.
        use_symbols: Whether to include symbols.

    Returns:
        A secure random password.

    Raises:
        TypeError: If length is not an integer.
        ValueError: If the length is outside the allowed range.
    """
    if not isinstance(length, int):
        raise TypeError("length must be an integer")

    if not 8 <= length <= 128:
        raise ValueError("length must be between 8 and 128")

    alphabet = string.ascii_letters + string.digits

    if use_symbols:
        alphabet += DEFAULT_SYMBOLS

    # نضمن وجود الأنواع الأساسية في كلمة المرور.
    required = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
    ]

    if use_symbols:
        required.append(secrets.choice(DEFAULT_SYMBOLS))

    remaining_count = length - len(required)

    remaining = [
        secrets.choice(alphabet)
        for _ in range(remaining_count)
    ]

    characters = required + remaining

    # خلط آمن باستخدام SystemRandom.
    secrets.SystemRandom().shuffle(characters)

    return "".join(characters)


def sha256_text(text: str) -> str:
    """
    Calculate SHA-256 hash for UTF-8 text.

    Args:
        text: Input text.

    Returns:
        Lowercase hexadecimal SHA-256 digest.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def check_connectivity(timeout: float = 3.0) -> bool:
    """
    Check whether the device can establish an outbound connection.

    Args:
        timeout: Connection timeout in seconds.

    Returns:
        True when a connection can be established, otherwise False.
    """
    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")

    try:
        with socket.create_connection(
            ("1.1.1.1", 53),
            timeout=timeout,
        ):
            return True

    except OSError:
        return False


def get_network_info() -> Dict[str, object]:
    """
    Return basic local network information.

    This does not scan other devices and does not perform
    network discovery.
    """
    hostname = socket.gethostname() or "Unknown"
    local_ip = "Unknown"
    online = False

    try:
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        ) as sock:
            sock.settimeout(3.0)
            sock.connect(("1.1.1.1", 53))

            local_ip = sock.getsockname()[0]

            if local_ip:
                online = not local_ip.startswith("127.")

    except OSError:
        # محاولة احتياطية للحصول على عنوان الجهاز المحلي.
        try:
            resolved_ip = socket.gethostbyname(hostname)

            if resolved_ip and not resolved_ip.startswith("127."):
                local_ip = resolved_ip

        except OSError:
            pass

    return {
        "hostname": hostname,
        "local_ip": local_ip,
        "online": online,
              }

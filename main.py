from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from threading import Thread

from kivy.app import App
from kivy.clock import mainthread
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from core.security import check_connectivity, generate_password, get_network_info, sha256_text


class DashboardScreen(Screen):
    pass


class NetworkScreen(Screen):
    pass


class ToolsScreen(Screen):
    pass


class LogsScreen(Screen):
    pass


class ShieldGuardApp(App):
    title = "ShieldGuard Mobile"

    app_status = StringProperty("Ready")
    network_status = StringProperty("Not checked")
    hostname = StringProperty("Unknown")
    local_ip = StringProperty("Unknown")
    generated_password = StringProperty("")
    hash_output = StringProperty("")
    logs_text = StringProperty("")

    def build(self):
        Builder.load_file(str(Path(__file__).with_name("shieldguard.kv")))
        self._log_file = Path(self.user_data_dir) / "shieldguard.log"
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_logs()
        self._log("Application started")
        return self.root

    def on_stop(self):
        self._log("Application closed")

    def _load_logs(self) -> None:
        try:
            if self._log_file.exists():
                self.logs_text = self._log_file.read_text(encoding="utf-8")[-12000:]
        except OSError:
            self.logs_text = ""

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        try:
            with self._log_file.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        except OSError:
            pass
        current = self.logs_text.rstrip()
        self.logs_text = (current + "\n" + line).strip()[-12000:]

    def go_to(self, screen_name: str) -> None:
        self.root.current = screen_name

    def refresh_network(self) -> None:
        self.app_status = "Checking network…"
        self.network_status = "Checking…"
        self._log("Network check started")
        Thread(target=self._network_worker, daemon=True).start()

    def _network_worker(self) -> None:
        try:
            details = get_network_info()
            online = details["online"]
            self._apply_network_result(online, details["hostname"], details["local_ip"], None)
        except Exception as exc:  # Defensive boundary for mobile runtime.
            self._apply_network_result(False, "Unknown", "Unknown", str(exc))

    @mainthread
    def _apply_network_result(
        self, online: bool, hostname_value: str, ip_value: str, error: str | None
    ) -> None:
        self.hostname = hostname_value or "Unknown"
        self.local_ip = ip_value or "Unknown"
        if error:
            self.network_status = "Check failed"
            self.app_status = "Network check finished with an error"
            self._log(f"Network check error: {error}")
        else:
            self.network_status = "Online" if online else "Offline"
            self.app_status = "Network check complete"
            self._log(f"Network status: {self.network_status}; IP: {self.local_ip}")

    def quick_connectivity_check(self) -> None:
        self.app_status = "Testing connectivity…"
        Thread(target=self._connectivity_worker, daemon=True).start()

    def _connectivity_worker(self) -> None:
        try:
            online = check_connectivity(timeout=3.0)
            self._apply_connectivity_result(online)
        except Exception as exc:
            self._apply_connectivity_result(False, str(exc))

    @mainthread
    def _apply_connectivity_result(self, online: bool, error: str | None = None) -> None:
        if error:
            self.app_status = "Connectivity test failed"
            self._log(f"Connectivity test error: {error}")
        else:
            self.app_status = "Connectivity: online" if online else "Connectivity: offline"
            self._log(f"Connectivity result: {'online' if online else 'offline'}")

    def make_password(self) -> None:
        tools = self.root.get_screen("tools")
        raw_length = tools.ids.password_length.text.strip()
        try:
            length = int(raw_length)
        except ValueError:
            length = 20
        length = max(8, min(64, length))
        tools.ids.password_length.text = str(length)

        use_symbols = tools.ids.include_symbols.active
        self.generated_password = generate_password(length=length, use_symbols=use_symbols)
        self.app_status = "Secure password generated"
        self._log(f"Generated a {length}-character password")

    def copy_password(self) -> None:
        if not self.generated_password:
            self.app_status = "Generate a password first"
            return
        Clipboard.copy(self.generated_password)
        self.app_status = "Password copied to clipboard"
        self._log("Password copied to clipboard")

    def hash_text(self) -> None:
        tools = self.root.get_screen("tools")
        text = tools.ids.hash_input.text
        self.hash_output = sha256_text(text)
        self.app_status = "SHA-256 calculated"
        self._log("SHA-256 hash calculated")

    def copy_hash(self) -> None:
        if not self.hash_output:
            self.app_status = "Calculate a hash first"
            return
        Clipboard.copy(self.hash_output)
        self.app_status = "Hash copied to clipboard"
        self._log("SHA-256 hash copied to clipboard")

    def clear_hash(self) -> None:
        tools = self.root.get_screen("tools")
        tools.ids.hash_input.text = ""
        self.hash_output = ""
        self.app_status = "Hash tool cleared"

    def clear_logs(self) -> None:
        try:
            self._log_file.unlink(missing_ok=True)
        except OSError:
            pass
        self.logs_text = ""
        self.app_status = "Local log cleared"
        self._log("Log cleared")


if __name__ == "__main__":
    ShieldGuardApp().run()

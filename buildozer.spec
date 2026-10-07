[app]

title = ShieldGuard Mobile
package.name = shieldguard
package.domain = org.shieldguard

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,json
source.exclude_dirs = tests,.github,.buildozer,bin

version = 2.2.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

# Current Android target/minimum settings used by the modern Buildozer/p4a toolchain.
android.api = 36
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
android.enable_androidx = True
android.permissions = INTERNET

# Keep the build deterministic by using the released Buildozer toolchain in CI.
# p4a chooses a compatible SDK/NDK combination for this Buildozer release.

[buildozer]
log_level = 2
warn_on_root = 1

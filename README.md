# ShieldGuard Mobile 2.2.0

A small defensive Android security toolkit built with Python + Kivy + Buildozer.

## Included features

- Basic local network status, hostname, and local IP information.
- A cryptographically strong password generator using Python's `secrets` module.
- SHA-256 hashing for text entered by the user.
- A local activity log stored inside the app's private data directory.
- Android build configuration and a GitHub Actions workflow that produces a debug APK artifact.

This project intentionally does **not** perform port scanning, host discovery, credential attacks, packet injection, exploitation, persistence, or other offensive network actions.

## Project layout

```text
ShieldGuard-Mobile/
├── .github/workflows/android.yml
├── core/__init__.py
├── core/security.py
├── tests/test_security.py
├── buildozer.spec
├── main.py
├── requirements.txt
└── shieldguard.kv
```

## Local desktop test

Install Python 3 and Kivy, then:

```bash
python -m pip install -r requirements.txt
python main.py
```

Run the pure-Python tests with:

```bash
python -m pytest -q
```

## GitHub Actions build

Push this project to a GitHub repository, keep the workflow file at `.github/workflows/android.yml`, and run **Build Android APK** from the Actions tab. The generated APK is uploaded as the `ShieldGuard-Mobile-debug` artifact.

The workflow deliberately uses current GitHub Actions releases and pins Buildozer 1.6.0 plus the Cython version recommended by the Buildozer project for its Android packaging toolchain.

## Important

The build creates a **debug** APK for testing. Before any public distribution, the Android package should be signed and the release configuration reviewed.

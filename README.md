# Password Manager & 2FA

A Windows 95-styled password manager with password generation, encrypted vault storage, and TOTP two-factor authentication.


## Features

- **Password Generator** — configurable length, character sets, strength indicator
- **Encrypted Vault** — AES-256-GCM encrypted local storage with master password
- **TOTP/2FA** — Time-based one-time password codes with countdown timer
- **Win95 UI** — Custom-drawn title bar, borders, and 3D buttons
- **Auto-Lock** — Vault locks after 2 minutes of inactivity
- **Multi-language** — Russian, English, Chinese

## Requirements

- Python 3.10+
- Dependencies: `cryptography` (install via `pip install -r requirements.txt`)

## Usage

```
python run.py
```

On first launch, you'll be prompted to create a master password. This password encrypts all stored credentials.

## Build

```
pyinstaller PasswordManager.spec
```

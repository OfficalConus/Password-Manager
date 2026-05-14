import string
import os

CHAR_SETS = {
    "lowercase": string.ascii_lowercase,
    "uppercase": string.ascii_uppercase,
    "digits": string.digits,
    "special": "!@#$%^&*()-_=+[]{}|;:,.<>?/~`",
}

CHAR_ORDER = ["lowercase", "uppercase", "digits", "special"]

VAULT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "PasswordManager")
os.makedirs(VAULT_DIR, exist_ok=True)
VAULT_FILE = os.path.join(VAULT_DIR, "vault.json")

ICON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")

# Win95 palette
W95_BG = "#C0C0C0"
W95_BTN = "#C0C0C0"
W95_HL = "#FFFFFF"
W95_SH = "#808080"
W95_DSH = "#404040"
W95_FG = "#000000"
W95_INPUT = "#FFFFFF"
W95_TITLE = "#000080"
W95_BTNFACE = "#C0C0C0"

FONT = ("Terminal", 10)
FONT_BOLD = ("Terminal", 10, "bold")
FONT_SM = ("Terminal", 9)
FONT_LG = ("Terminal", 14, "bold")
FONT_XL = ("Terminal", 16, "bold")
FONT_MONO = ("Terminal", 11)

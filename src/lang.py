_lang = "RU"

SUPPORTED = {"RU": "Русский", "EN": "English", "ZH": "中文"}


def set_lang(lang):
    global _lang
    if lang in SUPPORTED:
        _lang = lang


def get_lang():
    return _lang


def tr(key):
    return STRINGS.get(key, {}).get(_lang, STRINGS.get(key, {}).get("RU", key))


CHAR_LABELS = {
    "lowercase": {"RU": "строчные", "EN": "Lowercase", "ZH": "小写字母"},
    "uppercase": {"RU": "ЗАГЛАВНЫЕ", "EN": "Uppercase", "ZH": "大写字母"},
    "digits": {"RU": "цифры", "EN": "Digits", "ZH": "数字"},
    "special": {"RU": "спецсимволы", "EN": "Special", "ZH": "特殊字符"},
}

STRENGTH_LABELS = {
    0: {"RU": "Слабый", "EN": "Weak", "ZH": "弱"},
    1: {"RU": "Средний", "EN": "Medium", "ZH": "中"},
    2: {"RU": "Надёжный", "EN": "Strong", "ZH": "强"},
    3: {"RU": "Очень надёжный", "EN": "Very Strong", "ZH": "非常强"},
}


def tr_char(key):
    return CHAR_LABELS.get(key, {}).get(_lang, key)


def tr_strength(idx):
    return STRENGTH_LABELS.get(idx, {}).get(_lang, "")


STRINGS = {
    "app_title": {"RU": "Менеджер паролей и 2FA", "EN": "Password Manager & 2FA", "ZH": "密码管理器与2FA"},
    "tab_gen": {"RU": "Генератор", "EN": "Generator", "ZH": "生成器"},
    "tab_vault": {"RU": "Пароли", "EN": "Passwords", "ZH": "密码"},
    "tab_2fa": {"RU": "2FA", "EN": "2FA", "ZH": "2FA"},
    "gen_title": {"RU": "Генератор паролей", "EN": "Password Generator", "ZH": "密码生成器"},
    "gen_length": {"RU": "Длина пароля:", "EN": "Password length:", "ZH": "密码长度:"},
    "gen_charset": {"RU": "Набор символов:", "EN": "Character set:", "ZH": "字符集:"},
    "gen_password": {"RU": "Пароль:", "EN": "Password:", "ZH": "密码:"},
    "gen_strength": {"RU": "Надёжность:", "EN": "Strength:", "ZH": "强度:"},
    "gen_generate": {"RU": "Сгенерировать", "EN": "Generate", "ZH": "生成"},
    "gen_copy": {"RU": "Копировать", "EN": "Copy", "ZH": "复制"},
    "gen_copied": {"RU": "Скопировано!", "EN": "Copied!", "ZH": "已复制!"},
    "gen_save": {"RU": "Сохранить", "EN": "Save", "ZH": "保存"},
    "gen_save_title": {"RU": "Название / сайт:", "EN": "Name / site:", "ZH": "名称/网站:"},
    "gen_save_btn": {"RU": "Сохранить", "EN": "Save", "ZH": "保存"},
    "gen_saved": {"RU": "Пароль сохранён!", "EN": "Password saved!", "ZH": "密码已保存!"},
    "gen_no_chars": {"RU": "Выберите хотя бы один набор символов.", "EN": "Select at least one character set.", "ZH": "请至少选择一个字符集。"},
    "gen_no_name": {"RU": "Введите название!", "EN": "Enter a name!", "ZH": "请输入名称!"},
    "vault_title": {"RU": "Сохранённые пароли", "EN": "Saved Passwords", "ZH": "已保存的密码"},
    "vault_locked_title": {"RU": "Хранилище зашифровано", "EN": "Vault Encrypted", "ZH": "保险库已加密"},
    "vault_locked_desc": {"RU": "Используйте кнопку «Сохранить»\nв генераторе или вкладку 2FA\nчтобы разблокировать", "EN": "Use the «Save» button\nin the generator or the 2FA tab\nto unlock", "ZH": "使用生成器中的「保存」按钮\n或2FA标签页来解锁"},
    "vault_add": {"RU": "Добавить", "EN": "Add", "ZH": "添加"},
    "vault_copy": {"RU": "Копировать", "EN": "Copy", "ZH": "复制"},
    "vault_edit": {"RU": "Редактировать", "EN": "Edit", "ZH": "编辑"},
    "vault_delete": {"RU": "Удалить", "EN": "Delete", "ZH": "删除"},
    "vault_change_mp": {"RU": "Сменить пароль", "EN": "Change Master PW", "ZH": "更改主密码"},
    "vault_reset": {"RU": "Сбросить", "EN": "Reset", "ZH": "重置"},
    "vault_lock": {"RU": "Заблокировать", "EN": "Lock", "ZH": "锁定"},
    "vault_add_title": {"RU": "Добавить пароль", "EN": "Add Password", "ZH": "添加密码"},
    "vault_add_label": {"RU": "Название / сайт:", "EN": "Name / site:", "ZH": "名称/网站:"},
    "vault_add_pwd": {"RU": "Пароль:", "EN": "Password:", "ZH": "密码:"},
    "vault_add_btn": {"RU": "Добавить", "EN": "Add", "ZH": "添加"},
    "vault_added": {"RU": "Пароль добавлен!", "EN": "Password added!", "ZH": "密码已添加!"},
    "vault_edit_title": {"RU": "Редактировать пароль", "EN": "Edit Password", "ZH": "编辑密码"},
    "vault_edit_label": {"RU": "Название:", "EN": "Name:", "ZH": "名称:"},
    "vault_edit_pwd": {"RU": "Пароль:", "EN": "Password:", "ZH": "密码:"},
    "vault_edit_btn": {"RU": "Сохранить", "EN": "Save", "ZH": "保存"},
    "vault_edited": {"RU": "Пароль обновлён!", "EN": "Password updated!", "ZH": "密码已更新!"},
    "vault_delete_confirm": {"RU": "Удалить пароль для", "EN": "Delete password for", "ZH": "删除密码"},
    "vault_empty": {"RU": "Хранилище пусто", "EN": "Vault is empty", "ZH": "保险库为空"},
    "vault_copied": {"RU": "Пароль скопирован!", "EN": "Password copied!", "ZH": "密码已复制!"},
    "fill_all": {"RU": "Заполните все поля!", "EN": "Fill in all fields!", "ZH": "请填写所有字段!"},
    "confirm_delete": {"RU": "Подтверждение", "EN": "Confirm", "ZH": "确认"},
    "totp_title": {"RU": "Двухфакторная аутентификация (TOTP)", "EN": "Two-Factor Auth (TOTP)", "ZH": "双因素认证 (TOTP)"},
    "totp_add_key": {"RU": "Добавить ключ", "EN": "Add Key", "ZH": "添加密钥"},
    "totp_label": {"RU": "Название:", "EN": "Label:", "ZH": "标签:"},
    "totp_secret": {"RU": "Secret key:", "EN": "Secret key:", "ZH": "密钥:"},
    "totp_add_btn": {"RU": "Добавить", "EN": "Add", "ZH": "添加"},
    "totp_empty": {"RU": "Нет добавленных ключей\n\nНажмите «Добавить ключ» чтобы начать", "EN": "No keys added\n\nClick «Add Key» to start", "ZH": "未添加密钥\n\n点击「添加密钥」开始"},
    "totp_copy": {"RU": "Копировать", "EN": "Copy", "ZH": "复制"},
    "totp_delete": {"RU": "Удалить", "EN": "Delete", "ZH": "删除"},
    "totp_delete_confirm": {"RU": "Удалить ключ", "EN": "Delete key", "ZH": "删除密钥"},
    "totp_invalid_secret": {"RU": "Неверный Secret key (должен быть в Base32)!", "EN": "Invalid Secret key (must be Base32)!", "ZH": "密钥无效（必须是Base32格式）！"},
    "totp_refresh": {"RU": "Обновление через {} сек.", "EN": "Refresh in {} sec.", "ZH": "{} 秒后刷新"},
    "mp_change_title": {"RU": "Смена мастер-пароля", "EN": "Change Master Password", "ZH": "更改主密码"},
    "mp_current": {"RU": "Текущий пароль:", "EN": "Current password:", "ZH": "当前密码:"},
    "mp_new": {"RU": "Новый пароль:", "EN": "New password:", "ZH": "新密码:"},
    "mp_repeat": {"RU": "Повторите новый:", "EN": "Repeat new:", "ZH": "重复新密码:"},
    "mp_change_btn": {"RU": "Сменить", "EN": "Change", "ZH": "更改"},
    "mp_changed": {"RU": "Мастер-пароль изменён!", "EN": "Master password changed!", "ZH": "主密码已更改!"},
    "mp_wrong": {"RU": "Неверный текущий пароль!", "EN": "Wrong current password!", "ZH": "当前密码错误!"},
    "mp_no_match": {"RU": "Новые пароли не совпадают!", "EN": "New passwords do not match!", "ZH": "新密码不匹配!"},
    "mp_too_short": {"RU": "Пароль должен быть минимум 4 символа!", "EN": "Password must be at least 4 characters!", "ZH": "密码至少需要4个字符！"},
    "unlock_title_set": {"RU": "Установка мастер-пароля", "EN": "Set Master Password", "ZH": "设置主密码"},
    "unlock_title_in": {"RU": "Ввод мастер-пароля", "EN": "Enter Master Password", "ZH": "输入主密码"},
    "unlock_desc_set": {"RU": "Создайте мастер-пароль\nдля шифрования хранилища:", "EN": "Create a master password\nto encrypt the vault:", "ZH": "创建主密码\n以加密保险库:"},
    "unlock_desc_in": {"RU": "Введите мастер-пароль\nдля разблокировки хранилища:", "EN": "Enter your master password\nto unlock the vault:", "ZH": "输入主密码\n以解锁保险库:"},
    "unlock_btn_set": {"RU": "Готово", "EN": "Done", "ZH": "完成"},
    "unlock_btn_in": {"RU": "Разблокировать", "EN": "Unlock", "ZH": "解锁"},
    "unlock_wrong": {"RU": "Неверный мастер-пароль!", "EN": "Wrong master password!", "ZH": "主密码错误！"},
    "autolock_title": {"RU": "Автоблокировка", "EN": "Auto-Lock", "ZH": "自动锁定"},
    "autolock_msg": {"RU": "Хранилище заблокировано (прошло 2 минуты).\nВведите мастер-пароль для продолжения.", "EN": "Vault locked (2 minutes passed).\nEnter your master password to continue.", "ZH": "保险库已锁定（已过2分钟）。\n请输入主密码继续。"},
    "save_error": {"RU": "Ошибка сохранения", "EN": "Save Error", "ZH": "保存错误"},
    "save_error_msg": {"RU": "Не удалось сохранить vault.json:\n{}", "EN": "Failed to save vault.json:\n{}", "ZH": "保存 vault.json 失败：\n{}"},
    "reset_title": {"RU": "Сброс хранилища", "EN": "Reset Vault", "ZH": "重置保险库"},
    "reset_msg": {"RU": "ВСЕ сохранённые пароли и 2FA-ключи будут удалены!\nПродолжить?", "EN": "ALL saved passwords and 2FA keys will be deleted!\nContinue?", "ZH": "所有保存的密码和2FA密钥将被删除！\n继续？"},
    "reset_done": {"RU": "Хранилище сброшено. При следующем сохранении будет создан новый мастер-пароль.", "EN": "Vault reset. A new master password will be created on next save.", "ZH": "保险库已重置。下次保存时将创建新主密码。"},
    "ready": {"RU": "Готово", "EN": "Done", "ZH": "完成"},
    "error": {"RU": "Ошибка", "EN": "Error", "ZH": "错误"},
    "seconds_abbr": {"RU": "с", "EN": "s", "ZH": "秒"},
    "tab_notes": {"RU": "Заметки", "EN": "Notes", "ZH": "笔记"},
    "notes_title": {"RU": "Коды восстановления / Заметки", "EN": "Recovery Codes / Notes", "ZH": "恢复代码/笔记"},
    "notes_save": {"RU": "Сохранить", "EN": "Save", "ZH": "保存"},
    "notes_load": {"RU": "Загрузить", "EN": "Load", "ZH": "加载"},
    "notes_clear": {"RU": "Очистить", "EN": "Clear", "ZH": "清除"},
    "notes_saved": {"RU": "Сохранено", "EN": "Saved", "ZH": "已保存"},
    "notes_loaded": {"RU": "Загружено", "EN": "Loaded", "ZH": "已加载"},
    "notes_cleared": {"RU": "Очищено", "EN": "Cleared", "ZH": "已清除"},
    "notes_save_err": {"RU": "Ошибка сохранения", "EN": "Save error", "ZH": "保存错误"},
    "notes_load_err": {"RU": "Ошибка загрузки (неверный пароль?)", "EN": "Load error (wrong password?)", "ZH": "加载错误（密码错误？）"},
    "notes_clear_confirm": {"RU": "Очистить все заметки?", "EN": "Clear all notes?", "ZH": "清除所有笔记？"},
    "notes_locked": {"RU": "Сначала разблокируйте хранилище", "EN": "Unlock the vault first", "ZH": "请先解锁保险库"},
}

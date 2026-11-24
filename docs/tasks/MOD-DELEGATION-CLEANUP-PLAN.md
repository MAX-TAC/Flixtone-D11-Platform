# План вычистки: пункты MOD, ведущие в китайское меню

Дата: 2026-11-24.

---

## 1. Механизм «издевательства»

```java
// OemHardwareDelegatedSettings.java:19
private static final String ACTIVITY = "com.android.tv.settings.uicustom.MainActivity";

// :34-44
static Intent mainActivityIntent(Context context, String action) {
    ComponentName component = new ComponentName(context, ACTIVITY);   // ← ЖЁСТКО
    ...
    return new Intent(action).setComponent(component);                 // ← Куда бы ни шли
}
```

**Производитель подменил обработку стандартных Android-экшенов** своим меню.
`android.settings.PICTURE_SETTINGS` должен вести в AOSP Settings, но из-за
явного `setComponent()` ведёт в `uicustom.MainActivity`.

---

## 2. Полный список пунктов MOD, ведущих в китайское меню

| # | Ключ | Заголовок | Action | Раздел |
|---|---|---|---|---|
| 1 | `projectorsoft_firmware_update_oem` | Обновление прошивки | `DEVICE_INFO_SETTINGS` | Система |
| 2 | `projectorsoft_sources_oem` | Выбор источника и настройки HDMI | `dev.projectorsoft.settings.SOURCES` | Источники |
| 3 | `projectorsoft_boot_application_oem` | Приложение при включении | `SOURCES` | Источники |
| 4 | `projectorsoft_hdmi_game_oem` | Игровой режим HDMI | `SOURCES` | Источники |
| 5 | `projectorsoft_hdmi_cec_oem` | HDMI-CEC · расширенные настройки | `SOURCES` | Источники |
| 6 | `projectorsoft_picture_oem` | Редактировать изображение | `PICTURE_SETTINGS` | Изображение |
| 7 | `projectorsoft_sound_oem` | Дополнительные настройки звука | `SOUND_SETTINGS` | Звук |

**Плюс:**
- `OemRootMenuHook:28,44` — `mainActivityIntent()` для корневых ссылок
- `OemEarcDelegatedPreference:41` — `SOUND_SETTINGS` для eARC
- `OemSoundPanel:43` — `installSoundLink`
- `OemProjectionPanel:63` — `SETTINGS`

---

## 3. Замена каждого пункта

| # | Сейчас | Заменить на | Есть в MOD? |
|---|---|---|---|
| 1 | китайское OTA | прямой запуск `com.rjpj.yunota` | ❌ написать |
| 2 | китайский выбор источника | **наш** экран «Источники» | ✅ `OemHdmiPortInfo` |
| 3 | китайский выбор приложения | **наш** `OemPowerOnAppHook` | ✅ |
| 4 | китайский игровой режим | **наш** `OemGameModeHook` | ✅ |
| 5 | китайский CEC | **наш** `OemHdmiCecHook` / `CecAutoOff8054` | ✅ |
| 6 | китайское изображение | **наш** `OemInlineSlidersHook.installPicture` | ✅ |
| 7 | китайский звук | **наш** `OemSoundPanel` | ✅ |

**Вывод: 6 из 7 пунктов уже имеют собственную реализацию в MOD.**
Нужно только перестать переадресовывать.

---

## 4. План изменений

### 4.1. Убрать `mainActivityIntent()`

Заменить на специализированные методы:

```java
// Вместо: Intent к uicustom.MainActivity
// Сделать: прямые вызовы наших хуков

// Было:
add(context, category, pref, "projectorsoft_picture_oem",
    "Редактировать изображение", "...",
    "android.settings.PICTURE_SETTINGS", 211);

// Стало: пункта нет вообще, потому что
// OemInlineSlidersHook.installPicture() уже добавляет ползунки
```

### 4.2. Что удалить полностью

```java
OemHardwareDelegatedSettings.installSystemLinks()      // кроме OTA-ссылки
OemHardwareDelegatedSettings.installSourceLinks()      // всё дублируется
OemHardwareDelegatedSettings.installPictureLink()      // дубль
OemHardwareDelegatedSettings.installSoundLink()        // дубль
OemProjectionPanel:63 → mainActivityIntent("SETTINGS")  // убрать
OemRootMenuHook:28,44 → mainActivityIntent()            // убрать
```

### 4.3. Что оставить, но перенацелить

| Функция | Куда |
|---|---|
| Обновление прошивки | `com.rjpj.yunota` (прямой intent) |
| OTA-cсылка в System | туда же |

---

## 5. Риски

| Риск | Мера |
|---|---|
| `com.rjpj.yunota` может не экспортировать Activity | проверить `dumpsys package`, использовать `MAIN` action |
| Удаление `installSourceLinks` может убрать нужный HDMI-пункт | проверить, что `OemHdmiPortInfo` покрывает |
| `OemDelegatedMenuPolicy` может блокировать | он проверяет `exposeFirmwareUpdates`, оставить |
| Удаление пункта «Игровой режим HDMI» | `OemGameModeHook` должен быть установлен раньше |

---

## 6. Порядок

1. Проверить, что каждый «наш» хук **действительно добавлен** в соответствующую категорию.
2. Закомментировать вызовы `OemHardwareDelegatedSettings.*`.
3. Перенацелить OTA на `com.rjpj.yunota`.
4. Собрать, установить, проверить, что пункты не пропали, а ведут внутрь MOD.

---

## 7. Как проверить результат

| Проверка | Ожидание |
|---|---|
| Открыть «Изображение» | ползунки MOD, **не** китайское меню |
| Открыть «Звук» | `OemSoundPanel`, **не** китайское меню |
| Открыть «Источники» | HDMI-порты MOD, **не** китайское меню |
| Нажать «Обновление прошивки» | открывается OTA-приложение |
| Прожать все пункты подряд | **ни один** не ведёт в `uicustom.MainActivity` |
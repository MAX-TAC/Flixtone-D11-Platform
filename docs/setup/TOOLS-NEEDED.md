# Чего не хватает для работы над проектором

Дата: 2026-11-25. Составлено по факту проверки машины (`Get-Command`, реестр SDK).

---

## Что уже есть

| Инструмент | Версия / путь |
|---|---|
| Java JDK | 21.0.13.1 — `C:\Program Files\Microsoft\jdk-21.0.13.102-hotspot` |
| javac | 21 — работает |
| git | `C:\Program Files\Git\cmd\git.exe` |
| git-lfs | есть |
| adb | `C:\Program Files\platform-tools\adb.exe` (8.2 МБ) |
| winget | `C:\Users\a804483\AppData\Local\Microsoft\WindowsApps\winget.exe` |

## Чего НЕТ (по важности)

### 1. Android SDK — **критично**

Без него нельзя **собрать APK локально**. Каждая сборка идёт через GitHub Actions
(~2–5 минут), и ошибку видно только после загрузки логов. Отсюда все мучения.

Нужно:
```
platform-tools       (adb, fastboot)
build-tools;33.0.3   (aapt2, apksigner, zipalign, d8)
platforms;android-33 (android.jar)
cmdline-tools        (sdkmanager)
```

**Установка:**
```powershell
winget install Google.AndroidStudio --accept-package-agreements --accept-source-agreements
```
или только командные инструменты (легче, ~500 МБ):
```powershell
New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\Android\Sdk" | Out-Null
winget install Google.PlatformTools
```
Затем через `sdkmanager`:
```powershell
sdkmanager "platforms;android-33" "build-tools;33.0.3" "platform-tools"
```

### 2. apktool — **критично**

Декомпиляция и сборка APK. Сейчас сборка APK — это `apktool d` → правка smali →
`apktool b`. Без него я не вижу, что именно попадает в APK.

**Установка:**
```powershell
winget install --id apktool --accept-package-agreements --accept-source-agreements
```
Если нет в winget — скачать `apktool_2.11.1.jar` с
https://github.com/iBotPeaches/Apktool/releases и положить в `C:\tools\apktool\`.

Обёртка `apktool.cmd`:
```cmd
@echo off
java -jar C:\tools\apktool\apktool_2.11.1.jar %*
```

### 3. jadx — **критично**

Чтение DEX в читаемый Java. Сейчас я извлекаю строки самописным парсером —
это даёт только имена, но не логику. С jadx я увижу **код классов**.

**Установка:**
```powershell
winget install --id skylot.jadx --accept-package-agreements --accept-source-agreements
```

### 4. Python 3 (настоящий) — **критично**

Сейчас `python3 --version` печатает просто `Python` — это **Store-заглушка**,
не работает. А CI-скрипты (`tools/patch_*.py`, `compose_brightness_v3_apk.py`)
написаны на Python 3.

**Установка:**
```powershell
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
```
Затем **отключить** Store-заглушки: Параметры → Приложения → Дополнительные
параметры приложений → Псевдонимы выполнения приложений → выключить
`python.exe` и `python3.exe`.

Проверка:
```powershell
python --version   # должно быть Python 3.12.x
```

### 5. 7-Zip — желательно

Для работы с большими архивами (`super.img` 2.1 ГБ, `flixtone_backup.zip` 2 ГБ).

```powershell
winget install 7zip.7zip --accept-package-agreements --accept-source-agreements
```

### 6. Android Studio — опционально

Даёт визуальный просмотр layout'ов и удобный SDK Manager.
Тяжёлый (~3 ГБ). Если только ради SDK — не нужно, хватит п.1.

---

## Одной командой (копировать целиком)

```powershell
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
winget install 7zip.7zip --accept-package-agreements --accept-source-agreements
winget install --id skylot.jadx --accept-package-agreements --accept-source-agreements
winget install --id apktool --accept-package-agreements --accept-source-agreements
winget install Google.AndroidStudio --accept-package-agreements --accept-source-agreements
```

После установки — **перезапустить терминал**, чтобы обновился PATH.

---

## Что это даст на практике

| Сейчас | После установки |
|---|---|
| Сборка APK = 2–5 мин CI, ошибку видно в логах | Сборка локально = 10–20 сек |
| Правки DEX вслепую | jadx показывает код классов |
| Нельзя проверить, что в APK | apktool разбирает APK до smali |
| Python-скрипты только в CI | Скрипты работают локально |

**Главное:** цикл «правка → сборка → проверка» сократится с 5 минут до 30 секунд,
и я перестану отдавать не те сборки.

---

## Про DSH-плагины

Ничего дополнительно ставить **не нужно**. Уже работают:
- ADB-канал к проектору
- Chrome для чтения логов CI
- Файловые операции в рабочей папке

Если понадобится — можно добавить плагин для скриншотов устройства прямо в чат,
но это удобство, а не необходимость.
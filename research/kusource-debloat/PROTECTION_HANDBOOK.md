# ХЭНДБУК: Protection (бывш. KuSourceRJ / com.coolux.source) — полный итог работ

Дата фиксации: 2026-11-27. Владелец: MAX-TAC.
Этот документ — **единый источник правды** по приложению. При возврате к работе читать отсюда.

---

## 0. Краткая сводка (TL;DR)

- `com.coolux.source` (имя в системе было «Source», теперь «Protection») — **системный фоновый сервис** проектора FlixTone D11 (8054): термоконтроль, вентиляторы, яркость, защита от перегрева/пыли.
- Вырезан весь заводской мусор (88+16 файлов smali): тесты `testcast.*`, дубли MOD, DRM-проверка, aging-механизм.
- Осталось 7 компонентов: `TimeService` + 2 Receiver (`BootupReceiver`, `BrightReceiver`) + 3 Activity (перегрев/вентилятор/пыль) + provider.
- **Установка на устройство НЕ выполнена** — блокируется флагом `PERSISTENT` (см. §7). Тестирование отложено до пересборки super.img.

---

## 1. Артефакты (файлы)

| Файл | Назначение |
|---|---|
| `_analysis/Protection-5.3-final.apk` | **финальный подписанный APK** (без persistent, versionCode 42) |
| `_analysis/kusource_decoded/` | рабочая декомпиляция (apktool) — **источник правок** |
| `_analysis/kusource_decoded_ORIGINAL_BACKUP/` | бэкап исходной декомпиляции (для отката) |
| `_analysis/kusource_verify/` | декомпиляция собранного APK (для проверки) |
| `_analysis/keys/platform.pk8` + `platform.x509.pem` | публичный AOSP platform testkey (SHA `c8a2e9bc…`) |
| `_analysis/trdmiddle.apk` / `trdservice.apk` | декомпиляция TRD-фреймворка (для чтения температуры) |
| `_analysis/KUSOURCE_DEBLOAT_PLAN.md` | план вырезки |
| `_analysis/KUSOURCE_DEBLOAT_REPORT.md` | отчёт по вырезке |

**Параметры финального APK:**
- package `com.coolux.source`, versionCode **42**, versionName 5.3
- minSdk 28, targetSdk 33
- label **`Protection`** (все локали), иконка «термометр+вентилятор»
- подпись: platform AOSP testkey `c8a2e9bc…` (совпадает с оригиналом), схема v3
- `android:persistent` **удалён** (был `true`)
- SHA-256: `2FD21663E9DB8F8F146B998DD3A340BAEA9B4AD89ECDF0A3017779B1B7691FCA`

---

## 2. Что сделано (хронология правок)

### Этап 1 — вырезка основного мусора (88 файлов)
Удалено:
- `testcast.*` — 17 заводских тестов + `MyTestActivity`
- `MainActivity` (ярлык выбора источника), `BootSoureActivity(+Old)`
- `VoiceActivity` + `VoiceUtils` (звук кнопок)
- `AllAppAutoActivity` + `AllAppAutoAdapter` + `UtilsLogic*` (приложение при запуске)
- `AutomaticAdmissionActivity` (автоподача сигнала)
- `AuthorizationActivity` (DRM-тупик)
- вычищено: `myHttp`/`isShield`/`authorizationIntent` из `TimeService`; `TimeService$13`
- вычищено: `agingTest`/`rebootStart`/`startAgingIntent` из `BootupReceiver`

### Этап 2 — дубли MOD (16 файлов)
Удалено: `BrightActivity`, `KeystoneActivity`, `ProjectModelActivity`, `PoweronModeActivity`, `RestoreActivity`, `ScreensaverReceiver`.
Проверено: MOD (exact8054) их **не** вызывает (яркость через `BrightReceiver`, трапеция через `com.rjpj.tcorrection`).

### Этап 3 — ребрендинг + перевод
- label → `Protection`, иконка → термометр+вентилятор (mipmap 48–192px)
- перевод 12 строк на русский (`fan_detection_error*`, `temperature_shutdown*`, `temperature_error`, `dusproof_title*`)

### Этап 4 — попытка установки (заблокировано)
Причина и решение — см. §7.

---

## 3. Финальный состав (7 компонентов)

| Компонент | Тип | Роль |
|---|---|---|
| `TimeService` | Service | ядро: опрос датчиков раз в минуту (TIME_TICK) |
| `BootupReceiver` | Receiver | старт службы при BOOT_COMPLETED + стартовая яркость |
| `BrightReceiver` | Receiver | приём `com.action.brightReceiver` + `brightModel` → смена яркости |
| `HighTemperatureActivity` | Activity | экран перегрева, отсчёт 10 с → `reboot -p` |
| `FanDetectionActivity` | Activity | экран неисправности вентиляторов |
| `DustproofActivity` | Activity | напоминание о чистке фильтра |
| `InitializationProvider` | Provider | AndroidX startup (служебный) |

---

## 4. Датчики и как читать температуру (ВАЖНО для MOD)

### Путь (проверен по коду KuSource):
```java
// Способ 1 — SDK (классы ВШИТЫ в KuSource dex):
com.trd.sdk.TrdSystemManager.getInstance().getTemperatureCtrl()
    .getTemperatueLED();   // температура LED
    .getTemperatueLCD();   // температура матрицы

// Способ 2 — binder (если SDK не вшит):
android.os.IBinder binder = com.trd.common.TrdContext.getSystemService("TrdSystemService");
com.trd.framework.ITrdSystemService svc =
    com.trd.framework.ITrdSystemService$Stub.asInterface(binder);
com.trd.framework.ITemperatureCtrl temp = svc.getTemperatureCtrl();
float led = temp.getTemperatueLED();
float lcd = temp.getTemperatueLCD();
```

### Где лежат классы:
- `com.trd.sdk.*` + `com.trd.framework.ITrdSystemService$Stub` + `ITemperatureCtrl` — **в `trdservice.apk`** (`/system/app/trdservice/`, пакет `com.trd.service`), а также **вшиты в KuSource dex**.
- `com.trd.framework.k`/`k$a`/`g` (обфусцированные) — в `trdmiddle.apk` (`/vendor/priv-app/trdmiddle/`, пакет `com.trd.framework`).

### Ошибка в MOD (`OemCpuTemperature`):
Использовался `com.trd.framework.k$a.asInterface()` — **`k$a` не имеет `asInterface`** (только `asBinder`). Правильно — `ITrdSystemService$Stub.asInterface()`. Нужно исправить (задача на будущее).

### ⚠️ Путаница имён (вендор):
В KuSource `getLedTem()` читает `getTemperatueLCD()`, а `getLcdTem()` читает `getTemperatueLED()` — **перепутано**. При чтении в MOD сверять по факту.

---

## 5. Логика яркости и охлаждения (полная)

### Два механизма (независимы):
1. **Ручная яркость** — режим фиксирован, шкала 0–100%.
2. **Термозащита** — автоматически снижает яркость при нагреве.

### Датчики (через TRD binder `TrdSystemService` → `TemperatureCtrl`):
| Метод | Реально читает |
|---|---|
| `getLedTem()` | LCD (перепутано) |
| `getLcdTem()` | LED (перепутано) |
| `getFanStatus(i)` i=0..3 | boolean «исправен/нет» (не RPM) |
| `getTemperatueAMB()` | температура корпуса |

### Ручная яркость — режимы:
Смена: broadcast `com.action.brightReceiver` + `brightModel` (0–3) → `persist.bright.model`.

| Режим | brightModel | Яркость |
|---|---|---|
| Повышенная | 0 | **74%** (ступени 61%, 44%) |
| Стандартный | 1 | **44%** (ступень 31%) |
| Тихий | 2 | ниже |
| Высокогорный | 3 | щадящий |

Потолок пользователя = **74%** (не 100%). 100% только в стартовом `defaultGlPerformanceValue` (modelType==1).

`setBacklight` ограничивает 1…100, пишет через `SystemCtrl.setBacklight` (TRD).

### Термозащита, контур 1 (`startReduce`):
Читается LED-температура (v4), выбирается целевой `fs2Value` (шкала 450–1000), яркость плавно подводится шагом **−40/+100** за тик (раз в минуту).

| LED темп. | Целевой fs2Value |
|---|---|
| < 45°C | без вмешательства |
| 45–50 | 450 |
| 50–60 | 550→450 |
| 60–65 | 450 |
| 65–70 | 700→550 |
| 70–75 | 950→900→850 |
| 75–80 | 1000→900 |
| **> 80** | **авария** |

Константы: `45, 50, 60, 65, 70, 75, 80 °C`.

### Термозащита, контур 2 (`startHighTemReduce`) — страховка:
- `modelType==1`: **LED ≥ 65 °C ИЛИ LCD ≥ 58 °C**
- иначе: **LED > 75 °C**
- действие: яркость −3 (быстро).

### Авария > 80 °C:
`sendEmptyMessage(0)` → `HighTemperatureActivity` (CountDownTimer 10 с) → `UtilsTools.shutDown()` → `Runtime.exec("reboot -p")` (жёсткое выключение).

### Вентиляторы (`fanDetection`):
4 датчика `getFanStatus(0..3)` (boolean). XOR-логика → код неисправного (1–4) → `FanDetectionActivity`.

### Цикл (`TIME_TICK`, раз в минуту) — 9 шагов:
defaultData → defaultBright → isReduceFS → startThreadReduce518 → startThreadReduce → startThreadFanDetection → actualIHighTemThread → startThreadTemperatureError → brightReduce.

### Обработчик сообщений (`TimeService$1`):
| what | Действие |
|---|---|
| 0 | перегрев → HighTemperatureActivity |
| 1 | вентилятор → FanDetectionActivity(code) |
| 2 | Toast «датчик температуры неисправен» |

---

## 6. Связь с MOD (TvSettingsPlus)

| Направление | Механизм |
|---|---|
| MOD → Protection | `sendBroadcast(com.action.brightReceiver, brightModel)` → `BrightReceiver` |
| MOD → Protection | проверка наличия `BrightReceiver`/`TimeService` (PackageManager) |
| Protection → MOD | ничего (внутренние intents) |

**`BrightReceiver` ОБЯЗАТЕЛЕН** — MOD управляет яркостью только через него.
MOD не открывает Activity этого приложения (проверено по `exact8054`).

---

## 7. Проблема установки (КРИТИЧНО для будущего)

### Симптом:
```
Failure [INSTALL_FAILED_INVALID_APK: Package com.coolux.source is a persistent app. Persistent apps are not updateable.]
```

### Причина (выяснена точно):
`com.coolux.source` — системное приложение с **`android:persistent="true"`**, установленное в `/system/app/KuSourceRJ/` (флаг `SYSTEM` + `PERSISTENT`). Android **жёстко запрещает** обновлять persistent-приложения через `pm install`.

### Что проверено и НЕ помогло:
- подпись совпадает (`c8a2e9bc…`) — **не причина**
- versionCode поднят 41→42 — **не причина**
- `persistent` удалён из манифеста APK — **не помогло** (флаг берётся из системной записи `/data/system/packages.xml`)
- все флаги `pm install` (`-r -d`, `--dont-kill`) — блокируются одинаково

### Почему TvSettingsPlus MOD ставится, а KuSource нет:
У `TvSettingsPlus` **нет** `persistent=true` → обновление разрешено. У KuSource есть → запрещено.

### Реальные пути (на выбор):
1. **Пересборка super.img** (рекомендуется, безопасно) — положить наш APK в образ, прошить. Это этап 5b общего плана.
2. **Снять флаг PERSISTENT** из `/data/system/packages.xml` (ABX-бинарный, рискованно, нужен factory-reset при ошибке).
3. **overlayfs** — подменить `/system/app/KuSourceRJ/KuSourceRJ.apk` через overlay (overlay доступен в ядре).

### Решение владельца (2026-11-27):
**Приостановить установку.** Тестировать вырезанную версию только при пересборке прошивки. Сейчас — продолжить аудит остальных программ.

---

## 8. Среда / инструменты (что работает)

- `C:\Program Files\Microsoft\jdk-21.0.13.102-hotspot\bin\java.exe` — JDK 21 (для apktool/jadx)
- `C:\tools\apktool\apktool_3.0.3.jar` — apktool
- `C:\tools\jadx-gui-1.5.7-win\lib\jadx-gui-1.5.7-all.jar` — jadx
- `%LOCALAPPDATA%\Android\Sdk\build-tools\36.0.0` — aapt/aapt2/apksigner/zipalign/d8
- bundled Python: `C:\Users\a804483\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe` (с Pillow)
- `platform-tools\adb.exe` — ADB v37.0.3 (использовать именно его, не встроенный)
- **Сборка APK:** `apktool d -p <framework> --no-src` → правки → `apktool b -p <framework>` → подпись apksigner
- **versionCode патч:** `_repos/Projector-Soft/tools/patch_axml_version.py` (правит бинарный AXML)
- **ADB-нюанс:** каждый `pwsh` вызов = новый adb-демон → делать `kill-server`+`connect`+команды в одном скрипте. Синтаксис su: `su 0 <cmd>` (не `su -c`).

---

## 9. Ограничения среды (запомнить)

- Сеть из песочницы: TLS не проходит (`SEC_E_NO_CREDENTIALS`). Работает: `web_fetch` (HTTP), git с `-c http.sslBackend=openssl`.
- Запись вне workspace запрещена (`workspace-write`).
- `erofs-tools` (cygwin) не запускаются (signal pipe).
- `python3` — Store-заглушка; использовать `python`.
- GitHub push: нельзя из песочницы (credential-helper падает) — владелец пушит вручную.

---

## 10. Что осталось сделать (backlog)

1. **Исправить `OemCpuTemperature.java`** в MOD — заменить `k$a.asInterface` на `ITrdSystemService$Stub.asInterface` (задача отложена владельцем).
2. **Пересборка super.img** с финальным APK (этап 5b) — тогда и тестирование.
3. Опционально: вычистить ~14 мёртвых методов `IntentUtils` (безвредно, можно не делать).
4. После установки: проверить термоконтроль/яркость/трапецию по ADB.

---

## 11. Решения владельца (зафиксированы)

- Пороги температуры **не менять** (нет данных о пределах светодиода/матрицы).
- `reboot -p` в аварии **оставить**.
- Установку KuSource **отложить** до пересборки прошивки.
- Языки: английский + русский достаточно.
- Работать локально, документы дублировать на GitHub (владелец пушит сам).
- Навигацию по проектору без просьбы **не запускать**.

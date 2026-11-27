# ПОЛНЫЙ ТЕХНИЧЕСКИЙ HANDOFF ДЛЯ НОВОГО ИИ-АГЕНТА
## Прошивки проекторов, MediaTek/RUIOS, FlixTone D11 Master / Everycom CineLux, Touyinger ET32 и TvSettingsPlus MOD

**Авторский контекст:** инженерный проект владельца GitHub `MAX-TAC`.  
**Актуальность сверки GitHub:** 23 ноября 2026 г.  
**Основной язык проекта:** русский; код, названия API, сырые отчёты и комментарии могут быть английскими.  
**Назначение:** один самодостаточный входной документ для ИИ-агента, которому предстоит продолжать исследования, разработку, ревизию кода и подготовку безопасных экспериментов на реальных проекторах.  
**Главный целевой аппарат:** FlixTone D11 Master / Everycom CineLux, `ro.rjpj.machine.id=8054`, Android TV / RUIOS 13, MediaTek/MStar `mt5873_cd` / ядро `mt5873`, **два HDMI**.  
**НЕ СЧИТАТЬ:** этот handoff доказательством, что все перечисленные функции уже работают на аппарате, что полная кастомная прошивка готова к установке или что все результаты старых разговоров воспроизводимо проверены.

> **Критический принцип:** различай (1) собственно прочитанный исходник/ELF/дамп; (2) CI-сборку; (3) показание ADB реального 8054; (4) пользовательский визуальный/слуховой тест; (5) предположение; (6) запланированную реализацию. Нельзя превращать наличие символа/метода/флага в утверждение о реально работающей функции.

---

# 0. Краткая инструкция новому агенту: с чего начинать

1. **Открой четыре репозитория**, перечисленные в разделе 1. Особенно важны `MAX-TAC/Projector-Soft` и `MAX-TAC/FlixTone_8054_Backup`.
2. **Проверь HEAD веток и PR непосредственно в GitHub**. Этот файл — срез на 23.11.2026; `main` проекта `Projector-Soft` существенно старше рабочего Draft PR #10. Не брать `main` за текущую реализацию v41.
3. В `Projector-Soft` прочти `research/EXTERNAL_AI_HANDOFF_20261121/README.md` и документы `01`–`08`; затем поправь выводы с учётом более поздних PR #9 и #10 и этого документа. Старый пакет уже содержит **291 привязанную к коммитам ссылку на первичные источники** в `06_SOURCE_CATALOG.md`.
4. Для дальнейшей разработки ориентируйся на **PR #10** (`feature/8054-v41-picture-sound-safety-20261122`) и только после анализа его зависимости от **PR #9**. Для сравнения/отката используй зафиксированные SHA предыдущих PR.
5. **Не предпринимай действий на проекторе без отдельного разрешения владельца.** По умолчанию разрешены чтение GitHub, декомпиляция офлайн, анализ и unit/AndroidX тесты. Любые `adb shell settings put`, установка APK, изменение CEC/EDID/HDMI, root, motor/optics, `pm disable`, reboot, fastboot flash, AVB, factory и прошивка — отдельные согласования.
6. **Не возвращай китайское меню в пользовательский путь.** Конечная цель — настоящее `com.android.tv.settings.MainSettings`, собственные MOD-обработчики и штатные низкоуровневые службы Android/MediaTek, а не вызов `com.my.settings` как посредника.
7. Если обнаружишь противоречия, **перепроверь исходные бинарники или код**, сформулируй errata; не подгоняй реальность под предыдущие отчёты.

## 0.1 Уровни доказательности

| Метка | Что означает | Чего не означает |
|---|---|---|
| `RELEASE_METADATA` | Проверены метаданные GitHub Releases: имя, размер, публичный SHA/описание | Что образ подойдёт конкретной плате |
| `STATIC_CONFIRMED` | Есть конкретная цепочка методов/ELF-инструкций/ресурсов в известном source SHA | Что аппаратная функция вызвана на живом устройстве |
| `CI_PASS` | Сборка, тесты, сравнения бинарников или mock-ADB прошли | Что APK установлен и реально работает |
| `DEVICE_8054_OBSERVED` | Приведён вывод ADB/fastboot или наблюдение владельца на реальном 8054 | Универсальная совместимость и успех иных сценариев |
| `HARDWARE_EFFECT_VERIFIED` | Эффект проверен на изображении/звуке/оборудовании с известными условиями | Успех во всех режимах HDMI, SDR/HDR, после reboot |
| `NOT_VERIFIED` | Нет достоверной проверки или полный результат не получен | Что реализация заведомо невозможна |
| `DEFERRED` | Задача намеренно отложена с обозначением причины | Что задача выполнена/закрыта |

---

# 1. Репозитории пользователя: полный охват

По подключённому GitHub `MAX-TAC` на 23.11.2026 найдены **четыре непосредственно профильных** репозитория:

| Репозиторий | Назначение | Главная ветка | Статус |
|---|---|---|---|
| **[Projector-Soft](https://github.com/MAX-TAC/Projector-Soft)** | Модификация реального Android TV `TvSettingsPlus.apk`; системные, OEM и MediaTek API; TvSettingsPlus MOD v41; декомпиляция; 96 функций; CI, тесты, отчёты | `main`, работа в Draft PR и ветках | Основной активный проект |
| **[FlixTone_8054_Backup](https://github.com/MAX-TAC/FlixTone_8054_Backup)** | Точный бэкап живого FlixTone D11 Master 8054; MBOOT, AVB, разделы, recovery и Factory/HDMI исследования | `main` и `research/*` | Основная доказательная база реального устройства |
| **[Everycom-Cinelux-Firmware](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware)** | Заводские PKG двух ревизий, Android OTA 8052/8053; сравнения APK/HAL/ELF/DTBO/AVB; предварительный Custom v0 | `main`, ~20 отдельных исследовательских веток | Основной сравнительный firmware research |
| **[Firmware-CN-Projectors](https://github.com/MAX-TAC/Firmware-CN-Projectors)** | Исследование стороннего Touyinger ET32/`YG_6M046.bin`: MStar, Android 9, безопасность, утилиты распаковки | `main` | Отдельный проект, **не основа ROM для FlixTone** |

Другие репозитории пользователя (`lumon-panel`, VPN, загрузчик книг, 3D-принтер Anycubic и т.п.) не входят в scope этого projector handoff.

**ВАЖНО ПРО ВЕТКИ:** GitHub отображает все PR #1–#10 в `Projector-Soft` как **OPEN + DRAFT, не merged** (срез 23.11.2026). Некоторые ветки основаны на других незамёрженных ветках. Нельзя автоматически считать их независимыми или видеть последние изменения на `main`.

## 1.1 Ссылки клонирования

```bash
# Только чтение/изучение до отдельного разрешения на изменения в репозитории
git clone https://github.com/MAX-TAC/Projector-Soft.git
git clone https://github.com/MAX-TAC/FlixTone_8054_Backup.git
git clone https://github.com/MAX-TAC/Everycom-Cinelux-Firmware.git
git clone https://github.com/MAX-TAC/Firmware-CN-Projectors.git

# В Projector-Soft нужно отдельно получить нужные feature/research ветки:
cd Projector-Soft
git fetch origin --prune
git switch --detach b8071b40f2a62ebf2395cb5953ebd245dd8491be
# Не выполнять git merge / push автоматически.
```

Репозитории публичные по метаданным GitHub на момент сверки. Для чужого агента права на push и доступ к release assets могут отличаться.

---

# 2. Устройства, версии и почему нельзя смешивать ревизии

## 2.1 Целевой живой проектор — FlixTone D11 Master / 8054

| Свойство | Данные / статус |
|---|---|
| Коммерческие наименования | FlixTone D11 Master / совместимое семейство Everycom CineLux; сходное имя **не гарантирует** одинаковую плату |
| OEM machine ID | `8054` (`ro.rjpj.machine.id`) |
| Android | Android 13, API 33, `userdebug`, `test-keys` |
| Live Android build | `eng.suhaix.20260905.031903` в подтверждённом отчёте 21.11 |
| Платформа | MediaTek/MStar `mt5873_cd`; встречается семейное маркетинговое обозначение MT9660, его **не следует** считать точным идентификатором кристалла |
| HDMI | **Два входа**: `HW6:HDMI1`, `HW7:HDMI2` |
| Загрузчик | MBOOT Fastboot `01.01.260905` |
| Разметка | eMMC; Android A/B, dynamic `super`, EROFS logical partitions, Virtual A/B |
| Активный слот в проверке | `a`, слот A `successful`; B `bootable`, но не `successful`, логические B-партиции не обеспечивают доказанный fallback |
| Android после unlock | Загрузился успешно; `ro.boot.vbmeta.device_state=unlocked`, `verifiedbootstate=orange`, `veritymode=enforcing` |
| Пользовательское приложение настроек | Привилегированный `com.android.tv.settings` в `/system_ext/priv-app/TvSettingsPlus/TvSettingsPlus.apk` |
| Китайский GUI | `com.my.settings` / KuSettings; отдельный от OEM-расширений `com.android.tv.settings.uicustom` |

Идентификатор `8054` используется **строгим gate** для части MOD функций; при несовпадении исходной платформы потенциально опасные модификации должны оставаться заблокированными. Значения `8052`/`8053` не являются синонимами `8054`.

## 2.2 Другие исследованные платформы

- **Everycom CineLux 1 HDMI, 8052:** Android 13/API33, `mt5873_cd`, заводской образ `RUIOS.8052.1.0.1`, отдельная октябрьская OTA `RUIOS.8052.1.0.4`, один HDMI. Есть отдельные ADB-наблюдения устройства 8052; их нельзя объявлять результатом реального 8054.
- **Everycom CineLux 2 HDMI / заводская 8054:** PKG `RUIOS.8054.1.0.1` от сентября 2026, ToF/двухвходный профиль. Это **не то же самое**, что локальный backup владельца с билдом `20260905`, хотя оба используют номер 8054.
- **RUIOS 8053 OTA:** Android 13, билд `eng.luzhih.20260612.083454`, принадлежность FlixTone D11 **не подтверждена**. Не рекомендовать cross-flash.
- **Touyinger ET32:** Android 9/API28, предположительно другая MStar-платформа, прошивка `YG_6M046.bin` (модифицированный MStar update). Не использовать её библиотеки/bootloader/разделы как совместимые с D11 без специальной доказательной базы.

---

# 3. Репозиторий `Everycom-Cinelux-Firmware`: что проанализировано

## 3.1 Реальные архивы и релизы (из репозитория и handoff 21.11)

| Источник | Тип и версия | Размер архива, байт | SHA-256 архива |
|---|---|---:|---|
| [Original Firmware for 1 HDMI](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/releases/tag/Original_Firmware_for_1_HDMI_ports), `4K.HDMI-.-20260813.1.rar` | Заводской зашифрованный MStar PKG, **8052 / 1.0.1** | 1 122 636 304 | `bff981a9d440d1495bd6ab48a72fb13c4572de69fcbe81448fc117a3bba5f30f` |
| [Original Firmware for 2 HDMI](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/releases/tag/Original_Firmware), `4KTOF.HDMI-.-DPLS.-09.30.rar` | Заводской PKG, **8054 / 1.0.1**, ToF/two HDMI | 1 301 025 233 | `170f745dc1711c2dae6410dd51f0a8bf5bb7c637e11b8dd3e5f59fbea8c388f3` |
| [OTA Updates](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/releases/tag/OTA_Updates), `RJMT9660_firmware_8052.zip` | Полная Android A/B OTA, **RUIOS.8052.1.0.4** | 851 685 795 | `bedea70fbf3f08d3c18e59d5f91e7d12828c77fac314c30fcc98332c32c88e35` |
| Тот же релиз, `RJMT9660_firmware_8053.zip` | Полная Android A/B OTA, **RUIOS.8053.1.0.0** | 841 648 271 | `9ca8276448e79587b82e55cec0cf3da55154b750774f608378f64619c84f556b` |

Размеры и digest выше — опубликованные данные из версионированного handoff/релизов, **не** новый независимый расчёт SHA в ходе подготовки этого документа. В самих отчётах описаны проверки отдельных объектов CI.

## 3.2 Технические достижения

- Расшифрован заводской контейнер `upgrade_image.pkg` формата **MStar Secure New** (факт извлечения), AES-256-CBC, последовательные сегменты; использовалась известная стандартная схема `MSTAR_SECURE` из публичного инструментария `unixtract`. Это **не** получение уникального приватного OEM signing key.
- Восстановлены LZ4/Android sparse блоки, включая многократную запись кусочков в одни логические диапазоны: их нельзя просто конкатенировать.
- Из заводского 2-HDMI пакета восстановлен `super.img` **2 225 078 272 байт** и EROFS `system_a`, `vendor_a`, `product_a`, `system_ext_a`.
- Сравнены Android APK, OEM обработчики, подписи/DTBO, независимая embedded Linux/TVservice среда, конфиги изображения/звука/boot.
- Для двух заводских сборок найдено общее основание `mt5873_cd`, одинаковая GPT и сходная аппаратная база, но **активная board configuration** может отличаться, и прямой cross-flash небезопасен.
- В сравнении 207 содержательных DTBO payload совпадают по SHA, **порядок записей другой**: bootloader может выбирать DTBO по индексу. Не считать набор одинаковых blobs доказательством совместимости.
- Совпадающий код ELF `.text` и общий AVB RSA4096 public key не доказывают одинаковую OEM реализацию, совместимые factory data или возможность установить подменённый образ.
- Конфигурация HDMI в `vendor/build.prop`: 8052 — `HW6:HDMI`; 8054 — `HW6:HDMI1,HW7:HDMI2`.
- Среди OEM APK: `KuSettings`, `KuSourceRJ`, `RuiAutoFocus`, `KeystoneCorrection`, `TvSettingsPlus`, `LiveTV`, `TvServices`, `Factory`, `RuiYunOta`, `trdservice`, `trdmiddle`, `zxlauncher`, `zxstore`, иногда `KuSetupWizard` и preinstall-del приложения.
- Упоминаются опасные действия заводского upgrade script (`gpt clean`, записи partition и boot-critical разделов); **никогда не переиспользовать скрипт для другого SKU**.

## 3.3 OTA 8052/8053

- `payload.bin` формата Android A/B `CrAU` v2, восстановление партиций проведено.
- В отчётах OTA payload metadata signature проверялась на RSA-2048/SHA-256, сертификат совпадал с публичным AOSP testkey; **эта подпись и AVB RSA4096 в разделах — разные механизмы доверия**.
- 8053 — более ранняя июньская версия, а не заведомо «следующая» после 8052; номера машин не означают хронологический порядок.
- OTA URL/канал и маркетинговая метка `RJMT9660` не заменяют проверку `ro.rjpj.machine.id`, текущей платы, релизной даты и точного digest.

## 3.4 Каталоги и основные документы

```text
Everycom-Cinelux-Firmware/
├── .github/workflows/                 # многочисленные read-only анализы и сравнения
├── analysis/
│   ├── Original_Firmware/             # PKG: decrypt/header/upgrade/decrypted/reconstructed
│   ├── HDMI_Comparison/               # 1/2 HDMI, Android/AVB, engineering verdict
│   ├── DTBO_Comparison/               # 207 descriptors, перестановка индексов
│   ├── Deep_APK_Comparison/           # сравнение OEM методов, JSON + README
│   ├── Deep_Native_Comparison/        # ELF/конфиги/ISA
│   ├── TV_Service_Comparison/         # отличие TVservice/ext4
│   ├── Embedded_Linux/               # отдельная среда Linux
│   ├── RUIOS_OTA_Comparison/          # OTA 8052/8053
│   ├── RUIOS_OTA_Signatures/          # проверка подписей
│   ├── Full_Audit/                    # сводный полный отчёт и план портирования
│   ├── App_Research/                  # APK API исследование
│   └── [branch-only investigations]   # добавлены в исследовательских ветках
├── tools/                              # audit, inspect, compare, reconstruct
└── README.md
```

Стартовые первоисточники:
- [Full_Audit/README.md](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/blob/main/analysis/Full_Audit/README.md)
- [Full_Audit/TEST_AND_PORTING_PLAN.md](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/blob/main/analysis/Full_Audit/TEST_AND_PORTING_PLAN.md)
- [Original_Firmware/DECRYPTED_SUCCESS.md](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/blob/main/analysis/Original_Firmware/DECRYPTED_SUCCESS.md)
- [HDMI_Comparison/ENGINEERING_VERDICT.md](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/blob/main/analysis/HDMI_Comparison/ENGINEERING_VERDICT.md)
- [RUIOS_OTA_Comparison/ENGINEERING_SUMMARY_RU.md](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/blob/main/analysis/RUIOS_OTA_Comparison/ENGINEERING_SUMMARY_RU.md)
- [OTA / AVB comparison](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/tree/main/analysis/RUIOS_OTA_Comparison)

## 3.5 Custom v0: ЧТО СОБРАНО, А ЧТО НЕТ

Исследовательская ветка: [`custom-v0-staging-8052-8054-20261021`](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/tree/custom-v0-staging-8052-8054-20261021). Прочитан `custom-v0/README_RU.md` и `custom-v0/BUILD_STATUS_RU.md`.

**Реально собрано 21.10.2026:** два ZIP со staging-overlay, оба прошли GitHub Actions [run 39626053724](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/actions/runs/39626053724):
- `cinelux-custom-v0-8052-NONFLASHABLE` — для 8052 из OTA 1.0.4;
- `cinelux-custom-v0-8054-NONFLASHABLE` — для заводского 8054 1.0.1, **не** для произвольного live D11 без адаптации.

В staging включены FLauncher 0.18.0 (`me.efesser.flauncher`) и собственный простой ярлык `org.cinelux.settingsshortcut`, который открывает `com.android.tv.settings/.MainSettings`. Предложены удаления `zxlauncher`, `zxstore` и отдельных preinstall-del APK; `KuSetupWizard`, `KuSettings`, `TvSettingsPlus`, `trdservice`, `KuSourceRJ`, `RuiAutoFocus`, `KeystoneCorrection`, Factory, OTA и системный установщик сохраняются. Для 8054 планировалось удалить предустановленные Netflix/Prime Video, YouTube оставить.

**Не было создано:** готовых изменённых `system.img`, `super.img`, `update.pkg`, `payload.bin` или проверенного flashable ZIP. `REMOVALS.txt` — список планируемых удалений, не результат правки файловой системы. FLauncher как встроенный `/system/app` не проверен на устройстве. Подпись shortcut временная; для конечного продукта нужен стабильный собственный ключ. Нельзя выдавать staging ZIP за обновление.

---

# 4. `FlixTone_8054_Backup`: реальная прошивка владельца и разблокировка

## 4.1 Релиз и образы

[Релиз `FlixTone_8054_Backup`](https://github.com/MAX-TAC/FlixTone_8054_Backup/releases/tag/FlixTone_8054_Backup):

- `FlixTone_8054_Backup.zip`: **2 011 878 129 байт**, SHA-256 `4f53f2224c98b4c832a19a591b9dd7f925bde28528b5674a09732c0f0e41d362`.
- Отдельно в релизе: `boot_a.img`, `dtbo_a.img`, `vbmeta_a.img`, `vbmeta_system_a.img`.
- Владелец отдельно проверил RAW `super.img` размером **2 225 078 272 байта**; SHA-256 `ac16996dddaa7c8f5e5429a0736f73d18a12df7dc6b58a4e89a475f5af0c5a02`. В репозитории задокументирована сверка этого SHA с извлечением из release ZIP в CI.
- В архиве/анализах доступны точные разделы `system_a/vendor_a/product_a/system_ext_a` и связанные с ними OEM приложения, библиотеки, сервисы и конфигурации.
- Нельзя считать один ZIP автоматическим полным безопасным recovery-пакетом для всех физических разделов, включая персональные/калибровочные и без проверки схемы разделов.

Особо конфиденциальные/уникальные `private`, `tvcertificate`, `eeprom`, `factory`, `persist`, `project_id` нельзя бездумно распространять, публиковать или переносить между устройствами.

## 4.2 Подтверждённый fastboot unlock (21.11.2026)

В исходном README и [документе с реальными выводами](https://github.com/MAX-TAC/FlixTone_8054_Backup/blob/main/docs/8054_UNLOCK_AVB_PARTITIONS_VERIFIED_20261121.md) записано:

```text
fastboot flashing unlock    -> OKAY
fastboot getvar unlocked   -> no  → yes
fastboot getvar secure     -> yes → no
fastboot getvar current-slot -> a
fastboot getvar slot-count   -> 2
fastboot getvar is-userspace -> no
```

После разблокировки штатный Android **загрузился**, `ro.boot.vbmeta.device_state=unlocked`, `verifiedbootstate=orange`, но `veritymode=enforcing`. Следовательно, прежнее утверждение «загрузчик 8054 нельзя разблокировать» **устарело и опровергнуто**. Однако успешный unlock не доказывает успешную запись/загрузку изменённого `super`, обход всех MBOOT/OP-TEE проверок, recovery или возможность relock. Нельзя запускать `fastboot flashing lock` с модифицированными образами.

## 4.3 Физическое устройство и разметка

- Boot HAL: `android.hardware.boot@1.2::IBootControl`.
- Два слота; B не является доказанным запасным рабочим Android. В `lpdump` B logical partitions могли не содержать extents.
- Virtual A/B + userspace compression, EROFS logical partitions `system_a`, `vendor_a`, `product_a`, `system_ext_a`.
- eMMC физические разделы: boot/mboot/dtbo/vbmeta/OP-TEE/TVservice/tvconfig/factory/persist и др. Каждый имеет самостоятельные риски; полное изменение загрузочной цепочки не входит в задачу простого деблоата.
- Важно сохранять панельные конфиги, оптику/мотор/ToF, factory calibration, thermal/fan, аудио/HDMI/HDCP и точные UID/GID, SELinux labels, fs metadata.

## 4.4 USB, OTA, recovery

Из точного MBOOT офлайн найден литерал:

```text
Script format default file name is /usb_auto_update.txt
mtkupgrade usb -script
```

Это указывает на сценарный USB entrypoint, **но не доказывает**, что любой файл `usb_auto_update.txt` будет безопасно выполнен, и тем более не подтверждает `unlock.txt` как готовый рецепт. Не исследовать на живом устройстве путём случайной записи критических разделов.

Набор документов:
- [README](https://github.com/MAX-TAC/FlixTone_8054_Backup/blob/main/README.md)
- [8054_UNLOCK_AVB_PARTITIONS_VERIFIED_20261121.md](https://github.com/MAX-TAC/FlixTone_8054_Backup/blob/main/docs/8054_UNLOCK_AVB_PARTITIONS_VERIFIED_20261121.md)
- [USB_INSTALL_AND_UNLOCK_RESEARCH_20261121.md](https://github.com/MAX-TAC/FlixTone_8054_Backup/blob/main/docs/USB_INSTALL_AND_UNLOCK_RESEARCH_20261121.md)
- [CUSTOM_RUIOS_RELEASE_PLAN_20261121.md](https://github.com/MAX-TAC/FlixTone_8054_Backup/blob/main/docs/CUSTOM_RUIOS_RELEASE_PLAN_20261121.md)

## 4.5 Предложенная кастомная RUIOS — план, НЕ готовый релиз

Цель — **модифицированная OEM RUIOS на базе точного 8054**, а не необоснованный переход на LineageOS/AOSP: чистый совместимый TV launcher, штатные настройки с TvSettingsPlus MOD, нормальная клавиатура, удаление только доказанного мусора, аккуратная локализация и брендирование (имя Android/BT/Cast может задаваться разными компонентами), boot animation/ранний logo только после исследования.

План каналов поставки:
1. пользовательский APK upgrade (минимальный риск, если подпись/privileged-условия допускают);
2. подписанное OTA при проверенных ключах/обновляторе;
3. заводской USB/MBOOT механизм только при доказанной подписи и гарантированном восстановлении;
4. fastboot custom ROM — лишь после независимой проверки целостности backup, изменённых partitions, AVB и rollback.

**Никакой путь не считается готовым к flashing** на основе одной возможности unlock.

---

# 5. `Firmware-CN-Projectors`: независимый Touyinger ET32

Исследованный архив: `YG_6M046.zip` → `YG_6M046.bin`, предположительно модифицированный MStar update, **не гарантированно оригинальная заводская прошивка**.

В результате read-only анализа были восстановлены два Android-образа, которые опубликованы как **analysis-only**, не как прошивочные обновления: [Touyinger-ET32-unpacked](https://github.com/MAX-TAC/Firmware-CN-Projectors/releases/tag/Touyinger-ET32-unpacked):

- `ET32-system.ext4.zst`, логический размер system **2 646 605 824 байт**;
- `ET32-vendor.ext4.zst`, логический размер vendor **367 001 600 байт**;
- `SHA256SUMS.txt`.

Технические выводы по ET32: Android 9/API28, build марта 2025, security patch 2021-01-05; `userdebug`, `dev-keys`, `ro.adb.secure=0` в vendor props; boot args запрашивают permissive SELinux. Противоречащий Android version build fingerprint; утверждать точный SoC по одним строкам `mt5862_bga_1g`/`NL_MTK9255_D1E8` нельзя. Найдены APK `AutoFocus3`, `ZYSetting`, `TvSettingsPlus`, `NLHotkeyService`, `ZYCustomUI`, отдельные Binder-службы фокусировки/трапеции и доступные сетевые компоненты.

Из [QUALITY_REVIEW.md](https://github.com/MAX-TAC/Firmware-CN-Projectors/blob/main/analysis/ET32/QUALITY_REVIEW.md): потенциальная проблема Boa, работающего как root на TCP/80 и CGI с диагностическими переменными (по статике, без проверки реальной сетевой достижимости); опасные права `777` для конфигурации трапеции; возможный конфликт package name двух приложений; экспортированные Android-компоненты, требующие отдельной проверки полномочий.

Основная структура:

```text
Firmware-CN-Projectors/
├── .github/workflows/ # extract/analyze/audit/deep/boa
├── tools/             # extract_et32, reassemble_et32, анализ структур/ APK
└── analysis/ET32/
    ├── README.md
    ├── QUALITY_REVIEW.md
    ├── partition_map.json
    ├── firmware_report.md / partition_report.md / android_audit.md
    ├── projector_components.md / projector_apk_metadata.json
    ├── mstar_upgrade_commands.txt
    ├── vendor_hal_manifest.xml
    └── deep/          # BOA, статический аудит, JSON и MD
```

**Вывод для D11:** ET32 полезен как отдельный исследовательский опыт по MStar/Android OEM, но APK/драйверы/скрипты ET32 не считать совместимыми с MT5873/8054. Ни в коем случае не прошивать ET32 image на FlixTone D11.

---
# 6. `Projector-Soft`: главная цель, архитектура и источники

## 6.1 Цель заказчика — не менять

Создать **полноценный TvSettingsPlus MOD** на базе **реального оригинального** Android TV Settings APK, сохраняющий согласованный современный интерфейс v41 и заменяющий неудобные китайские пользовательские настройки проектора:

```text
Пульт / ярлык / нормальный Android TV Settings
  → оригинальный системный com.android.tv.settings.MainSettings + MainFragment
  → существующие MOD Leanback Preference-страницы и ползунки
  → собственный безопасный обработчик пользовательского действия
  → проверенный Android/OEM/MediaTek consumer backend
  → сохранённые TvServices / KuSourceRJ / Focus / Keystone / HDMI / Audio HAL
  → реальный аппаратный эффект
```

НЕ ДОПУСКАЕТСЯ целевое устройство вида:

```text
MOD row -> китайская com.my.settings.Activity -> чужой OEM callback -> driver
MOD row -> FactoryMenu Activity -> factory UI callback -> driver
MOD row -> новая самодельная оболочка, имитирующая AOSP MainSettings
```

Китайское меню (`com.my.settings` KuSettings) и инженерное меню могут оставаться **независимыми клиентами** тех же системных служб, но не должны служить программным посредником в пользовательском маршруте MOD. Не удалять штатные аппаратные сервисы только из-за желания избавиться от UI. UI-миграция и физическое удаление APK — разные этапы.

### Критерии стадий

- **M1 / UI independent:** весь обычный поддерживаемый пользователем функционал доступен в TvSettingsPlus MOD; китайские Activity/Fragment не запускаются по соответствующим пунктам. `com.my.settings` при этом физически ещё может быть установлен.
- **M2 / package independent:** только после переноса/проверки boot/watchdog/time/remote/thermal зависимостей разрешена **отдельно согласованная** проверка временного отключения KuSettings с обеспеченным возвратом.
- **M3 / removal candidate:** после M2 и полноценного recovery/ROM-плана рассматривать удаление/исключение китайского APK из кастомной RUIOS. Никакой автоматический переход M1→M3.

**Сохранять неизменными, если нет доказанной необходимости:** штатные сетевые/BT/приложения/дата/язык Android TV; низкоуровневые `TvServices`, `TVInput`, `trdservice/trdmiddle`, `KuSourceRJ`, `RuiAutoFocus`, `KeystoneCorrection`, ToF/моторы, LED/fan/thermal, factory calibrations, OTA, DRM/HDCP, kernel и HAL.

## 6.2 Точный original Android TV Settings APK

По read-only исследованию реальной 8054:

```text
system_ext_a/priv-app/TvSettingsPlus/TvSettingsPlus.apk
Package: com.android.tv.settings
Platform: Android 13 / API 33
Stock APK SHA256: f8e0c6fe0f46e7eb8db651c31d85ef8b32a769b37e4dd0f96ed19a64725d74ee
Stock signing certificate SHA256: c8a2e9bccf597c2fb6dc66bee293fc13f2fc47ec77bc6b2b0d52c11f51192ab8
```

**Почему это важно:** при обновлении системного приложения PackageManager проверяет подпись, package identity, версию, разрешения/privileged/shared UID и совместимость манифеста. Обычная сборка нового APK с другим сертификатом не является корректной заменой. В диагностике `com.android.tv.settings` упоминался system UID 1000; наличие разрешения в `dumpsys package` не гарантирует, что конкретный API доступен текущему процессу — выполнять runtime permission/behavior check.

Отчёты по v39–v41 описывают сохранение 15 нетронутых исходных DEX и ограниченное изменение `classes13.dex`, а также original resource/manifest checks. Эти свойства **перепроверять на конкретном новом SHA**, а не автоматически наследовать от старого артефакта.

## 6.3 Структура активной ветки проекта (23.11.2026)

В HEAD PR #10 доступно около **580 объектов Git tree (включая каталоги)**, включая:

```text
Projector-Soft/
├── .github/workflows/
│   ├── build-tvsettingsplus-8054-audit.yml        # exact-8054 APK / ROM baseline
│   ├── [AndroidX / OEM / UI / manifest / signature / PR audit workflows]
│   ├── export-external-ai-handoff-20261121.yml    # экспорт старого evidence bundle
│   └── [исторические workflows v2...v33, исследования 8052/8054]
├── app/tvsettingsplus-mod/
│   ├── src/main/java/dev/projectorsoft/tvsettings/
│   │   ├── ProjectorCapabilities.java
│   │   ├── ProjectorCompatibilityPolicy.java
│   │   ├── BootSourceMapping.java
│   │   ├── KuSourceRecoveryService.java
│   │   ├── KuSourceRecoveryBootReceiver.java
│   │   ├── OemHdmiCecHook.java / OemHdmiEdidHook.java
│   │   ├── OemFiveBandEqualizerHook.java
│   │   ├── OemHardwareDelegatedSettings.java
│   │   ├── OemPowerOnSourceHook.java
│   │   ├── OemProjectorOrientationHook.java
│   │   └── [другие shared OEM compatibility adapters]
│   ├── src/exact8054/java/dev/projectorsoft/tvsettings/
│   │   ├── ModMainSettingsActivity.java
│   │   ├── ModSettingsActivity.java
│   │   ├── NativeRootFragment.java / NativeSections.java
│   │   ├── NativePicturePanel.java / PictureUserEditPolicy.java
│   │   ├── NativeEqualizerPanel.java
│   │   ├── NativeMediaRouteBridge.java
│   │   ├── NativeMediaRouteTransaction.java
│   │   ├── NativeMediaRoutePicker.java
│   │   ├── NativeAudioOutputReadout.java
│   │   ├── OemCustomerOptions.java / OemCpuTemperature.java
│   │   ├── HdmiCecSettingsActivity.java / HdmiOneStatusActivity.java
│   │   ├── HdmiTwoStatusActivity.java / SourcesSettingsActivity.java
│   │   ├── ProjectionSettingsActivity.java / PictureSettingsActivity.java
│   │   ├── ColorTemperatureSettingsActivity.java / MemcSettingsActivity.java
│   │   ├── SoundSettingsActivity.java / EqualizerSettingsActivity.java
│   │   ├── BluetoothSettingsActivity.java / BluetoothDevicesSettingsActivity.java
│   │   ├── NetworkSettingsActivity.java / AppsSettingsActivity.java
│   │   ├── SystemSettingsActivity.java / DeviceAboutSettingsActivity.java
│   │   ├── HardwareStatusSettingsActivity.java / ProjectorPowerSettingsActivity.java
│   │   ├── NativeOverlayWindow.java / StockMainSettingsMenu.java
│   │   └── [прочие exact-8054 controllers]
│   ├── src/test/                          # JVM tests
│   └── [AndroidX/UI tests / support infrastructure]
├── tools/
│   ├── patch_8054_mainsettings.py
│   ├── patch_8054_unified_manifest.py
│   ├── verify_8054_native_host.py / verify_8054_unified.py
│   ├── repack_tvsettingsplus_dex.py
│   ├── audit_8054_mod.js
│   ├── trace_8054_*.py / trace_8054_selected_smali.js
│   ├── collect_tvsettingsplus_adb_diagnostics.sh
│   ├── diagnose_8054_v40.ps1
│   ├── generate_8054_release_parity.py
│   └── [другие audit/extract/compare/validation tools]
├── research/
│   ├── 8054/
│   │   ├── FINAL_FUNCTION_PARITY_8054.csv
│   │   ├── USER_SETTINGS_MIGRATION_TRACKER.md
│   │   ├── PICTURE_BLOCK_STATUS_8054.md
│   │   ├── SOUND_BLOCK_STATUS_8054.md
│   │   ├── HDMI_BLOCK_STATUS_8054.md
│   │   ├── PROJECTION_BLOCK_8054.md
│   │   ├── KUSETTINGS_DEPENDENCIES_8054.md
│   │   ├── MTK_DIRECT_CONSUMER_CONTROL_CONTRACT_20261122.md
│   │   ├── [сравнения APK, smali, routes, audio, EDID, panel, device tests]
│   │   └── native/ [в исследовательских ветках, см. PR #3]
│   ├── EXTERNAL_AI_HANDOFF_20261121/
│   │   ├── README.md
│   │   ├── 01_FIRMWARE_REPOSITORIES_AND_RELEASES.md
│   │   ├── 02_CUSTOM_FIRMWARE_FEASIBILITY.md
│   │   ├── 03_TVSETTINGSPLUS_MOD_TECHNICAL_STATE.md
│   │   ├── 04_PRODUCT_REQUIREMENTS_AND_ACCEPTANCE.md
│   │   ├── 05_EVIDENCE_OPEN_QUESTIONS_AND_REVIEW_PLAN.md
│   │   ├── 06_SOURCE_CATALOG.md
│   │   ├── 07_INDEPENDENT_AI_REVIEW_TASK.md
│   │   ├── 08_OWNER_VERIFIED_ANDROID_TV_PICTURE.md
│   │   └── evidence_manifest.json
│   └── oem-apps/ [8052 и межревизионная декомпиляция]
├── docs/
│   ├── 8054_FINAL_MENU_SPEC.md
│   ├── 8054_RELEASE_CHANGELOG.md
│   ├── 8054_HARDWARE_TEST_PLAN.md
│   ├── 8054_KUSETTINGS_MIGRATION.md
│   ├── TVSETTINGSPLUS_8054_V41_PICTURE_SOUND_IMPLEMENTATION_20261122.md
│   ├── TVSETTINGSPLUS_8054_AUDIO_ROUTE_HARDWARE_ACCEPTANCE_20261122.md
│   ├── TVSETTINGSPLUS_8054_R5_UI_AND_LAUNCHER_20261122.md
│   ├── TVSETTINGSPLUS_8054_R7_PICTURE_SECTIONS_AND_KEY307_20261122.md
│   └── [исторические версии v2–v41, MENU, architecture, parity]
└── README.md
```

**Важное различие:** `app/tvsettingsplus-mod/src/main/...` — исходные shared classes; `src/exact8054/...` — конкретный билд 8054. Ряд OEM символов/файлов доступен не в `main`, а только в соответствующих research/feature branch. Перед правкой открыть настоящий source tree нужного `HEAD` и build workflow.

## 6.4 Хронология разработки

| Период/версия | Результат | Ограничения |
|---|---|---|
| Октябрь, v2–v23 | Каталог OEM функций, первые Android TV Settings хуки, picture/sound/source/CEC/EDID/brightness/launcher, изолированные CI-сборки и тесты | В основном static/mocks, совместимость точной платы не доказана |
| v24–v33, ноябрь | Read-only thermal telemetry; OEM firmware routes/OTA; power on after AC; keypress tones; boot app; text scale; sleep policies; Bluetooth HID; TimeService/KuSource; diagnostics of 9 legacy Intents | KuSettings watchdog и автоподключение remote не замещены |
| v35–v38 | Нативные Android 13/Leanback страницы, original fragment host, runtime gating, навигация и D-pad, отдельные MOD Activity | Контракт реального устройства требует теста |
| v39 | Встройка восьми разделов в оригинальный `MainSettings/MainFragment` | Владелец обнаружил регрессии/вопросы UI |
| v40 | Коррекция Bluetooth, HOME, статуса HDMI, boot source, CEC, EDID и др. по обратной связи | Не полноценная аппаратная приёмка |
| v41 (base) | OEM bottom picture panel, mode/color/gamma/MEMC readback, EQ 5 полос, специализированные страницы, signed exact-8054 APK | Не объявлять все controls hardware verified |
| v41 экспериментальные PR #4/#5/#7 | Контракт безопасного PIC04, экспериментальный direct write и отдельно STOCK Picture route | Это разные ветки, не одна собранная версия |
| 22.11, PR #9/#10, R3–R7 | Direct backend research, User/factory guards, Bass/Treble, аудиовыход, UI R4 transparent, R5 alias, R6 gamma guard, R7 компактные слайдеры + три группы; remote key 307 | Большинство изменений только CI или частичные проверки на устройстве; route issue не закрыт |

Исторический базовый v41 APK из `docs/8054_RELEASE_CHANGELOG.md`: `versionCode=41`, SHA-256 `a93af51dda3ec723a1e895c935f7d68c31760b6f8d8169090e5d02b19256037e`, исходный commit `a3ca1a2`, [GitHub Actions artifact](https://github.com/MAX-TAC/Projector-Soft/actions/runs/44769301913/artifacts/14645503299). **Этот SHA относится к конкретному старому APK, а не к R7.** Фактическую целевую сборку всегда идентифицировать тройкой *source HEAD SHA + APK SHA256 + device version/signature*.

## 6.5 Согласованное меню v41 (8 корневых разделов)

1. **Wi-Fi и сеть** — оригинальные Android TV NetworkActivity/NetworkFragment, Wi-Fi и Ethernet; платформенную функциональность не дублировать.
2. **Bluetooth** — действительный статус; сопряжённые устройства; добавление; сохранение OEM поведения пульта. Выключение Bluetooth — защищённый/ограниченный сценарий, пока не доказана независимость пульта.
3. **Источники** — Android TV Home, HDMI1/HW6, HDMI2/HW7, статусы, источник при включении, HDMI auto play/hotplug, CEC/Auto Off, EDID readback/условный редактор.
4. **Проекция** — режим яркости источника света (это **не** Picture Brightness), автофокус при включении/движении, автокоррекция, Four Corner, H/V keystone, zoom, ориентация, отдельные связанные параметры. Масштаб текста перенесён сюда в R5.
5. **Изображение** — picture mode, HDR, MEMC, gamma, brightness, contrast, saturation, sharpness, hue, Color Temperature, RGB в User, picture format/overscan при доказанной поддержке. Дизайн R7 описан ниже.
6. **Звук** — sound profile, пять полос EQ, Bass/Treble, Surround/AVC, устройство вывода (Speaker/BT/Auto — эксперимент), цифровой формат/ARC/eARC/SPDIF, индивидуальные задержки, системные звуки.
7. **Приложения** — оригинальная Android TV AppsActivity/AppsFragment, не копировать список OEM приложений.
8. **Настройки устройства** — About, hardware status/temperature, power, date/time/language/storage/security/accessibility, поведение и параметры Android TV. Не создавать пустые разделы.

Разделы 1/7 в значительной степени штатные платформенные. Разделы 3/4/5/6 требуют привязки каждой строки к соответствующему Android/OEM consumer API. Дерево уже согласовано; **не перестраивать с нуля**.

## 6.6 Реальная Android TV навигация

- Графический и функциональный host: оригинальный `com.android.tv.settings.MainSettings` и `MainFragment`, а не новое отдельное приложение.
- MOD страницы: наследование `TvSettingsActivity`, штатный `FlavorUtils → FeatureFactory → SettingsFragmentProvider`, OEM/Leanback `PreferenceScreen`, lifecycle focus/Back/DPAD.
- Не использовать внешние `Intent` extras как произвольные инструкции выполнения hardware action.
- Сохранить штатный TV preview/theme и правила одного/двух панелей, совместимость исходных ресурсов, оригинальных Activity и системной подписи.
- Отдельный explicit launch для проверки MOD alias:

```bash
adb shell am start -n com.android.tv.settings/com.android.tv.settings.mod.SettingsLauncher
```

Данные именно об этой алиасной Activity относятся к R5/R7, а не к исходному stock. Нельзя утверждать, что одна установка MOD автоматически изменит глобальную аппаратную кнопку Settings.

## 6.7 R7 — текущая форма экрана «Изображение»

На ветке PR #10 `NativePicturePanel.showSlider` использует **единое компактное нижнее окно** для PQ и RGB: ширина ограничена приблизительно **66% экрана** с учётом доступных отступов, нижний отступ **28 dp**, `BOTTOM|CENTER_HORIZONTAL`. Раньше видео-PQ диалоги были `MATCH_PARENT` и заполняли почти всю ширину.

`NativeSections.Picture` перестраивает **существующие** Preference в три stock-blue `PreferenceCategory` без дублирования set/get:

```text
Изображение
├── Обработка изображения
│   ├── HDR
│   └── MEMC
├── Цвет и баланс белого
│   └── Цветовая температура -> User RGB / Standard/Cool/Warm...
└── Параметры видеотракта
    ├── Режим изображения
    ├── Информация: Picture PQ воздействует на видео, не на Android UI
    ├── Яркость
    ├── Контрастность
    ├── Насыщенность
    ├── Резкость
    ├── Оттенок
    ├── Гамма
    └── (Условно) формат HDMI-изображения
```

Технический первоисточник: [R7 UI и кнопка 307](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/docs/TVSETTINGSPLUS_8054_R7_PICTURE_SECTIONS_AND_KEY307_20261122.md). AndroidX/UI тесты были проведены; живой внешний вид и взаимодействие владельцу следует проверять отдельно. В текущей рабочей среде имеется локальный `8054_R7_UI_test_results.zip` с XML test results и `ui-evidence/*.png`; он **не** равнозначен физическим снимкам экрана проектора.

## 6.8 Защита пресетов Picture

Пожелание владельца: **не копировать «Кино» в «Пользовательский» и не усложнять поведение**, достаточно запретить ручную регулировку ползунков в заводских пресетах. Инженерное меню по-прежнему может менять factory значения — это не задача MOD.

- `picture_mode` и User ID (`0` согласно OEM mapping для конкретного профиля) проверяются через `PictureUserEditPolicy` и OEM массивы; скалярные PQ-ползунки в preset доступны только для просмотра.
- Guard должен существовать **в UI и в write callback**, чтобы устаревший onClick не записал значение после смены профиля.
- R6 добавил User-only запрет для **гаммы**, а HDR/MEMC/температура остаются независимыми от режима, если OEM не требует дополнительного gating.
- Нельзя выдавать `Settings.Global` readback за физическую проверку PQ. Сохранять сигнал/вход/профиль и rollback перед любыми экспериментальными изменениями.
- Замечание владельца с реального проектора: при `saturation=0` фильм HDRezka становится чёрно-белым, но Android launcher/UI остаются цветными; гамма также явно влияет на видео. Значит эффект PQ **проверен для видео**, но **не** надо распространять его автоматически на композитор Android или все HDMI-входы без теста.
- Соотношение реальных HDMI входов, SDR/HDR и stored `inputGroup=-1` всё ещё требует исследования; по пользовательскому решению это пока **не критический блокер дальнейшей UI-разработки** и не повод спекулировать, работает ли настройка на HDMI.

---

# 7. История Pull Requests и актуальный Git SHA

**Проверено по GitHub 23.11.2026: все перечисленные PR OPEN, DRAFT, NOT MERGED.**

| PR | Ветка / HEAD | Назначение | Важные ограничения |
|---|---|---|---|
| [#1](https://github.com/MAX-TAC/Projector-Soft/pull/1) | `feature/tvsettingsplus-thermal-telemetry`, `ad258ff32a05754eed9b923b3e95bd0ce97f2369` | Исторический 8052 MOD v33 + telemetry, Ku dependencies | Не 8054 релиз; `main` база |
| [#2](https://github.com/MAX-TAC/Projector-Soft/pull/2) | `audit/8054-tvsettingsplus-20261117`, `fbb41e92a47a94a2a4b0f4122100e5a1cb43cfe5` | Baseline exact-8054 v41 / native UI / gated controls | База для параллельных экспериментов |
| [#3](https://github.com/MAX-TAC/Projector-Soft/pull/3) | `research/8054-mediatek-native-api-20261120`, `d1854db0539c522f81f3c2ee355d08338197ae8a` | Полный owner dump, native JNI/HIDL/rpc evidence | STATIC only, без hardware writes |
| [#4](https://github.com/MAX-TAC/Projector-Soft/pull/4) | `feature/8054-product-001-pic04-20261120`, `4c3f68e5bda55dda9a38c232df2667898a456d97` | `Pic04ContrastStep` pure Java guarded policy | Fake Port, не подключён к production editor |
| [#5](https://github.com/MAX-TAC/Projector-Soft/pull/5) | `feature/8054-user-settings-migration-20261120`, `12951829cccfac635ed6815fcc4faa99efe1226e` | Экспериментальные Picture provider writes + 96-item tracker | +1/-1 предварительный шаг; live input/profile не доказан |
| [#6](https://github.com/MAX-TAC/Projector-Soft/pull/6) | `docs/external-ai-complete-handoff-20261121`, `6d3a6c90119e7463e6ee9fa156814ebef19477be` | Полный старый handoff 01–08 + 291 source catalog | Срез до R7 и новых HDR/AFR задач |
| [#7](https://github.com/MAX-TAC/Projector-Soft/pull/7) | `feature/8054-stock-picture-route-20261121`, `c15d7633a35d6564c6eada93e0094a949bceda33` | Подключение подтверждённого штатного PictureActivity | Отдельная ветка от #2; не объединена автоматически с #5 |
| [#8](https://github.com/MAX-TAC/Projector-Soft/pull/8) | `feature/8054-sound-batch-audit-20261121`, `b4dd971bec4dc269c3352312e70ab6eef2043bbe` | Единый read-only Termux аудит SND01–SND13 | Mock CI, не физическое подтверждение эффектов |
| [#9](https://github.com/MAX-TAC/Projector-Soft/pull/9) | `research/8054-direct-mediat-ek-api-contracts-20261122`, `6f3409c9908209342b6a182cc41ea512d9e63e69` | Android/MediaTek consumer контракт: CEC, HDMI, PQ, HDR/DV, MEMC | Исследования, без модификации installed APK |
| **[#10](https://github.com/MAX-TAC/Projector-Soft/pull/10)** | **`feature/8054-v41-picture-sound-safety-20261122`, `b8071b40f2a62ebf2395cb5953ebd245dd8491be`** | **Рабочая R7: picture UI, User guards, EQ/output, launcher alias, key 307 trace** | **Текущий приоритет, ещё Draft; по GitHub base = ветка PR #9** |

Особо учесть **нелинейную историю**: PR #9 основан на `docs/external-ai-complete-handoff-20261121` (#6), PR #10 — на ветке #9; #6 в свою очередь зависит от ветки #5; другие PR идут параллельно от #2. Для ревизии сравнить **merge-base**, файлы в диффе, конфликтующие изменения и реально применённую версию `NativePicturePanel` на HEAD #10. Не объединять PR по номеру вслепую. Старые названия PR/заголовки могут не отражать последующие дописывания в body.

### Важные зафиксированные исходные SHA/CI

- Exact-8054 v41 baseline `a3ca1a2`, APK SHA выше, [run 44769301913](https://github.com/MAX-TAC/Projector-Soft/actions/runs/44769301913).
- PR #4 `4c3f68e`, [run 44808298783](https://github.com/MAX-TAC/Projector-Soft/actions/runs/44808298783) — PIC04 policy tests, не живой эффект.
- PR #5 [UI run 44816235981](https://github.com/MAX-TAC/Projector-Soft/actions/runs/44816235981), [exact APK 44816462929](https://github.com/MAX-TAC/Projector-Soft/actions/runs/44816462929) — сборка не равна acceptance.
- PR #7 — native Android TV PictureActivity route.
- PR #10 R6 [run 45046945295](https://github.com/MAX-TAC/Projector-Soft/actions/runs/45046945295), R7 [run 45050140196](https://github.com/MAX-TAC/Projector-Soft/actions/runs/45050140196) — при продолжении перепроверить run conclusion, exact commit и test reports.

Не записывать SHA-256 APK R5/R6/R7 по догадке; вычислять по реально скачанному финальному asset. В локальной беседе присутствовали кандидаты `TvSettingsPlus-8054-v41-R3/R4/R5/R6/R7-20261122.apk`, но их наличие в папке чата не делает их проверенной последней production прошивкой.

---

# 8. Матрица полноты 96 функций и разделы управления

## 8.1 Источник истины

[`research/8054/FINAL_FUNCTION_PARITY_8054.csv`](https://github.com/MAX-TAC/Projector-Soft/blob/audit/8054-tvsettingsplus-20261117/research/8054/FINAL_FUNCTION_PARITY_8054.csv) — **96 строк**, включая платформенные и непользовательские элементы.

Статусы **старого базового PR #2**: `DIRECT_MOD=22`, `DELEGATED_OEM=23`, `READ_ONLY=21`, `NOT_IMPLEMENTED=17`, `BLOCKED=11`, `HIDDEN=2` (в сумме 96). Это статистика **конкретного исторического среза**, а не актуальный доказанный прогресс на R7. Все аппаратные статусы требовали `RUNTIME_TEST_REQUIRED`.

Трекер прогресса: [USER_SETTINGS_MIGRATION_TRACKER.md](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-user-settings-migration-20261120/research/8054/USER_SETTINGS_MIGRATION_TRACKER.md). При обновлении реестра обязательно различать `present`, `read-only`, `writer`, `backend checked`, `physical effect`, `rollback` и `KuSettings UI independence`.

## 8.2 PICTURE / PQ / PIC

| Функция | Исследованный основной путь | Состояние и особые условия |
|---|---|---|
| Picture mode | OEM enum/readback, TvServices updates dependent values | Статическое взаимодействие есть, побочные значения проверить по каждому пресету |
| Brightness/Contrast/Saturation/Sharpness/Hue | `Settings.Global` → TvServices → `g_video__*` MediaTek config | OEM stock UI имеет работающие ползунки; MOD R7 имеет UI и guards; +1/-1 step, связь с входом не экстраполировать без измерений |
| Gamma | `picture_gamma` → `g_disp__disp_gamma`; отдельный native handler | В R6 доступен для записи только в User; в factory presets read-only, double guard |
| Color Temperature | OEM список `User=0, Cool=1, Standard=2, Warm=3` по текущей таблице; OEM может использовать customer-dependent IDs | Отдельная страница, независимая от picture mode; User позволяет RGB |
| RGB | OEM оригинальные controller keys, зависимость от температуры/режима | Не путать с заводской WB calibration; требуется проверка actual effect и restore |
| HDR ON/OFF | OEM callback `AdvanceSettingsSecondaryController$9/$10`, значения 1/0 | UI флаг ≠ текущий реальный HDR; SDR/HDR metadata определяется playback/video pipeline |
| MEMC/MJC | `tv_picture_advance_video_mjc_effect`, OEM resource pair `0x7f030084/85`, `partner_mjc.xml` | Обычно Off/Low/Medium/High; точные enum и FPS **проверять по stock arrays**. Отдельный MJC demo и FRC — не тот же пользовательский пункт |
| HDMI picture format / overscan | OEM `MtkTvAVModeBase`, `Customize`, `MtkTvFApiDisplay.setOverScan(type,timingIdx,...)` | Заводская ветка зависит от HDMI/timing; не делать auto write и не ломать геометрию |
| Picture Reset | OEM multi-key reset / ALS/FPS/energy metadata | Это не scalar rollback; не предлагать «сброс одного контраста» путём общего сброса |
| Noise Reduction / DNR / MPEG NR | Пока **не найден подтверждённый user callback exact-8054** | Дополнительная исследовательская задача; наличие типичного MTK NR не доказательство доступности функции на этой плате |

### Точный подтверждённый OEM путь для contrast

```text
com.android.tv.settings.partnercustomizer.picture.PictureActivity
  → PictureFragment / ProgressDialogPreference
  → PreferenceConfigUtils.updatePreferenceChanged
  → Settings.Global.putInt("picture_contrast", value)
  → TVMenuSettingsService / SettingObserver
  → TVSettingConfig.setConifg("g_video__contrast", value)
  → MtkTvConfigBase.setConfigValue(configId, value)
  → TVNativeWrapper.setConfigValue_native(-1, configId, value, 3)
  → libcom_mediatek_twoworlds_tv_jni.so
  → a_mtktvapi_config_set_value [JNI → PLT/GOT]
  → отдельная ветка HIDL/service RPC setter
  → реальный HW write [не подтверждён на всём маршруте]
```

Исследование PR #3 показало ELF/JNI и отдельные HIDL/RPC границы. Непрерывная end-to-end native call chain **не доказана**. Спорная семантика `inputGroup=-1`, update mode `3`, адресации HDMI/SDR/HDR и firmware-dependent reapplication остаётся открытой. Принцип: **при наличии оригинального consumer key используй его**; не перешивать HIDL без реального функционального блокера.

Оригинальный `PictureActivity` **проверен владельцем** (`dumpsys window mCurrentFocus/mFocusedApp`): Activity действительно `com.android.tv.settings/.partnercustomizer.picture.PictureActivity`, её редакторы меняют сохранённые значения, которые видны в KuSettings. Это не китайская `com.my.settings` Activity. [Owner verified 21.11](https://github.com/MAX-TAC/Projector-Soft/blob/docs/external-ai-complete-handoff-20261121/research/EXTERNAL_AI_HANDOFF_20261121/08_OWNER_VERIFIED_ANDROID_TV_PICTURE.md).

**Оригинальный `OemPicturePanel`/provider route в отдельных PR неодинаков:** PR #4 отказоустойчивый pure Java step без production write; PR #5 непосредственная запись Global с непроверенным step; PR #7 штатный Activity reuse; PR #10 guarded own controls. Новый агент должен **сравнить реальный код HEAD #10**, а не слепо складывать все эти идеи.

## 8.3 SOUND / SND

| Область | Точные наблюдения / API | Что проверить |
|---|---|---|
| Sound mode | `sound_style`, `g_audio__sound_mode`, OEM User `0`, другие modes с ограничениями | Эффект/связанные EQ/Bass/Treble после переключения |
| Bass/Treble | `sound_bass`, `sound_treble`; `g_audio__aud_bass`, `g_audio__aud_treble`; 0..100 в историческом OEM документе | Эффект именно на выбранном аудиовыходе, не только Global echo |
| Five-band EQ | 5 OEM пользовательских полос, значения из OEM, User profile | Не путать с 13-band factory PEQ; backends и читаемые bounds; изоляция preset/profile |
| Surround / AVC | Профильные ограничения и OEM media outputs | Фактический эффект на audio_flinger/HAL и на слух |
| SPDIF/digital/ARC/eARC | `AudioManager`, `HdmiControlManager`, `audio_policy`, OEM flags и sound_* | CEC side effects, реальный ARC established, формат passthrough, rollback |
| Speaker/SPDIF delay | Отдельные OEM gating conditions, `sound_speaker_delay`, sound_effects / audio_output | Раздельные availability/units, нельзя смешивать |
| Output route | `NativeMediaRouteBridge`, `NativeMediaRoutePicker`, system UID 1000, `MODIFY_AUDIO_ROUTING` | Реальная смена active route Speaker ↔ A2DP в процессе playback, а не изменение предпочтения на бумаге |
| System sounds | Отдельная обычная настройка Android TV | Не ломать штатный keytone при кастомной навигации |

Из live-дампов в пользовательской сессии 22.11:

```text
Speaker: AudioPolicy port 2
BT A2DP Out (Redmi TV Soundbar): AudioPolicy port 18
USAGE_MEDIA / STRATEGY_MEDIA: фактически направляется в A2DP
AudioFlinger: AUDIO_DEVICE_OUT_BLUETOOTH_A2DP
mArcEstablished=false
```

То есть A2DP **работает**, а ARC/eARC **не подтверждён как действующее подключение**. `0 Effect Chains` во время конкретного воспроизведения — повод исследовать DSP/EQ, но не доказательство, что весь OEM EQ не влияет на динамики или BT (возможен другой аудиопуть).

### Аудиопереключатель R3–R7: предупреждение

В PR #10 разработан экспериментальный media-route picker на `AudioProductStrategy`/`AudioManager.setPreferredDevicesForStrategy` с runtime permission check, перечислением действительных Speaker/A2DP, сохранением prior preference, `removePreferredDeviceForStrategy` для Auto, повторной проверкой и **обязательным пользовательским подтверждением слышимого звука**; по timeout/закрытию/ошибке должна выполняться попытка отката. Длительность окна подтверждения в источнике: 25 сек, первичный readback 4,5 сек.

Но сама реализация **не подтверждена успешным переключением на железе**. Есть архив `8054_route_fail.zip`: в снимке после соответствующего сценария AudioTrack `USAGE_MEDIA` остаётся deviceId 18, AudioPolicy и AudioFlinger показывают BT A2DP. `logcat.txt` внутри этого архива пустой. **Не объявлять поддержку Speaker↔BT работающей и не делать вывод о точной причине только по этому ZIP**. Нужны synchronous logcat, output picker logs, preferred strategy и AudioFlinger при попытке.

[Audio hardware acceptance PR #10](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/docs/TVSETTINGSPLUS_8054_AUDIO_ROUTE_HARDWARE_ACCEPTANCE_20261122.md) и [Audio implementation](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/docs/TVSETTINGSPLUS_8054_V41_PICTURE_SOUND_IMPLEMENTATION_20261122.md).

Нельзя считать, что если устройство видно в `AudioManager.getDevices(GET_DEVICES_OUTPUTS)`, оно доступно через предпочтение одного media strategy. `getPreferredDevicesForStrategy` показывает preference, не гарантированный actual hardware routing.

## 8.4 HDMI / SOURCE / CEC / EDID

- Два физических порта: **HDMI1=HW6, HDMI2=HW7** на exact 8054; для одного HDMI 8052 другой профиль.
- Нативный путь выбора через TV Input / LiveTV passthrough найден; `TvInputManager.getInputState` говорит о connected/not connected, но **не** определяет текущий активный physical input.
- Boot source/boot app — разные OEM сценарии, не подменять одним переключателем. `KuSourceRJ` критичен для системного поведения.
- **CEC main enable**: штатный consumer `CompatibleApis.setHdmiCecControlEnabled`/Android `HdmiControlManager`, изменения могут затронуть eARC и auto device off. **CEC auto-off** — отдельный callback, не тот же глобальный флаг.
- **ARC/eARC**: наличие HAL или UI не гарантирует `mArcEstablished`; при текущем ADB проверка `false`, физический handshake не доказан.
- **EDID**: stored mode/readback не гарантирует, что порт фактически пересогласовал EDID; возможен разрыв HDMI, смена HDR/audio capabilities. Нужны раздельные проверки обоих портов и обратимость.
- **HDMI picture format/overscan**: точная OEM процедура зависит от input type, timing index, `MtkTvFApiDisplay.setOverScan` и сохранения `HDMIOverscanSetting`.
- **Game mode**: может влиять на задержку/путь видео и вызывать resetTrapezoid/keystone. До реального теста не внедрять автоматические writes.
- После нескольких циклов источника/режима проверить, не протекают ли picture параметры между HDMI1/2 или между SDR/HDR; пользователь решил **не задерживать весь проект ради неподтверждённых частных случаев**, но фиксировать их как открытые.

Первоисточники:
- [HDMI_BLOCK_STATUS_8054.md](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/research/8054/HDMI_BLOCK_STATUS_8054.md)
- [HDMI_PICTURE_FORMAT_8054.md](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/research/8054/HDMI_PICTURE_FORMAT_8054.md)
- [EDID_GLOBAL_ROUTE_8054.md](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/research/8054/EDID_GLOBAL_ROUTE_8054.md)
- [MTK_DIRECT_CONSUMER_CONTROL_CONTRACT_20261122.md](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/research/8054/MTK_DIRECT_CONSUMER_CONTROL_CONTRACT_20261122.md)

## 8.5 PROJECTION / PRJ

Обычные пользовательские функции: orientation Front/Rear/Ceiling, LED/light source brightness mode, автофокус после включения и при перемещении, авто-трапеция, manual focus, 4-corner, H/V keystone, digital zoom, obstacle avoidance и auto screen fit только при актуальной плате/сенсорах.

- Нативные OEM пути часто используют `ProjectorManager`, `Factory ApiService`, `RuiAutoFocus`, `KeystoneCorrection`, `KuSourceRJ` и proprietary callbacks. **Используй проверенные consumer controls, не копируй моторные algorithms в MOD**.
- `OemProjectionPanel.projectionIntent()` в старом состоянии мог явно указывать `com.my.settings.activity.ProjectionActivity`. Такой user route противоречит финальному требованию M1. Требуется ревизия реального PR #10 и подмена на собственную страницу/штатный non-Chinese backend без потери hardware controls.
- Для FourCorner/DigitalZoom возможно временное использование **штатного аппаратного редактора** из другого (не китайского) OEM пакета, но это не всегда означает завершённый собственный UI. Проверять exact exported Activity/permission/gesture.
- Значение Picture Brightness и яркость источника света LED — **разные** параметры.
- Не вводить factory calibration, скрытые I²C, raw motor steps, fan/thermal параметры как стандартные незащищённые ползунки.
- Для регулировок, связанных с физическим движением, нужны защита от повторной отправки, пределы, реальное устройство/профиль, stop/restore и согласованный hardware test.

[PROJECTION_BLOCK_8054.md](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/research/8054/PROJECTION_BLOCK_8054.md) и [8054_RELEASE_MENU_TREE.md](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/docs/8054_RELEASE_MENU_TREE.md).

## 8.6 POWER, SYSTEM, BOOT и OTHER

Проверенные/исследованные области: включение после подачи AC, выбранный источник/приложение при boot, timeout/sleep/dream/saver, power-off timer/schedule, системные звуки/масштаб текста, статус CPU/temperature, Android About/Apps/Network/BT. Сохранить native power handlers и OEM recovery paths; не смешивать разные timers: `power_sleep_timer`, `power_switch_off_timer`, `TimerSetActivity` могут иметь разные условия.

В Android TV уже есть зрелые платформенные настройки — не переносить их заново, если они работоспособны. Особое внимание: Bluetooth HID пульт, автоподключение по OEM имени и сервиса, recovery после зависания `KuSourceRJ.TimeService` и телеметрия вентиляторов/температуры.

## 8.7 Удаление KuSettings: основная найденная зависимость

```text
com.my.settings / KuSettings
  BootupReceiver (BOOT_COMPLETED)
    → IntentUtils.startTime
    → MySetTimeService.onStartCommand
    → TIME_TICK receiver (MySetTimeService$1)
    → KuSourceRJ.TimeService recovery / restart
         ↳ связанная логика power/thermal/fan/vendor
```

Эта цепочка в статическом 8054 анализе **доказана как кодовая зависимость**, её runtime необходимость/полное действие в разных ошибках ещё требует аппаратных проверок. `KuSourceRecoveryBootReceiver` и `KuSourceRecoveryService` в MOD source существуют, но исторически были **неактивными / без boot filter и без hardware qualification**; их наличие не означает готовую замену watchdog.

Другие потенциальные зависимости: AutoBluetooth/MyAutoBluetoothActivity, Wi-Fi Display/Miracast, KuSourceRJ, явные ComponentName вызовы KuSettings из system services и OEM SetupWizard. Действительный reachable edge на 8054 отличать от строкового совпадения в классе 8052.

**Категорический запрет до M2:** `pm disable-user com.my.settings`, удаление системного APK, удаление `KuSourceRJ`, выключение привязанных сервисов, перехват boot receiver без проверки альтернативы. При отказе критической фоновой службы может страдать не только меню, но охлаждение и цикл загрузки.

Первоисточники: [KUSETTINGS_DEPENDENCIES_8054.md](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/research/8054/KUSETTINGS_DEPENDENCIES_8054.md), [KUSETTINGS_SERVICE_MIGRATION_8054.md](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/research/8054/KUSETTINGS_SERVICE_MIGRATION_8054.md), [KUSETTINGS_RETIREMENT.md](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/docs/KUSETTINGS_RETIREMENT.md).

---
# 9. Аппаратная кнопка SETTINGS: точно установлена причина, переназначение ещё не сделано

Владелец подтвердил, что независимый ярлык MOD запускается:

```bash
adb shell am start -n com.android.tv.settings/com.android.tv.settings.mod.SettingsLauncher
```

Но физическая кнопка **Settings** на пульте всё ещё вызывает старую китайскую/OEM плавающую панель. Архив диагностики `8054_settings_route.zip` дал конкретную цепочку:

```text
20:13:38.278  TrdTvWindowMangerImpl interceptKeyBeforeQueueing keyCode:307
20:13:38.280  trdservice KeyEventCtrlService interceptKeyBeforeQueueing keyCode:307 down:true
20:13:38.321  ActivityManager starts process com.android.tv.settings
               for service com.android.tv.settings.uicustom.floatmenu.FloatMenuService
20:13:38.779  FloatMenuManager showMenu
20:13:38.924  FloatMenuManager Loading initial sub menu for index: 0
```

Отдельно проверено:

```text
android.settings.SETTINGS    → com.my.settings/.SettingActivity
android.settings.RJ_SETTINGS → com.android.tv.settings/.uicustom.MainActivity
```

Но **физическое нажатие** не использует ни один из этих implicit Intent. Оно перехватывается policy `TrdTvWindowMangerImpl`/`PhoneWindowManager` и запускает `FloatMenuService` напрямую; окно имеет `APPLICATION_OVERLAY`. Поэтому R5 попытка перехвата `android.settings.SETTINGS` через `activity-alias` не решила проблему; этот generic filter **убран в R7**, оставлен отдельный иконный launcher alias.

**Искомое решение:** найти безопасную точку перенаправления оригинального системного service/policy пути на `MainSettings`, не делая китайский UI частью работающего MOD, без уничтожения boot/focus/volume/remote path. Варианты — проверенная поддержка изменения default action в политике, контролируемый patch OEM service, либо система с гибкой маршрутизацией клавиш, **но выбор только после чтения exact original code и отката**. Нельзя просто удалить `FloatMenuService`, `KuSettings` или менять keylayout наугад.

Первоисточник: [R7 remote key 307](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/docs/TVSETTINGSPLUS_8054_R7_PICTURE_SECTIONS_AND_KEY307_20261122.md).

---

# 10. Изображение: HDR, Dolby Vision, HDR10+, HDR Vivid, MEMC — исследования 22.11

Этот раздел основан на **ранее предоставленных в текущей исследовательской сессии архивных ADB/ELF материалах** плюс результатах их изучения. **Не все сырые большие `.ko/.so` файлы опубликованы в GitHub.** Перед написанием драйверного патча повторно воспроизводи сигнатуры, дизассемблирование и значения на реальном устройстве. Факт наличия символа = `STATIC_CONFIRMED`, не `HARDWARE_EFFECT_VERIFIED`.

## 10.1 HDR capabilities Android / HWC

Из архивов `8054_hdr_audit.zip`, `8054_hdr_caps.zip`:

```text
Display.HdrCapabilities.mSupportedHdrTypes=[2, 3]  # HDR10, HLG
SurfaceFlinger/HWC Support:
  wideColorGamut=false
  hdr10plus=false
  hdr10=true
  hlg=true
  dv=false
  metadata=3
```

**Подтверждённый пользовательский вывод:** HDR10 и HLG заявлены; Dolby Vision и HDR10+ как полноценные режимы дисплея HWC **не объявлены**. Наличие OEM строк Dolby Vision и `media_codecs.xml` не меняет результат `dv=false`.

### HDR10+ реальный тест ролика

В `8054_hdr_atmos_20261122_231713.zip`, сценарий `HDR10_PLUS`:
- media renderer/logcat output format содержал `hdr10-plus-info=java.nio.HeapByteBuffer[pos=0 lim=49 cap=49]` и HDR static info;
- видеослой SurfaceFlinger в этом тесте указывал `dataspace=BT2020_ITU_PQ`, `hdr metadata types=4` — этот бит относится к типу **динамических HDR10+ метаданных SurfaceFlinger**, не Android integer `HdrCapabilities`;
- HWC при этом по-прежнему `hdr10plus=false`.

**Вывод:** динамические данные проходят декодер и доходят до compositor layer; использование их проекторным tone mapping в реальном оптическом изображении **не доказано**. Возможен HDR10 fallback. Отдельный нативный MediaTek видеопуть также не исключён.

### Dolby Vision реальный тест

В сценарии с роликом **Dolby Vision Profile 5** (названия двух полей теста `DV_P7` и `DV_P8` — только названия файлов/этапов, а не реально проверенные профили!) в `DV_P7_logcat.txt`:

```text
GTVBox Native: Dolby Vision metadata found (not supported). Reveting to: 31766568
MediaEngineNC: Video track added: video/hevc. HW: 1
configureCodec: codecName = c2.mtk.hevc.decoder
```

Владелец наблюдал неправильные/инвертированные цвета. Второй этап использовал **тот же Profile 5 файл**, не отдельный P7/P8 ролик. Поэтому нельзя писать «проверены и не работают все Dolby Vision P5/P7/P8». Доказано только неработающее DV P5 воспроизведение в конкретном плеере/конфигурации; был использован обычный HEVC decoder.

### Dolby Atmos

В тесте с BT A2DP `AudioFlinger` выводил PCM 16 bit stereo 48 kHz. HAL сообщал отсутствующую активную ARC capability. **Не доказано**, что внутри файла отсутствовало декодирование Atmos или что устройство никогда не декодирует Atmos; было доказано отсутствие Atmos bitstream на текущем A2DP выходе. Для E-AC3/JOC/TrueHD/MAT нужен отдельный тест начала playback и совместимого HDMI audio sink.

## 10.2 Извлечённые нативные файлы

Последовательно собранные read-only архивы:

| Архив | Содержание / обнаруженное |
|---|---|
| `8054_hdr_libraries.txt` | Первоначальный узкий поиск; случайный hit `libkeystoneCA.so` из-за подстроки `tone` в `keystone` — **не** HDR evidence |
| `8054_hdr_components_v2.txt` | HWC, `libcodec2_mtk_vdec.so`, `libcodec2_mtk_c2store.so`, `kdrv_hdrvivid.ko`, HWC config/service |
| `8054_hdr_native.zip` | `hwcomposer.mt5873.so`, Codec2 video libs, `kdrv_hdrvivid.ko`, `hwcomposer13.ini`, `composer_service.rc`, kernel modules/properties |
| `8054_hdr_backend.zip` | `libmi3.so`, `libmi3_client.so`, `libmmdisp.so`, `libcodec2.MTK.so`, `vendor.mediatek.api.mtktvapi@1.0-cwrapper.so` |
| `8054_hdr_driver.zip` | `libutopia.so`, `mik.ko`, `dtv_driver.ko`, `/proc/modules` |
| `8054_hdr_caps.zip` | `utpa2k.ko`, `kdrv_xc.ko`, `kdrv_alg.ko`, `surfaceflinger.txt`, kernel capture, module parameters |

Большие бинарники находятся в файлах, предоставлявшихся владельцем в чате; следующий агент должен **попросить конкретные архивы или открыть их в переданной среде**, а не полагаться только на это описание.

## 10.3 Проверенные/ранее установленные границы исполнения HDR

Из анализа ELF/драйверов в проекте:

```text
libcodec2_mtk_vdec.so
  Hdr10PlusInfoInputSetter / Hdr10PlusInfoOutputSetter
  Hdr10PlusFromContainer / SendHdr10Plus
  input.hdr10-plus-info / output.hdr10-plus-info

libcodec2.MTK.so
  MsVdec_CheckSupportDolbyVision
  MSVdecConfigDolbyVision
  Wrapper_MsVdec_GetDolbyVisionSupportProfile
  Wrapper_MsVdec_SetHDR10PlusConfig

libmi3.so
  MI_DISP_GetCaps
  mi_video_GetDolbyVisionInfo

hwcomposer.mt5873.so
  HWComposerDisplayHalMiOsd::getHdrCapabilities
  → MI_DISP_GetCaps

mik.ko
  MI_VDEC_GetDolbyVisionInfo / _MI_VDEC_GetDolbyVisionTable
  _MI_VDEC_GetMetaData_HDR10PLUS / _MI_VDEC_SetHDR10PLUSInfo
  _MI_VIDEO_FillXcShmMetadata
  MI_DISP_GetCaps → mi_hwcaps_GetDispCaps / MApi_XC_GetChipCaps

kdrv_xc.ko
  KHal_XC_SupportHDR10PLus / KHal_XC_SupportDolbyHDR
  KDrv_XC_Debug_CfdGetHdr10PlusEnable
  KDrv_XC_Debug_CfdSetHdr10PlusEnable
  KDrv_XC_DV_Wrapper_GetDolbyCapabilityInfo

kdrv_alg.ko
  MHal_Cfd_HDR10Plus_Gen12PointTmo
  MHal_Cfd_HDR10Plus_Gaming_Gen12PointTmo
```

По ранее сделанному дизассемблированию `KHal_XC_SupportHDR10PLus` и `KHal_XC_SupportDolbyHDR` в данной сборке возвращают `1`, но это **не** эквивалент полной возможности дисплея. Для DV были обнаружены callback/настройки таблиц LUT и отдельная проверка профилей через драйвер. Изучен код обращения `MI_DISP_GetCaps` в `libmi3.so` к ioctl `0xC01C1202`, а `mi_video_GetDolbyVisionInfo` к ioctl `0xC01415AB` (значения зафиксированы в прошлом ELF-разборе, **перепроверять на оригинальном бинарнике**). API `Wrapper_MsVdec_SetHDR10PlusConfig` относится к декодеру, не доказанному включению режима дисплея.

**Не найден:** достоверный безопасный универсальный переключатель Dolby Vision/HDR10+ для конкретной платы; нет device-level позитивной проверки сквозного tone mapping. Пользователь **отложил** дальнейшую глубокую работу над DV/HDR10+: не превращать это в главный приоритет без его нового запроса.

## 10.4 HDR Vivid

В модуле `/vendor/lib/modules/kdrv_hdrvivid.ko` присутствовали:

```text
HDRVIVID driver
HDRVIVID_1_2_0
MApi_HDRVivid_CalcCurve
MDrv_HdrVivid_Handle
CuvaMetadata
```

В `/proc/modules` соответствующий драйвер **загружен**; в момент проверки use-count равен нулю. HDR Vivid — **не** HDR10+ и не Dolby Vision. Наличие кода tone mapping не доказывает реальную обработку конкретного видео. Не использовать его «как обманку» для DV.

## 10.5 MEMC / MJC: режимы, FPS и механизм

В OEM 8054 есть пользовательский ключ `tv_picture_advance_video_mjc_effect` и resource pair `0x7f030084/85` (`partner_mjc.xml`); UI находится в `MemcSettingsActivity`/OEM MJC-пути. Типичная пользовательская шкала — **Off / Low / Medium / High**, но конкретный список числовых значений надо читать из OEM resource array и результата активного пользовательского профиля.

**Что такое MEMC:** Motion Estimation / Motion Compensation — анализ двух соседних видеокадров, вычисление векторов движения, построение промежуточных изображений и выдача на FRC/video path. Нейросеть и NPU **не обязательны**; аппаратные специализированные блоки выполняют такие операции без DLSS-подобной архитектуры.

**Чего не знаем для MT5873:** сколько искусственных кадров в секунду реально добавляет каждый уровень Low/Medium/High; используют ли они единый target 50/60 Гц или разные пороги качества/сглаживания; реальные frame buffers, latency и ошибки на HDMI. Символы `FRC Enable`, `KHal_XC_GetFRCFrameCount`, `KDrv_XC_FRC_EnableBWCtrl` показывают инфраструктуру FRC, но не конкретный runtime fps.

Пример **только теоретического** пересчёта (не measured 8054): 30→60 Hz может добавлять 30 промежуточных изображений/с; 25→50 — 25; 24→60 — 36 при непостоянной временной разметке. Low/Medium/High не обязательно означают соответственно 1/2/3 дополнительных кадра.

Достоверный пользовательский эксперимент — одинаковый 24/30 FPS motion test ролик, MEMC Off/Low/Medium/High, камера 120/240 fps, анализ экранного движения, артефактов, физической задержки. Статистика FPS плеера не измеряет кадровую интерполяцию **после** декодирования.

---

# 11. AFR, VRR, ARR, частота и «мыльный» 1080p Android (новые задачи 23.11)

**Эти пункты обсуждены после основных GitHub PR и пока не оформлены отдельным проверенным кодовым изменением.** Доступна read-only предварительная база из ранее собранного `8054_hdr_audit.zip`.

## 11.1 Точные данные дампа `dumpsys display` / SurfaceFlinger

```text
supportedModes:
  3840 × 2160 @ 50.000 Hz
  3840 × 2160 @ 60.000004 Hz
mActiveModeId=2
mRefreshRateChangeable: false
supportsFrameRateOverrideByContent=false
mCurrentLayerStackRect=Rect(0, 0 - 1920, 1080)
mCurrentDisplayRect=Rect(0, 0 - 3840, 2160)
mBaseDisplayInfo: real 3840×2160
mOverrideDisplayInfo: real 1920×1080
```

**Интерпретация:** Android сообщает только 50/60 Hz как режимы встроенного дисплея; активен 60 Hz. Логическая композиционная область Android **1920×1080** масштабируется на выходную область **3840×2160**. Это гораздо сильнее пользовательского визуального предположения «интерфейс как 1080p», но надо отдельно изучить физические planes, матрицу и размеры отдельных graphic buffers. `3840x2160` в Android не является само по себе доказательством нативной физической матрицы.

В дампе одновременно виден `Surface.setFrameRate` request для одного UID на 60 Hz, однако `supportsFrameRateOverrideByContent=false`; сам запрос **не означает** смену display mode. В нескольких HDR/DV/Atmos снимках оставался 60 Hz.

## 11.2 AFR — Auto Frame Rate

Цель: оптимально выводить 23.976/24/25/30/50/60 FPS без неравномерных микрорывков, **если аппарат поддерживает нужные тайминги**.

| Исходный FPS | Подходящий доступный mode | Вывод |
|---|---|---|
| 25 | 50 Гц | Равномерное повторение ×2, нет обязательной нужды в отдельном 25 Гц |
| 30 | 60 Гц | Равномерное повторение ×2, нет обязательной нужды в отдельном 30 Гц |
| 50 | 50 Гц | 1:1 |
| 60 | 60 Гц | 1:1 |
| 24 | 60 Гц | Неравномерный 3:2 cadence, возможен judder |
| 24 | 48 Гц (гипотетически) | Равномерный ×2, но режим **не объявлен устройством** |
| 23.976 | 47.952 Гц (гипотетически) | Равномерный ×2, но режим **не объявлен** |

Android 13 имеет `Surface.setFrameRate()`/display mode preferences, но **плеер должен подавать hint, а DisplayManager/HWC обязаны разрешить переключение**. Глобальное переключение для нескольких сторонних плееров не реализуется одним простым callback приложения настроек; могут потребоваться системные hooks и различные сценарии Foreground/video surface/HDMI.

**Перспектива:** сначала безопасно проверить реальное переключение 50↔60, затем статически исследовать 48/47.952 Hz в MediaTek timings; **не прописывать** новый 24/48 Гц режим вслепую. Неверный тайминг может дать чёрный экран/сбой вывода. Увеличение количества modes в `dumpsys` не является само по себе физической поддержкой.

## 11.3 VRR / FreeSync и ARR

- **AFR/MRR:** переход между отдельными фиксированными display modes (50 ↔ 60 и, возможно, 48 при подтверждённой аппаратной поддержке).
- **VRR/FreeSync/HDMI VRR:** физически изменяющийся интервал обновления по кадрам/источнику. Требует совместимого HDMI receiver, timing controller, display pipeline, буферов/FRC и матрицы. В конкретном 8054 **не подтверждён**.
- **Стандартный Android ARR** в архитектуре новых Android версий не равнозначен FreeSync; типовая реализация появилась позже Android 13 и требует соответствующего HAL/ядра. На текущем 8054 Android 13 + HWC 2.4, **нет оснований утверждать наличие стандартного ARR**. Наличие фирменного не-AOSP адаптивного механизма MStar/MTK отдельно не исключено и отдельно не доказано.

Для кино с постоянным FPS AFR/правильный cadence важнее игровой VRR. Пользователь считает VRR интересным, но не основной текущей задачей.

## 11.4 1080p UI и рывки меню

**Один уже доказанный факт:** `mOverrideDisplayInfo 1920x1080` при физическом display frame 3840x2160. Это может объяснить размытие мелких шрифтов/иконок, тогда как 4K-video идёт отдельным MediaTek Video Plane и выглядит чётко. Времена кадров UI и frame drops **не измерены**, ощущение 30 FPS пока гипотеза.

Нужна read-only диагностика:
- `adb shell wm size`, `wm density`;
- `dumpsys display`, `dumpsys SurfaceFlinger`, размеры Layer/Buffer/SourceCrop;
- `dumpsys gfxinfo com.android.tv.settings framestats` **после** controlled reset histogram и 15–20 сек реальной навигации;
- `dumpsys cpuinfo`, `dumpsys meminfo com.android.tv.settings`, возможно `dumpsys graphicsstats`;
- systrace/Perfetto по отдельному согласию (без длительной фоновый записи);
- сравнение stock `MainSettings`, MOD `MainSettings`, launcher и video playback, не путая разные процессы.

**Не выполнять сходу:** `wm size 3840x2160`, изменение `ro.surface_flinger.*`, SurfaceFlinger/HWC patch, неизвестные OEM DP/OSD параметры. 4K UI увеличит нагрузки на GPU/буферы в ~4 раза и может ухудшить скорость/стабильность.

## 11.5 Шумоподавление DNR / MPEG NR

Выполнялось обсуждение возможных функций MediaTek:
- DNR/Noise Reduction — подавление случайного шума;
- MPEG NR — подавление блоков и mosquito noise из сжатого видео.

**На exact-8054 пока нет подтверждённого consumer control path/enum для этих опций.** Их надо искать в OEM Picture advanced, factory PQ конфигурациях и TV API, но не переносить заводские калибровки без понимания побочных эффектов. Сильное NR размывает фактуры/плёночное зерно. Включать UI пункт только после обнаружения реально поддерживаемого OEM consumer backend, диапазонов и readback.

---

# 12. Аудит прошивки и код — что проверено, а что ещё нужно доказать

## 12.1 Техническая карта основных программ и служб

| Программа/слой | Роль | Что нельзя делать без анализа |
|---|---|---|
| `com.android.tv.settings` / TvSettingsPlus | Реальный Android TV Settings, MainSettings, OEM partnercustomizer/uicustom, platform signer | Не менять package/signature/UID/manifest без exact проверки |
| `com.my.settings` / KuSettings | Китайский user GUI + boot/service dependencies | Не удалять после одного успешного запуска MOD |
| `TvServices` / `TVMenuSettingsService` | Отражение Settings.Global → OEM TVSettingConfig / MediaTek config, async sync | Не заменять низкоуровневые функции простыми storage flags |
| `KuSourceRJ` / TimeService | Источники, загрузочное поведение и связанная recovery/thermal логика | Не отключать service owner |
| `trdservice`, `trdmiddle` | Пульт, OEM key 307, источники/прочие hardware события | Не менять input policy без разборки полного key route |
| `LiveTV`, `TvInputManager` | HDMI passthrough, input states | Не смешивать connected input с foreground active HDMI |
| `RuiAutoFocus`, `KeystoneCorrection` | Оптика, фокус, geometry, ToF | Не посылать случайные raw motor commands |
| `Factory.apk` | Инженерные интерфейсы / калибровка / диагностика | Не делать Factory UI промежуточным обработчиком пользовательских строк |
| `libcodec2*.so`, `libmi3.so`, `hwcomposer.mt5873.so`, `mik.ko`, `kdrv_*.ko` | Codec2, display capabilities, HDR/FRC/PQ, низкоуровневые драйверы | Наличие функции или хеша не доказывает hardware-enabled |
| `zxlauncher`, `zxstore`, `KuSetupWizard` | Launcher/магазин/первичная настройка | Не удалять до отдельного HOME fallback и first-boot плана |

## 12.2 Механизмы прямых consumer вызовов

**Приоритет:** использовать `Android`/OEM **consumer** путь, прежде чем идти к HAL:

```text
UI action
  → OEM-proven consumer callback/getter
  → Settings.Global / Android framework API / OEM service
  → TvServices observer / HAL
  → verify backend readback
  → verify physical effect when possible
```

Правило для каждой новой функции:

```text
probeCapability
→ readBaseline
→ verifyExactDeviceAndContext(input, signal, mode, activeOutput)
→ validateOriginalEnumAndBounds
→ applyViaVerifiedConsumerPath
→ awaitStableReadback (not provider echo alone)
→ verifySideEffects
→ commit evidence OR controlled manual rollback
```

Если поведение недоступно — **fail-closed**, read-only или скрыть по доказанной штатной availability; не угадать значение. Никогда не рассчитывать на `Settings.Global.putInt` как независимое подтверждение, что аппарат применил режим.

## 12.3 Аудиты по областям: где смотреть

| Направление | Канонический источник |
|---|---|
| Обзор прошивок, hashes, 8052/8053/8054 | `research/EXTERNAL_AI_HANDOFF_20261121/01_FIRMWARE_REPOSITORIES_AND_RELEASES.md` |
| Custom ROM, MBOOT, AVB, GPT/LP, restore | `.../02_CUSTOM_FIRMWARE_FEASIBILITY.md`; `FlixTone_8054_Backup/docs/*` |
| MOD APK v41, версия, структура, 96 статус | `.../03_TVSETTINGSPLUS_MOD_TECHNICAL_STATE.md` |
| Полное пользовательское ТЗ, критерии готовности | `.../04_PRODUCT_REQUIREMENTS_AND_ACCEPTANCE.md` |
| Источники, ошибки, риски, план независимой проверки | `.../05_EVIDENCE_OPEN_QUESTIONS_AND_REVIEW_PLAN.md` |
| 291 pinned ссылок | `.../06_SOURCE_CATALOG.md` |
| Готовое ТЗ другому ИИ | `.../07_INDEPENDENT_AI_REVIEW_TASK.md` |
| Действующая штатная PictureActivity, owner ADB | `.../08_OWNER_VERIFIED_ANDROID_TV_PICTURE.md` |
| Native JNI/ELF/HIDL/PIC04 | PR #3 `research/8054/native/*` |
| All consumer direct API control map | `research/8054/MTK_DIRECT_CONSUMER_CONTROL_CONTRACT_20261122.md` |
| UI дерева v41 | `docs/8054_FINAL_MENU_SPEC.md`, `docs/8054_RELEASE_MENU_TREE.md` |
| R7 визуальные изменения, key 307 | `docs/TVSETTINGSPLUS_8054_R7_PICTURE_SECTIONS_AND_KEY307_20261122.md` |
| Picture read/write / native implementation | `research/8054/PICTURE_BLOCK_STATUS_8054.md` |
| Sound routes, EQ, Dolby/DTS, delay | `research/8054/SOUND_BLOCK_STATUS_8054.md`, `AUDIO_EQ_PQ_STATIC_ROUTE_8054.md`, `AUDIO_DELAY_8054.md` |
| HDMI / EDID / Format | `research/8054/HDMI_BLOCK_STATUS_8054.md`, `HDMI_PICTURE_FORMAT_8054.md` |
| Focus, orientation, keystone, zoom | `research/8054/PROJECTION_BLOCK_8054.md` |
| KuSettings service dependencies | `research/8054/KUSETTINGS_DEPENDENCIES_8054.md`, `KUSETTINGS_SERVICE_MIGRATION_8054.md` |
| Testing procedure | `research/8054/DEVICE_TEST_MATRIX_8054.md`, `docs/8054_HARDWARE_TEST_PLAN.md` |
| Read-only ADB scripts | `tools/collect_tvsettingsplus_adb_diagnostics.sh`, `tools/diagnose_8054_v40.ps1` |

Для приоритета на дату 23.11 используй документы в **HEAD PR #10**, а не автоматически `main`. Для firmware и старых экспериментов сохранить конкретные commit и SHA.

---
# 13. Практическая процедура работы ИИ-агента и Quality Gates

## 13.1 Прежде чем менять исходники

1. Получить `git status`, список remotes/branches, `git rev-parse HEAD`, base/merge-base для PR #9/#10.
2. Прочитать **`AGENTS.md` если он реально существует в этой checkout**; не предполагать его наличие по разговорам. Уточнить систему логов задач и уже существующие project conventions. Не перезаписывать пользовательские инструкции автоматически.
3. Прочитать исходный `README.md`, активный `docs/8054_RELEASE_CHANGELOG.md` и relevant source/tests; составить минимальный воспроизводимый test case.
4. Выяснить, какие ограничения взяты из физического ADB, какие — из исходников 8052 или фабричного 8054, а какие из тестовых stub.
5. Не объединять соседние исторические ветки автоматически; если требуется объединение, сделать separate merge analysis / conflict map и согласовать с владельцем.
6. Каждое потенциальное изменение классифицировать: `UI ONLY`, `ANDROID API`, `OEM USER CONFIG`, `MEDIA ROUTE`, `CEC/EDID`, `OPTICS/MOTOR`, `FACTORY`, `BOOT/FLASH`. Для последних категорий обязательный отдельный риск/restore.

## 13.2 Правильная структура записи каждого audit/control

Для новой пользовательской функции заводить короткую карточку или запись в матрице:

```yaml
id: PIC-or-SND-or-HDM-or-PRJ-...
name_ru: "..."
source_device: "FlixTone 8054 / factory 8054 / OTA 8052 (не смешивать)"
source_commit: "exact sha"
original_activity_and_callback: "package/class/method"
original_provider_or_service_key: "..."
actual_backend_getter: "..."
actual_backend_setter: "..."
value_enum: "read from exact OEM resources"
min_max_step_units: "measured OEM or UNKNOWN"
current_input_signal_profile: "known or UNKNOWN"
possible_side_effects: ["..."]
mod_controller: "exact filename/class"
mod_state: "READ_ONLY | SOURCE_IMPLEMENTED | BUILT_UNTESTED | DEVICE_TESTED"
physical_effect_evidence: "file timestamp + observation or NONE"
rollback: "actual known baseline + manual recovery, or NOT SAFE"
ku_ui_dependency: "NONE | REMAINS | UNKNOWN"
confidence: "STATIC_CONFIRMED | DEVICE_8054_OBSERVED | NOT_VERIFIED"
```

Значения `UNKNOWN` не заменять домыслами. Статус `SOURCE_IMPLEMENTED` не равнозначен `DEVICE_TESTED`. Для каждой версии APK вести **отдельный** файл `source SHA`, `CI run`, `APK SHA256`, signing cert, versionCode, test log, hardware regression report.

## 13.3 Уровни испытаний / приёмка

### P0 — офлайн/статические тесты

- Сравнение ROM blobs, source dependencies, DEX/manifest/resource diff;
- Java compile, unit tests, Robolectric/AndroidX UI;
- exact-8054 signed APK build при действительном SHA input;
- `apksigner verify --print-certs`, package/version/shared UID/preferred Activity;
- `zipalign`, целостность контейнера, сохранение OEM DEX/resource files;
- никаких новых небезопасных exported Activity, receiver или permission loopholes;
- изменение документируется в changelog и матрице.

### P1 — read-only диагностика живого 8054 (только по разрешению)

- Снять machine/Android/build/installed APK SHA, signer/PM policy;
- записать активный HDMI/source/HDR/SDR, picture/sound mode, CEC/eARC/BT route;
- применить `dumpsys`, `getprop`, logcat и штатные readings без writes;
- проверить возможный восстановительный путь после падения Settings и наличие отдельного ADB доступа;
- обезличить личные данные, MAC, Wi-Fi и account information в архиве перед публикацией.

### P2 — проверка установки конкретного APK

- Получить отдельное разрешение пользователя на установку именно выбранного APK/hash;
- заранее подготовить фактический ручной restore, а не предположение «сможем удалить обновление»;
- проверить Home/Settings, D-pad, Back, фокус, preview, сохранённые меню и доступность ADB;
- выполнить живую фото/UI приёмку R7 компактных ползунков и трёх категорий.

### P3 — отдельная безопасная проверка настройки

- Базовый readback, записанный оригинальный профиль, режим сигнала, HDMI, audio output;
- одно минимальное изменение через **известный OEM user control**, не Factory API;
- стабильное чтение backend, внешний эффект, отсутствие collateral state;
- ручной откат **на том же исходном контексте** и повторная проверка, включая выход/возврат/кратковременную смену источника, если безопасно;
- отчёт с PASS/FAIL/SKIPPED и известными ограничениями.

### P4 — boot, service migration, ROM

Этот уровень **НЕ входит** в обычные тесты меню. Для любых `pm disable`, firmware/AVB/partitions, thermal watchdog, motor calibration требуется самостоятельный план восстановления и согласованное окно. Никогда не экспериментировать на live 8054 ради доказательства отсутствия функции.

## 13.4 Важные негативные сценарии

- Некорректный `picture_mode`/сохранённый user baseline, смена HDMI в процессе регулировки;
- быстрый DPAD repeat, двойной click, закрытие окна, ContentObserver echo;
- переход SDR↔HDR и динамическая синхронизация зависимых PQ keys;
- отсутствие/обрыв BT, несовпадение preferred и actual AudioPolicy output;
- eARC отсутствует, но OEM eARC menu есть;
- CEC OFF приводит к дополнительным изменениям audio/eARC/auto-off;
- HDMI EDID вызывает re-handshake/потерю видеосигнала;
- отсутствие focus/keystone sensor в чужом SKU;
- приложение обновлено, но system key 307 по-прежнему открывает FloatMenuService;
- плеер рендерит 4K, а Android MainSettings 1080p + frame drops;
- stock fastboot unlock успешен, но второй слот не даёт рабочего Android;
- любой factory-only или неизвестный property приводит к отказу/readonly, **а не к попытке записи**.

---

# 14. Риски и правила безопасности

## 14.1 Что нельзя делать автоматически

**Без отдельного согласия пользователя и восстановления** запрещено:

- `adb shell settings put ...` или стихийные изменения `setprop`, `service call`, `cmd ...` которые меняют систему;
- устанавливать APK/менять package defaults/делать `pm disable`, даже если это «просто тест»;
- перегружать ТВ/проектор/SurfaceFlinger/MediaTek services (можно потерять доступ к картинке);
- вызывать `fastboot flashing unlock/lock`, `fastboot flash/erase`, `dd of=/dev/block/*`, MBOOT USB upgrade, OTA apply или запись EROFS;
- скрытые инженерные `Factory` I²C/LED/fan/thermal/PQ calibration/optics/motor commands;
- обновлять EDID/CEC/game mode/overScan без сохранённого известного рабочего видеовыхода;
- заменять `KuSourceRJ.TimeService`, hardware drivers и original boot receiver, не понимая связи с охлаждением;
- выставлять Android display 4K UI или экспериментальные 48/24 Hz как permanent boot mode без read-only hardware audit.

**Приватность:** не публиковать calibration/device-unique secrets, Widevine/HDCP, private keys, DRM, device serial, unique MAC, WLAN credentials, пользовательские логины и токены. Для GitHub public repositories публиковать только отчёты и необходимый неуникальный открытый код.

## 14.2 Дистанционный доступ к ADB

Владелец предлагал внешний NAT порт, например `45912 → 5555` проектора. **Не рекомендовать публиковать ADB напрямую в интернет**. ADB предоставляет широкие возможности управления, нестандартный порт — не защита. Текущий обычный ChatGPT-чатоагент не обладает произвольным прямым TCP-доступом к пользовательскому устройству.

Если нужен полуавтономный цикл диагностики, предпочтительны:

```text
ИИ / поставленная инженерная задача
  → Codex/управляемый агент, запущенный на ПК владельца
  → локальный adb с явно указанным serial
  → проектор в домашней LAN (либо защищённая VPN с ACL)
  → read-only отчёты и контролируемые пользовательские approval
```

Учитывать, что наличие локального Codex **не означает**, что он уже имеет доступ к пользовательской сети, shell или проектору. Сначала проверить доступ, согласовать область команд и обеспечить отказоустойчивое логирование. Секреты маршрутизации/доступа не хранить в открытом GitHub.

## 14.3 Что откладывать при отсутствии доказательств

- Dolby Vision/HDR10+ «unlock» путём подмены `HdrCapabilities` — эффект и license/SoC gating не доказаны; владелец сознательно отложил.
- Реальный FreeSync/VRR без HDMI/display аппаратного подтверждения.
- Force 4K UI без GPU/fps профилирования.
- Очевидные на словах «noise reduction» ползунки без exact OEM map.
- Удаление Factory/KuSettings/Update/KuSetupWizard без dependency graph и recovery.

---

# 15. Приоритеты дальнейшей работы (актуализированы на 23.11.2026)

## P0 — срочно / основной продукт

1. **Сверка рабочего HEAD #10 и CI**: анализ diff, реального наличия и статуса каждой функции, конкурирующих PR; зафиксировать exact baseline и артефакты R7.
2. **Устранение остаточных проблем пользовательского меню**: проверить R7 три группы и одинаковые компактные слайдеры, цвет категорий, D-pad/Back/focus, preview и поведение в User/factory mode. Не переписывать оформление без конкретной ошибки.
3. **Аппаратная кнопка SETTINGS → MOD**: трассировать original policy/service start по `keyCode:307`, найти управляемый, reversible route без китайского UI-посредника. Существующий launcher alias уже отдельно работает, implicit `android.settings.SETTINGS` не подходит.
4. **Аудиовыход**: исследовать, почему опыт с `NativeMediaRouteBridge` не доказал реального Speaker↔BT A2DP переключения; проверить `AudioProductStrategy`, policy preferred vs actual и разрешения, журнал ошибок, rollback. Не объявлять баг исправленным без слышимого результата.
5. **Завершить потребительские Picture/Sound блоки** с проверкой оригинальных OEM callbacks и практической работой на 8054; не создавать новые обёртки вокруг китайского GUI.

## P1 — высоко / качество изображения и UI

6. **1080p Android UI vs 4K display area**: исследовать size/override/SurfaceFlinger layers и тяжесть GPU/30 FPS ощущения, собрать gfxinfo/Perfetto при разрешении. Сначала выяснить bottleneck, затем исследовать безопасный масштаб/разрешение.
7. **AFR 50/60 Hz**: проверить возможное реальное переключение на 25↔50 и 30↔60, методы Android 13, поддержку дисплейной HAL. Затем рассмотреть 48/47.952 Hz только после подтверждения timings. Не обещать 24 Гц на основании Android `setFrameRate`.
8. **Шумоподавление**: найти точные DNR/MPEG NR или схожие OEM пользовательские опции, если доступны; внедрять лишь с bounds/readback.
9. **MEMC**: при необходимости экспериментально измерить различия Off/Low/Medium/High и артефакты, не додумывать кадровую частоту по названию пресета.

## P2 — закончить функциональную независимость M1

10. Систематический gap-audit `FINAL_FUNCTION_PARITY_8054.csv` и китайских пользовательских маршрутов;
11. HDMI CEC/EDID/ARC/eARC/power source/auto play/game/overscan с допустимыми штатными условиями;
12. Проекция/focus/keystone/4-corner/zoom/orientation/LED: собственные UI handlers + сохранение OEM аппаратного backend;
13. Bluetooth/boot/power/timer/OTA/vendor user functions и platform-friendly нативные страницы;
14. Полное M1 acceptance: user menu **не открывает `com.my.settings`**, но китайские boot services пока сохранены.

## P3 — условно после M1 и автономного разрешения

15. Инвентаризовать и перенести boot/watchdog/autoBluetooth/TimeService сервисы, доказать отсутствие дублирования watchdog.
16. Провести отдельно разрешённое M2 испытание временного disable с восстановлением и полным cold-boot/thermal/network/audio/HDMI/regression matrix.
17. Только после этого оценить физическое исключение KuSettings APK и полноценный Custom RUIOS 8054 ROM; сохранять OEM low-level stock и исключить уникальные калибровки из публичного дистрибутива.

## P4 — отложено, пока пользователь не изменит приоритет

- Принудительное Dolby Vision/HDR10+ на закрытом MediaTek видеотракте;
- hardware VRR/FreeSync;
- кросс-прошивка 8052/8053/ET32;
- полная замена vendor/kernel/HAL вместо точечной доработки OEM RUIOS;
- релиз с удалением системных служб без полного восстановления.

---

# 16. Для нового ИИ: самостоятельное первое задание

> **Выполнить independent code review, а не подтверждать старые оптимистичные выводы.**
>
> 1. Изучить четыре профильных GitHub репозитория. В `Projector-Soft` открыть и прочитать handoff `research/EXTERNAL_AI_HANDOFF_20261121/README.md`, затем документы 01–08 и данный обновлённый handoff.
> 2. Получить live GitHub status всех PR #1–#10, особенно #9/#10, точные `HEAD`, `base`, merge-base, diff и нужные Actions test results. Сообщить, какие изменения действительно присутствуют на текущем HEAD #10, а какие только в других ветках. Не считать `main` релизом v41.
> 3. Описать архитектуру пользовательских настроек, actual backend/getter/setter/permissions и безопасный режим для каждой незакрытой функции с источниками на конкретный commit.
> 4. Составить матрицу `CODE_IMPLEMENTED / DEVICE_VERIFIED / SIDE_EFFECTS / ROLLBACK / KU_UI_DEPENDENCY`. Обязательные блоки: Picture/User guards/MEMC, Sound/EQ/BT media route, HDMI/CEC/EDID/ARC, focus/keystone, boot/thermal.
> 5. Найти и указать в коде причину каждого доказанного дефекта: маршрут keyCode 307, неудавшийся actual audio routing, 1080p UI, гипотеза 30fps animations, AFR 50/60 (при наличии source proof). Если доказательств нет — явно указать, какие read-only данные нужны.
> 6. Предложить **минимальный** очередной PR с одним завершённым и проверяемым функциональным блоком, без нового дизайна приложения и без повторной бесконечной декомпиляции; предоставить diff, тесты, изменение документации и rollback.
> 7. Не запускать команды на проекторе без отдельного разрешения. Не добавлять «удалить KuSettings» как быстрый шаг. Не открывать китайскую Activity в качестве посредника из MOD.
> 8. Результаты оформить в Markdown с указанием каждой неопределённости, exact source links, commit SHA и способов проверки. Все аппаратные claims подтверждать реальным 8054, не 8052/фабричным 8054 и не unit-test.

---

# 17. Сводная карта входных документов и прямых ссылок

## 17.1 Главный handoff, которым нельзя пренебрегать

**[research/EXTERNAL_AI_HANDOFF_20261121/README.md](https://github.com/MAX-TAC/Projector-Soft/blob/docs/external-ai-complete-handoff-20261121/research/EXTERNAL_AI_HANDOFF_20261121/README.md)** — собственный prior independent handoff, 8 секций, 291 source citations. Дата предыдущего среза **21.11.2026**; обязательно дополнять PR #9/#10 и более поздними ADB/ELF находками.

Прямые ссылки:

1. [01 — firmware repositories and releases](https://github.com/MAX-TAC/Projector-Soft/blob/docs/external-ai-complete-handoff-20261121/research/EXTERNAL_AI_HANDOFF_20261121/01_FIRMWARE_REPOSITORIES_AND_RELEASES.md)
2. [02 — custom ROM feasibility](https://github.com/MAX-TAC/Projector-Soft/blob/docs/external-ai-complete-handoff-20261121/research/EXTERNAL_AI_HANDOFF_20261121/02_CUSTOM_FIRMWARE_FEASIBILITY.md)
3. [03 — TvSettingsPlus technical state](https://github.com/MAX-TAC/Projector-Soft/blob/docs/external-ai-complete-handoff-20261121/research/EXTERNAL_AI_HANDOFF_20261121/03_TVSETTINGSPLUS_MOD_TECHNICAL_STATE.md)
4. [04 — owner requirements and acceptance](https://github.com/MAX-TAC/Projector-Soft/blob/docs/external-ai-complete-handoff-20261121/research/EXTERNAL_AI_HANDOFF_20261121/04_PRODUCT_REQUIREMENTS_AND_ACCEPTANCE.md)
5. [05 — evidence, limitations and errata](https://github.com/MAX-TAC/Projector-Soft/blob/docs/external-ai-complete-handoff-20261121/research/EXTERNAL_AI_HANDOFF_20261121/05_EVIDENCE_OPEN_QUESTIONS_AND_REVIEW_PLAN.md)
6. [06 — 291 pinned sources](https://github.com/MAX-TAC/Projector-Soft/blob/docs/external-ai-complete-handoff-20261121/research/EXTERNAL_AI_HANDOFF_20261121/06_SOURCE_CATALOG.md)
7. [07 — task for independent AI](https://github.com/MAX-TAC/Projector-Soft/blob/docs/external-ai-complete-handoff-20261121/research/EXTERNAL_AI_HANDOFF_20261121/07_INDEPENDENT_AI_REVIEW_TASK.md)
8. [08 — owner-verified stock picture](https://github.com/MAX-TAC/Projector-Soft/blob/docs/external-ai-complete-handoff-20261121/research/EXTERNAL_AI_HANDOFF_20261121/08_OWNER_VERIFIED_ANDROID_TV_PICTURE.md)

## 17.2 Важнейшие обновлённые источники 22.11

- [PR #9: direct MediaTek consumer control research](https://github.com/MAX-TAC/Projector-Soft/pull/9).
- [PR #10: TvSettingsPlus MOD R7](https://github.com/MAX-TAC/Projector-Soft/pull/10).
- [R7 slider/menu/key307](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/docs/TVSETTINGSPLUS_8054_R7_PICTURE_SECTIONS_AND_KEY307_20261122.md).
- [R5 launcher / video-only PQ effect](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/docs/TVSETTINGSPLUS_8054_R5_UI_AND_LAUNCHER_20261122.md).
- [Sound/media route test contract](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/docs/TVSETTINGSPLUS_8054_AUDIO_ROUTE_HARDWARE_ACCEPTANCE_20261122.md).
- [MediaTek consumer API contract](https://github.com/MAX-TAC/Projector-Soft/blob/research/8054-direct-mediat-ek-api-contracts-20261122/research/8054/MTK_DIRECT_CONSUMER_CONTROL_CONTRACT_20261122.md).
- [Current NativePicturePanel Java](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/app/tvsettingsplus-mod/src/exact8054/java/dev/projectorsoft/tvsettings/NativePicturePanel.java).
- [Current NativeSections Java](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/app/tvsettingsplus-mod/src/exact8054/java/dev/projectorsoft/tvsettings/NativeSections.java).
- [Current NativeMediaRouteBridge](https://github.com/MAX-TAC/Projector-Soft/blob/feature/8054-v41-picture-sound-safety-20261122/app/tvsettingsplus-mod/src/exact8054/java/dev/projectorsoft/tvsettings/NativeMediaRouteBridge.java).

## 17.3 Firmware and bootloader primary sources

- [Factory 8052/8054 releases and OTA](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/releases)
- [Factory complete audit](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/blob/main/analysis/Full_Audit/README.md)
- [Factory PKG decrypt](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/blob/main/analysis/Original_Firmware/DECRYPTED_SUCCESS.md)
- [8052/8054 engineering verdict](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/blob/main/analysis/HDMI_Comparison/ENGINEERING_VERDICT.md)
- [Custom v0 staging only](https://github.com/MAX-TAC/Everycom-Cinelux-Firmware/blob/custom-v0-staging-8052-8054-20261021/custom-v0/BUILD_STATUS_RU.md)
- [Live 8054 backup](https://github.com/MAX-TAC/FlixTone_8054_Backup/releases/tag/FlixTone_8054_Backup)
- [8054 unlock/AVB/partitions](https://github.com/MAX-TAC/FlixTone_8054_Backup/blob/main/docs/8054_UNLOCK_AVB_PARTITIONS_VERIFIED_20261121.md)
- [Custom RUIOS 8054 release plan](https://github.com/MAX-TAC/FlixTone_8054_Backup/blob/main/docs/CUSTOM_RUIOS_RELEASE_PLAN_20261121.md)
- [ET32 research and recovery images](https://github.com/MAX-TAC/Firmware-CN-Projectors/blob/main/analysis/ET32/README.md)
- [ET32 quality/security review](https://github.com/MAX-TAC/Firmware-CN-Projectors/blob/main/analysis/ET32/QUALITY_REVIEW.md)

---

# 18. Чего не хватает в этом одном файле

Несмотря на объём, **один Markdown не заменяет исходные ROM/ZIP, полный 96-строчный CSV, тысячи smali-файлов и бинарники для повторного дизассемблирования**. Данный handoff намеренно переносит контекст, карту источников, доказательства, ограничения и план, а не повторяет дословно все отчёты, уже находящиеся в GitHub.

Для полной воспроизводимости новому агенту надо иметь:

1. **Текущий checkout** конкретных 4 репозиториев и GitHub PR, включая незамёрженные ветки и конкретные commit SHA.
2. **Полный предыдущий handoff 01–08**, особенно 291 pinned source link и раздел с errata.
3. **Реальные ROM assets**, если нужен повторный static parse: заводские PKG/OTA и exact backup release 8054.
4. **Локальные диагностические ZIP из беседы владельца**, если требуется повторное исследование HDR/audio/key307: `8054_hdr_audit.zip`, `8054_hdr_atmos_20261122_231713.zip`, `8054_hdr_native.zip`, `8054_hdr_backend.zip`, `8054_hdr_driver.zip`, `8054_hdr_caps.zip`, `8054_route_fail.zip`, `8054_settings_route.zip`, `8054_R7_UI_test_results.zip`. **Сами файлы в этот MD не встроены**. Они должны быть переданы отдельно, если агент не находится в среде с этими загрузками.
5. **Реальный ADB** только при явном разрешении владельца: аппаратные эффекты, HDMI режимы, звук, UI FPS, набор доступных display modes нельзя достоверно вывести исключительно из статических имён методов.

Не обещать пользователю, что «всё уже проверено» или «полный ROM готов». Открытые задачи сохранять открытыми, ошибки прежних выводов исправлять письменно и с указанием первоисточника.

**Итоговая цель неизменна:** законченный удобный TvSettingsPlus MOD на реальном FlixTone D11 Master 8054, максимально сохраняющий работающие штатные драйверы/сервисы MediaTek и OEM, без китайского GUI в обычном пользовательском пути; затем — только при доказанной обратимости — очищенная кастомная RUIOS для той же аппаратной ревизии.

---

*Конец handoff. Срез GitHub и ранее проведённой диагностики: 23.11.2026. Изменения после этой даты должны сопровождаться новым source HEAD, APK hash, CI и отдельной аппаратной приёмкой.*

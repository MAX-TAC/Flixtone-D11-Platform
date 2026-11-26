# KuSourceRJ (`com.coolux.source`) — вырезка мусора. ОТЧЁТ

Дата: 2026-11-26. Владелец: MAX-TAC. Статус: **СОБРАН И ПОДПИСАН**, не установлен.

## Артефакт

| Параметр | Значение |
|---|---|
| Файл | `_analysis/Protection-5.3-signed.apk` |
| Размер | 58 415 851 Б (оригинал 58 460 781 Б) |
| SHA-256 | `3A9297E2BB557E973A824DC27BDDDBAB37A8C98867E44930B4FAC33BB23C30EC` |
| package | `com.coolux.source` (не менялся) |
| **label (имя)** | **`Protection`** (было `Source`) |
| **иконка** | **новая**: красный термометр + вентилятор (mipmap все разрешения) |
| **языки** | английский (базовый) + русский (для служебных экранов) |
| versionCode / versionName | 41 / 5.3 (не менялись) |
| minSdk / targetSdk | 28 / 33 |
| Подпись | platform AOSP testkey, SHA-256 `c8a2e9bc…192ab8` — **совпадает с оригиналом** |
| Схемы подписи | v3 (v1/v2 не требуются при minSdk 28) |

### Итоговый состав (после двух этапов вырезки)

| Компонент | Тип | Назначение |
|---|---|---|
| `TimeService` | Service | **термоконтроль**: температура LED/LCD, 4 вентилятора, снижение яркости, пороги 65/70/75/80 °C |
| `BootupReceiver` | Receiver | старт службы при `BOOT_COMPLETED` + стартовая яркость |
| `BrightReceiver` | Receiver | яркость по broadcast `com.action.brightReceiver` (используется MOD) |
| `HighTemperatureActivity` | Activity | экран предупреждения о перегреве (отсчёт 10 с → выключение) |
| `FanDetectionActivity` | Activity | экран неисправности вентиляторов |
| `DustproofActivity` | Activity | напоминание о чистке пылевого фильтра |
| `androidx.startup.InitializationProvider` | Provider | служебный (AndroidX) |

## Что удалено

### 1. Заводские тесты `testcast.*` — 17 Activity + `MyTestActivity`
`TestCastActivity`, `InterfaceTestActivity`, `StandbyActivity`, `DlpActivity`,
`InterfaceActivity`, `BrightTestActivity`, `AudioVideoActivity`, `LeftRightVideoActivity`,
`AgingModelActivity`, `AgingActivity`, `RebootNumActivity`, `PrintTestActivity`,
`CustomBrightActivity`, `OtherActivity`, `ClearTimeActivity`, `SetTimeActivity`,
`WifiSNActivity`, `WiredSNActivity` + `MyTestActivity`.
Удалено 61 файл smali всего пакета `testcast` + 1 файл `MyTestActivity`.

### 2. Дубли MOD и лишние экраны
| Компонент | Файлы smali | Причина |
|---|---|---|
| `MainActivity` (LAUNCHER, выбор источника) | 3 | дубль MOD `NativeSections.Sources` |
| `BootSoureActivity` + `BootSoureActivityOld` | 6 | дубль MOD `NativeBootDestination` |
| `VoiceActivity` + `VoiceUtils` | 3 | звук кнопок, дубль MOD |
| `AllAppAutoActivity` + `AllAppAutoAdapter` | 6 | дубль MOD `BootAppPickerSettingsActivity` |
| `AutomaticAdmissionActivity` | 2 | заводская автоподача сигнала |
| `AuthorizationActivity` | 2 | DRM-тупик («Error, shutdown after 30 seconds») |
| `UtilsLogic` + `UtilsLogicImpl` + `$1/$2` | 4 | обслуживали только `AllAppAutoActivity` |

Итого удалено **88 файлов smali**.

### 3. Дубли MOD (второй этап, по запросу владельца) — 5 Activity + 1 Receiver
| Компонент | Файлы | Причина |
|---|---|---|
| `BrightActivity` | 3 | яркость в MOD идёт через `BrightReceiver` (broadcast), не через этот экран |
| `KeystoneActivity` | 2 | трапеция в MOD через отдельное приложение `com.rjpj.tcorrection` |
| `ProjectModelActivity` | 2 | ориентация проекции перенесена в MOD |
| `PoweronModeActivity` | 2 | режим включения перенесён в MOD |
| `RestoreActivity` | 6 | сброс настроек перенесён в MOD |
| `ScreensaverReceiver` | 1 | ничем не вызывался; яркость в «screensaver» не нужна (сон/заставка отключены) |

Итого второго этапа: **16 файлов smali**. Суммарно два этапа — **104 файла**.

### 4. DRM/OTA-цепочка внутри `TimeService` (вычищена)
- метод `private myHttp(Context)` — HTTP-опрос сервера обновлений;
- поле `socicalLogic`;
- класс `TimeService$13` (обработчик ответа → `isShield()` → `authorizationIntent()`);
- вызов `myHttp()` из `defaultData()`;
- методы `authorizationIntent` и `autoApp` в `IntentUtils`.

**Следствие:** проверка «заблокирована ли прошивка» больше не выполняется, устройство
не выключится само при откате/смене прошивки.

### 5. Aging-механизм (заводской прогон на выносливость)
- `BootupReceiver.agingTest()`;
- `BootupReceiver.rebootStart()` (счётчик перезагрузок для aging);
- вызовы `startAgingIntent()` в `BootupReceiver`;
- `IntentUtils.startAgingIntent()` и `IntentUtils.agingTest()`.

**Следствие:** при загрузке больше не проверяется флаг `agingAuto`, автозапуска
`AgingActivity` не будет (класс удалён, ссылок нет).

### 6. Кнопка «автоподача сигнала» + тестовый ввод в трапеции
- пункт `automatic_admission_layout` удалён из `res/layout/activity_keystone.xml`;
- обработчики click/key удалены из `KeystoneActivity` (метод `enterKey`, `access$100`, `keyListenner`, `KeystoneActivity$2`).

### 7. Перевод служебных экранов на русский
Добавлены в `res/values-ru/strings.xml` (12 строк): `fan_detection_error*`,
`temperature_shutdown0/1/2`, `temperature_error`, `dusproof_title*`.

### 5. Кнопка «автоподача сигнала» в трапеции
- пункт `automatic_admission_layout` удалён из `res/layout/activity_keystone.xml`;
- обработчик этого пункта удалён из `KeystoneActivity.enterClick()`;
- цепочка меток перестроена, ссылки проверены.

## Что сохранено (НЕ тронуто)

| Компонент | Зачем |
|---|---|
| `TimeService` | **термоконтроль**: LED/LCD-температура, 4 вентилятора, снижение яркости, пороги 65/70/75/80 °C |
| `BootupReceiver` | при `BOOT_COMPLETED`: `defaultInit` → `defaultBright` → `UtilsTools.startTime()` |
| `BrightReceiver` | управление яркостью (вызывается из MOD через `KuSourceRjBrightnessGateway`) |
| `ScreensaverReceiver` | заставка |
| `BrightActivity` | яркость LED (открывается из MOD `OemProjectionPanel`) |
| `KeystoneActivity` | трапеция |
| `ProjectModelActivity` | режим проектора |
| `PoweronModeActivity` | режим включения |
| `HighTemperatureActivity` | предупреждение о перегреве |
| `FanDetectionActivity` | диагностика вентиляторов |
| `DustproofActivity` | защита от пыли |
| `RestoreActivity` | сброс настроек |
| `model/AppInfo`, `UtilsTools`, `SharedPreferencesTest`, `ImageUtils`, `MyTimeUtils` | рабочие утилиты (используются MOD и логикой) |

## Проверки (выполнены)

- `apktool b` — EXIT 0, APK собран.
- `aapt dump badging` — package/версия не изменились.
- `aapt dump xmltree` — в манифесте **нет** ни одного удалённого компонента,
  **нет** LAUNCHER; остались 8 Activity + 3 Receiver + 1 Service + 1 Provider.
- повторная декомпиляция собранного APK: ключевые классы на месте, удалённые — отсутствуют.
- `TimeService` — нет `myHttp`/`socicalLogic`/`authorization`, термоконтроль (`startHighTemReduce`, `temperatureError`, `startReduce`, `fanDetection`, `registerTimeTick`) на месте.
- `BootupReceiver` — нет `agingTest`/`rebootStart`/`startAgingIntent`.
- `apksigner verify` — `Verifies`, сертификат `c8a2e9bc…` = оригинал.
- `grep` по всему smali — ни одной `const-class` ссылки на удалённые классы.

## Установка

⚠️ **Требуется полная перезагрузка после установки** (служба `persistent`, поднимется с новым кодом).

Процедура (по согласованию, отдельным разрешением):
1. Установить APK поверх существующего (подпись совпадает, `sharedUserId` сохранится).
2. Полная перезагрузка проектора.
3. Проверить: термоконтроль (`logcat` → `TimeService`), яркость, трапеция, перегрев.
4. Откат: переустановить оригинал `_apks/com.coolux.source.apk`.

## Ограничения

- Мёртвые «тестовые» методы `IntentUtils` (`audioVideoTest`, `dlpTest`, `interfaceTest`,
  `otherTest`, `printTest`, `projectNumTest` и пр.) **оставлены**: они используют строковые
  intent-экшены, сборку не ломают. Удаляются отдельным проходом при желании.
- `SocaicalLogicImpl`/`SocicalLogic`/`RsFwUpdatePackage`/`JsonUtil` оставлены как «мёртвый»
  код (не вызываются, но и не мешают).
- Ключи подписи скопированы в `_analysis/keys/` (публичный AOSP testkey, не секрет).

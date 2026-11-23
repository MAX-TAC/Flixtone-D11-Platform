# KuSourceRJ (`com.coolux.source`) — разбор

Дата: 2026-11-24. Источник: DEX `classes.dex` (8.9 МБ), манифест, `dumpsys`.
Уровень: **`STATIC_CONFIRMED`**, если не указано иное.

---

## 1. Главное открытие: вся железная часть проектора идёт через `trd.framework`

`KuSourceRJ` **не работает с железом напрямую**. Он подключается к Binder-сервису
`com.trd.framework.TrdSystemService` и использует его интерфейсы:

| Интерфейс `trd.framework` | Что делает |
|---|---|
| `IProjectorCtrl` | режим проектора (потолок/тыл), проекция |
| `IMotorCtrl` | **моторы**: фокус, трапеция |
| `ITofCtrl` | **ToF-датчик** |
| `ITofDataListener` | данные ToF (обратный вызов) |
| `ITemperatureCtrl` | **температура** |
| `ISensorCtrl` | датчики (положение, движение) |
| `ICommunicationCtrl` | связь с MCU/нижней платой |
| `ISystemCtrl` | системные команды |
| `ITrdSystemService` | корневой сервис |

**Это меняет картину.** Раньше считалось, что «охлаждение и термо зависят от KuSourceRJ».
На самом деле **логика в `trd.framework`**, а `KuSourceRJ` — лишь один из клиентов.

---

## 2. Что действительно делает `TimeService`

В DEX найдены:

```
com.coolux.source.service.TimeService
com.coolux.source.service.TimeService$1      ← это TIME_TICK-приёмник
TemperatureCtrlImpl.java
TemperatureCtrl.java
fanDetection
fanStatue
fanString
fan_detection_error, fan_detection_error2..4
temperature_error, temperature_shutdown, temperature_shutdown0..2
temperatureHandel
temperatureMillis
brightModel=
```

**Расшифровка:** `TimeService` — это **периодический опрос**, который:
1. читает температуру через `ITemperatureCtrl`;
2. читает состояние вентиляторов (`fan1`, `fan2`, `fan3`);
3. при превышении — показывает ошибку / выключает (`temperature_shutdown`);
4. контролирует яркость (`brightModel`).

**Критично:** если `TimeService` остановить, проектор **не получит защиту от перегрева**.
Это не «сторож ради галочки» — это реальный термоконтроль в Android-слое.

**Но** есть и второй уровень: `trd.framework` сам работает в отдельном процессе и, возможно,
имеет собственный watchdog. Это надо проверить экспериментально (позже, в этапе 5).

---

## 3. Все Activity (38 компонентов) — что из этого мусор

### 3.1. Пользовательские (нужны)

| Activity | Назначение |
|---|---|
| `BrightActivity` | яркость LED |
| `KeystoneActivity` | трапеция |
| `BootSoureActivity` | источник при включении (опечатка «Soure» — OEM) |
| `ProjectModelActivity` | режим проектора |
| `HighTemperatureActivity` | предупреждение о перегреве |
| `FanDetectionActivity` | обнаружение вентиляторов |
| `DustproofActivity` | защита от пыли / загрязнения фильтра |
| `RestoreActivity` | восстановление настроек |
| `VoiceActivity` | голосовое управление |
| `AuthorizationActivity` | авторизация (?) |
| `MainActivity` | точка входа |

### 3.2. Заводские тесты (`testcast.*`) — 15 Activity

```
TestCastActivity, InterfaceTestActivity, StandbyActivity, DlpActivity,
InterfaceActivity, BrightTestActivity, AudioVideoActivity, LeftRightVideoActivity,
AgingModelActivity, AgingActivity, RebootNumActivity, PrintTestActivity,
CustomBrightActivity, OtherActivity, ClearTimeActivity, SetTimeActivity,
WifiSNActivity, WiredSNActivity
```

Это **производственные тесты и режим старения** (aging — прогон на заводе сутками).
Пользователю не нужны, но:
- `ClearTimeActivity` и `SetTimeActivity` — **`exported=true`**, то есть любой APK может
  сбросить/подменить время наработки. Это потенциальная уязвимость и точно мусор.

**Рекомендация:** в кастомной прошивке вырезать весь блок `testcast.*` (15 Activity),
оставив только `ClearTimeActivity`/`SetTimeActivity` недоступными.

### 3.3. Приёмники (2)

```
BootupReceiver        ← BOOT_COMPLETED, запускает TimeService
ScreensaverReceiver   ← com.action.screensaver
BrightReceiver        ← com.action.brightReceiver, яркость
```

---

## 4. Выводы для проекта

### Что можно удалять (безопасно)

| Блок | Компонентов | Почему безопасно |
|---|---|---|
| `testcast.*` | 15 Activity | заводские тесты, не вызываются в обычной работе |
| `AuthorizationActivity` | 1 | требует проверки — может быть активация |
| `VoiceActivity` | 1 | если нет микрофона/пульта с голосом |

### Что НЕЛЬЗЯ удалять

| Компонент | Почему |
|---|---|
| `TimeService` + `BootupReceiver` | термоконтроль и вентиляторы |
| `BrightReceiver` | управление яркостью LED |
| `ScreensaverReceiver` | заставка |
| `HighTemperatureActivity` | предупреждение о перегреве |
| `FanDetectionActivity` | диагностика вентилятора |

### Что надо переносить, а не оставлять как есть

`TimeService` надо **переписать** в наш MOD, а не выкидывать. Он делает реальную работу:
опрос температуры и вентиляторов через `trd.framework`.

---

## 5. Уточнение по прошлому выводу

Ранее я писал: «KuSettings нужен только ради `MySetTimeService → TimeService`».
Теперь уточнение: **`KuSettings` перезапускает `KuSourceRJ.TimeService`, если тот упал.**

Схема:

```
KuSettings.MySetTimeService (TIME_TICK, раз в минуту)
   ↓ проверяет, работает ли
KuSourceRJ.TimeService (START_NOT_STICKY)
   ↓ опрашивает
trd.framework.ITemperatureCtrl / вентиляторы
```

То есть `TimeService` — `START_NOT_STICKY`, он **не перезапускается сам**. Если он упадёт,
без `MySetTimeService` никто его не поднимет — и **термоконтроль пропадает**.

**Это и есть настоящая причина, почему нельзя просто удалить KuSettings.**

Правильное решение: свой watchdog в MOD, который делает то же самое (проверяет
`TimeService` и поднимает его). В MOD такой класс `KuSourceRecoveryService` уже был,
но он **включён только для 8052** (`KuSourceRecoveryActivationPolicy`).

**Задача:** разблокировать `KuSourceRecoveryService` для 8054, проверить в лаборатории,
потом отключать `KuSettings`.

---

## 6. Про приложение для отображения при регулировке трапеции

**Ответ: `com.trd.service`** — у него есть:

```
res/layout/autokeystone_view.xml      ← вид для автотрапеции
метод InitAutoKeyStoneView
res/layout/focus_dialog.xml           ← диалог фокуса
res/layout/rj_focus_dialog.xml
методы: "focus_direction:%d,motorStatus:%d"
        "FocusDialog turn around motorStatus:"
класс com.trd.service.ui.UICtrlImpl
класс com.trd.service.ui.FanDialog
класс com.trd.service.jni.MotorJNI     ← прямая работа с моторами
```

То есть **наложение (оверлей) при регулировке фокуса и трапеции рисует `com.trd.service`**,
а не `com.rjpj.tcorrection` и не `KuSourceRJ`.

А `com.rjpj.tcorrection` — это **пользовательские Activity** для четырёх углов, зума и
H/V-трапеции (`FourCornerActivity`, `DigitalZoomActivity`, `HVKeystoneActivity`, все `exported=true`).

**Схема:**

| Что | Кто рисует/делает |
|---|---|
| Оверлей при регулировке (сетка, стрелки) | `com.trd.service` → `UICtrlImpl` + `autokeystone_view.xml` |
| Сами пользовательские экраны трапеции/зума | `com.rjpj.tcorrection` (3 exported Activity) |
| Моторы | `com.trd.service.jni.MotorJNI` |
| Логика авто-трапеции | `persist.rjpj.autokeystone.poweron` (пишет KuSourceRJ, читает trd.service) |

**Для MOD:** не надо переизобретать оверлей — он уже есть в `trd.service`. Достаточно
вызвать соответствующую OEM-Activity или Intent, как это делает `OemHardwareDelegatedSettings`.

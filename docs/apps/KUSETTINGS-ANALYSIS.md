# KuSettings (`com.my.settings`) — полный разбор

Дата: 2026-11-24. Источник: APK 17 997 485 B (идентичен 8052/8054), 15 DEX, `dumpsys`.
Уровень: **`STATIC_CONFIRMED`**, если не указано иное.

---

## 1. Что это такое и зачем существует

`com.my.settings` — **китайский OEM-лаунчер настроек** («KuSettings»).
Владелец называет его «заводским меню, которое бесит».

Он **дублирует** стандартные Android TV настройки, но при этом содержит
несколько служб, которых больше нигде нет. Именно из-за них нельзя просто удалить APK.

---

## 2. Полный список компонентов (17 Activity + 2 Service)

### 2.1. Activity

| Activity | Назначение | Судьба |
|---|---|---|
| `MainActivity` | главный экран | **удалить** |
| `SettingActivity` | Settings-интент, претендует на кнопку пульта | **удалить** |
| `ProjectionActivity` | экран проекции | **заменить** своим в MOD |
| `activity.AllAppActivity` | список всех приложений | **удалить** |
| `activity.ScreenshotActivity` | скриншот | **удалить** |
| `activity.MenuPromptActivity` | подсказка меню | ⚠️ проверить вызовы |
| `activity.WarningActivity` | предупреждение | ⚠️ проверить вызовы |
| `time.DateTimeActivity` | дата и время | **удалить** (есть системный) |
| `wifi.MyWifiActivity` | Wi-Fi | **удалить** (есть системный) |
| `wifi.ProvisionWifiActivity` | первичная настройка Wi-Fi | **удалить** (есть в SetupWizard) |
| `bluetooth.MyBluetoothActivity` | Bluetooth | **удалить** (есть системный) |
| `bluetooth.MyAutoBluetoothActivity` | автоподключение BT | ⚠️ проверить: может управлять автопарингом пульта |
| `bluetooth.ProvisionBluetoothActivity` | первичная настройка BT | **удалить** |
| `language.LanguageActivity` | язык | **удалить** (есть системный) |
| `language.LanguageLocalActivity` | локальный язык | **удалить** |

### 2.2. Service

| Service | Назначение | Критичность |
|---|---|---|
| `service.MySetTimeService` | **watchdog для KuSourceRJ.TimeService** | **КРИТИЧНО** |
| `service.ScreenServices` | заставка, `screensaver_size` | средняя |

### 2.3. Receiver

| Receiver | Назначение |
|---|---|
| `service.BootupReceiver` | `BOOT_COMPLETED`, `mPriority=1000` — запускает службы |

---

## 3. Критичное: `MySetTimeService`

### 3.1. Что найдено в DEX

```
Lcom/my/service/MySetTimeService;
Lcom/my/service/MySetTimeService$1;      ← TimeTask
startMyTimeService
startSourceTimeService
TimeServiceSourceHasStart
com.coolux.source.service.TimeService     ← прямая ссылка
com.my.service.MySetTimeService
```

### 3.2. Схема работы

```
MySetTimeService
   ├─ TimeTask (периодический)
   ├─ проверяет: TimeServiceSourceHasStart()
   └─ если НЕ запущен → startSourceTimeService()
            ↓
com.coolux.source/.service.TimeService
   ├─ START_NOT_STICKY  (не перезапускается сам!)
   ├─ опрашивает ITemperatureCtrl (AMB/LCD/LED)
   ├─ опрашивает fan1/fan2/fan3
   ├─ при перегреве → temperature_shutdown
   └─ при отказе вентилятора → shutdown
```

### 3.3. Почему это критично

`TimeService` объявлен как **`START_NOT_STICKY`** — система его **не поднимет** после падения.
Если `MySetTimeService` удалить, а `TimeService` упадёт — **термозащита пропадает навсегда**
до перезагрузки.

**Термозащита = защита матрицы 1LCD от выгорания.** Это не «галочка», это физика.

---

## 4. `ScreenServices` — что делает

Найдено:
```
Lcom/my/service/ScreenServices;
ScreenServices$1..$4, ScreenServices$4$1
screensaver_size
```

**Функция:** управление заставкой и её размером.
**Критичность:** средняя — если пропадёт, заставка будет работать по-системному.

---

## 5. `BootupReceiver`

```
com.my.settings/com.my.service.BootupReceiver
  Action: android.intent.action.BOOT_COMPLETED
  mPriority=1000
```

**Высокий приоритет.** Запускается первым среди приложений.
Что именно поднимает — надо выяснить (STATIC не даёт ответа, нужен `logcat` на загрузке).

**Гипотеза:** запускает `MySetTimeService` и `ScreenServices`.

---

## 6. План переноса в MOD

### 6.1. Что уже есть в `Projector-Soft`

```
KuSourceRecoveryService.java            watchdog, реализован
KuSourceRecoveryActivationPolicy.java   ⚠️ разрешён только для 8052
KuSourceRecoveryPolicy.java
KuSourceRecoveryBootReceiver.java       BOOT_COMPLETED
```

### 6.2. Что надо сделать

1. **Разблокировать `KuSourceRecoveryActivationPolicy` для 8054.**
   Сейчас: `automaticRecoveryAllowed` возвращает `true` только для 8052.
   Нужно: разрешить для обеих плат (8052 и 8054).

2. **Проверить на устройстве**, что после отключения KuSettings
   `TimeService` действительно поднимается нашим `KuSourceRecoveryService`.

3. **Перенести управление заставкой** (`ScreenServices`) в MOD
   либо оставить системной заставке Android.

4. **Проверить `BootupReceiver`** — что он запускает на самом деле (по `logcat` после перезагрузки).

### 6.3. Что проверить до удаления

| Проверка | Как |
|---|---|
| `TimeService` не падает без KuSettings | Убить процесс `com.coolux.source`, ждать, смотреть, поднялся ли |
| Вентиляторы работают | `dumpsys` + физически послушать |
| Термозащита жива | Поднять температуру (нагрузка), смотреть `temperature_shutdown` |
| Заставка работает | Ждать простоя |

---

## 7. Риски удаления

| Риск | Последствие | Мера |
|---|---|---|
| `TimeService` упадёт и не поднимется | **перегрев, выгорание матрицы** | watchdog в MOD **до** удаления |
| `BootupReceiver` поднимает что-то ещё | неизвестная потеря | изучить `logcat` на загрузке |
| `MyAutoBluetoothActivity` связан с автопарингом пульта | пульт может отвалиться | проверить перед удалением |
| `MenuPromptActivity` / `WarningActivity` вызываются из систем | пропадут диалоги | проверить, кто вызывает |

---

## 8. Порядок действий (утверждён владельцем)

```
1. Добить MOD меню (текущий этап)
2. Изучить KuSettings (ЭТОТ ДОКУМЕНТ)
3. Перенести критичное в MOD
4. Вычистить мусор из MOD
5. Удалить KuSettings
6. Релиз
7. Доработать KuSource
8. Доработать KeystoneCorrection (UI трапеции/фокуса/зума)
```

---

## 9. Открытые вопросы

| Вопрос | Как закрыть |
|---|---|
| Что запускает `BootupReceiver`? | `logcat` после перезагрузки |
| Кто вызывает `MenuPromptActivity` / `WarningActivity`? | grep по всем APK |
| Нужен ли `MyAutoBluetoothActivity` для пульта? | Тест: отключить, проверить пульт |
| `ScreenServices` используется заставкой Android или своей? | `dumpsys` после простоя |
# Заводские и сервисные приложения: разбор

Дата: 2026-11-24. Источник: манифесты + DEX. Уровень: **`STATIC_CONFIRMED`**.

---

## 1. `com.trd.factory` — **заводской сервисный центр проектора**

24 компонента. Это не «тесты», это **инженерный инструмент наладки**.
Восстановленные Activity из DEX:

| Activity | Что делает | Ценность |
|---|---|---|
| `home.HomeActivity` | главное меню сервисного центра | точка входа |
| `fan.FanActivity` | **вентиляторы**: управление и диагностика | **высокая** |
| `tof.TofActivity` | **ToF-датчик**: калибровка | **высокая** |
| `sensor.SensorActivity` | датчики (положение, гироскоп) | высокая |
| `sensor.AngleCalculator` | расчёт углов (для трапеции) | высокая |
| `optical.OpticalActivity` | оптика | высокая |
| `lcos.LCOSActivity` | **LCOS-панель** (наша технология!) | **критичная** |
| `aging.AgingActivity` | режим старения | только завод |
| `wallpaper.WallpaperActivity` | заставка | не нужна |
| `keypad.KeypadActivity` | **`exported=true`** — клавиатура сервиса | уязвимость |
| `mac.read.MacInfoActivity` | **`exported=true`** — чтение MAC | уязвимость |
| `mac.write.MacInfoActivity` | запись MAC | опасная |
| `service.InfraredDetectionService` | определение IR-пульта | нужная |
| `journeyapps.barcodescanner.CaptureActivity` | сканер QR (для заводской наклейки) | не нужна |

**Главное:** здесь есть `LCOSActivity` — работа с **LCOS-панелью**, то есть с самим
изображением на уровне панели. И `AngleCalculator` — расчёт углов трапеции.

**Вывод:** это самая ценная из «скрытых» программ. Через неё можно понять, как
управляется панель и как считаются углы. **Удалять нельзя**, но и в пользовательский UI
пускать нельзя — это сервисный вход со своими рисками (запись MAC, режим старения).

**Действие:** оставить, но скрыть из лаунчера (оставить доступ по явному Intent/паролю).

---

## 2. `mediatek.factorymenu.ui` — инженерное меню MediaTek

23 компонента, из них самое интересное:

| Activity | Что |
|---|---|
| `designmenu.FactoryMenuActivity` | **главное инженерное меню** |
| `designmenu.FactoryMemcActivity` | **MEMC напрямую** |
| `designmenu.FactoryPqUpdateActivity` | обновление PQ |
| `designmenu.FactoryDTSActivity` | **DTS** |
| `designmenu.FactoryDolbyActivity` | **Dolby Vision** |
| `designmenu.AdvancedEffectActivity` | продвинутые эффекты |
| `designmenu.VIF` / `VD` / `AUDIO_nonStan` | видео/аудио сервис |
| `testpatternforpanel.TestImagePatternsActivity` | тестовые изображения для панели |
| `designmenu.ExecuteShellActivity` | **выполнение shell-команд** (!) |
| `ApiService` (service) | API для других приложений |

**Два важных момента:**

1. **`FactoryDolbyActivity` и `FactoryDTSActivity` существуют** — значит, через инженерное меню
   можно включать DV/DTS. Это ровно то, что делал форумчанин с eARC.
2. **`ExecuteShellActivity`** — прямая дыра: если Activity доступна, любой APK может
   попросить его выполнить shell-команду. Надо проверить `exported` (в нашем парсере пусто —
   значит default, а на targetSdk 30+ default = `false`, безопаснее).

**Действие:** не трогать. Это наш исследовательский инструмент для проверки
DV, DTS, MEMC.

---

## 3. `com.rjpj.yunota` — OTA-обновление

```
OTASystemNetworkUpdateActivity  exported=true   ← обновление по сети
OTASystemLocalUpdateActivity    exported=true   ← обновление с флешки
OTADownloadService                               служебное
OTACheckService                                  служебное
FileSelector                                     выбор файла
AbUpdate                                         A/B обновление
```

**Оба activity обновления `exported=true`** — любой APK может инициировать обновление
с произвольного URL/файла. Это **потенциальная уязвимость** (подмена источника OTA).

**Действие:** оставить (владелец хочет получать заводские обновления), но рассмотреть
возможность ограничить. Пока — зафиксировать как находку безопасности.

---

## 4. `com.mediatek.miracast` — Miracast-приёмник

```
MiracastSplitActivity    exported=true
MiracastPlayer1..4Activity  exported=true  ×4
MiracastPlayerBaseActivity  exported=true
MiracastService          exported=true
```

**Пять плееров** — это заготовка на четыре разделённых экрана (multiview).
Для проектора не нужен, но и не мешает.

**Действие:** кандидат на удаление при чистке. Сейчас не запущен.

---

## 5. `com.mediatek.autopair` — автоподключение пульта

```
BootBroadcastReceiver   ← BOOT_COMPLETED
AutoPairService
AppService
```

**Это то, что автоматически подключает Bluetooth-пульт после перезагрузки.**
Критично: если удалить, пульт будет требовать ручного сопряжения после каждого ребута.

**Действие: сохранить.** Это одна из «скрытых зависимостей», из-за которой
нельзя произвольно чистить систему.

---

## 6. `com.rjpj.bluetoothspeaker` — режим BT-колонки

```
MainActivity
```

Одна Activity — превращает проектор в Bluetooth-колонку.
Судя по имени и размеру, это тонкая обёртка над `A2dpSinkService`.

**Действие:** оставить (полезная функция), но проверить, нужна ли.

---

## 7. `fusion.android.tv.demo` (RetailDisplay) — витринное демо

```
MainActivity        exported=true
VerticalActivity    exported=true
HorizontalActivity  exported=true
MovieActivity
```

Это **демонстрационный режим для магазина** — крутит рекламные ролики.
На домашнем проекторе нужен как рыбе зонтик.

**Действие: удалить в кастомной прошивке.** Кандидат №1 на вырезание после zxlauncher/zxstore.

---

## 8. `com.mstar.android.tv.disclaimercustomization`

```
MainActivity
```

Одна Activity — кастомизация юридического текста при первом запуске.
Полезно для своего брендинга.

**Действие:** оставить, может пригодиться для брендирования.

---

## 9. Служебные Android-пакеты — ничего интересного

Остальные 40+ пакетов (`com.android.webview`, `systemui`, `keychain`, `packageinstaller`,
`printspooler`, `providers.*`, RRO-оверлеи) — стандартный AOSP. Разбирать незачем.

Единственное, что стоит отметить: **в системе есть RRO-оверлеи**
(`com.android.wifi.resources.rro`, `com.android.networkstack.tethering.rro`) — механизм
подмены ресурсов без правки APK. Это может пригодиться нам для локализации/брендинга.

---

## Итоговая таблица решений

| Пакет | Решение | Обоснование |
|---|---|---|
| `com.trd.factory` | **сохранить, скрыть** | LCOS, ToF, вентиляторы, углы — инженерная ценность |
| `mediatek.factorymenu.ui` | **сохранить** | инструмент для DV/DTS/MEMC-исследований |
| `com.rjpj.yunota` | сохранить | владелец хочет OTA |
| `com.mediatek.autopair` | **сохранить обязательно** | автоподключение пульта |
| `com.mediatek.miracast` | кандидат на удаление | не используется, 5 Activity |
| `fusion.android.tv.demo` | **удалить** | витринное демо, мусор |
| `com.rjpj.bluetoothspeaker` | сохранить | полезная функция |
| `com.mstar...disclaimercustomization` | сохранить | брендинг |
| `com.zeasn.launcher`, `zxstore` | **удалить** | по решению владельца |

---

## Задачи безопасности (зафиксированы, не решаются сейчас)

| # | Находка | Риск |
|---|---|---|
| S1 | `KuSourceRJ.testcast.ClearTimeActivity` / `SetTimeActivity` — `exported=true` | сброс наработки |
| S2 | `com.rjpj.yunota` оба update-activity `exported=true` | подмена OTA |
| S3 | `trd.factory.keypad.KeypadActivity` / `mac.read` — `exported=true` | доступ к сервису |
| S4 | `mediatek.factorymenu.ui.ExecuteShellActivity` | shell-команды |

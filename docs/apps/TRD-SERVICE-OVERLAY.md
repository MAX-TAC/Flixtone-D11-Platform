# `com.trd.service` (trdservice) — оверлеи, фокус, и разграничение с trd.framework

Дата: 2026-11-27. Уровень: **STATIC_CONFIRMED** (разбор `/system/app/trdservice/trdservice.apk`, 1.9 МБ).

---

## 1. Что это и чем отличается от `com.trd.framework`

| | `com.trd.framework` (trdmiddle) | `com.trd.service` (trdservice) |
|---|---|---|
| APK | `/vendor/priv-app/trdmiddle/trdmiddle.apk` | `/system/app/trdservice/trdservice.apk` |
| Роль | **Binder-сервис `TrdSystemService`** — железо | **Оверлеи + UI-слой** (фокус, диалоги, JNI-моторы) |
| Ключевые классы | `ITrdSystemService$Stub`, `ITemperatureCtrl`, `TrdSystemService` | `UICtrlImpl`, `RJFocusDialog`, `MotorJNI`, `FanDialog` |
| Layout | (нет UI) | `focus_dialog.xml`, `rj_focus_dialog.xml`, `autokeystone_view.xml`, `temperature_counter.xml`, `shutdown_cooldown_dialog.xml` |

**Итог:** `trd.service` — это **владелец экранных оверлеев** (рисует поверх видео/любого экрана)
и диалогов (перегрев, вентиляторы, выключение). `trd.framework` — само железо.

---

## 2. Оверлеи (что рисует trd.service)

| Layout | Назначение | Статус |
|---|---|---|
| `rj_focus_dialog.xml` | **оверлей ручной фокусировки** (350×350dp: чёрный круг + кольцо-шкала + стрелки) | мыльный (PNG 400×400) |
| `focus_dialog.xml` | второй вариант фокуса | то же |
| `autokeystone_view.xml` | пустышка 1×1px (сетка автотрапеции рисуется программно в `UICtrlImpl`) | заглушка |
| `temperature_counter.xml` | счётчик температуры | рабочий |
| `shutdown_cooldown_dialog.xml` | диалог «выключение через N с» | рабочий |
| `rj_dialog_poweroff_list_item.xml` | пункт списка выключения | рабочий |

### Классы отрисовки:
- `UICtrlImpl` (+ `$1..$5`, `$UiHandler`, `$FanDialogShowRunnable`, `$TemperDialogShowRunnable`) — главный контроллер UI.
- `RJFocusDialog` — оверлей фокуса (то, что вы видели «мыло»).
- `FanDialog` — диалог вентиляторов.

---

## 3. Графика фокуса (что мыльно)

| Ресурс | Размер | Проблема |
|---|---|---|
| `rj_focus_bg1.xml` | shape (чёрный круг 400dp) | ок |
| `rj_focus_bg2.png` | **400×400** | кольцо-шкала, растягивается → мыло |
| `rj_focus_in_out.png` | **400×400** | стрелки «внутрь/наружу», мыло |

**Решение (по согласованию):** заменить PNG на **4K-версии** (владелец готовит картинку),
либо векторные `VectorDrawable`, либо программную отрисовку. **Логику `UICtrlImpl`/`RJFocusDialog` не трогать** — только графику.

---

## 4. `RuiAutoFocus.apk` — НЕ про фокус (важное уточнение)

APK `RuiAutoFocus.apk` (20.9 МБ, в `vendor/reference/8052/APK/`) — это пакет **`com.hysd.screen`**:
- `com.hysd.xymscreen.MainActivity` (MAIN) — **калибровка экрана** (xy-экран, тестовые паттерны)
- `com.hysd.client.VAF2S` (service)

Это то, на что ссылался `KuSource IntentUtils.startCalibration()`. **К фокусировке отношения не имеет.**
Название «AutoFocus» в имени файла — вводит в заблуждение.

---

## 5. JNI / моторы

`com.trd.service.jni.MotorJNI` — прямой доступ к моторам (фокус) через JNI.
`libtrdclient.so` / `libtrdclient_imp.so` / `libtrd_driver.so` — клиентские библиотеки TRD.

---

## 6. Мусор / что можно чистить (для будущей кастомной прошивки)

- `RuiAutoFocus.apk` (`com.hysd.screen`) — калибровка экрана, пользователю не нужна (заводская).
- Старые/дублирующие layout (`focus_dialog.xml` vs `rj_focus_dialog.xml`) — разобраться, какой реально используется.
- `abc_*.xml` (AndroidX AppCompat) — стандартная библиотека, не мусор.

---

## 7. Вывод для задачи модернизации

1. **Фокус-оверлей** — в `trd.service` (`rj_focus_dialog.xml` + `RJFocusDialog`). Заменяем только графику (PNG → 4K/вектор).
2. **Экраны трапеции/зума** — в `com.rjpj.tcorrection` (отдельное приложение, см. карту tcorrection). Переносим в MOD.
3. **Железо** — в `trd.framework` (не трогаем).
4. **Калибровка экрана** — `com.hysd.screen` (RuiAutoFocus.apk), заводская, удалить из кастомной прошивки.

Трёхслойная архитектура (железо → оверлей → UI) **оправдана** и менять её не нужно:
оверлей должен быть отдельным сервисом (рисует поверх видео), железо — отдельным binder-сервисом.
Избыточна только tcorrection (можно встроить в MOD) и RuiAutoFocus (заводская).

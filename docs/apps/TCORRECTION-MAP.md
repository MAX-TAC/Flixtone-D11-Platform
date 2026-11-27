# КАРТА: com.rjpj.tcorrection (KeystoneCorrection) — полный разбор

Дата: 2026-11-27. Уровень: **STATIC_CONFIRMED** (разбор APK 2.3 МБ, `vendor/reference/8052/APK/KeystoneCorrection.apk`).

---

## 1. Что это

Отдельное системное приложение (`sharedUserId=android.uid.system`, **НЕ persistent**) —
**пользовательские экраны геометрической коррекции проекции**:
- коррекция 4 углов
- горизонтальная/вертикальная трапеция
- цифровой зум

**Экрана фокусировки здесь НЕТ** — фокус-оверлей рисует `com.trd.service` (см. карту trd).

**Установка:** `/system/priv-app/KeystoneCorrection/KeystoneCorrection.apk`, versionCode 33, versionName 13.
**ВАЖНО:** не persistent → **можно обновлять через `pm install -r`** (в отличие от KuSource с `PERSISTENT`).
Значит перенос экранов в MOD + замена tcorrection реальны без пересборки super.

**Связь с MOD:** MOD обращается к `KeystoneUtil.resetKeystone()` через `DexClassLoader`
по пути `/system/priv-app/KeystoneCorrection/KeystoneCorrection.apk` (кнопка «Сбросить все коррекции»).
При переносе логики в MOD этот DexClassLoader-путь станет не нужен.

---

## 2. Состав (компоненты манифеста)

| Компонент | Intent | Роль |
|---|---|---|
| `MainActivity` | — | точка входа (выбор режима) |
| `FourCornerActivity` | `rjpj.action.keystone.FOUR_CORNER` | коррекция 4 углов |
| `HVKeystoneActivity` | `rjpj.action.keystone.HV` | H/V трапеция |
| `DigitalZoomActivity` | `rjpj.action.keystone.DIGITAL_ZOOM` | цифровой зум |
| `TCorrectionBroadcastReceiver` | exported | приём broadcast (назначение — уточнить) |
| `InitializationProvider` | — | AndroidX startup |

Все 3 корректирующих Activity: `excludeFromRecents=true`, `launchMode=singleTask`, `exported=true`.

---

## 3. Ключевые классы

| Класс | Роль |
|---|---|
| `KeystoneUtil` | **главная логика**: `adjustPixel`, `resetKeystone`, `setLB/LT/RB/RTOffset`, `writeParcelToFlinger`, `updateKeystoneProperties` |
| `I2CDevice` | I2C-интерфейс к железу (`/dev/i2c-1`) |
| `Constant` | флаг `isFPGA` (Build.A_RJ_ADAPTER_ID == 1) |
| `TCorrectionBroadcastReceiver` | broadcast-приёмник |

---

## 4. Persist-ключи (координаты 8 углов)

Все пишутся/читаются через `SystemProperties` (`persist.*`):

**X-координаты:**
- `persist.rjpj.fourcorner.keystone_lbx` (left-bottom X)
- `persist.rjpj.fourcorner.keystone_ltx` (left-top X)
- `persist.rjpj.fourcorner.keystone_rbx` (right-bottom X)
- `persist.rjpj.fourcorner.keystone_rtx` (right-top X)

**Y-координаты:**
- `persist.rjpj.fourcorner.keystone_lby`, `lty`, `rby`, `rty`

**Дополнительно (из MOD `ProjectorExtras`):**
- `persist.display.keystone_*` — второй набор (альтернативный)
- `persist.rjpj.autokeystone.move` / `persist.rjpj.autokeystone.poweron` — автотрапеция

---

## 5. Как работает коррекция (механика)

1. Пользователь двигает угол/трапецию → Activity вызывает `KeystoneUtil.setXXOffset(x, y)`.
2. `setXXOffset` валидирует (`checkValidValue` против `MAX_VALUE_X`/`MAX_VALUE_Y`), сохраняет в поля `mLeftBottomX` и т.д.
3. `writeParcelToFlinger(index)` — **пишет в `/dev/i2c-1`** через `I2CDevice` (8 регистров, по 2 на угол X/Y).
4. **I2C → FPGA/аппаратный блок коррекции** выполняет геометрическое искажение на уровне видеотракта (не GPU, не мотор).
5. `updateKeystoneProperties()` — синхронизирует значения в `persist.*` (для восстановления после ребута).

**Вывод:** коррекция трапеции — **аппаратная** (FPGA через I2C), а не программная. Менять можно только **UI** (экраны и ввод), но НЕ механику записи в I2C.

---

## 6. Ограничения (MAX_VALUE)

`KeystoneUtil.<clinit>`:
- `MAX_VALUE_X` = **480** (0x1e0) если `isFPGA` (Build.A_RJ_ADAPTER_ID==1), иначе **192** (0xc0)
- `MAX_VALUE_Y` = **270** (0x10e) если `isFPGA`, иначе **108** (0x6c)

`checkValidValue(value, 0, MAX)` — клампинг в диапазон [0, MAX].

### TCorrectionBroadcastReceiver (программный API)

Принимает broadcast с extras: `type`, `lt_x`, `lt_y`, `lb_x`, `lb_y`, `rb_x`, `rb_y`, `rt_x`, `rt_y`.
Это **API для установки коррекции извне** (используется автотрапецией из trd.service/KuSettings).
При переносе в MOD — сохранить этот receiver для совместимости с автокоррекцией.

---

## 7. Layout и графика (что мыльно)

| Ресурс | Размер | Проблема |
|---|---|---|
| `keystone.png` (сетка) | 1920×1080 (drawable-hdpi) | PNG-сетка, на 4K растягивается |
| `keystone_bg.png` | 1920×1080 (584 байта, почти пустой) | фон |
| `keystone_up/down/left/right.png` | 32×32 | стрелки (мелкие, но рабочие) |

Layout: `activity_four_corner_correction.xml` (5.4 КБ), `activity_hvkeystone_correction.xml` (4 КБ), `activity_digital_zoom.xml` (4 КБ), `activity_main.xml`.

Все на `ConstraintLayout` + `ImageView` (сетка) + `TextView` (подписи) + `Space`.

---

## 8. Что менять под 4K (для переноса в MOD)

1. **Сетку `keystone.png`** (1920×1080 PNG) → заменить на **программную отрисовку** (View.onDraw рисует тонкие линии — резкость в любом разрешении).
2. **Стрелки** 32×32 → векторные `VectorDrawable` (масштабируются).
3. **Числовые координаты** углов (X/Y) — взять из `persist.rjpj.fourcorner.keystone_*`, показывать на экране (сейчас их нет — не информативно).
4. **Выбор шага** (1/2/5/10) — для точной подстройки.
5. **Кнопка «Сброс»** — вызов `KeystoneUtil.resetKeystone()` (или сброс всех 8 persist-ключей).
6. **Индикатор активного угла** — подсветка.

---

## 9. Перенос в MOD (план)

НЕ трогая MOD сейчас — подготовить **новые Activity + layout** как отдельный модуль:
- Код Activity: скопировать логику `KeystoneUtil` (запись в I2C + persist) — она рабочая, переносим без изменений.
- Layout: перерисовать с нуля (программная сетка, векторные стрелки, числа).
- Intent-экшены: сохранить те же (`rjpj.action.keystone.*`), чтобы кнопки в MOD работали.
- В MOD: заменить вызовы `com.rjpj.tcorrection.*Activity` на новые встроенные Activity.

**Ключевое:** механику записи (I2C через `/dev/i2c-1`, `KeystoneUtil`) **не переделывать** — она аппаратная и рабочая. Меняем только UI-слой.

---

## 10. Открытые вопросы

| Вопрос | Как выяснить |
|---|---|
| Точные `MAX_VALUE_X/Y` | прочитать `<clinit>` KeystoneUtil |
| Назначение `TCorrectionBroadcastReceiver` | разобрать smali |
| Как MOD сейчас вызывает экраны | grep в `exact8054` (`ProjectorExtras`, `OemProjectionPanel`) |
| Зум — программный или тоже I2C? | разобрать `DigitalZoomActivity` |

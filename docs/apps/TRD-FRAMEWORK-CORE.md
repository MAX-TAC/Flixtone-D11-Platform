# `com.trd.framework` — ядро работы с железом проектора

Дата: 2026-11-24. Источник: DEX (2.1 МБ), `libtrdmiddle.so` (arm64, 104 КБ), `libopencv_java4.so`.
Уровень: **`STATIC_CONFIRMED`**.

---

## 1. Что это такое

`com.trd.framework` — **Binder-сервис** `TrdSystemService`, через который всё Android-ПО
говорит с железом проектора. Это не «одно из приложений», это посредник между Android и MCU.

```
Настройки / KuSettings / KuSourceRJ / Factory
        ↓ Binder (AIDL)
  TrdSystemService  (com.trd.framework)
        ↓
  libtrdmiddle.so  (JNI + OpenCV)
        ↓
     MCU / моторы / ToF / датчики
```

**Публичные интерфейсы (AIDL):**

| Интерфейс | Назначение |
|---|---|
| `ITrdSystemService` | корневой сервис |
| `IMotorCtrl` | моторы: фокус, трапеция, зум |
| `ITofCtrl` | ToF-датчик |
| `ITofDataListener` | обратный вызов с данными ToF |
| `ITemperatureCtrl` | температура |
| `ISensorCtrl` | датчики (акселерометр, гироскоп) |
| `IProjectorCtrl` | режим проектора (потолок/тыл) |
| `ICommunicationCtrl` | связь с MCU |
| `ISystemCtrl` + `ISystemCtrlCallback` | системные команды и события |
| `ITrdSystemListener` | подписка на события |

---

## 2. Главное открытие: трапеция считается **нативно, через OpenCV**

В APK лежат **17 МБ `libopencv_java4.so`** — это полноценный OpenCV. Не зря.

В `libtrdmiddle.so` найдены JNI-функции:

```
Java_com_trd_framework_projector_TrapezoidUtil_AutoTrapezoidInit
Java_com_trd_framework_projector_TrapezoidUtil_setEigen
Java_com_trd_framework_projector_TrapezoidUtil_SetLeftRightTrapezid
Java_com_trd_framework_projector_TrapezoidUtil_SetUpDownTrapezid__F        (1 float)
Java_com_trd_framework_projector_TrapezoidUtil_SetUpDownTrapezid__FFF      (3 float)
Java_com_trd_framework_projector_TrapezoidUtil_SetUpDownTrapezid__FFFFFF   (6 float)
Java_com_trd_framework_projector_TrapezoidUtil_UpDownTrapezidIncrease
Java_com_trd_framework_projector_TrapezoidUtil_LeftRightIncrease
```

И строки отладки в нативе:

```
draw_warp_grid p0.x:%f,y:%f,i:%d,j:%d
init_grid_points[%d].x:%f,y:%f
calc point %d, x %d, y %d
control_points
corner_points
choose_point_idx
choose_flag
h_trans / h_trans_inv        ← гомография (перспективное преобразование)
horAngle
autotrapezoid
keystone: save to pth: %s
SetUpDownTrapezid2 offset_x:%.3f,offset_y:%.3f,offset_z:%.3f,KeyStone_axis:%d,KeyStone_Polarity:%d
```

### Что это значит

**Трапеция — это не «поворот мотора», а гомография (перспективное преобразование)
сетки из OpenCV.** Алгоритм:

1. `AutoTrapezoidInit` — строит начальную сетку (`init_grid_points`).
2. `setEigen` — задаёт параметры (углы, позиция).
3. `SetUpDownTrapezid(6 float)` — задаёт преобразование по 6 точкам (4 угла + 2 опорные).
4. `draw_warp_grid` — рисует деформированную сетку.
5. `h_trans` / `h_trans_inv` — прямое и обратное преобразование.

`SetLeftRightTrapezid` и `UpDownTrapezidIncrease` — отдельные функции для лево-право и
верх-низ.

### Отладочные пути (важно!)

```
/sdcard/projector/img/       ← сохранение картинки
/sdcard/projector/log/       ← лог
keystone: save to pth: %s
isDebugMode
```

**Следствие:** если включить `isDebugMode`, natивный слой **будет сохранять картинку и лог
в `/sdcard/projector/`**. Это бесценно для отладки трапеции — можно увидеть, что именно
происходит внутри. Надо выяснить, чем включается (build flag или property).

---

## 3. ToF-подсистема

```
com.trd.framework.tof.TofCtrlService
com.trd.framework.tof.TofController
com.trd.framework.tof.TofMessage / TofMessageBuilder
nativeReadTofData / nativeSetTofStatus
getL1TofData / getTmfTofData / getTofData / GetTofType
addTofDataListener / handleTofCommand / handleIncomingTofCommand
```

Типы данных ToF: **L1** и **TMF** — два разных формата. `TofMessageBuilder` собирает сообщения
для отдачи клиентам.

---

## 4. API фокуса и трапеции (полный список)

**Чтение:**

```
getAutoFocusBoot / getAutoFocusMove
getAutoKeystoneBoot / getAutoKeystoneMove
GetKeystone / getKeystoneValue / getTrapezoidSt
getUpDownAutoKeystone
getMotorCtrl / getMotorPosition / getMotorStep / GetMotorStatus / getMotorType
getMotorCtrlSetting / motorSettingImplinstance
getScreenZoom / isZoomEnable
getPOPTunerFocus
isNoAutoFineTune / noAutoFineTune
onlyChgFocus
```

**Запись:**

```
setAutoFocusBoot / setAutoFocusMove
setAutoKeystoneBoot / setAutoKeystoneMove
setUpDownAutoKeystone
setScreenZoom
setNoAutoFineTune
cusRestoreKeyStone / cusTrapezoidLeftRight / cusTrapezoidUpDown / cusAdjZoomAll
```

**Ключевое наблюдение:** API **полный и понятный**. Автофокус при включении, автофокус при
движении, автотрапеция, зум, восстановление — всё есть.

---

## 5. Что это даёт проекту

### 5.1. Можно делать собственный UI без посредников

Все параметры проектора доступны **напрямую через `TrdSystemService`**:
`getAutoFocusBoot`, `setAutoKeystoneMove`, `setScreenZoom` и так далее.

**Это значит: `KuSourceRJ` для управления железом не нужен.** KuSettings тоже — он только
перезапускает `TimeService`.

### 5.2. Трапеция — вычисляемая, а не «моторная»

То, что раньше выглядело как «послать команду мотору», на самом деле гомография сетки.
Это значит:
- можно сделать **свой UI с превью** (показать, как будет искажено, до применения);
- можно проверять значения математически, а не только «на глаз»;
- можно восстановить точную геометрию из сохранённой матрицы.

### 5.3. Отладка трапеции через `/sdcard/projector/`

Включение `isDebugMode` даст файлы в `/sdcard/projector/img/` и `/sdcard/projector/log/`.
**Это надо попробовать** — возможно, увидим, что именно считается.

---

## 6. Чего пока не знаю

| Вопрос | Как проверить |
|---|---|
| Чем включается `isDebugMode` | поиск property/build flag в DEX |
| Точная семантика 6 float в `SetUpDownTrapezid` | дизассемблирование `libtrdmiddle.so` |
| Работает ли `TrdSystemService` без `KuSourceRJ` | экспериментально, после watchdog |
| Есть ли свой watchdog в `trd.framework` | поиск таймеров/Handler в DEX |
| Порог температур и логика shutdown | DEX `ITemperatureCtrl` + эксперимент |

---

## 7. Следующие шаги

1. **Найти в DEX, чем включается `isDebugMode`** — это откроет отладку трапеции.
2. Разобрать `ITemperatureCtrl` — пороги, реакция на перегрев.
3. Разобрать `ICommunicationCtrl` — как идут команды на MCU (протокол).
4. Проверить, не проще ли ходить в `TrdSystemService` напрямую из MOD
   (у нас системный UID, права есть).

Это ядро. Поняв его, мы получаем контроль над всем железом проектора
из нашего собственного приложения.

---

## 8. Ключи состояния (найдено в DEX) — `DEVICE_VERIFIABLE`

### 8.1. Координаты трапеции — 8 ключей, по одному на каждый угол

```
persist.display.keystone_ltx      левый верхний  X
persist.display.keystone_lty      левый верхний  Y
persist.display.keystone_rtx      правый верхний X
persist.display.keystone_rty      правый верхний Y
persist.display.keystone_lbx      левый низ      X
persist.display.keystone_lby      левый низ      Y
persist.display.keystone_rbx      правый низ     X
persist.display.keystone_rby      правый низ     Y
```

Это **прямое подтверждение** гипотезы о гомографии: трапеция хранится как 4 точки
(8 координат), а не как «углы мотора». Именно эти 8 чисел подаются в
`SetUpDownTrapezid` / `SetLeftRightTrapezid`.

### 8.1b. ВТОРОЙ набор ключей + аппаратный путь (уточнение 2026-11-27)

⚠️ **Разбор `com.rjpj.tcorrection` выявил второй, аппаратный механизм коррекции:**

- Ключи **`persist.rjpj.fourcorner.keystone_{lt,rt,lb,rb}{x,y}`** — их читает/пишет
  `com.rjpj.tcorrection.KeystoneUtil` (приложение экранов коррекции).
- Запись идёт **НЕ** через `SetKeystone` (гомографию), а через **`I2CDevice.writeRegister()` в `/dev/i2c-1`**
  — то есть **FPGA/аппаратный блок** выполняет геометрию на уровне видеотракта.
- `persist.display.keystone_*` — это «зеркало» (display-side mirror) для состояния.

**Итог — два механизма, которые не путать:**
| Механизм | Кто | Куда пишет |
|---|---|---|
| Гомография (OpenCV) | `trd.framework` (native `TrapezoidUtil`) | `SetUpDownTrapezid` через binder |
| Аппаратная (FPGA) | `com.rjpj.tcorrection.KeystoneUtil` | `/dev/i2c-1` через `I2CDevice` |

Для **своего UI** (перенос в MOD) достаточно сохранить логику `KeystoneUtil`
(запись в I2C + persist), не трогая механику — она рабочая.

### 8.2. Смещение оптики

```
persist.sys.offset_x
persist.sys.offset_y
persist.sys.offset_z
```

Три оси — совпадает с `SetUpDownTrapezid2 offset_x:%.3f,offset_y:%.3f,offset_z:%.3f`
из нативной библиотеки.

### 8.3. Автотрапеция

```
persist.sys.trd.projector.auto_keystone_move
persist.vendor.autokeystone
trd_keystone_enable / trd_keystone_boot / trd_keystone_move
```

### 8.4. Размер экрана и машина

```
persist.vendor.disp.screensize
persist.trd.machine          ← тип машины
persist.trd.acc.order        ← порядок осей акселерометра
persist.sys.fun_test         ← «fun test» — вероятно, заводской режим
```

### 8.5. Методы управления (DEX)

```
SetKeystone / SetKeystoneInit / SetKeystoneReset / setKeystoneValue / GetKeystone
resetKeyStone / cusRestoreKeyStone
setAutoKeystoneBoot / setAutoKeystoneMove / setUpDownAutoKeystone
onKeyStoneValue        ← колбэк изменения
```

### 8.6. Отладочные пути MediaTek

```
/data/mtk_fapi_debug
/data/mtk_tvapi_debug
```

Это **файлы-флаги**: если файл существует — включается отладочный вывод
MediaTek FAPI/TvAPI. Гораздо проще, чем `isDebugMode` в нативе.

**Как проверить:** создать файл (нужен root), посмотреть, появится ли больше логов.
Это запись — требуется согласие владельца.

---

## 9. Практический вывод: как управлять трапецией правильно

Из найденного складывается **полная и понятная схема**:

```
1. Прочитать 8 координат:  persist.display.keystone_{lt,rt,lb,rb}{x,y}
2. Изменить нужную точку (например, левый верхний X)
3. Записать обратно
4. Вызвать SetKeystone (или setKeystoneValue)
   → нативный слой пересчитает гомографию и применит
```

**Никаких моторов.** Это чистая математика на уровне изображения.

**Почему это важно:** значит наш MOD может:
- показать **точные числовые координаты** углов (вместо «ползунка на глаз»);
- дать **сброс в ноль** одной командой (`SetKeystoneReset`);
- сделать **превью** до применения;
- сохранять/восстанавливать профили геометрии (например, «стена», «потолок»).

Это qualitatively лучше, чем то, что даёт сток (там только стрелки пульта).

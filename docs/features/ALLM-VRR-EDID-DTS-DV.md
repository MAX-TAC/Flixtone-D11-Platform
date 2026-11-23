# Задачи по функциям: ALLM, VRR, EDID, DTS, Dolby Vision

Дата: 2026-11-23. Основание: дампы `research/device-slices/2026-11-23/` + DEX-строки.

Уровни: `DEVICE_VERIFIED` — подтверждено дампом с устройства; `STATIC_CONFIRMED` — найдено в коде;
`ASSUMPTION` — гипотеза.

---

## 1. ALLM — реально работает, нужен только UI

**Статус: `DEVICE_VERIFIED` для поддержки, `STATIC_CONFIRMED` для механизма.**

Из `dumpsys display`:

```
allmSupported true
mAllmSupported=true
mAllmRequested=false          ← сейчас не запрашивается
mGameContentTypeSupported=false
mGameContentTypeRequested=false
```

Из DEX `TvSettingsPlus` (classes5):

```
g_video__vid_allm_switch
tv_picture_video_allm
device_picture_advanced_video_allm
KEY_PICTURE_ADVANCE_VIDEO_ALLM
AdvanceVideoALLMPref
ACTION_NOTIFY_ALLM
ALLMValue =
```

**Вывод:** дисплей **уже заявляет** `allmSupported=true`, а в настройках есть готовый
переключатель `AdvanceVideoALLMPref`. То есть ALLM не надо «изобретать» — надо только
вывести пункт в меню и проверить, меняет ли `g_video__vid_allm_switch` значение
`mAllmRequested` с `false` на `true`.

**Что делать:** добавить строку в раздел «Изображение» или «Источники» (логичнее в
«Источники», рядом с Game Mode), писать в `g_video__vid_allm_switch`, читать обратно
`g_video__vid_allm_switch` и `dumpsys display | grep mAllmRequested`.

**Риск: низкий.** Это флаг, а не режим дисплея.

**Важное уточнение:** `gameContentTypeSupported=false` — значит **автоматическое**
переключение по метаданным контента работать не будет. Только ручной переключатель.
Это надо честно написать в UI, иначе пользователь ждёт магии, которой нет.

---

## 2. VRR — ключ есть, поддержки панели нет

**Статус: `ASSUMPTION` (скорее не заработает).**

Из `dumpsys display`:

```
supportedModes [{id=1, 3840x2160, fps=50.0, alternativeRefreshRates=[60.000004]},
                {id=2, 3840x2160, fps=60.000004, alternativeRefreshRates=[50.0]}]
supportsFrameRateOverrideByContent=false
mRefreshRateChangeable=false
```

**Ровно два режима**, причём это два фиксированных тайминга, а не диапазон.
VRR требует, чтобы панель принимала переменный интервал кадров.

Из DEX найден только **ключ** `g_video__vid_vrr_switch` и константы
`VIDEOINFO_TYPE_VRR_ENABLE`, `VIDEOINFO_TYPE_VRR_FREQ`, `VIDEOINFO_TYPE_VRR_HIGH_FRAME_RATE_MODE`
— все в контексте **информации о сигнале** (какой режим пришёл от источника), а не управления дисплеем.

**Вывод:** `g_video__vid_vrr_switch` — это, вероятнее всего, **чтение состояния** источника
(включён ли VRR на входе HDMI), а не переключатель проектора. Наш проектор не TV-панель
с переменной частотой, а фиксированный DLP-путь.

**Что делать:** не обещать VRR. Проверить можно только так: включить ключ и посмотреть,
меняется ли что-то в `dumpsys display` и в таблице таймингов `SurfaceFlinger`.

**Честный прогноз: скорее не заработает.** Не строить на этом UI.

---

## 3. EDID: 4 ключа при 2 портах

**Статус: `STATIC_CONFIRMED`.**

Найдено:

```
g_video__set_hdmi_edid_port1
g_video__set_hdmi_edid_port2
g_video__set_hdmi_edid_port3
g_video__set_hdmi_edid_port4
```

При этом физических портов **два** (`ro.rjpj.hdmi.ports=HW6:HDMI1,HW7:HDMI2`),
а `tv_input` регистрирует четыре логических входа (HW5–HW8).

Это **нормальная ситуация** для MediaTek-платформы: код один на всю линейку TV,
где портов бывает четыре. Лишние ключи просто не используются, они не «сломаны».

**Что делать:** **ничего не удалять и не переделывать**. В UI показывать только
два фактически зарегистрированных порта, определяя их через `TvInputManager`
(как уже делает `OemHdmiPortInfo` в MOD). Не пытаться «исправить» прошивку под
два порта — это сломает совместимость с линейкой.

**Риск переделки: высокий, пользы ноль.** Моя рекомендация — отказаться от этой идеи.

---

## 4. DTS и 7.1 — источник проблемы найден

**Статус: `DEVICE_VERIFIED`.**

Из `dumpsys media.audio_policy` — профиль выхода **HDMI ARC**:

```
12. "HDMI ARC"; {AUDIO_DEVICE_OUT_HDMI_ARC}
  - Profiles (4):
    1. AUDIO_FORMAT_AC3
    2. AUDIO_FORMAT_E_AC3
    3. AUDIO_FORMAT_DTS
    4. AUDIO_FORMAT_DTS_HD
  sampling rates: 8000…48000
  channel masks: 0x0001, 0x0003, 0x003f, 0x063f
```

**Что это означает.** Маска каналов `0x063f` — это 5.1. Восьмого канала (бит `0x0800`,
side left/right или rear) **в списке нет**. То есть ARC физически объявлен
как максимум **5.1**, а не 7.1.

При этом:
- для `DTS` в глобальном списке есть маска `0x2d03f` (7.1) — то есть кодек умеет;
- но у **выходного устройства** ARC маска ограничена `0x063f` (5.1).

**Вывод: 7.1 не заработает через ARC не потому, что «сломалось», а потому что полоса
ARC не рассчитана на 7.1.** Это ограничение стандарта ARC (не eARC). eARC полосу
имеет, но `mArcEstablished=false` и ресивера нет — проверить нечем.

**Что делать:**
- для форумчанина — объяснить, что 7.1 через ARC невозможен по определению;
- для нас — проверить, проходит ли 7.1 через **eARC** (нужен ресивер);
- в UI: показывать реально доступные форматы для выбранного выхода, а не общий список.

**Важно:** это не баг прошивки. Это честное ограничение железа, и его надо объяснять,
а не «чинить».

---

## 5. Dolby Vision — ключ есть, компоненты тоже есть

**Статус: `STATIC_CONFIRMED` для наличия, `ASSUMPTION` для перспективы.**

Найдено:
```
g_video__dovi_user_switch
g_video__dovi_reset_pic_setting
picture_mode_dolby, picture_mode_dolby_game, picture_mode_dolby_iq
PICTURE_MODE_DOVI_BRIGHT / DARK / GAME / VIVID
picture_mode_dovi_entries, picture_mode_dovi_entry_values
PICTURE_DOLBY_VISION_DARK_MODE
```

Плюс из ранних исследований: `libcodec2.MTK.so` содержит
`MsVdec_CheckSupportDolbyVision`, `MSVdecConfigDolbyVision`;
`mik.ko` — `MI_VDEC_GetDolbyVisionInfo`; `kdrv_xc.ko` — `KHal_XC_SupportDolbyHDR`.

**Но:** `HWC Support: dv=false`, `mSupportedHdrTypes=[2,3]`, `maxLuminance=500`.

**Вывод:** Android-слой (настройки, режимы, декодер) для DV **присутствует**. Отсутствует
только заявление дисплея `dv=false`. Это значит, что HWC не сообщает о поддержке DV —
и Android не включит DV-путь даже при наличии файла.

**Что исследовать дальше:**
1. Почему `hwcomposer.mt5873.so` возвращает `dv=false` — панель не та, или ключ не активирован.
2. Что делает `DolbyVisionService$SettingObserver` по ключу `dovi_user_switch`.
3. Есть ли в `system_ext` лицензионные файлы DV (`dolby/`, `dv_*`).
4. Реагирует ли что-то в оптическом тракте (это проверится только на живом видео).

**Прогноз:** шанс есть, но требуется вмешательство в HWC и, вероятно, лицензия.
Это отдельный исследовательский проект, не блокер основного.

---

## Итоговая приоритизация (по вашей оценке + техника)

| Функция | Готовность | Приоритет | Мой прогноз |
|---|---|---|---|
| ALLM | код и поддержка есть | **высокий** | заработает, нужен UI |
| DTS/7.1 | ограничение ARC | высокий (объяснение) | 7.1 через ARC невозможен, через eARC — проверить |
| EDID 2 порта | не нужно менять | **низкий** | рекомендация: не трогать |
| VRR | только ключ-читалка | низкий | скорее не заработает |
| Dolby Vision | Android есть, HWC нет | отдельно | требует вмешательства в HWC |
| 3D | не нужно | отказ | — |
| Караоке | не нужно | отказ | — |

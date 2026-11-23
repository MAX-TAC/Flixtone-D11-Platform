# eARC: почему не включается и что делать

Дата: 2026-11-24. Источник: DEX `com.android.tv.settings` (classes5), `dumpsys audio_policy`, `dumpsys hdmi_control`.
Уровень: **`STATIC_CONFIRMED`** для кода, `DEVICE_VERIFIED` для состояния устройства.

---

## 1. Что найдено

В `TvSettingsPlus` есть **отдельный класс** `EarcFragment`
(`com.android.tv.settings.partnercustomizer.sound.EarcFragment`) и приёмник
`com.android.tv.settings.partnercustomizer.utils.SoundEARCReceiver`.

Логика, восстановленная по строкам DEX:

```
EarcFragment
  ├── isSupportEARC()                    ← проверка поддержки
  ├── getEarcCaps()                      ← чтение возможностей eARC
  ├── isEnableEarc()                     ← текущее состояние
  ├── setEarcEnable(boolean)             ← запись
  │      "setEarcEnable value same ? "   ← защита от повторной записи
  │      "setEarcEnable(false)"
  └── updateEARCSettingValueToDrive
         "updateEARCSettingValueToDrive ex: "
         "updateEARCSettingValueToDrive,EARCSettingValue=="
         ↓
      KEY_SOUND_EARC  (defaultValue отдельно)
         ↓
      Settings.Global sound_earc
```

Плюс в `TvServices` найден **второй, независимый слой** eARC:

```
CFG_AUD_EARC_INFO_SPEAKER_MAPPING   → g_audio__earc_info_speaker_mapping
CFG_AUD_EARC_INFO_HW_BYPASS         → g_audio__earc_info_hw_bypass
CFG_AUD_EARC_INFO_LAYOUT            → g_audio__earc_info_layout
CFG_AUD_EARC_INFO_MUTE              → g_audio__earc_info_mute
CFG_AUD_EARC_INFO_WORD_LENGTH       → g_audio__earc_info_word_length
```

И **третий** — стандартный Android:

```
Settings.Global.HDMI_ARC_CONTROL_ENABLED   (в classes5 TvSettingsPlus)
```

---

## 2. Почему eARC «не включается» у форумчанина

Три независимых механизма, и все три должны совпасть:

| Слой | Что переключает | Где живёт |
|---|---|---|
| 1. Android | `HDMI_ARC_CONTROL_ENABLED` | AOSP `HdmiControlManager` |
| 2. OEM-настройка | `sound_earc` (`KEY_SOUND_EARC`) | `EarcFragment` в TvSettingsPlus |
| 3. MediaTek-инфо | `g_audio__earc_info_*` | `TvServices` |

**Гипотеза (`ASSUMPTION`, но очень вероятная):** пользовательский переключатель в обычных
настройках пишет только слой 2 (`sound_earc`), а слой 1 (`HDMI_ARC_CONTROL_ENABLED`) или
слой 3 остаются в состоянии «выключено». Тогда eARC не поднимается, хотя UI показывает «включено».

Именно это он и описал: **«принудительно включал в медиатек меню»** — то есть через
инженерное меню, которое достучалось до слоя 3.

---

## 3. Что Проверить при подключённом ресивере

Порядок (только чтение, до любых записей):

```
1. settings get global sound_earc
2. settings get global HDMI_ARC_CONTROL_ENABLED
3. settings get global g_audio__earc_info_hw_bypass      (и остальные earc_info_*)
4. dumpsys hdmi_control | grep -E "mArcEstablished|mArcFeatureEnabled|port_id"
5. dumpsys media.audio_policy | grep -E "HDMI ARC|ARC capability"
```

Ожидаемая картина при рабочем eARC:

```
mArcEstablished = true
mArcFeatureEnabled = {2=true}        (или порт, к которому подключено)
ARC capability: dd:1, ddp:1(atmos:1), dts:1, aac:1, mat-truhd:1, dtshd:1
```

Сейчас на устройстве:

```
mArcEstablished = false
mArcFeatureEnabled = {1=false, 2=true, 3=false, 4=false}
Supported ARC capability: dd:0, ddp:0(atmos:0), dts:0, aac:0, mat-truhd:0, dtshd:0
```

Все нули — ресивер не согласован.

---

## 4. Что это значит для форумчанина с 7.1

Если у него ресивер есть, но eARC не поднялся, он слушает **обычный ARC**, а ARC
физически не несёт 7.1 (маска каналов у ARC — `0x063f`, это 5.1).

**Поэтому:** 7.1 не работает не из-за 7.1, а из-за того, что **eARC не поднялся**, и звук
упал на ARC с 5.1. Как только eARC заработает — появятся и DTS-HD, и TrueHD, и 7.1.

**Это важная корректировка моего предыдущего вывода:** я сначала предположил, что у него
нет ресивера. Это было неверно. Правильная формулировка: **проблема в поднятии eARC,
а не в поддержке 7.1.**

---

## 5. Что делать в MOD

Правильный подход: **один переключатель, но пишущий во все три слоя последовательно.**

```
Пользователь включает eARC
  ↓
1. Settings.Global.putInt("HDMI_ARC_CONTROL_ENABLED", 1)
2. Settings.Global.putInt("sound_earc", 1)
3. Проверить g_audio__earc_info_hw_bypass / layout / word_length
   (если пустые — заполнить значениями из ресурсов OEM)
  ↓
readback: dumpsys hdmi_control → mArcEstablished
  ↓
если true  → успех
если false → честно показать «ресивер не ответил», а не «включено»
```

**Ключевое:** подтверждение должно опираться на `mArcEstablished`, а не на значение в
`Settings.Global`. Запись в настройки — не доказательство.

---

## 6. Чего не делать

- **Не отключать CEC ради eARC** без проверки: в этой прошивке они связаны
  (в предыдущих отчётах зафиксировано, что «отключение CEC отключает eARC»).
- **Не писать `g_audio__earc_info_*` наугад** — эти ключи зеркалят состояние сигнала,
  их неправильное значение может дать тишину.
- **Не обещать 7.1 через ARC** — только через eARC.

# HDMI ARC / eARC: что реально умеет проектор

Дата: 2026-11-25. Источники: `dumpsys hdmi_control`, `dumpsys audio_policy`,
`dumpsys tv_input` (срез 2026-11-23).
Уровень: **`DEVICE_VERIFIED`** — все значения сняты с живого 8054.

---

## 1. Физические и логические порты

`tv_input` регистрирует 4 логических HDMI:

```
HW5 → hdmi_port=1
HW6 → hdmi_port=2
HW7 → hdmi_port=3
HW8 → hdmi_port=4
```

На корпусе — 2 физических порта. Логических 4 (типовой шаблон MediaTek).

---

## 2. ARC есть только на одном порту

`dumpsys hdmi_control`:

```
port_id: 1, type: HDMI_IN, cec: true, arc: false
port_id: 2, type: HDMI_IN, cec: true, arc: true     ← ЕДИНСТВЕННЫЙ С ARC
port_id: 3, type: HDMI_IN, cec: true, arc: false
port_id: 4, type: HDMI_IN, cec: true, arc: false
```

**ARC = `hdmi_port 2` = HW6 = «HDMI 2» на корпусе.**

---

## 3. Что даёт ARC по звуку

`dumpsys audio_policy`, устройство `AUDIO_DEVICE_OUT_HDMI_ARC`:

```
- Profiles (4):
1. AC3      channel masks: 0x0001, 0x0003, 0x003f, 0x063f
2. E_AC3    channel masks: 0x0001, 0x0003, 0x003f, 0x063f
3. DTS      channel masks: 0x0001, 0x0003, 0x003f, 0x063f
4. DTS_HD   channel masks: 0x0001, 0x0003, 0x003f, 0x063f
```

`0x063f` = FL + FR + FC + LFE + RL + RR = **5.1 (6 каналов)**.

| Формат | Поддержка |
|---|---|
| Dolby Digital (AC3) 5.1 | **да** |
| Dolby Digital Plus (E_AC3) 5.1 | **да** |
| DTS 5.1 | **да** |
| DTS-HD 5.1 | **да** |
| 7.1 любого формата | **нет** (максимум `0x063f`) |
| Dolby TrueHD / Atmos | **нет** (нужен eARC) |

---

## 4. eARC — НЕТ

В `audio_policy` **отсутствует** `AUDIO_DEVICE_OUT_HDMI_EARC`.
Есть только `AUDIO_DEVICE_OUT_HDMI_ARC` (обычный ARC).

**Следствие:** TrueHD, Atmos, DTS-HD MA 7.1 через HDMI невозможны.
Максимум — 5.1 в сжатых форматах.

В OEM-слое есть ключи `sound_earc`, `g_audio__earc_info_*`, `EarcFragment`,
но Android-политика eARC-устройство не объявляет. То есть eARC либо не
реализован на этой плате, либо реализован только для внутренних путей.

---

## 5. Блокер: ARC не заявлен в CEC

```
Device features: record_tv_screen: Y  set_osd_string: N  deck_control: N
                 set_audio_rate: N  arc_tx: N  arc_rx: N  set_audio_volume_level: Y

mArcEstablished: false
mArcFeatureEnabled: {1=false, 2=true, 3=false, 4=false}
```

**`arc_tx: N`** — проектор **не объявляет** себя как ARC-передатчик в CEC.
**`mArcEstablished: false`** — ARC-канал не поднят.

Без объявления `arc_tx` ресивер не узнает, что проектор умеет отдавать звук
по ARC, и не станет его запрашивать.

При этом `mArcFeatureEnabled={2=true}` — **функция включена в настройках**
именно для порта 2. Значит блокер не в настройке, а в capability-объявлении.

---

## 6. Ответ на вопрос «сделать HDMI1 входом, а HDMI2 выходом»

**Нельзя, и это не ограничение прошивки — это природа ARC.**

ARC (Audio Return Channel) — не отдельный выход. Это **обратный канал на том же
входном порту**: видео идёт от источника к проектору, звук — обратно по тому же
кабелю (линия HEC).

Поэтому:
- Все 4 порта объявлены как `HDMI_IN` — выходного порта нет и не будет.
- **ARC уже работает на порту 2** ровно в том смысле, который нужен.

---

## 7. Схема, которая должна работать

```
Приставка / ПК ──HDMI──► HDMI 1 (вход, видео)
                         Проектор
Ресивер (ARC) ───HDMI──► HDMI 2 (ARC-порт)
```

Проектор принимает видео по HDMI 1, извлекает звук и отдаёт его по ARC
в ресивер через HDMI 2. Ресивер получает DD 5.1 / DTS 5.1.

**Условия:**
1. Ресивер подключён **именно к HDMI 2** (единственный ARC-порт).
2. На ресивере ARC включён (обычно в настройках HDMI).
3. ARC поднялся (`mArcEstablished` → `true`).
4. Проектор заявил `arc_tx` в CEC.

**Пункт 4 сейчас не выполняется** — это и есть реальный блокер.

---

## 8. Что проверять на устройстве

| Проверка | Как |
|---|---|
| Какой физический разъём = port 2 | Подключить источник по очереди в оба, смотреть `dumpsys hdmi_control` |
| Можно ли включить `arc_tx` | MediaTek factory menu → ARC/eARC (форумчанин так и делал) |
| Поднимается ли ARC | `dumpsys hdmi_control \| grep mArcEstablished` после подключения ресивера |
| Идёт ли 5.1 | `dumpsys media.audio_flinger \| grep -E "Output devices\|format"` |

---

## 9. Нужен ресивер

Без ресивера с ARC проверить нельзя. У владельца его пока нет.
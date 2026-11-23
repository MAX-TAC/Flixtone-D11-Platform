# Звук: выходы, эквалайзер, одновременный вывод

Дата: 2026-11-24. Источник: DEX `TvServices` (`AudioCustomizedService`, `SoundSpeakerStatusService`),
`dumpsys media.audio_policy`, `dumpsys media.audio_flinger`.
Уровень: **`STATIC_CONFIRMED`** + `DEVICE_VERIFIED` для текущего состояния.

---

## 1. Выходы звука в системе проектора

MediaTek определяет **три** выходных устройства:

```
AUD_OUTDEV_SPEAKER       встроенные динамики
AUD_OUTDEV_BLUETEETH     Bluetooth (A2DP)
AUD_OUTDEV_USB           USB-аудио
```

А Android добавляет свои (из `dumpsys`): `HDMI Out`, `HDMI ARC`, `Spdif`, `Wired Headphone`.

**Важно:** `Spdif` в MediaTek-списке **отсутствует** — подтверждает ранний вывод, что
SPDIF объявлен только в Android-политике, но не в OEM-логике. Физического выхода, скорее всего, нет.

Ключ состояния: `g_audio__aud_out_port` (`CFG_AUD_AUD_OUT_PORT`).

---

## 2. Служба статуса динамика — механизм переключения

Найдена `com.mediatek.tv.agent.SoundSpeakerStatusService`:

```
setSpeakerStatusToAudioManager
KEY_SOUND_SPEAKER_STATUS → sound_speaker_status
SOUND_SPEAKER_STATUS_OFF
SOUND_SPEAKER_STATUS_BT_OUTPUT
SOUND_SPEAKER_STATUS_ARC_CONNECTED   → sound_speaker_status_acr_connected_notify
                                    (опечатка «acr» в OEM)
sound_speaker_status_audio_output_is_bt_notify
android.settings.SOUND_SPEAKER_STATUS   ← broadcast
```

**Как это работает:**

```
Подключился BT-саундбар
   ↓
AudioManager меняет активный выход
   ↓
SoundSpeakerStatusService.setSpeakerStatusToAudioManager(...)
   ↓
пишет sound_speaker_status = SOUND_SPEAKER_STATUS_BT_OUTPUT
   ↓
рассылает broadcast android.settings.SOUND_SPEAKER_STATUS
   ↓
UI (настройки) узнаёт, что звук теперь на BT
```

**Отсюда первый ответ на вопрос «почему EQ не работает на саундбаре»:**
когда активный выход — BT, статус меняется на `BT_OUTPUT`, и **OEM-эквалайзер отключается**
для этого выхода. Это не баг, это задумано: ОЕМ считает, что обработку звука делает саундбар.

---

## 3. Эквалайзер: три разные системы

| Система | Префикс ключей | Назначение |
|---|---|---|
| **DAP** (Dolby Audio Processing) | `g_audio__dolby_*`, `AUDIO_INFO_GET_TYPE_DAP_*` | Dolby-обработка: leveler, virtualizer, dialogue enhancer, DRC |
| **BBE EQ** | `g_audio__aud_bbe_eq_mode`, `APP_CFG_AUD_BBE_EQ_BAND_*` | **5-полосный эквалайзер для TV и AV отдельно** |
| **PEQ** (Parametric EQ) | `CFG_AUD_AUD_BBE_EQ_BAND` | параметрический, заводской |

### Ключевое открытие: BBE EQ разделён по источнику

```
APP_CFG_AUD_BBE_EQ_BAND_TV_1 … TV_5      ← для ТВ-тюнера
APP_CFG_AUD_BBE_EQ_BAND_AV_1 … AV_5      ← для AV-входов (HDMI!)
```

То есть **на каждый источник своя кривая эквалайзера**. Наш проектор — это AV-путь
(HDMI), значит должна применяться группа **AV**.

### И ещё: есть отдельные DAP-параметры

```
AUDIO_INFO_GET_TYPE_DAP_LEVELER
AUDIO_INFO_GET_TYPE_DAP_VIRTUALIZER
AUDIO_INFO_GET_TYPE_DAP_DE_ENABLE     dialogue enhancer
AUDIO_INFO_GET_TYPE_DAP_DE_AMOUNT
AUDIO_INFO_GET_TYPE_DAP_DE_DUCKING
AUDIO_INFO_GET_TYPE_DAP_DD_MUTEX_NEEDED
DAP_CONTENT_STRING
"atmosEnabled . dapValue="
```

Dolby DAP — это **отдельный DSP-процессор**, который может работать независимо от BBE EQ.
`atmosEnabled` в логе — значит, DAP может включать Dolby Atmos-обработку.

---

## 4. Почему EQ не действует на саундбар (ответ)

Три возможные причины, и они не исключают друг друга:

1. **`sound_speaker_status = BT_OUTPUT`** → OEM-логика отключает эквалайзер для BT-выхода.
2. **BBE EQ применяется к группе AV**, а при BT-выходе сигнал идёт мимо этой группы
   (в Android-путь, а не в MediaTek-путь).
3. **EQ работает только на встроенный DSP**, а BT-кодек (SBC/AAC) отправляет звук уже
   после DSP — либо до него.

Чтобы определить точную причину, нужен **эксперимент с чтением ключей**:
1. Включить саундбар.
2. Прочитать `sound_speaker_status`, `g_audio__aud_bbe_eq_mode`, `g_audio__aud_out_port`.
3. Переключить эквалайзер.
4. Прочитать снова — изменились ли ключи.

**Только по этому срезу можно сказать, ломается запись или применение.**

---

## 5. Одновременный вывод на два устройства

### Технически в Android

Android 13 поддерживает `AudioProductStrategy` + `setPreferredDevicesForStrategy`.
Но **одновременный вывод** на два устройства — это отдельный механизм:

- **`AudioDeviceInfo.TYPE_*** с несколькими устройствами в одном маршруте — AOSP это не поддерживает штатно.
- **Duplicated output** реализуется на уровне AudioPolicy, и на MTK-платформах часто
  настраивается через `audio_policy_configuration.xml` (`mixPort` с несколькими `devicePort`).

Смотрим, что в нашем `audio_policy`:

```
Sources: "primary output", "mmap_no_irq_out", "hw_av_sync output",
         "offload output", "Tv Tuner", "HDMI In", "Line In", "tv_monitor"
```

**`tv_monitor`** — интересное: это может быть monitor-выход (для записи/дублирования).

### Что есть в OEM

В `dumpsys` у стримов:

```
STREAM_MUSIC: Devices: speaker(2)
```

Одно устройство на стрим. Ни одного стрима с двумя устройствами.

### Реалистичная оценка

| Сценарий | Реализуемость | Как |
|---|---|---|
| Динамики + BT одновременно | **низкая** | нужен новый `mixPort` в audio_policy, правка `/vendor/etc` |
| BT + BT (два саундбара) | **очень низкая** | Android 13 не умеет dual A2DP без патча фреймворка |
| Динамики + HDMI | средняя | возможно через HDMI passthrough, но требует CEC/ARC |

**Честный вывод:** одновременный вывод на два устройства — **задача уровня кастомной прошивки
с правкой audio_policy**, а не настройка. Моя рекомендация — не обещать это, а сначала
сделать простое и полезное: **переключение выхода** (динамики ↔ саундбар) из нашего меню.

---

## 6. Что делать по приоритетам

### 6.1. Переключение выхода (сразу)

У нас в MOD уже был `NativeMediaRouteBridge` — но он не заработал (в прошлых тестах
`USAGE_MEDIA` оставался на BT). 

**Теперь понятно, почему:** мы пытались через Android `setPreferredDevicesForStrategy`,
а OEM-путь использует свой `AUD_OUTDEV_*` + `sound_speaker_status`.

**Правильный подход — два слоя:**

```
Наш UI: «Выход звука: Динамики / Саундбар»
   ↓
1. Android: setPreferredDevicesForStrategy(SPEAKER) / (BLUETOOTH_A2DP)
2. OEM:  g_audio__aud_out_port = AUD_OUTDEV_SPEAKER / AUD_OUTDEV_BLUETEETH
   ↓
проверка: dumpsys audio → Devices: (что реально играет)
   ⇄ сравнить с намерением
```

### 6.2. Эквалайзер на внешнем выходе

Сначала — **диагностика**: понять, ломается ли запись или применение.
Потом — решение: писать в `g_audio__aud_bbe_eq_mode` + группы `AV_n`, а не только `TV_n`.

### 6.3. Одновременный вывод

Отложить до этапа прошивки. Зафиксировать как «требует правки audio_policy».

---

## 7. Что нужно проверить на устройстве (когда включён)

```
1. settings get global sound_speaker_status
2. settings get global g_audio__aud_out_port
3. settings get global g_audio__aud_bbe_eq_mode
4. settings get global sound_equalizer_detail_120hz … 10000hz
5. settings get global sound_style
6. dumpsys audio | grep Devices:
7. dumpsys media.audio_flinger | grep "Output devices"
```

Повторить с саундбаром отключённым и подключённым, а также после смены эквалайзера.
Это даст ответ, работает ли запись и меняется ли маршрут.

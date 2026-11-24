# Результаты аппаратной проверки (2026-11-24)

Проектор: FlixTone D11 8054, контент: YouTube HDRezka / LoFi, звук: BT-саундбар Redmi TV Soundbar.

---

## 1. Эквалайзер на Bluetooth — РАБОТАЕТ ✅

**Уровень: `DEVICE_VERIFIED`**

```
EQ bandLevelRange = -1500..1500 mB (±15 dB)
numBands = 5
band0 = 60 Hz
band1 = 230 Hz
band2 = 910 Hz
band3 = 3600 Hz
band4 = 14000 Hz
```

Тест: розовый шум + бас +12 dB / высокие +12 dB на саундбаре.
**Владелец подтвердил: «да, эквалайзер работает с саундбаром, все изменения частот слышал отчётливо».**

**Следствие:** OEM-эквалайзер (`g_fusion_sound__*`) на BT не работает, но
`android.media.audiofx.Equalizer` — **работает на любом выходе**.

**Решение для MOD:** использовать `audiofx.Equalizer`, а не OEM-ключи.

### Профили по устройствам (задача владельца)

```
Настройки → Звук → Эквалайзер
  Устройство: [Динамики] [Soundbar] [Наушники]
  Кривая для выбранного (5 полос, ±15 dB)
```

Хранить значения в SharedPreferences, применять при смене выхода.

---

## 2. Переключение выхода через Android API — не работает ❌

```
reflect getAudioProductStrategies: java.lang.reflect.InvocationTargetException
strategyCount=0
```

**Причина:** `com.android.tv.settings` работает под `userId=1000` (системный).
Наш зонд — `userId=10058` (обычное приложение). Метод требует системных прав.

**Это и есть причина провала v41.** Не логика, не ключи — права.

**Решение:** MOD ставится как `com.android.tv.settings` с `sharedUserId="android.uid.system"`
→ UID 1000 → API заработает.

---

## 3. Управление динамиками через TrdSystemService — найден механизм 🔶

В `com.trd.framework` найдены:

```
AUDIO_SPEAKER_ON      динамики включены
AUDIO_SPEAKER_OFF     динамики выключены
AUDIO_SPEAKER_CEC     через CEC
метод: setBasicSoundEffect
```

**Потенциал:** управление встроенными динамиками **без UID 1000**.
Плюс `AUDIO_SPEAKER_ON` при активном BT = **одновременный вывод** (динамики + саундбар).

**Статус:** не проверено (ключ `g_audio__tv_speaker_status` через settings не сработал).
Нужен прямой вызов Binder-сервиса из кода.

---

## 4. Функции изображения — проверено

| Параметр | Результат | Уровень |
|---|---|---|
| Насыщенность | ✅ видно (ч/б при 0) | `DEVICE_VERIFIED` |
| Контраст | ✅ видно | `DEVICE_VERIFIED` |
| Яркость | ✅ видно | `DEVICE_VERIFIED` |
| Резкость | ✅ видно | `DEVICE_VERIFIED` |
| HDR | ✅ видно (серость при 0) | `DEVICE_VERIFIED` |
| AISR | ❌ не видно на приложениях | `NOT_WORKING_APP` |
| Live Tone | ❌ не видно на HDR в приложении | `NOT_WORKING_APP` |
| ALLM | ❌ ключ не влияет | `NEEDS_OTHER_TEST` |
| Local Dimming | — отменено (1 LED) | `NOT_APPLICABLE` |

**Важно:** параметры PQ применяются к **видеотракту MediaTek**, а не к Android-слою.
Поэтому на рабочем столе они не действуют — это нормально, не баг.

AISR и Live Tone нужно проверить на **HDMI-входе** (там чистая MediaTek-плоскость).

---

## 5. TVNativeWrapper(Emu) — это НЕ заглушка

Ранее я предполагал, что `Emu` в логе означает «эмуляция вместо реального вызова».
**Проверка показала обратное:** насыщенность, контраст, яркость, резкость реально меняют
картинку, хотя все они проходят через `TVNativeWrapper(Emu)`.

**Вывод:** `Emu` — внутренняя деталь обёртки, не признак неработающего кода.

---

## 6. Инструмент: ProjectorProbe APK

Собран и установлен. Репозиторий: `Projector-Soft`, ветка `probe/audio-eq-diagnostic`.

Команды:
```
adb shell am broadcast -n dev.projectorsoft.probe/.ProbeReceiver -a dev.projectorsoft.probe.CMD --es cmd status
... --es cmd tone_start / tone_stop
... --es cmd eq_on / eq_off / eq_bass / eq_treble / eq_flat / eq_info
... --es cmd out_speaker / out_bt / out_both
```

Собирается через GitHub Actions: `.github/workflows/build-projector-probe.yml`.

**Важные технические детали сборки:**
- `AudioProductStrategy` — скрытый API, компилируется только через рефлексию
- `resources.arsc` должен быть несжатым (`zip -0`)
- `zipalign -f -p 4` (без `-a`, его нет в build-tools 33)

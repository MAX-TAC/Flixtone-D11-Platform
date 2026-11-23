# Архитектура настроек 8054 (этап 1, часть 1)

Дата: 2026-11-23. Источник: 71 системный APK с устройства + DEX-строки + дампы `research/device-slices/2026-11-23/`.
Уровень всех утверждений ниже: **`STATIC_CONFIRMED`** (прочитано в DEX/манифесте), если не указано иное.

---

## 1. Главная находка: две цепочки записи настроек

Настройки проектора существуют в **двух независимых мирах**, и они связаны через один класс.

### Цепочка A — Android TV Settings (то, что видит пользователь)

```
com.android.tv.settings (TvSettingsPlus)
  PictureFragment / SoundFragment / partnercustomizer
    ↓ Settings.Global.putInt("picture_contrast", value)
    ↓
TVSettingConfig   ← ЖИВЁТ ВНУТРИ com.android.tv.settings
   (com.android.tv.settings.partnercustomizer.tvsettingservice.TVSettingConfig)
    ↓ setConifg("g_video__contrast", value)
    ↓
MtkTvConfigBase.setConfigValue(configId, value)
    ↓
TVNativeWrapper.setConfigValue_native(...)
    ↓
libcom_mediatek_twoworlds_tv_jni.so → драйвер
```

Ключевой факт: **`TVSettingConfig` — это не отдельный сервис, а класс внутри APK настроек.**
Значит, он уйдёт вместе с `TvSettingsPlus`, если тот заменить. И наоборот — наш MOD,
построенный на этом APK, имеет прямой доступ к этому классу.

### Цепочка B — MediaTek TV Services (параллельная)

```
com.mediatek.tv.service (TvServices)
  ├── TVMenuSettingsService$SettingObserver   — слушает Settings.Global
  ├── AudioCustomizedService$SettingObserver
  ├── CommonService$SettingObserver
  └── DolbyVisionService$SettingObserver
       ↓
       ЧИТАЕТ тот же Settings.Global и применяет те же ключи g_video__* / g_audio__*
       ↓ импортирует TVSettingConfig из com.android.tv.settings
```

Это **дублирующая обработка**. Оба процесса реагируют на одни и те же ключи.
Отсюда и проблемы, которые наблюдались ранее: рассинхронизация, «запись есть, эффекта нет»,
повторное применение после смены источника.

**Вывод для плана модернизации:** писать нужно в `Settings.Global` тем же ключом, что и сток,
и не пытаться обойти `TvServices` — он всё равно применит ключ по-своему. Наш UI должен
управлять **теми же ключами**, а не создавать свои.

---

## 2. Что немедленно означает эта находка для проекта

| Вопрос | Ответ на основе DEX |
|---|---|
| Можно ли написать свой экран PQ? | Да, если писать в те же `picture_*` + синхронизировать `g_video__*` |
| Нужен ли KuSettings для работы картинки? | **Нет.** KuSettings не встречается в цепочках PQ/звука |
| Зачем нужен KuSettings? | `MySetTimeService` → `KuSourceRJ.TimeService` (термо/вентилятор) |
| Кто владеет источником при старте? | `KuSourceRJ` — `persist.trd.source_id` |
| Кто владеет яркостью LED? | `KuSourceRJ` — `persist.bright.model` + broadcast `com.action.brightReceiver` |

То есть **KuSettings нужен только ради одного сервиса-сторожа**, а не ради UI. Это сильно
упрощает M2/M3: UI можно заменить полностью уже сейчас, а пакет удалять — только после
переноса `MySetTimeService`.

---

## 3. Разложение по владельцам состояний

### 3.1. Проектор (оптика, свет, геометрия)

| Параметр | Владелец | Механизм |
|---|---|---|
| Режим проекции (потолок/тыл) | `KuSourceRJ` + Factory | `persist.rjpj.projector.mode` |
| Яркость LED | `KuSourceRJ` | `persist.bright.model` + `com.action.brightReceiver` |
| Автофокус при включении | `KuSourceRJ` | `persist.rjpj.autofocus.poweron` |
| Автофокус при движении | `KuSourceRJ` | `persist.rjpj.autofocus.move` |
| Авто-трапеция при движении | `KuSourceRJ` | `persist.rjpj.autokeystone.move` |
| Обнаружение препятствий (ToF) | `KuSourceRJ` | `persist.rjpj.obstacle.avoidance` |
| ToF автофокус | `KuSourceRJ` | `persist.rjpj.tof.autofocus` |
| 4-угла / зум / трапеция | `com.rjpj.tcorrection` | Activity `FourCorner`, `DigitalZoom`, `HVKeystone` (все exported=true) |
| Автофокус (движок) | `com.hysd.screen` | только 1 сервис `VAF2S` + 1 Activity |

### 3.2. Источник и питание

| Параметр | Владелец | Механизм |
|---|---|---|
| Источник при включении | `KuSourceRJ` | `persist.trd.source_id` |
| Автовоспроизведение HDMI | `KuSourceRJ` | `persist.rjpj.hdmiplug.autoplay` |
| Кнопка Settings на пульте | `TvServices` | `HotKeyService` + `GlobalKeyReceiver` |
| Заставка / скринсейвер | `KuSourceRJ` | `com.action.screensaver` + `ScreensaverReceiver` |

### 3.3. Изображение и звук

| Параметр | Ключ `Settings.Global` | Кто применяет |
|---|---|---|
| Режим изображения | `picture_mode` | TvServices + TVSettingConfig |
| Яркость | `picture_brightness` | то же (`g_video__brightness`) |
| Контраст | `picture_contrast` | `g_video__contrast` |
| Насыщенность | `picture_saturation` | `g_video__vid_sat` |
| Резкость | `picture_sharpness` | `g_video__vid_shp` |
| Оттенок | `picture_hue` | `g_video__vid_hue` |
| Гамма | `picture_gamma` | `g_disp__disp_gamma` |
| RGB gain | `picture_red/green/blue_gain` | `g_video__clr_gain_r/g/b` |
| Цветовая температура | `picture_color_temperature` | `g_video__clr_temp` |
| HDR | `picture_list_hdr` | `g_video__vid_hdr` |
| MEMC | `picture_mjc*` | `g_video__vid_mjc_effect` |
| DNR (шумоподавление) | `tv_picture_advance_video_dnr` | подтверждённый ключ существует |
| Звуковой профиль | `sound_style` / `sound_advanced_sound_mode` | `g_audio__sound_mode` |
| Эквалайзер (5 полос) | `sound_equalizer_detail_*hz` | `g_audio__aud_bass/treble` |
| Цифровой выход | `sound_digital_output` / `sound_spdif_type` | `g_audio__spdif` |
| Задержка динамиков | `sound_speaker_delay` | `g_audio__speaker_delay` |
| eARC | `sound_earc` | `g_audio__aud_out_port` |

### 3.4. Что есть в системе, но не выведено в UI

Из 567 найденных ключей **большинство не имеет пользовательского интерфейса**. Найдены, например:

- `g_video__vid_3d_*` — целый блок 3D (14 ключей): `vid_3d_mode`, `vid_3d_to_2d`,
  `vid_3d_depth`, `vid_3d_fpr`, `vid_3d_lr_switch`, `vid_3d_osd_depth` и др.;
- `g_video__vid_allm_switch` — ALLM (Auto Low Latency, подтверждён `allmSupported=true` в `dumpsys display`);
- `g_video__vid_vrr_switch` — VRR (наличие **ключа** не означает поддержку панели);
- `g_video__dovi_user_switch`, `g_video__dovi_reset_pic_setting` — Dolby Vision user switch;
- `g_video__set_hdmi_edid_port1..port4` — EDID **по портам**, хотя на проекторе 2 порта;
- `g_video__vid_pic_hdr10_min_max`, `vid_pic_hlg_min_max` — калибровка HDR-яркости;
- `g_audio__karaoke_*` — караоке (гораздо больше, чем ожидаешь);
- `g_audio__dts_*` — полный блок DTS;
- `g_video__vid_pq_demo`, `vid_mjc_demo` — демонстрационные режимы разделённого экрана.

Это **кандидаты в «активацию скрытых функций»** (этап 5), но сначала нужна проверка,
реагирует ли на ключ железо.

---

## 4. Что это меняет в плане

1. **MOD должен писать те же ключи, что сток.** Свои ключи бесполезны — `TvServices` их не знает.
2. **`TVSettingConfig` внутри `TvSettingsPlus` — это и есть «backend»**, за который раньше
   не могли ухватиться. Он доступен напрямую из нашего кода, потому что мы работаем
   внутри того же APK.
3. **KuSettings перестаёт быть блокером UI.** Он нужен только ради `TimeService`.
   Это позволяет сделать M1 намного быстрее, чем планировалось.
4. **Скрытые функции проектора — не миф.** Ключи `3d`, `allm`, `vrr`, `dovi_*`, `edid_port` уже
   есть в системе; вопрос только в том, включено ли железо.

---

## 5. Чего пока не знаю (честно)

- Есть ли проверка `machine.id` внутри самого `TvServices` перед применением ключей.
- Обрабатывает ли `TVMenuSettingsService` ключи `g_video__*` напрямую или только через `TVSettingConfig`.
- Что реально делает `DolbyVisionService` с `g_video__dovi_user_switch`.
- Порядок инициализации: кто первый пишет `Settings.Global` при старте — Android или TvServices.
- Почему `HotKeyService` открывает `FloatMenuService`, а не наши настройки (это уже известно,
  но точное место вызова — нет).

Всё это — задачи следующей итерации, и почти всё решается чтением DEX и одним `dumpsys`.

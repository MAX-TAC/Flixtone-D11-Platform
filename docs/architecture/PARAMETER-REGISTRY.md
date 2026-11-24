# Реестр параметров для кастомного меню (сводный)

Дата: 2026-11-24. Источник: DEX всех системных APK + `dumpsys`.
Уровень: **`STATIC_CONFIRMED`** для наличия ключей, `DEVICE_VERIFIABLE` для значений.

Этот документ — ответ на требование владельца: «нужно знать все параметры, которые будем
добавлять в кастомное меню».

---

## A. Изображение

### A.1. Базовые PQ (уже работают)

| Параметр | Ключ | Группа MediaTek |
|---|---|---|
| Режим изображения | `picture_mode` | `g_video__picture_mode` |
| Яркость | `picture_brightness` | `g_video__brightness` |
| Контраст | `picture_contrast` | `g_video__contrast` |
| Насыщенность | `picture_saturation` | `g_video__vid_sat` |
| Резкость | `picture_sharpness` | `g_video__vid_shp` |
| Оттенок | `picture_hue` | `g_video__vid_hue` |
| Гамма | `picture_gamma` | `g_disp__disp_gamma` |
| Цветовая температура | `picture_color_temperature` | `g_video__clr_temp` |
| RGB gain | `picture_{red,green,blue}_gain` | `g_video__clr_gain_{r,g,b}` |
| RGB offset | `tv_picture_color_tune_offset` | `g_video__clr_offset_{r,g,b}` |
| Подсветка | `picture_backlight` | `g_disp__disp_back_light` |

### A.2. HDR / Dolby Vision

| Параметр | Ключ | Статус |
|---|---|---|
| HDR вкл/выкл | `picture_list_hdr` | работает |
| HDR для игр | `picture_hdr_game` | есть |
| **DV user switch** | `g_video__dovi_user_switch` | есть, дисплей не заявляет |
| **DV сброс картинки** | `g_video__dovi_reset_pic_setting` | есть |
| **DV Bright / Dark / Vivid / Game** | `APP_CFG_PIC_MODE_DOVI_*` | есть |
| **DV IQ** | `picture_mode_dovi_iq_*` | есть |
| **DV IQ + датчик света** | `VIDEOINFO_TYPE_DOVI_LIGHT_SENSE_DATA` | есть |
| **MEMC для DV** | `APP_CFG_MJC_DOVI` | есть |
| DV min/max калибровка | `g_video__vid_pic_fmm_dovi_min_max` | есть |
| HLG min/max | `g_video__vid_pic_hlg_min_max` | есть |
| HDR10 min/max | `g_video__vid_pic_hdr10_min_max` | есть |
| FMM + DV | `picture_mode_filmmaker_dovi_ref_entries` | есть |

### A.3. Обработка видео (скрытое)

| Параметр | Ключ | Что это |
|---|---|---|
| **ALLM** | `g_video__vid_allm_switch` | **работает**, `allmSupported=true` |
| MEMC | `tv_picture_advance_video_mjc_effect` | работает |
| MEMC demo | `picture_mjc_demo` | разделённый экран |
| **AISR** | `tv_picture_video_aisr` | AI Super Resolution |
| AISR уровень | `VIDEOINFO_TYPE_AISR_LEVEL` | уровень |
| **Local Dimming** | `tv_picture_video_local_dimming` | локальное затемнение |
| **Live Tone** | `tv_picture_video_live_tone` | тональная компрессия |
| **IMAX** | `g_video__vid_imax_auto_detect_switch` | IMAX Enhanced |
| DNR | `tv_picture_advance_video_dnr` | шумоподавление |
| MPEG NR | `g_video__vid_mpeg_nr` | блоки сжатия |
| Filmmaker Mode | `picture_film_maker_mode` | FMM |
| Adaptive Luma | `tv_picture_video_adaptive_luma_control` | адаптивная яркость |
| Black stretch | `g_video__vid_black_stretch` | растяжение чёрного |
| Super resolution | `g_video__vid_super_resolution` | апскейл |
| Game mode + MEMC | `g_video__vid_game_mode_with_memc_switch` | игровой режим |
| Формат HDMI | `picture_format` | overscan |
| EDID порты | `g_video__set_hdmi_edid_port1..4` | по портам |
| **VRR** | `g_video__vid_vrr_switch` | **только чтение сигнала** |

---

## B. Звук

### B.1. База

| Параметр | Ключ |
|---|---|
| Профиль звука | `sound_style` / `sound_advanced_sound_mode` |
| Эквалайзер (5 полос) | `sound_equalizer_detail_{120,500,1500,5000,10000}hz` |
| Bass / Treble | `sound_bass` / `sound_treble` |
| Баланс | `sound_balance` |
| Выход звука | `g_audio__aud_out_port` → `AUD_OUTDEV_SPEAKER/BLUETEETH/USB` |
| Статус динамика | `sound_speaker_status` → `OFF/BT_OUTPUT/ARC_CONNECTED` |
| Задержка динамиков | `sound_speaker_delay` |
| Задержка SPDIF | `sound_spdif_delay` |
| Цифровой выход | `sound_digital_output` / `sound_spdif_type` |
| LR swap | `sound_speaker_lr_swap` |

### B.2. Dolby Audio Processing (DAP)

| Параметр | Ключ |
|---|---|
| DAP вкл/выкл | `sound_advanced_dolby_ap` |
| **Atmos** | `g_audio__aud_dolby_atmos` + `avr_capability_ddp_atmos` |
| Atmos popup | `g_audio__aud_dolby_atmos_pop_msg_switch` |
| Dolby sound mode | `APP_CFG_DOLBY_AUD_SOUND_MODE_*` (MOVIE/MUSIC/NEWS/GAME/VOIP/AUTO/USER/NIGHT/OFF) |
| Dialogue enhancement | `APP_CFG_DOLBY_DIALOGUE_ENHANCEMENT_*` (OFF/LOW/MID/HIGH) |
| Volume leveler | `sound_advanced_volume_leveler` |
| Surround virtualizer | `sound_advanced_surround_virtualizer` |
| **DAP GEQ (13–20 полос)** | `E_MTK_FAPI_KEY_TYPE_DAP_BAND_GEQ_TARGET_0..19` |
| DAP IEQ | `E_MTK_FAPI_KEY_TYPE_DAP_BAND_IEQ_TARGET_*` |
| DAP Optimizer (поканально) | `DAP_BAND_OPTIMIZER_GAIN_{LEFT,RIGHT,CENTER,SURROUND,LFE}_*` |
| DAP Regulator | `DAP_BAND_REGULATOR_THRESHOLD_{LOW,HIGH}_*` |
| DAP версия | `eDolbyVersion` / `getEDolbyVersion` / `setEDolbyVersion` |

### B.3. DTS

| Параметр | Ключ |
|---|---|
| DTS вкл | `sound_dts_*` |
| DTS Studio Sound | `sound_dts_studio_enable` |
| DTS TruVolume | `sound_dts_studio_truevolume` |
| DTS Virtual:X | `sound_dts_virtual_x` |
| DTS DRC | `sound_dts_drc` |
| DTS Limiter | `sound_dts_limiter` |
| DTS Dialog Clarity | `sound_dts_dialogClarity` |
| DTS TBHDX | `sound_dts_tbhdx` |

---

## C. Проектор (оптика)

| Параметр | Ключ / API | Владелец |
|---|---|---|
| Координаты трапеции (4 угла) | `persist.display.keystone_{lt,rt,lb,rb}{x,y}` | `trd.framework` |
| Смещение оптики | `persist.sys.offset_{x,y,z}` | `trd.framework` |
| Автофокус при включении | `setAutoFocusBoot` / `persist.rjpj.autofocus.poweron` | KuSourceRJ |
| Автофокус при движении | `setAutoFocusMove` / `persist.rjpj.autofocus.move` | KuSourceRJ |
| Автотрапеция при включении | `setAutoKeystoneBoot` | trd.framework |
| Автотрапеция при движении | `setAutoKeystoneMove` / `persist.rjpj.autokeystone.move` | KuSourceRJ |
| Автотрапеция вверх-вниз | `setUpDownAutoKeystone` | trd.framework |
| Цифровой зум | `setScreenZoom` / `isZoomEnable` | trd.framework |
| Позиция мотора | `getMotorPosition` / `getMotorStep` | trd.framework |
| Сброс трапеции | `SetKeystoneReset` / `resetKeyStone` | trd.framework |
| Яркость LED | `persist.bright.model` + broadcast `com.action.brightReceiver` | KuSourceRJ |
| Режим проектора | `persist.rjpj.projector.mode` | KuSourceRJ |
| Обнаружение препятствий | `persist.rjpj.obstacle.avoidance` | KuSourceRJ |
| ToF автофокус | `persist.rjpj.tof.autofocus` | KuSourceRJ |

---

## D. Термо и вентиляторы

| Параметр | API |
|---|---|
| Температура AMB (воздух) | `getTemperatueAMB` |
| Температура LCD (панель) | `getTemperatueLCD` |
| Температура LED (источник) | `getTemperatueLED` |
| Температура CPU | `ReadCpuTemperature` |
| Состояние вентилятора | `TRD_MSG_TYPE_FAN_RUNOK` / `FAN_NORUN_WARNING` |
| Детектор вентилятора | `SetFanDec` → `/devices/platform/fandec` |
| Перегрев | `TRD_MSG_TYPE_TEMPERATURE_HIGH` |
| Термистор отсутствует | `TRD_MSG_TYPE_NTC_NONDETECT` |
| Значение NTC | `TRD_MW_EVT_TEMP_NTC_TEMPVALUE` / `_VOLVALUE` |

---

## E. HDMI / CEC / EDID

| Параметр | Ключ |
|---|---|
| HDMI CEC | `hdmi_cec_enabled` + `HdmiControlManager` |
| CEC версия | `hdmi_cec_version` |
| Power control | `power_control_mode` |
| ARC control | `HDMI_ARC_CONTROL_ENABLED` |
| eARC | `sound_earc` + `g_audio__earc_info_*` |
| Wake on one touch | `tv_wake_on_one_touch_play` |
| Standby on sleep | `tv_send_standby_on_sleep` |
| EDID порт 1..4 | `g_video__set_hdmi_edid_port{1..4}` |
| Autoplay HDMI | `persist.rjpj.hdmiplug.autoplay` |
| Источник при старте | `persist.trd.source_id` |

---

## F. Что скрыто в стоке и заслуживает вывода в меню

| Функция | Почему стоит | Риск |
|---|---|---|
| **ALLM** | работает, ноль усилий | нет |
| **IMAX Enhanced** | режим есть целиком | низкий |
| **AISR** | AI-апскейл, 3 параметра | средний (неизвестно качество) |
| **Local Dimming** | влияет на контраст | средний |
| **Live Tone** | тональная компрессия | низкий |
| **DV-режимы** | 4 режима + IQ | зависит от HWC |
| **DAP GEQ** | 13–20 полос, полноценный EQ | средний |
| **Atmos** | включается сам при eARC | нет |
| **Отдельный EQ по выходам** | задача владельца | средний |
| **Переключатель выхода** | задача владельца | средний |

---

## G. Что НЕ выводить

| Функция | Причина |
|---|---|
| 3D | нет нормального стерео, только анаглиф |
| Караоке | не нужна |
| EDID 4 порта | реально 2, не исправлять |
| VRR | только чтение сигнала, панель не поддерживает |
| DVB/спутник | нет тюнера |
| Aging / заводские тесты | производство |

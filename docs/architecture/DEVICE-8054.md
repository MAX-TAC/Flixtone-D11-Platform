# Устройство: FlixTone D11 Master (8054)

Срез: **2026-11-23**, ADB `192.168.31.99:5555`, только чтение.
Все строки таблиц — `DEVICE_VERIFIED`, если не указано иное.

---

## 1. Идентичность

| Параметр | Значение |
|---|---|
| Коммерческое имя | FlixTone D11 Master (семейство Everycom CineLux) |
| `ro.rjpj.machine.id` | `8054` |
| Build fingerprint | `MediaTek/mt5873_cd/mt5873:13/TP1A.220624.021.A1/eng.suhaix.20260905.031903:userdebug/test-keys` |
| Android / SDK | 13 / 33, security patch 2026-04-05 |
| Плата / SoC семейство | `mt5873_cd`, `ro.boot.hardware=mt9660`, ядро 5.15.189 |
| Тип сборки | `userdebug`, `test-keys`, присутствует `su`, SELinux **Permissive** |
| OTA-канал | `RUIOS.8054.1.0.0`, `https://www.szrjyun.com/ota/android/mt9660/8054/8054_ota.json` |
| Bootloader | разблокирован 2026-11-21: `device_state=unlocked`, `verifiedbootstate=orange`, `veritymode=enforcing` |
| Слот | `a` (successful); B не является рабочим fallback |

## 2. Дисплей

| Параметр | Значение |
|---|---|
| Панель | `persist.sys.paneltype=C500AFH011` |
| Режимы | `id=1` 3840×2160@50.000, `id=2` 3840×2160@60.000004 (активен) |
| base DisplayInfo | real 3840×2160, density 640 (320 dpi) |
| override DisplayInfo | real 1920×1080, density 320 (160 dpi) |
| логический слой | `mCurrentLayerStackRect = 1920×1080` → `mCurrentDisplayRect = 3840×2160` |
| HDR capabilities | `[2, 3]` = HDR10, HLG; `maxLuminance=500`, `maxAverageLuminance=500` |
| HWC Support | `hdr10=true`, `hlg=true`, `hdr10plus=false`, `dv=false`, `wideColorGamut=false`, `metadata=3` |
| ALLM | `allmSupported=true`, `gameContentTypeSupported=false` |
| UI refresh | `supportsFrameRateOverrideByContent=false`, `mRefreshRateChangeable=false` |

## 3. HDMI / CEC

| Параметр | Значение |
|---|---|
| Порты | `ro.rjpj.hdmi.ports=HW6:HDMI1,HW7:HDMI2`, `port.count=2` |
| TV input | `HDMIInputService/HW5, HW6, HW7, HW8` — 4 логических входа при 2 физических портах |
| CEC доступность | `mIsCecAvailable=false` при `hdmi_cec_enabled=1` |
| CEC настройки | `power_control_mode=to_tv_and_audio_system`, `system_audio_control=1`, `tv_wake_on_one_touch_play=1`, `tv_send_standby_on_sleep=1` |
| ARC | `arc:true` только у `port_id 2`; `mArcEstablished=false`; `mArcFeatureEnabled={1:false,2:true,3:false,4:false}` |
| Active source | `(invalid, invalid)` на момент среза |

## 4. Аудио

| Параметр | Значение |
|---|---|
| Выходы в политике | `Speaker` (port 2), `BT A2DP Out` (port 18), `HDMI Out`, `HDMI ARC`, `Spdif`, USB — jack-узлов в `/sys/class/switch/` нет |
| HAL | `hdmi arc mode: auto`, `hdmi tx mode: auto`, `spdif mode: auto`, `spdif delay: 0`, `HDMI audio codec: XPCM` |
| ARC capability | `dd:0, ddp:0(atmos:0), dts:0, aac:0, mat-truhd:0, dtshd:0` — ресивер не согласован |
| Global-ключи (срез) | `sound_style=0`, `sound_digital_output=7`, `sound_spdif_type=7`, `sound_spdif_delay=0`, `sound_speaker_delay=0`, `sound_equalizer=0`, `sound_advanced_sound_mode=8` |

## 5. Изображение (`Settings.Global`, срез)

`picture_mode=3`, `picture_brightness=50`, `picture_contrast=70`, `picture_saturation=60`,
`picture_sharpness=12`, `picture_hue=0`, `picture_gamma=3`, `picture_color_temperature=2`,
`picture_list_hdr=1`, `picture_backlight=40`, `picture_format=7`, `picture_als=0`.

## 6. Загруженные модули ядра (используется в HDR/HDCP/видеотракте)

`mik`, `kdrv_alg`, `kdrv_xc`, `kdrv_hdrvivid` (use-count 0), `xcker`, `hdcp2x`, `hdcp1x`,
`utpa2k`, `mdrv_gflip`, `pnl_cust`, `misck`, `iniparser`, `mtk_module_thermal`.

## 7. Термо

`cpu=45…52 °C`. `gpu`, `npu`, `skin`, `power_amplifier`, `battery` — `0.0` (датчики не отдают значения
через `thermalservice`; отдельный путь охлаждения разбирается в `docs/architecture/`).

## 8. Пользовательская конфигурация (зафиксировать перед любыми записями)

- HOME-лаунчер заменён владельцем на `ru.pro100tehnika.tvlauncher` (`/data/app`).
- `com.zeasn.launcher` присутствует в `/system/app`, но не является HOME.
- `android.settings.SETTINGS` → `com.my.settings.SettingActivity`.
- Bluetooth-саундбар подключён как A2DP (`08:EB:ED:58:7E:FE`).

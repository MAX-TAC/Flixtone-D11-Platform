# Что осталось в TvSettingsPlus после чистки

Собрано по манифесту `TvSettingsPlus-8054-2.23-MAINSETTINGS.apk` (versionCode 223).
Исходный заводской манифест объявлял **105** Activity, после чистки осталось **79**.
Удалено 26 — они перечислены в конце с причиной.

Пометки:
- **меню** — открывается из нашего меню (прямо или через фрагмент);
- **система** — вызывается системой/другими приложениями по стандартному Intent;
- **внутри** — открывается как переход внутри другого экрана;
- **резерв** — сейчас недоступно из UI, но нужно для работы чего-то другого.

---

## Об устройстве — 3

| Activity | Зачем |
|---|---|
| `about.AboutActivity` | Заводской экран «Об устройстве» (модель, версия, сборка, серийники). Используется как фрагмент внутри «Настройки системы». |
| `about.StatusActivity` | «Статус» — сеть, серийные номера, IP, MAC. |
| `about.LicenseActivity` | Юридическая информация и лицензии (требование Android). |

## Bluetooth и аксессуары — 5

| Activity | Зачем |
|---|---|
| `accessories.AddAccessoryActivity` | Подключение нового Bluetooth-пульта/аксессуара. **меню** (кнопка в Bluetooth). |
| `accessories.BluetoothAccessoryActivity` | Экран конкретного подключённого аксессуара. |
| `accessories.BluetoothActionActivity` | Диалог действия (забыть/переименовать) для аксессуара. |
| `accessories.BluetoothDevicePickerActivity` | Выбор Bluetooth-устройства из списка. |
| `accessories.BluetoothRequestPermissionActivity` | Запрос разрешения на сопряжение. |

## Учётные записи — 4

| Activity | Зачем |
|---|---|
| `accounts.AccountsActivity` | Заводской экран аккаунтов. Заменён нашим фрагментом, но остаётся для системных вызовов. |
| `accounts.AccountsTrampolineActivity` | Промежуточный экран, который система открывает по `ACTION_SYNC_SETTINGS`. **система** |
| `accounts.AccountSyncActivity` | Настройка синхронизации конкретного аккаунта. |
| `accounts.AddAccountWithTypeActivity` | Добавление аккаунта конкретного типа. **система** |

## Автозаполнение — 2

| Activity | Зачем |
|---|---|
| `autofill.AutofillPickerActivity` | Выбор сервиса автозаполнения. **система** (Android 8+). |
| `autofill.AutofillPickerTrampolineActivity` | Обёртка для того же вызова на старых API. |

## Wi-Fi и сеть — 7

| Activity | Зачем |
|---|---|
| `connectivity.NetworkActivity` | Заводской экран Wi-Fi. **меню** (Wi-Fi и сеть). |
| `connectivity.AddWifiNetworkActivity` | Добавление сети вручную (скрытая сеть). |
| `connectivity.WifiConnectionActivity` | Подключение к выбранной сети. |
| `connectivity.setup.WifiSetupActivity` | Мастер первичной настройки Wi-Fi. **система** (setup wizard). |
| `connectivity.EditIpSettingsActivity` | Ручной IP/DNS. |
| `connectivity.EditProxySettingsActivity` | Настройка прокси. |
| `connectivity.NetworkRequestDialogActivity` | Диалог запроса сети от приложения. **система** |

## Приложения — 11

| Activity | Зачем |
|---|---|
| `device.apps.AppsActivity` | Заводской список приложений. **меню** (Приложения). |
| `device.apps.AllAppsActivity` | Полный список (включая системные). |
| `device.apps.AppManagementActivity` | Карточка приложения: данные, кэш, удаление, разрешения. |
| `device.apps.ConfirmationActivity` | Подтверждение удаления/очистки. |
| `device.apps.MoveAppActivity` | Перенос приложения между хранилищами. |
| `device.apps.specialaccess.AlarmsAndRemindersActivity` | Доступ к точным будильникам. |
| `device.apps.specialaccess.AllFilesAccessActivity` | Доступ ко всем файлам. |
| `device.apps.specialaccess.AppUsageAccessActivity` | Доступ к статистике использования. |
| `device.apps.specialaccess.ExternalSourcesActivity` | Установка из неизвестных источников. |
| `device.apps.specialaccess.PictureInPictureActivity` | Разрешение «картинка в картинке». |
| `device.apps.specialaccess.SystemAlertActivity` | Разрешение на системные окна поверх других. |

## Экран и звук — 6

| Activity | Зачем |
|---|---|
| `device.sound.SoundActivity` | Заводской экран звука. **меню** (Звук). |
| `device.sound.AudioOutputActivity` | Выбор аудиовыхода. Сейчас не используется (переключение не работает на этой плате), но остаётся. |
| `device.displaysound.DisplaySoundActivity` | Объединённый экран «Экран и звук» (Android TV). **система** |
| `device.display.daydream.DaydreamActivity` | Заставка. **резерв** — заставка сейчас отключена, но экран нужен, если её включат. |
| `partnercustomizer.DisplayAndSoundActivity` | OEM-дубль «Экран и звук». |
| `partnercustomizer.EnergyCommonActivity` | OEM-энергосбережение/эко-режим. |

## Хранилище — 6

| Activity | Зачем |
|---|---|
| `device.StorageResetActivity` | «Хранилище» из «Настроек системы». Открывается фрагментом. |
| `device.storage.FormatActivity` | Форматирование USB/SD. |
| `device.storage.MigrateStorageActivity` | Перенос данных на новый носитель. |
| `device.storage.NewStorageActivity` | Настройка нового накопителя. |
| `device.storage.UnmountActivity` | Безопасное извлечение. |
| `device.storage.ResetActivity` | Сброс накопителя. |

## Клавиатура и ввод — 2

| Activity | Зачем |
|---|---|
| `inputmethod.KeyboardActivity` | Заводской экран клавиатуры. Заменён нашим фрагментом; остаётся как fallback. |
| `inputmethod.InputMethodAndSubtypeEnablerActivity` | Включение раскладок конкретной клавиатуры. **система** |

## Имя устройства — 3

| Activity | Зачем |
|---|---|
| `name.DeviceNameSettingsActivity` | Смена имени устройства (в «Об устройстве»). |
| `name.DeviceNameSuggestionActivity` | Подсказки имени. **система** |
| `name.setup.DeviceNameFlowStartActivity` | Шаг мастера настройки. **система** |

## OEM-ссылки — 5

| Activity | Зачем |
|---|---|
| `oemlink.AccessibilitySettingsActivity` | «Специальные возможности». Используется как фрагмент. |
| `oemlink.AccessibilityServiceActivity` | Экран конкретной службы доступности. |
| `oemlink.AccessibilityCaptionActivity` | Настройка субтитров. |
| `oemlink.NetworkSettingsActivity` | OEM-дубль сетевых настроек. |
| `oemlink.FactoryResetActivity` | Заводской сброс. **система** (вызывается по `ACTION_FACTORY_RESET`). |

## OEM — проектор и картинка — 14

| Activity | Зачем |
|---|---|
| `partnercustomizer.picture.PictureActivity` | Заводской экран изображения. **меню** (Изображение). |
| `partnercustomizer.picture.DisplayModeActivity` | Выбор режима изображения (кино/спорт/…). |
| `partnercustomizer.picture.PictureConfirmActivity` | Подтверждение сброса картинки. |
| `partnercustomizer.picture.PictureResetActivity` | Сброс настроек изображения. |
| `partnercustomizer.power.PowerActivity` | Заводской экран питания. **меню** (Питание). |
| `partnercustomizer.power.PictureOffActivity` | Выключение изображения (только звук). |
| `partnercustomizer.inputs.InputsActivity` | Заводской экран источников. |
| `partnercustomizer.date.DateTimeActivity` | Заводской экран даты/времени. |
| `partnercustomizer.sound.AudioResetActivity` | Сброс настроек звука. |
| `partnercustomizer.timer.TimerActivity` | Таймер сна/выключения. **меню** (`OemStockUserSettings`). |
| `partnercustomizer.timer.TimerSetActivity` | Установка таймера. |
| `partnercustomizer.timer.TimePickerActivity` | Выбор времени. |
| `partnercustomizer.multicast.NormalCastActivity` | Miracast-приём (беспроводной каст). |
| `uicustom.fragment.projector.KeystoneCalibrationActivity` | OEM-калибровка трапеции. **меню** (коррекция четырёх углов). |

## Приватность — 2

| Activity | Зачем |
|---|---|
| `privacy.NotificationAccessActivity` | Доступ к уведомлениям. **система** |
| `privacy.SensorToggleActivity` | Отключение датчиков (микрофон/камера). **система** |

## Системные — 10

| Activity | Зачем |
|---|---|
| `system.DateTimeActivity` | Дата и время. Открывается фрагментом. |
| `system.LanguageActivity` | Язык системы. Открывается фрагментом (в «Язык и ввод»). |
| `system.AppLanguageActivity` | Язык конкретного приложения (Android 13). **система** |
| `system.LocationActivity` | Местоположение. Фрагмент. |
| `system.SecurityActivity` | Безопасность. Фрагмент. |
| `system.development.DevelopmentActivity` | Для разработчиков. Фрагмент. |
| `system.TextToSpeechActivity` | Синтез речи (TTS). **система** |
| `system.CaptionSetupActivity` | Настройка субтитров. **система** |
| `system.InputsActivity` | Настройки входов Android TV (TV Input). **система** |
| `partnercustomizer.date.DateTimeActivity` | (см. выше, OEM-дубль) |

---

## Что удалено (26) и почему

| Категория | Кол-во | Причина |
|---|---|---|
| `partnercustomizer.vendor.channels.*` + `vendor.ResetActivity` | 5 | DVB/спутник — у 1LCD-проектора **нет тюнера** |
| `partnercustomizer.sound.wireless.*` | 8 | беспроводные колонки — вывод на спикеры отключён |
| `partnercustomizer.retailmode.*` | 2 | магазинный демо-режим |
| `slice.SliceActivity`, `accounts.AccountSliceActivity`, `accounts.ManageUserServicesSliceActivity`, `device.display.ambient.AmbientSliceActivity` | 4 | Android TV slices — в сборке нет ни одной slice-поверхности |
| `EmptyStubActivity`, `RemoteBugreportActivity`, `vendor.VendorActivity`, `enterprise.EnterprisePrivacySettingsActivity`, `partnercustomizer.utils.ProgressDialogActivity` | 5 | мёртвые экраны без входа |
| `uicustom.MainActivity`, `uicustom.floatmenu.MenuJumpActivity` | 2 | дубли OEM-меню, заменены нашим |

---

## Что это дало

- Манифест: **105 → 79** Activity.
- Ни одна удалённая Activity не имела входа ни из нашего меню, ни из системы.
- Манифест остаётся валидным (проверено `aapt2 dump xmltree`).
- Следующий шаг — вырезать DEX-классы этих 26 Activity (сейчас код лежит мёртвым грузом).
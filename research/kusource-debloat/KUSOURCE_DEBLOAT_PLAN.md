# План вырезки KuSourceRJ (`com.coolux.source`) — согласованный объём

Дата: 2026-11-26. Владелец: MAX-TAC. Статус: **согласовано**.

## Цель

Вырезать из APK `com.coolux.source` (58 460 781 Б, versionName 5.3, versionCode 41)
весь заводской мусор и дубли MOD, сохранив:
- термоконтроль (`TimeService` + вентиляторы + яркость),
- загрузочную логику (`BootupReceiver`, `BrightReceiver`, `ScreensaverReceiver`),
- пользовательские экраны: `BrightActivity`, `KeystoneActivity`, `ProjectModelActivity`,
  `HighTemperatureActivity`, `FanDetectionActivity`, `DustproofActivity`,
  `RestoreActivity`, `PoweronModeActivity`.

## Решения (подтверждены владельцем)

| Компонент | Решение |
|---|---|
| `testcast.*` (17 Activity) + `MyTestActivity` | удалить |
| `VoiceActivity` + `VoiceUtils` | удалить |
| `AllAppAutoActivity` + `AllAppAutoAdapter` + model `AppInfo` | удалить |
| `AutomaticAdmissionActivity` | удалить |
| `ClearTimeActivity` + `SetTimeActivity` | удалить |
| `MainActivity` (ярлык LAUNCHER) | удалить (Вариант A) |
| `BootSoureActivity` (+ `BootSoureActivityOld`) | удалить |
| `AuthorizationActivity` | удалить |
| DRM-цепочка в `TimeService`: `myHttp` / `isShield` / `authorizationIntent` | вычистить |
| `BootupReceiver.agingTest()` / `startAgingIntent()` | вычистить |

## Критичные НЕ трогать

- `TimeService` (термоконтроль, `START_NOT_STICKY`, перезапускается `BootupReceiver` → `UtilsTools.startTime()`)
- `BootupReceiver.onReceive` → `defaultInit` / `defaultBright` / `startTime` / `rebootStart`
- `BrightReceiver`, `ScreensaverReceiver`
- `ImageUtils.enterHdmi` (переключение источника — используется из IntentUtils)
- Все `SharedPreferencesTest` / `ImageUtils` / `MyTimeUtils` (хранилище состояния)

## Механика вырезки

1. **Манифест** — удалить `<activity>` для каждого вырезаемого компонента
   (иначе `apktool b` соберёт мёртвые ссылки).
2. **smali** — удалить соответствующие `.smali` файлы классов.
3. **`IntentUtils`** — вычистить методы-запускаторы удалённых экранов
   (`authorizationIntent`, `agingTest`, `prepareTest`, `dlpTest`, `audioVideoTest`,
   `interfaceTest`, `otherTest`, `printTest`, `rebootNumTest`, `projectModelTest`,
   `startAgingIntent`, `autoApp`, и пр.), оставив только рабочие.
4. **`TimeService`** — в `defaultData()` удалить вызов `myHttp()`; удалить
   метод `myHttp`, поле `socicalLogic`, вложенный класс `TimeService$13`.
5. **`BootupReceiver`** — в `onReceive` удалить вызов `agingTest()`; удалить
   метод `agingTest` и его поле `agingAuto`-логику (проверить `rebootStart`).
6. **`UtilsTools`** — если `isShield`/`shutDown` больше ничем не вызываются,
   оставить (не критично) либо пометить. Решение: `isShield` вычистить,
   `shutDown` оставить (нужен для `AuthorizationActivity` — но тот удаляем,
   значит `shutDown` тоже можно удалить, проверить ссылки).

## Сборка и подпись

- `apktool b --no-res` (ресурсы не пересобираются, байтовый репак).
- Подпись: `platform.pk8` + `platform.x509.pem` (публичный AOSP testkey,
  SHA-256 `c8a2e9bc…`), через `apksigner` build-tools 36.0.0.
- После установки — **полная перезагрузка** (служба поднимется с новым кодом).

## Ограничения среды

- Сеть из песочницы закрыта → ключи подписи нужно скачать вручную (см. задачу).
- erofs-tools (cygwin) не работают → для super.img используются Python-парсеры.
- `python3` — Store-заглушка, использовать `python`.

# trdservice — модернизация фокуса (4K) — статус и артефакт

Дата: 2026-11-27.

## Что сделано (готовый APK)

Модернизирован оверлей ручной фокусировки в `com.trd.service` (trdservice.apk):

| Изменение | Было | Стало |
|---|---|---|
| Размер окна | 46% шир × 75% выс (0.46/0.75) | **88% × 88%** (0.88/0.88) — почти весь экран |
| Layout | 350×350dp | `match_parent` |
| Фон `rj_focus_bg2` | 400×400 PNG (мыло) | **1254×1254** (4K 1:1, `rj_focus_bg2_4k_1to1.png`) |
| Вращение `rj_focus_in_out` | 400×400 PNG (мыло) | **2160×2160** (4K 1:1, `rj_focus_in_out_square.png`) |
| versionCode / Name | 33 / 13 | **34 / 14** |

**Механика вращения не менялась:** `RJFocusDialog` вращает `focus_in_out` вокруг центра
ImageView (`setPivotX/Y = width/2, height/2`), что корректно для квадратной картинки.

**Файлы правок:**
- `smali/com/trd/service/ui/RJFocusDialog.smali` — константы 0.46→0.88, 0.75→0.88
- `res/layout/rj_focus_dialog.xml` — 350dp→match_parent
- `res/drawable/rj_focus_bg2.png`, `res/drawable/rj_focus_in_out.png` — заменены

## Артефакт

- **`_analysis/trdservice-focus-4k-signed.apk`** (2.44 МБ)
- SHA-256: `6614E4F70B051DCF068D688BFAC932E1F09769710DB50F94D15CB6117CDD77B8`
- подпись platform `c8a2e9bc…` (совпадает)
- versionCode 34, versionName 14

## ⚠️ Блокировка установки

`com.trd.service` — **persistent** приложение (`android:persistent="true"`):
```
Failure [INSTALL_FAILED_INVALID_APK: Package com.trd.service is a persistent app. Persistent apps are not updateable.]
```
Установка поверх через `pm install` **невозможна** (та же причина, что у `com.coolux.source`).

## Задача на сборку кастома (ОБЯЗАТЕЛЬНО)

При пересборке super.img:
1. **Снять `persistent`** у `com.trd.service` и `com.coolux.source` (или убрать флаг `PERSISTENT`
   из системной записи), чтобы после установки кастома **не было блокировки будущих обновлений/фиксов**.
2. Вшить готовые APK: `trdservice-focus-4k-signed.apk` + `Protection-5.3-final.apk`.

## Для проверки (когда будет возможность)

После установки: открыть ручную фокусировку → оверлей должен быть ~88% экрана, резкий (4K),
фон-кольцо + вращающаяся метка — чёткие, не мыльные.

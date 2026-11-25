# Ревизия пяти репозиториев и план консолидации

Дата: 2026-11-25. Составлено по факту проверки локальных клонов.

---

## 1. Что есть сейчас

| # | Репозиторий | Размер | Файлов | Ветка | Назначение |
|---|---|---|---|---|---|
| 1 | `Flixtone-D11-Platform` | 2.6 МБ | 56 | `main` | **ГЛАВНЫЙ** — документация, ADR, исследования |
| 2 | `Projector-Soft` | 254.5 МБ | 586 | `mod/v41-bt-eq-gamemode` | Код MOD, вендорские APK-референсы, CI |
| 3 | `Everycom-Cinelux-Firmware` | 4.2 МБ | 116 | `main` | **Другой проектор** (Everycom/Cinelux) |
| 4 | `Firmware-CN-Projectors` | 0.8 МБ | 62 | `main` | Общая база по китайским проекторам (ET32) |
| 5 | `FlixTone_8054_Backup` | 0.1 МБ | 18 | `main` | Бэкап-скрипты, USB-обновление |

---

## 2. Диагноз беспорядка

### 2.1. Документация в одном месте, код в другом

- `Flixtone-D11-Platform` — все знания (ADR, архитектура, разборы APK)
- `Projector-Soft` — весь код и все сборки

Разорвано: чтобы понять, **как** собирается APK, надо идти в `Projector-Soft`.
Чтобы понять **почему** так — в `Flixtone-D11-Platform`.

### 2.2. Два набора исходников в одном репозитории

**Это главная причина, почему я трижды отдал не ту сборку.**

```
app/tvsettingsplus-mod/src/main/java/        82 файла   ← СТАРАЯ ветка
app/tvsettingsplus-mod/src/exact8054/java/   41 файл    ← v41, КАСТОМНЫЙ UI
```

Собираются **разными** workflow:

| Workflow | Исходники | Артефакт |
|---|---|---|
| `build-tvsettingsplus-inline-v33.yml` | `src/main/java/` | `v33-native-controls` |
| `build-tvsettingsplus-inline-v42-bt-eq.yml` | `src/main/java/` | `v33-native-controls` |
| **`build-tvsettingsplus-8054-audit.yml`** | **`src/exact8054/java/`** | **`v41-mainsettings`** ← **ТОТ, ЧТО НУЖЕН** |

**Правило на будущее:** кастомный интерфейс = `src/exact8054/java/` +
`build-tvsettingsplus-8054-audit.yml`. Остальные workflow — устаревшие.

### 2.3. Ветки внутри Projector-Soft

```
main                                  ← старая база
feature/8054-v41-picture-sound-safety-20261122   ← v41, рабочая
mod/v41-bt-eq-gamemode                ← мои правки (на базе v41)
mod/v17-bt-eq-gamemode                ← мёртвая (на базе main)
```

### 2.4. Три репозитория про другие устройства

`Everycom-Cinelux-Firmware`, `Firmware-CN-Projectors` — про другие проекторы.
`FlixTone_8054_Backup` — бэкап-утилиты.

---

## 3. Целевая структура: ОДИН репозиторий

**`Flixtone-D11-Platform`** становится единственным местом работы:

```
Flixtone-D11-Platform/
├── README.md                    ← точка входа
├── docs/                        ← ЗНАНИЯ (уже есть)
│   ├── decisions/               ADR
│   ├── architecture/            архитектура, реестр параметров
│   ├── features/                ARC, eARC, DV, keystone
│   ├── apps/                    разборы APK (TvSettingsPlus, KuSettings, KuSource)
│   ├── tasks/                   спеки и планы
│   └── setup/                   инструменты, окружение
├── app/                         ← КОД МОДА (перенести из Projector-Soft)
│   └── tvsettingsplus-mod/
│       ├── src/exact8054/java/  ← ЕДИНСТВЕННЫЙ набор исходников
│       ├── src/test/java/       JVM-тесты
│       └── src/exact8054/generated/  (генерируется в CI)
├── tools/                       ← скрипты сборки (перенести)
├── .github/workflows/           ← ОДИН build workflow
└── vendor/reference/            ← вендорские APK (через git-lfs или релиз)
```

### 3.1. Что делать с `Projector-Soft`

**Не удалять** — 254 МБ истории и вендорских APK. Но:

| Действие | Как |
|---|---|
| Код мода | **перенести** в `Flixtone-D11-Platform/app/` |
| Скрипты сборки | **перенести** в `Flixtone-D11-Platform/tools/` |
| Workflow | **перенести один** (`8054-audit.yml`) |
| Вендорские APK (254 МБ) | оставить, подключить `git-lfs` |
| Остальные workflow (~80 шт.) | **архивировать** (папка `_archive/workflows/`) |
| Статус репозитория | `Projector-Soft` → **архив (read-only)** |

### 3.2. Что делать с остальными

| Репозиторий | Действие | Причина |
|---|---|---|
| `Everycom-Cinelux-Firmware` | **архивировать** | другой проектор, не наш |
| `Firmware-CN-Projectors` | **архивировать** | другие устройства (ET32) |
| `FlixTone_8054_Backup` | **слить** в `Flixtone-D11-Platform/tools/backup/` | 18 файлов, наши утилиты |

---

## 4. Порядок работ

### Этап 1: зафиксировать правило сборки

1. В `README.md` — таблица «какой workflow что собирает».
2. Удалить/архивировать `v33` и `v42` workflow, оставить `8054-audit.yml`.
3. Удалить мёртвую ветку `mod/v17-bt-eq-gamemode`.

### Этап 2: перенести код

1. `app/tvsettingsplus-mod/src/exact8054/` → в `Flixtone-D11-Platform`.
2. `tools/*.py` → туда же.
3. `8054-audit.yml` → туда же.
4. Проверить сборку из нового репозитория.

### Этап 3: добавить мои функции в ПРАВИЛЬНЫЕ исходники

Сейчас мои хуки лежат в `src/main/java/` — **их надо перенести в `src/exact8054/java/`**:

| Хук | Куда подключить |
|---|---|
| `OemBtEqualizerHook` | `SoundSettingsActivity` / `NativeEqualizerPanel` |
| `OemAudioOutputHook` | `NativeMediaRouteBridge` / `SoundSettingsActivity` |
| `OemGameModeHook` | `SourcesSettingsActivity` |
| `OemPictureEnhanceHook` | `PictureSettingsActivity` |

### Этап 4: архивировать лишнее

1. `Projector-Soft` → archive в настройках GitHub.
2. Остальные три → archive.
3. Всё нужное живёт в `Flixtone-D11-Platform`.

---

## 5. Правило, чтобы больше не путаться

> **Один репозиторий. Один набор исходников. Один workflow.**
>
> Кастомный интерфейс — это `src/exact8054/java/`.
> Всё остальное — архив и не собирается.

---

## 6. Открытые вопросы к владельцу

1. **Вендорские APK 254 МБ** — оставить в Git (через git-lfs) или вынести в Release-ассеты?
2. **`FlixTone_8054_Backup`** — сливать в главный или оставить отдельно?
3. **Репозитории про другие проекторы** — архивировать или они ещё нужны?
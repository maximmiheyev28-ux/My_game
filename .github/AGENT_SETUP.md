# Автономная команда разработки

В репозитории подготовлены три GitHub Copilot custom agent-профиля:

- `.github/agents/pixel-art-director.agent.md` — художественное направление, оригинальный pixel art, анимации, противники и катсцены.
- `.github/agents/godot-engineer.agent.md` — Godot 4.7.2, игровые системы, Android, производительность и сборки.
- `.github/agents/qa-coordinator.agent.md` — независимый аудит, два QA-прохода, проверка ресурсов и релизная готовность.

Общие ограничения проекта находятся в `.github/copilot-instructions.md`. Профили созданы именно в формате `.agent.md`, который распознаётся GitHub Copilot как custom agents.

## Как запустить облачного агента

GitHub Copilot cloud agent требует доступной платной подписки Copilot и включённой функции cloud agent для аккаунта/репозитория. Наличие ChatGPT Plus/Free не включает и не заменяет GitHub Copilot.

1. Откройте [план производства — Issue #2](https://github.com/maximmiheyev28-ux/My_game/issues/2).
2. В правой панели GitHub выберите **Assignees → Copilot**. Если Copilot отсутствует в списке, сначала требуется включить/оформить Copilot и разрешить cloud agent в настройках GitHub.
3. Оставьте задачу в состоянии open. GitHub создаст агентную сессию и ожидаемый pull request.
4. В сессии можно выбрать один из профилей выше. Если runtime поддерживает делегирование, Copilot может использовать их как специализированные роли в рамках сессии.
5. Просматривайте pull request и CI. Не сливайте изменения, пока не проверены diff, результаты Godot import/export и APK.

## Автоматическая проверка

Workflow `.github/workflows/android-build.yml` теперь запускается для pull request в `main`, а также при изменениях исходников/ресурсов на `main`. Он восстанавливает проект, выполняет проверки и экспортирует Android ARM64 debug APK. Успешный CI не заменяет визуальную проверку и тест на реальном телефоне.

## Важное ограничение

Профили и CI настроены в репозитории, но они не запускают себя сами. Для фактической облачной сессии требуется включённый GitHub Copilot cloud agent и назначение задачи Copilot. Доступный GitHub-инструмент не предоставляет специальный параметр `agent_assignment` REST API: простое назначение login `copilot` было отклонено GitHub как недопустимое. Поэтому я не утверждаю, что сессия уже стартовала.

Первый объём работы ограничен аудитом исходной базы и одним отполированным вертикальным срезом. Затем агент должен открывать небольшие проверяемые PR, не пытаться искусственно увеличить APK и не объявлять готовыми непроверенные главы, катсцены или тесты устройства.

## Разделённые задачи команды (2026-11-06)

Работа разделена на независимые потоки, чтобы специалисты не перезаписывали одни и те же файлы:

- **Pixel Art Director:** [Issue #3](https://github.com/maximmiheyev28-ux/My_game/issues/3) — аудит визуала, спецификация/оригинальные ассеты vertical slice. Не меняет игровые скрипты.
- **Godot Engineer:** [Issue #4](https://github.com/maximmiheyev28-ux/My_game/issues/4) — технический аудит и ограниченный playable vertical slice. Не редактирует арт-пакет до согласования контракта.
- **QA Coordinator:** [Issue #5](https://github.com/maximmiheyev28-ux/My_game/issues/5) — read-only baseline-аудит и тест-план. Не меняет код и ресурсы.

Master roadmap: [Issue #2](https://github.com/maximmiheyev28-ux/My_game/issues/2).

### Фактический запуск
Создание Issues и наличие custom agent profiles не запускают сессии автоматически. Для каждого потока требуется открыть соответствующий Issue и выбрать **Assignees → Copilot** либо начать задачу в GitHub **Agents**, если эта функция включена в аккаунте. Доступный здесь GitHub API-инструмент не предоставляет операцию запуска Copilot cloud-agent сессии или назначения специального agent identity. Поэтому до появления сессии в GitHub Agents и PR статус каждого потока — **prepared, not running**.

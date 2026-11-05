#!/usr/bin/env python3
"""Apply the branch-aware narrative pass to the restored Godot source."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "scripts" / "game" / "game_state.gd"
OLD = """func chapter_data() -> Dictionary:
    return CHAPTERS[clampi(chapter_index, 0, CHAPTERS.size()-1)]"""
NEW = """func chapter_data() -> Dictionary:
    var data: Dictionary = CHAPTERS[clampi(chapter_index, 0, CHAPTERS.size()-1)].duplicate(true)
    var lines: Array = data.get("dialogue", [])
    match chapter_index:
        0:
            lines.append({"speaker":"СИСТЕМА", "text":"Архивная дата: 2091 год. Протокол «Тихий день» закрыт."})
            lines.append({"speaker":"НОЛЬ", "text":"Если протокол закрыт, почему город всё ещё подаёт сигнал бедствия?"})
        1:
            if int(flags.get("trust_mara", 0)) > 0:
                lines.append({"speaker":"МАРА", "text":"Я оставила тебе одну запись. Не потому, что ты мне доверился. Потому что ты мог отказаться."})
            else:
                lines.append({"speaker":"МАРА", "text":"Ты сохранил запись. Теперь знаешь: я вырезала из неё последние одиннадцать секунд."})
            lines.append({"speaker":"НОЛЬ", "text":"Что произошло за эти одиннадцать секунд?"})
        2:
            if int(flags.get("trust_lira", 0)) > 0:
                lines.append({"speaker":"ЛИРА", "text":"Ты вернулся. Я оставила для тебя открытым служебный канал. Не спрашивай, как долго он будет работать."})
            else:
                lines.append({"speaker":"ЛИРА", "text":"Ты ушёл тогда, и город стёр мой маршрут. Я не уверена, что сейчас говорю с тобой, а не с записью."})
            lines.append({"speaker":"НОЛЬ", "text":"Если ты запись, почему боишься тишины?"})
        3:
            if bool(flags.get("saved_names", false)):
                lines.append({"speaker":"АРХИВ", "text":"Список погибших восстановлен. Среди имён найдено имя руководителя первой смены."})
            else:
                lines.append({"speaker":"АРХИВ", "text":"Протокол эксперимента сохранён. В журнале подтверждён приказ закрыть ворота изнутри."})
            lines.append({"speaker":"НОЛЬ", "text":"Значит, кто-то знал, что люди останутся по ту сторону."})
        4:
            if bool(flags.get("spared_kair", false)):
                lines.append({"speaker":"КАЙР", "text":"Я оставил ключ там, где ты меня пощадил. Не называй это прощением. Это мой последний долг."})
            else:
                lines.append({"speaker":"СИСТЕМА", "text":"Боец Кайр исключён из активного списка. Его последняя запись сохранена в локальном буфере."})
                lines.append({"speaker":"КАЙР / ЗАПИСЬ", "text":"Приказ был твоим. Но палец на спуске был моим. Не снимай с меня эту вину."})
            lines.append({"speaker":"НОЛЬ", "text":"Я больше не хочу, чтобы чужой приказ решал, кем мне быть."})
        5:
            if bool(flags.get("accepted_echo", false)):
                lines.append({"speaker":"ЭХО", "text":"Теперь я помню за нас обоих. Но иногда я не могу отличить твоё воспоминание от своего."})
            else:
                lines.append({"speaker":"ЭХО", "text":"Ты оставил меня за дверью. Странно: впервые я слышу собственные мысли отдельно от твоих."})
            lines.append({"speaker":"НОЛЬ", "text":"Я не обязан быть оригиналом, чтобы отвечать за свои решения."})
    if chapter_index == 5 and memory_count >= 8:
        lines.append({"speaker":"АРХИВ", "text":"Обнаружен полный набор фрагментов. Восьмой сеанс не запускался: он уже проходил этот маршрут."})
    data["dialogue"] = lines
    return data"""

if not TARGET.is_file():
    raise SystemExit(f"Restored source file not found: {TARGET}")
source = TARGET.read_text(encoding="utf-8")
if 'var lines: Array = data.get("dialogue", [])' in source:
    print("Narrative pass already applied.")
elif OLD in source:
    TARGET.write_text(source.replace(OLD, NEW, 1), encoding="utf-8")
    print("Applied branch-aware dialogue to all six chapter intros.")
else:
    raise SystemExit("Narrative patch anchor not found; source layout changed.")

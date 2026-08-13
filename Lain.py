import re
import datetime
import os
import shutil

# Часовой пояс MSK (UTC+3)
MSK_OFFSET = datetime.timedelta(hours=3)

def get_moscow_time():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_msk = now_utc + MSK_OFFSET
    return now_msk.strftime("[%d %b %Y] [%H:%M:%S MSK]")

# Получаем путь к папке со скриптом
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "lines_data.txt")
BACKUP_FILE = os.path.join(SCRIPT_DIR, "lines_data_backup.txt")

# Загрузка или создание списка
lines = {}
last_time = ""

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        
        # Убираем заголовок если есть
        content = re.sub(r'^#[-]+\s*\n#\s*Lines\s*\n', '', content)
        content = re.sub(r'^#[-]+\s*\n', '', content)
        
        parts = content.split("\n\n")
        
        # Если есть время в конце
        if len(parts) > 1 and parts[-1].strip().startswith("["):
            last_time = parts[-1].strip()
            lines_content = parts[0]
        else:
            lines_content = content
        
        for line in lines_content.split("\n"):
            line = line.strip()
            if line and line.startswith("q"):
                parts_line = line.split(" - ", 1)
                if len(parts_line) == 2:
                    num = parts_line[0].replace("q", "")
                    lines[num] = line
else:
    # Создаём начальный файл с q1 - ! до q100 - !
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("#------------------\n")
        f.write("# Lines\n")
        f.write("#------------------\n")
        for i in range(1, 101):
            line = f"q{i} - !"
            lines[str(i)] = line
            f.write(line + "\n")
        f.write("\n" + get_moscow_time())

def save_to_file():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("#------------------\n")
        f.write("# Lines\n")
        f.write("#------------------\n")
        for i in range(1, 101):
            f.write(lines[str(i)] + "\n")
        if last_time:
            f.write("\n" + last_time)
        else:
            f.write("\n" + get_moscow_time())

def copy_last_list():
    """Копирует последний список в буфер обмена"""
    result = []
    result.append("#------------------")
    result.append("# Lines")
    result.append("#------------------")
    for i in range(1, 101):
        result.append(lines[str(i)])
    result.append("")
    if last_time:
        result.append(last_time)
    else:
        result.append(get_moscow_time())
    
    full_text = "\n".join(result)
    
    try:
        import pyperclip
        pyperclip.copy(full_text)
        print("Список скопирован в буфер обмена!")
    except ImportError:
        print("=" * 60)
        print("СКОПИРУЙТЕ ЭТОТ ТЕКСТ ВРУЧНУЮ (Ctrl+C):")
        print("=" * 60)
        print(full_text)
        print("=" * 60)
        print("Установите pyperclip для автоматического копирования: pip install pyperclip")
    
    return full_text

def show_all_lines():
    print("#------------------")
    print("# Lines")
    print("#------------------")
    for i in range(1, 101):
        print(lines[str(i)])
    print()
    if last_time:
        print(last_time)
    else:
        print(get_moscow_time())

def show_line(num):
    key = str(num)
    if key in lines:
        print(lines[key])
    else:
        print(f"Ошибка: q{num} не найдено")

def set_user_line(num, user):
    global last_time
    key = str(num)
    if 1 <= num <= 100:
        last_time = get_moscow_time()
        lines[key] = f"q{num} - {user}"
        save_to_file()
        print(f"Сохранено: {lines[key]}")
        print(last_time)
    else:
        print("Ошибка: номер должен быть от 1 до 100")

def remove_user_from_line(num):
    """Убирает ник из строки (ставит !)"""
    key = str(num)
    if 1 <= num <= 100:
        lines[key] = f"q{num} - !"
        save_to_file()
        print(f"Удалено: {lines[key]}")
    else:
        print("Ошибка: номер должен быть от 1 до 100")

def shift_lines():
    shutil.copy(DATA_FILE, BACKUP_FILE)
    
    new_lines = {}
    new_lines["1"] = "q1 - !"
    
    for i in range(2, 101):
        old_key = str(i)
        new_key = str(i - 1)
        if old_key in lines:
            old_line = lines[old_key]
            new_line = re.sub(r'^q\d+', f'q{new_key}', old_line)
            new_lines[new_key] = new_line
    
    for i in range(1, 101):
        key = str(i)
        if key in new_lines:
            lines[key] = new_lines[key]
        else:
            lines[key] = f"q{i} - !"
    
    save_to_file()
    print("Сдвиг выполнен! Все строки сдвинуты на 1 вниз.")

def shift_lines_up():
    shutil.copy(DATA_FILE, BACKUP_FILE)
    
    new_lines = {}
    
    for i in range(1, 100):
        old_key = str(i)
        new_key = str(i + 1)
        if old_key in lines:
            old_line = lines[old_key]
            new_line = re.sub(r'^q\d+', f'q{new_key}', old_line)
            new_lines[new_key] = old_line
    
    new_lines["100"] = "q100 - !"
    
    for i in range(1, 101):
        key = str(i)
        if key in new_lines:
            lines[key] = new_lines[key]
        else:
            lines[key] = f"q{i} - !"
    
    save_to_file()
    print("Сдвиг вверх выполнен! Все строки сдвинуты на 1 вверх.")

def show_info():
    print("=" * 60)
    print("ДОСТУПНЫЕ КОМАНДЫ:")
    print("=" * 60)
    print("  /<номер> <текст>     - записать сообщение в строку")
    print("                         Пример: /36 Salvador")
    print()
    print("  /-<номер>            - удалить ник из строки (поставить !)")
    print("                         Пример: /-36")
    print("                         Результат: q36 - !")
    print()
    print("  /<номер>             - показать содержимое строки")
    print("                         Пример: /36")
    print()
    print("  /copy                - скопировать весь список в буфер обмена")
    print()
    print("  /sdvig               - сдвинуть все строки на 1 вниз")
    print("                         q3 → q2, q4 → q3, ..., q100 → q99")
    print()
    print("  /sdvigup             - сдвинуть все строки на 1 вверх")
    print("                         q2 → q3, q3 → q4, ..., q99 → q100")
    print()
    print("  /list                - показать все строки")
    print()
    print("  /list <N>            - показать первые N строк")
    print()
    print("  /clear               - очистить все строки (qN - !)")
    print()
    print("  /time                - показать текущее время")
    print()
    print("  /info                - показать это сообщение")
    print()
    print("  /exit                - выход")
    print("=" * 60)

print("=" * 50)
print("Чат-логгер")
print("Введите /info для списка команд")
print("=" * 50)

# Показываем список при запуске
show_all_lines()

while True:
    command = input(">>> ").strip()
    
    if command == "/exit":
        save_to_file()
        print("Выход...")
        break
    
    if command == "/info":
        show_info()
        continue
    
    if command == "/copy":
        copy_last_list()
        continue
    
    if command == "/sdvig":
        shift_lines()
        continue
    
    if command == "/sdvigup":
        shift_lines_up()
        continue
    
    if command == "/time":
        print(get_moscow_time())
        continue
    
    if command == "/clear":
        for i in range(1, 101):
            lines[str(i)] = f"q{i} - !"
        save_to_file()
        print("Все строки очищены")
        continue
    
    if command == "/list":
        show_all_lines()
        continue
    
    # /list <N>
    match = re.match(r'^/list\s+(\d+)$', command)
    if match:
        count = int(match.group(1))
        if count > 100:
            count = 100
        for i in range(1, count + 1):
            print(lines[str(i)])
        continue
    
    # /-<номер> (удаление)
    match = re.match(r'^/-(\d+)$', command)
    if match:
        num = int(match.group(1))
        remove_user_from_line(num)
        continue
    
    # /<номер> <текст>
    match = re.match(r'^/(\d+)\s+(.+)$', command)
    if match:
        num = int(match.group(1))
        user = match.group(2)
        set_user_line(num, user)
        continue
    
    # /<номер>
    match = re.match(r'^/(\d+)$', command)
    if match:
        num = int(match.group(1))
        show_line(num)
        continue
    
    print("Неизвестная команда. Введите /info для списка команд")
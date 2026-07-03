import os
import shutil
import glob

# 1. Определяем папку, в которой лежит сам скрипт
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Создаем папку для результатов
output_dir = os.path.join(current_dir, "Собранные_Иконки")
os.makedirs(output_dir, exist_ok=True)

# 3. Ищем все файлы .png с @3x во всех подпапках рядом со скриптом
search_pattern = os.path.join(current_dir, "**", "*@3x*.png")
found_files = glob.glob(search_pattern, recursive=True)

copied_count = 0
unique_names = set()  # Множество для хранения чистых имён классов

# 4. Шаг первый: Собираем и очищаем картинки
for file_path in found_files:
    if "Собранные_Иконки" in file_path:
        continue
        
    file_name = os.path.basename(file_path)
    
    # Убираем суффикс @3x
    new_file_name = file_name.replace("@3x", "")
    destination_path = os.path.join(output_dir, new_file_name)
    
    # Запоминаем имя без расширения .png для будущего словаря
    name_without_ext = os.path.splitext(new_file_name)[0]
    unique_names.add(name_without_ext)
    
    try:
        shutil.copy2(file_path, destination_path)
        copied_count += 1
    except Exception as e:
        print(f"Ошибка копирования {file_name}: {e}")

# 5. Шаг второй: Генерируем новый словарь на основе реально созданных файлов
dict_file_path = os.path.join(current_dir, "new_dict.txt")

# Сортируем имена по алфавиту для красоты
sorted_names = sorted(list(unique_names))

# Считаем максимальную длину имени, чтобы выровнять пробелы в коде как у вас
max_len = max(len(name) for name in sorted_names) if sorted_names else 20

with open(dict_file_path, "w", encoding="utf-8") as f:
    f.write("CLASS_ICONS = {\n")
    for name in sorted_names:
        # Форматируем строку с красивыми отступами
        spaces = " " * (max_len - len(name))
        f.write(f"    '{name}':{spaces} '{name}.png',\n")
    f.write("}\n")

print(f"Успешно скопировано иконок: {copied_count}")
print(f"Все картинки без '@3x' сохранены в: {output_dir}")
print(f"Новый словарь Python успешно создан и записан в файл: {dict_file_path}")

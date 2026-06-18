#!/bin/bash
# Универсальный скрипт упаковки изменений из git-репозитория в zip-архив.
# Использование:
#   ./package_changes.sh                  # изменения относительно HEAD
#   ./package_changes.sh origin/master    # изменения относительно ветки
#   ./package_changes.sh v1.0.0           # изменения относительно тега

set -euo pipefail

# --- Настройки ---
REF="${1:-HEAD}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEFAULT_NAME="inventory_changes_${TIMESTAMP}.zip"
ARCHIVE_NAME="${2:-$DEFAULT_NAME}"

# --- Проверки ---
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Ошибка: скрипт должен запускаться внутри git-репозитория." >&2
    exit 1
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# --- Сбор файлов ---
# 1. Изменённые файлы (modified + staged) относительно REF
# 2. Новые (untracked) файлы, не в .gitignore
CHANGED_FILES=$(git diff --name-only "$REF" 2>/dev/null || true)
STAGED_FILES=$(git diff --cached --name-only "$REF" 2>/dev/null || true)
UNTRACKED_FILES=$(git ls-files -o --exclude-standard)

# Объединяем, удаляем дубликаты и пустые строки
ALL_FILES=$(printf '%s\n%s\n%s' "$CHANGED_FILES" "$STAGED_FILES" "$UNTRACKED_FILES" | sort -u | grep -v '^$')

if [ -z "$ALL_FILES" ]; then
    echo "Нет изменений относительно $REF — архив не создан."
    exit 0
fi

# --- Фильтрация существующих файлов ---
EXISTING_FILES=()
while IFS= read -r file; do
    if [ -f "$file" ]; then
        EXISTING_FILES+=("$file")
    else
        echo "  ⚠ Пропущен (удалён или не файл): $file"
    fi
done <<< "$ALL_FILES"

if [ ${#EXISTING_FILES[@]} -eq 0 ]; then
    echo "Нет существующих файлов для архивации."
    exit 0
fi

# --- Упаковка ---
rm -f "$ARCHIVE_NAME"
echo "Создание архива: $ARCHIVE_NAME"
echo "База сравнения: $REF"
echo "Файлов для архивации: ${#EXISTING_FILES[@]}"
echo ""

# zip принимает список файлов относительно текущей директории
printf '%s\n' "${EXISTING_FILES[@]}" | zip -@ "$ARCHIVE_NAME"

echo ""
echo "✅ Готово: $(pwd)/$ARCHIVE_NAME"
echo ""
echo "Содержимое архива:"
unzip -l "$ARCHIVE_NAME" | tail -n +4 | head -n -2

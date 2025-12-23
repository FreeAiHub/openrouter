#!/bin/bash
# Скрипт для загрузки на GitHub
# Автоматически создано Claude AI

set -e

echo "🚀 Загрузка OpenRouter Integration на GitHub"
echo "=============================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Проверка что мы в правильной директории
if [ ! -d ".git" ]; then
    echo -e "${RED}Ошибка: Запустите скрипт из директории проекта!${NC}"
    exit 1
fi

echo -e "${YELLOW}Репозиторий:${NC} https://github.com/FreeAiHub/openrouter.git"
echo -e "${YELLOW}Ветка:${NC} main"
echo ""

# Показываем что будет загружено
echo -e "${YELLOW}Файлы для загрузки:${NC}"
git status --short
echo ""

# Проверяем коммиты
COMMITS=$(git rev-list --count HEAD)
echo -e "${GREEN}✓${NC} Коммитов готово: $COMMITS"
echo ""

# Инструкции для пользователя
echo "=============================================="
echo "ВАЖНО: Для загрузки нужны права доступа к GitHub"
echo "=============================================="
echo ""
echo "Вариант 1: SSH ключ (рекомендуется)"
echo "  1. Создайте SSH ключ: ssh-keygen -t ed25519"
echo "  2. Добавьте на GitHub: Settings > SSH Keys"
echo "  3. git remote set-url origin git@github.com:FreeAiHub/openrouter.git"
echo ""
echo "Вариант 2: Personal Access Token"
echo "  1. Создайте токен: github.com/settings/tokens"
echo "  2. При git push используйте токен вместо пароля"
echo ""
echo "=============================================="
echo ""

# Спрашиваем готовность
read -p "Готовы загрузить на GitHub? (y/n) " -n 1 -r
echo
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Загружаем на GitHub...${NC}"
    echo ""
    
    # Пробуем push
    if git push -u origin main; then
        echo ""
        echo "=============================================="
        echo -e "${GREEN}✅ УСПЕШНО ЗАГРУЖЕНО!${NC}"
        echo "=============================================="
        echo ""
        echo "Проверьте: https://github.com/FreeAiHub/openrouter"
        echo ""
        echo "Следующие шаги:"
        echo "1. Откройте репозиторий на GitHub"
        echo "2. Проверьте что все файлы загружены"
        echo "3. Actions должны автоматически запуститься"
        echo "4. Отправьте Manus ссылку и файл MANUS_README.md"
        echo ""
    else
        echo ""
        echo "=============================================="
        echo -e "${RED}Ошибка при загрузке${NC}"
        echo "=============================================="
        echo ""
        echo "Возможные причины:"
        echo "1. Нет прав доступа к репозиторию"
        echo "2. Неправильная аутентификация"
        echo "3. Репозиторий уже содержит файлы"
        echo ""
        echo "Решения:"
        echo "1. Настройте SSH ключ (см. выше)"
        echo "2. Используйте Personal Access Token"
        echo "3. Или выполните вручную: git push -u origin main"
        echo ""
    fi
else
    echo ""
    echo "Отменено. Когда будете готовы, выполните:"
    echo "  git push -u origin main"
    echo ""
fi

import os
import sys

# Убедитесь, что вы находитесь в директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортировать настройки проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')

import django

django.setup()

from django.contrib.auth.models import User


def create_users():
    for i in range(4, 102):
        username = str(i)
        password = "Qwerty4321"

        # Создать пользователя
        user = User.objects.create_user(
            username=username,
            password=password
        )

        print(f"Пользователь {username} создан")


if __name__ == "__main__":
    create_users()

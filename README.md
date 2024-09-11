# Домашний проект Django REST Framework

## Описание

Этот проект использует Django REST Framework (DRF) для создания API с аутентификацией, разрешениями и троттлингом. Основная цель проекта — предоставить API для управления объявлениями, которые могут быть созданы и изменены пользователями.

## Установленные зависимости

Проект использует следующие пакеты:

- `rest_framework` — основной пакет для создания API в Django.
- `rest_framework.authtoken` — поддержка аутентификации через токены.
- `rest_framework_simplejwt` — поддержка аутентификации через JWT (JSON Web Tokens).
- `app_splitting_access` — пользовательское приложение с моделями, сериализаторами и представлениями.

## Конфигурация DRF

В настройках Django (`settings.py`) установлены следующие параметры для DRF:

- **Аутентификация**:
  ```python
  'DEFAULT_AUTHENTICATION_CLASSES': [
      'rest_framework.authentication.TokenAuthentication',
      'rest_framework.authentication.SessionAuthentication',
      'rest_framework.authentication.BasicAuthentication',
      'rest_framework_simplejwt.authentication.JWTAuthentication',
  ]
  ```
  Поддерживаются различные методы аутентификации, включая токены, сессии, базовую аутентификацию и JWT.

- **Разрешения**:
  ```python
  'DEFAULT_PERMISSION_CLASSES': [
      'rest_framework.permissions.IsAuthenticated',
  ]
  ```
  Доступ к API разрешен только аутентифицированным пользователям.

- **Троттлинг (ограничение количества запросов)**:
  ```python
  'DEFAULT_THROTTLE_CLASSES': [
      'rest_framework.throttling.UserRateThrottle',
      'rest_framework.throttling.AnonRateThrottle'
  ]
  'DEFAULT_THROTTLE_RATES': {
      'user': '10/minute',
      'anon': '2/minute'
  }
  ```
  Для аутентифицированных пользователей установлен лимит 10 запросов в минуту, а для неаутентифицированных пользователей — 2 запроса в минуту.

## Модели

**`Adv`** — модель для хранения объявлений.

- **`user`**: связь с моделью `User`, указывающая на владельца объявления.
- **`text`**: текст объявления.
- **`created_at`**: дата и время создания объявления.
- **`open`**: статус объявления (открыто/закрыто).

```python
from django.contrib.auth.models import User
from django.db import models

class Adv(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    open = models.BooleanField(default=True)
```

## Разрешения

**`IsOwnerOrReadOnly`** — пользовательское разрешение, позволяющее пользователю редактировать только свои объявления.

```python
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user == obj.user
```

## Сериализаторы

- **`UserSerializer`** — сериализатор для модели `User`.

- **`AdvSerializer`** — сериализатор для модели `Adv`. Включает поле `user` для отображения пользователя-владельца объявления.

```python
from rest_framework import serializers
from app_splitting_access.models import Adv
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class AdvSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Adv
        fields = ['id', 'user', 'text', 'created_at', 'open']
        read_only_fields = ['user',]
```

## Представления

**`AdvViewSet`** — представление для управления объявлениями. Использует `AdvSerializer` и применяет разрешения и троттлинг.

```python
from rest_framework.viewsets import ModelViewSet
from app_splitting_access.models import Adv
from app_splitting_access.permissions import IsOwnerOrReadOnly
from app_splitting_access.serializers import AdvSerializer
from rest_framework.throttling import AnonRateThrottle

class AdvViewSet(ModelViewSet):
    queryset = Adv.objects.all()
    serializer_class = AdvSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    throttle_classes = [AnonRateThrottle]

    def perform_create(self, serializer):
        user_name = self.request.user.username
        text = serializer.validated_data['text']
        text_with_user = text.replace('{{ user }}', user_name)
        serializer.save(user=self.request.user, text=text_with_user)
```

## Как запустить проект

1. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

2. Выполните миграции:

    ```bash
    python manage.py migrate
    ```

3. Запустите сервер разработки:

    ```bash
    python manage.py runserver
    ```

Теперь ваш проект будет доступен по адресу `http://localhost:8000/`.
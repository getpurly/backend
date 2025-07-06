from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

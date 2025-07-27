from django.apps import AppConfig


class AddressConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "purly.address"
    verbose_name = "Address Management"

    # def ready(self):
    #     import address.signals

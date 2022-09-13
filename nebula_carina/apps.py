try:
    from django.apps import AppConfig
    from django.utils.translation import gettext_lazy as _


    class NebulaCarinaConfig(AppConfig):
        name = "nebula_carina"
        label = "nebula_carina"

        verbose_name = _("Nebula Carina")

except ModuleNotFoundError:
    pass

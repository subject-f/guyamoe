from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class ReaderConfig(AppConfig):
    name = 'reader'
    verbose_name = _('reader')

    def ready(self):
        import reader.signals  # noqa
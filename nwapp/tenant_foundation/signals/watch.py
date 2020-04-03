from django.db.models.signals import post_save
from django.dispatch import receiver

from tenant_foundation.models import Watch, UnifiedSearchItem


@receiver(post_save, sender=Watch)
def save_watch(sender, instance, **kwargs):
    """
    Function will either update or create the `UnifiedSearchItem` object so
    we have a unified searchable record for all our data.
    """
    print("SIGNAL: save_watch") # For debugging purposes only.
    UnifiedSearchItem.objects.update_or_create_watch(instance)


@receiver(post_save, sender=Watch)
def invalidate_watch_cache(sender, instance, **kwargs):
    """
    Clear the watch's cache post save.
    """
    print("SIGNAL: invalidate_watch_cache") # For debugging purposes only.
    instance.invalidate_all()

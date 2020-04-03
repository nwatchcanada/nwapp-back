from django.db.models.signals import post_save
from django.dispatch import receiver

from tenant_foundation.models import AreaCoordinator, UnifiedSearchItem


@receiver(post_save, sender=AreaCoordinator)
def save_area_coordinator(sender, instance, **kwargs):
    """
    Function will either update or create the `UnifiedSearchItem` object so
    we have a unified searchable record for all our data.
    """
    print("SIGNAL: save_area_coordinator") # For debugging purposes only.
    UnifiedSearchItem.objects.update_or_create_area_coordinator(instance)


@receiver(post_save, sender=AreaCoordinator)
def invalidate_area_coordinator_cache(sender, instance, **kwargs):
    """
    Clear the area_coordinator's cache post save.
    """
    print("SIGNAL: invalidate_area_coordinator_cache") # For debugging purposes only.
    instance.invalidate_all()

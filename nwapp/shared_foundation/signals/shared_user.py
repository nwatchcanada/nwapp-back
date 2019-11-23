from django.db.models.signals import post_save
from django.dispatch import receiver

from shared_foundation.models import SharedUser


@receiver(post_save, sender=SharedUser)
def invalidate_shared_user_cache(sender, instance, **kwargs):
    """
    Clear the shared user's cache post save.
    """
    instance.invalidate_all()

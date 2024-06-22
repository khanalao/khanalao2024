from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import UserProfile, User


# post save signal
@receiver(post_save, sender=User)
def create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            UserProfile.objects.create(user=instance)


# post_save.connect(create_profile_receiver(sender=User))
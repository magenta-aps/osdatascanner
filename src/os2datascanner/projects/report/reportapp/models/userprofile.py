from PIL import Image

from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.projects.report.organizations.models import Organization, Alias


class UserProfile(models.Model):

    organization = models.ForeignKey(Organization,
                                     null=True, blank=True,
                                     verbose_name='Organisation',
                                     on_delete=models.PROTECT)
    user = models.OneToOneField(User,
                                related_name='profile',
                                verbose_name='Bruger',
                                on_delete=models.PROTECT)
    last_handle = models.DateTimeField(verbose_name='Sidste håndtering',
                                       null=True, blank=True)
    _image = models.ImageField(upload_to="media/images/",
                               default=None, null=True, blank=True, verbose_name=_('image'))

    delegate_all_to = models.ForeignKey(
        Alias,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name=_('Delegate all matches to'),
        related_name='delegate_all_from')

    delegate_all_message = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Delegation message'))

    def __str__(self):
        """Return the user's username."""
        return self.user.username

    def update_last_handle(self):
        self.last_handle = time_now()
        self.save()

    @property
    def time_since_last_handle(self):
        return (time_now() - self.last_handle).total_seconds() if self.last_handle else 60*60*24*3

    @property
    def image(self):
        return self._image.url if self._image else None


@receiver(post_save, sender=UserProfile)
def resize_image(sender, **kwargs):
    size = (300, 300)
    try:
        with Image.open(kwargs["instance"]._image.path) as image:
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(kwargs["instance"]._image.path, optimize=True)
    except ValueError as e:
        print(e)

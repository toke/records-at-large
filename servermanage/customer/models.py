from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.ForeignKey(User, unique=True)
    company = models.CharField(maxlength=150, blank=True, verbose_name="Company")
    street = models.CharField(maxlength=255, blank=False, verbose_name="Street")
    street_add = models.CharField(maxlength=255, blank=True, verbose_name="Street additional")
    area_code = models.CharField(maxlength=10, verbose_name="Area Code", blank=False)
    city = models.CharField(maxlength=150, blank=False)
    country = models.CharField(maxlength=150, blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)

    class Admin:
        list_filter   = ('area_code', 'country')
        search_fields = ('user',)

    def __str__(self):
        return '%s (%s)' % (self.company, self.user)


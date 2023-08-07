from __future__ import unicode_literals
import datetime
import uuid
# For the arrivals
from django.utils import timezone, dateformat

# For the guest code
import secrets

from django.db import models
from django.dispatch import receiver

def _random_uuid():
    return uuid.uuid4().hex

def generate_code():
    # You can choose whatever range you like, just make sure it's big enough for your guest list.
    for i in range (1, 128):
        code_value = str(secrets.randbits(21))
    return code_value


class Party(models.Model):

    class Meta:
        verbose_name_plural = "Parties"
    """
    A party consists of one or more guests.
    """
    name = models.TextField()
    # I use category to identify the bride and groom sides of the guest list. Check forms.py in guests. 
    category = models.CharField(max_length=20, null=True, blank=True)
    save_the_date_sent = models.DateTimeField(null=True, blank=True, default=None)
    save_the_date_opened = models.DateTimeField(null=True, blank=True, default=None)
    invitation_id = models.CharField(max_length=32, db_index=True, default=_random_uuid, unique=True)
    invitation_sent = models.DateTimeField(null=True, blank=True, default=None)
    invitation_opened = models.DateTimeField(null=True, blank=True, default=None)
    # The old default was False here, but why is anyone on your guest list who isn't invited?
    is_invited = models.BooleanField(default=True)
    rehearsal_dinner = models.BooleanField(default=False)
    is_attending = models.BooleanField(null=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return 'Party: {}'.format(self.name)

    @classmethod
    def in_default_order(cls):
        return cls.objects.order_by('category', '-is_invited', 'name')

    @property
    def ordered_guests(self):
        return self.guest_set.order_by('is_child', 'pk')

    @property
    def any_guests_attending(self):
        return any(self.guest_set.values_list('is_attending', flat=True))

    @property
    def guest_emails(self):
        return list(filter(None, self.guest_set.values_list('email', flat=True)))


MEALS = [
    ('beef', 'braised beef shortrib'),
    ('fish', 'salmon'),
    ('vegan', 'vegan'),
]


class Guest(models.Model):
    """
    A single guest
    """
    party_name = models.ForeignKey('Party', on_delete=models.CASCADE)    # Keeping the variable name the same as the model created errors
    first_name = models.TextField()
    last_name = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    is_attending = models.BooleanField(null=True)
    meal = models.CharField(max_length=20, choices=MEALS, null=True, blank=True)
    is_child = models.BooleanField(default=False)

    # We rented a place called Caboose Farm for our guests. Please rename it if you want and remember to makemigrations. 
    caboose_farm = models.BooleanField(default = None, null=True, blank=True)          
    # We had guests arriving from all over the world. Having their arrival dates was helpful.           
    arrival_date = models.DateField(blank = True, auto_now = False, auto_now_add = False)
    # For security purposes, every guest gets a numerical code
    guest_code = models.PositiveIntegerField(default = generate_code, null = False, blank = False)

    @property
    def name(self):
        return u'{} {}'.format(self.first_name, self.last_name)

    @property
    def unique_id(self):
        # convert to string so it can be used in the "add" templatetag
        return str(self.pk)

    def __str__(self):
        return 'Guest: {} {}'.format(self.first_name, self.last_name)

    # For Caboose Farm date check. Follow up with anyone who entered a date outside the Caboose Farm range. Call these methods in the dashboard view. 
    def is_too_early(self):
        caboose_date_check = datetime.date(2122, 6, 16)
        if self.arrival_date < caboose_date_check:
            return True
        else:
            return False

    def is_too_late(self):
        caboose_date_check = datetime.date(2122, 6, 18)
        if self.arrival_date > caboose_date_check:
            return True
        else:
            return False

class UploadedGuestList(models.Model):
    guest_list_file = models.FileField(upload_to='guest-list/%Y/%m/%d')  # this is where uploaded guest list CSVs get saved.

    class Meta:
        verbose_name = "Guest List CSV"

    def __str__(self):
        return str(self.guest_list_file)
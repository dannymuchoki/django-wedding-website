from django.contrib import admin
from .models import Guest, Party, UploadedGuestList


# Register your models here.
admin.site.site_header = "Wedding Day Admin"
admin.site.site_title = "Wedding Day Admin Portal"
admin.site.index_title = "Welcome to the Wedding Day Admin Portal"


class GuestInline(admin.TabularInline):
    model = Guest
    fields = ('first_name', 'last_name', 'email', 'is_attending', 'meal', 'is_child', 'caboose_farm', 'arrival_date')
    readonly_fields = ('first_name', 'last_name', 'email')


class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'save_the_date_sent', 'invitation_sent', 'rehearsal_dinner', 'invitation_opened',
                    'is_invited', 'is_attending')
    list_filter = ('category', 'is_invited', 'is_attending', 'rehearsal_dinner', 'invitation_opened')
    inlines = [GuestInline]


class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'party_name', 'email', 'is_attending', 'is_child', 'meal', 'caboose_farm', 'arrival_date')
    list_filter = ('is_attending', 'is_child', 'meal', 'party_name__is_invited', 'party_name__category', 'party_name__rehearsal_dinner','caboose_farm')


admin.site.register(Party, PartyAdmin)
admin.site.register(Guest, GuestAdmin)
admin.site.register(UploadedGuestList)

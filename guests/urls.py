from django.conf.urls import url
from django.urls import path
from guests import views

from guests.views import (guest_list_view, test_email, save_the_date_preview, save_the_date_random, export_guests, 
invitation, confirmation, invitation_email_preview, invitation_email_test, rsvp_confirm, dashboard, add_guest_view, UploadGuestListView, send_all_invitations, rsvp_forgot, download_csv, manage_invitations_view, wipe_guests)

urlpatterns = [
    url(r'^dashboard/$', dashboard, name='dashboard'),
    url(r'^dashboard/guest-list/$', guest_list_view, name='guest-list'),
    url(r'^dashboard/add-guest/$',  add_guest_view, name='add-guest-view'),
    url(r'^dashboard/upload/$',  UploadGuestListView.as_view(), name='upload-csv'),
    url(r'^dashboard/manage-invites/$', manage_invitations_view, name='manage-invitations'),
    url(r'^guests/export$', export_guests, name='export-guest-list'),
    url(r'^invite/(?P<invite_id>[\w-]+)/$', invitation, name='invitation'),
    # Added a confirmation. Basically the invite but read-only
    url(r'^confirmation/(?P<invite_id>[\w-]+)/$', confirmation, name='confirmation'),
    # guest-invite is purely experimental. It was my way of understanding this project.
    # url(r'^guest-invite/(?P<guest_code>[\w-]+)/$', guest_invite, name='guest-invite'),
    url(r'^invite-email/(?P<invite_id>[\w-]+)/$', invitation_email_preview, name='invitation-email'),
    url(r'^invite-email-test/(?P<invite_id>[\w-]+)', invitation_email_test, name='invitation-email-test'),
    #url(r'^invite-email-test/(?P<invite_id>[\w-]+)/(?P<guest_code>[\w-]+)', invitation_email_test, name='invitation-email-test'),
    url(r'^invite-all/', send_all_invitations, name='send-all-invitations'),
    url(r'^save-the-date/$', save_the_date_random, name='save-the-date-random'),
    url(r'^save-the-date/(?P<template_id>[\w-]+)/$', save_the_date_preview, name='save-the-date'),
    url(r'^email-test/(?P<template_id>[\w-]+)/$', test_email, name='test-email'),
    url(r'^rsvp/confirm/(?P<invite_id>[\w-]+)/$', rsvp_confirm, name='rsvp-confirm'),
    url(r'^forgot/', rsvp_forgot, name='rsvp-forgot'),
    # URL for downloading guest list. 
    url(r'dashboard/download/$', download_csv, name='download-csv'),
    url(r'wipeguests/$', wipe_guests, name='wipe-guests'),
]

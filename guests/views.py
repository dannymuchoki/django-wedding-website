import csv, io # added io for CSV parsing
import base64
from collections import namedtuple
import random
import datetime
import this
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView
from guests import csv_import
from guests.invitation import (get_invitation_context, INVITATION_TEMPLATE, guess_party_by_invite_id_or_404, guest_by_code_or_404, 
    send_invitation_email, send_reminders, resend_invite, gate_crashers)
from guests.models import Guest, MEALS, Party, UploadedGuestList
from guests.save_the_date import (get_save_the_date_context, send_save_the_date_email, SAVE_THE_DATE_TEMPLATE, 
    SAVE_THE_DATE_CONTEXT_MAP)

from guests.forms import UploadGuestListForm, AddGuestForm

# My mods
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView,ListView,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView, FormView)

guest_list = Guest.objects.all().order_by('party_name', 'last_name', 'first_name')
parties_with_pending_invites = Party.objects.filter(is_invited=True, is_attending=None).order_by('category', 'name')
parties_with_unopen_invites = parties_with_pending_invites.filter(invitation_opened=None)
parties_with_open_unresponded_invites = parties_with_pending_invites.exclude(invitation_opened=None)
attending_guests = Guest.objects.filter(is_attending=True).order_by('party_name')
not_attending = Guest.objects.filter(is_attending=False).order_by('party_name')
guests_without_meals = Guest.objects.filter(is_attending=True).filter(is_child=False).filter(Q(meal__isnull=True) | Q(meal='')).order_by('party_name__category', 'first_name')
meal_breakdown = Guest.objects.filter(is_attending=True).exclude(meal=None).values('meal').annotate(count=Count('*'))
category_breakdown = Guest.objects.filter(is_attending=True).values('party_name__category').annotate(count=Count('*'))
invitations_unsent = Party.objects.filter(is_invited = True, guest__is_attending__isnull=True, invitation_sent__isnull=True, invitation_opened=None).order_by('category', 'name')
no_response =  Guest.objects.filter(party_name__is_invited = True, party_name__invitation_opened__isnull = False, is_attending__isnull=True)

# Counts
invited_guest_count = Guest.objects.filter(party_name__is_invited=True).count()
pending_invites_count = Party.objects.filter(is_invited=True, is_attending=None).order_by('category', 'name').count()
pending_guests_count = Guest.objects.filter(party_name__is_invited=True, is_attending=None).count()
unopened_invite_count = Party.objects.filter(is_invited=True, is_attending=None, invitation_opened=None).count()
total_invites_count = Party.objects.filter(is_invited=True).count()
not_attending_guests_count = Guest.objects.filter(is_attending=False).count()

@login_required
def dashboard(request):
    add_guest_form = AddGuestForm
    return render(request, 'guests/dashboard.html', context={
        #Added to upload CSVs to the dashbaord.
        'csv_upload_form': UploadGuestListForm,
        'add_guest_form': AddGuestForm,
        # The rest of this is pretty much original, though I changed 'party' to 'party_name' and explicitly called out the count querysets.
        'couple_name': settings.BRIDE_AND_GROOM,
    })

@login_required
def guest_list_view(request):
    guest_list = Guest.objects.all().order_by('party_name', 'last_name', 'first_name')
    return render(request, 'guests/guest-list.html', 
                    context={'guest_list':guest_list,
                    'couple_name': settings.BRIDE_AND_GROOM})

@login_required
def export_guests(request):
    export = csv_import.export_guests()
    response = HttpResponse(export.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all-guests.csv'
    return response

@login_required
def manage_invitations_view(request):
    return render(request, 'guests/manage-invitations.html',
                    context={'couple_name': settings.BRIDE_AND_GROOM,
                            'guest_count': Guest.objects.filter(is_attending=True).count(),
                            # This is the earliest date anyone could arrive at Caboose Farm. 
                            'caboose_arrival_minimum' : datetime.datetime(2022, 6, 16).strftime('%B-%m-%Y'),
                            'possible_guests_count': invited_guest_count,
                            'pending_invites_count' : pending_invites_count,
                            'pending_guests_count': pending_guests_count,
                            'unopened_invite_count' : unopened_invite_count,
                            'parties_with_unopen_invites' : Party.objects.filter(is_invited=True, invitation_opened=None),
                            'parties_with_open_unresponded_invites': Party.objects.filter(is_invited=True, is_attending=None).exclude(invitation_opened=None), 
                            'total_invites_count': total_invites_count,
                            'attending_guests': attending_guests,
                            'not_attending': not_attending,
                            'not_attending_guests_count': not_attending_guests_count ,
                            'guest_without_meals':Guest.objects.filter(is_attending=True).filter(is_child=False).filter(Q(meal__isnull=True) | Q(meal='')).order_by('party_name__category', 'first_name'),
                            'meal_breakdown' : Guest.objects.filter(is_attending=True).exclude(meal=None).values('meal').annotate(count=Count('*')),
                            'guests_without_meals': Guest.objects.filter(is_attending=True).filter(is_child=False).filter(Q(meal__isnull=True) | Q(meal='')).order_by('party_name__category', 'first_name')})

# Because the CSV upload is in the dashboard view above, let's define the logic here using a class-based view. Why not a FBV? Ehh.  
class UploadGuestListView(LoginRequiredMixin, FormView):
    def get_success_url(self):
        return reverse('guest-list') # When a CSV is uploaded, return to guest list.
    
    def form_valid(self, request,  *args, **kwargs):
        form = UploadGuestListForm(request.POST)                    # Created a new forms.py with just the upload form in it.
        if form.is_valid():
            return self.form_valid(form)
        return HttpResponseRedirect(self.get_success_url())
    
    def post(self, request, *args, **kwargs):                                 
        uploaded_file = request.FILES['guest_list_file']
        if not uploaded_file.name.endswith('.csv'):
            print("this is not a csv")                              # At some point, I was going to build some more error checks
            return HttpResponseRedirect(self.get_success_url())

        guest_data = uploaded_file.read().decode('UTF-8')           # Decode the csv
        io_string = io.StringIO(guest_data)                         # pass it into an IO wrapper
        next(io_string)                                             # Iterates through the IO wrapper
        for column in csv.reader(io_string, delimiter=','):
            # This is for CSV formatting that doesn't agree with Python.
            for i in range(1, len(column)):
                if column[i] == 'TRUE':
                    column[i] = 'True'
                elif column[i] == 'FALSE':
                    column[i] = 'False'
                else:
                    pass 
             # To upload a CSV of guests, we need to update two models in one for-loop. There may be a more pythonic way to do this but eh.
            _, created = Party.objects.update_or_create(
                name = column[0],
                category = column[5],
            )
   
            party_id = Party.objects.filter(name= column[0])[0]           
            id = party_id.id 
            # Second part of the for-loop. 
            _, created = Guest.objects.update_or_create(
                party_name_id = id,  
                first_name = column[1],
                last_name = column[2],
                is_child = column[4],
                email = column[7],
                is_attending = '',
                caboose_farm = column[8],
                arrival_date = datetime.datetime.utcnow(),
                )

        # Save the CSV to the database. Good naming habits aren't enforced here. Maybe they should be. But you can delete the CSVs in admin. 
        uploaded_file = UploadedGuestList(guest_list_file = self.get_form_kwargs().get('files')['guest_list_file'])
        # The file is in the admin.
        uploaded_file.save()

        # Redirect the user back to the success url
        return HttpResponseRedirect(self.get_success_url())

@login_required
def download_csv(request):
    # This will return a CSV of your guest list. 
    queryset = Guest.objects.filter(is_attending=True).values_list('first_name', 'last_name', 'email', 'party_name__name', 'caboose_farm', 'arrival_date', 'meal')
    response = HttpResponse(content_type = 'text/csv')
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Email', 'Party', 'Invited to Caboose Farm?', 'Caboose Farm Arrival Date', 'Meal'])
    for guest in queryset:
        writer.writerow(guest)
    response['Content-Disposition'] = 'attachment; filename = "Guest List.csv"'
    return response

@login_required
def add_guest_view(request):
    form = AddGuestForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email_address = request.POST['email_address']
            category = request.POST['category']
            meal = request.POST['meal']
            
            if 'is_child' in request.POST:
                is_child = True
            else:
                is_child = False 
  
            if 'caboose_farm' in request.POST:
                caboose_farm = True
            else:
                caboose_farm = False
            party_name = str(first_name + " " + last_name)

            Party.objects.update_or_create(
                    name = party_name,
                    category = category,
                    )

            party_id = Party.objects.filter(name= party_name)[0]  
            id = party_id.id 
            invitation_id = party_id.invitation_id[0]
            Guest.objects.update_or_create(
                    party_name_id = id,  
                    first_name = first_name,
                    last_name = last_name,
                    is_child = is_child,
                    email = email_address,
                    is_attending = '',
                    meal = meal, 
                    caboose_farm = caboose_farm,
                    arrival_date = datetime.datetime.utcnow(),
                    )
    return render(request, template_name='guests/guest-list.html', context={
        'response': f"We've added {party_name} to the guest list", 
        'site_url' : settings.WEDDING_WEBSITE_URL,
        'guest_list' : Guest.objects.filter(party_name = id).order_by('last_name', 'first_name'),
        'couple_name': settings.BRIDE_AND_GROOM,
        })


InviteResponse = namedtuple('InviteResponse', ['guest', 'is_attending', 'meal'])


def invitation(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    # Write an if-then that assignes a True/False value to whether someone is at Caboose farm. Render that in template. 
    caboose_farm = Guest.objects.filter(party_name=party, caboose_farm=True)
    # Some guests are invited to caboose farm. They get the arrival_date field
    if len(caboose_farm) >= 1:
        caboose_farm = True 
    else:
        caboose_farm = False

    if party.invitation_opened is None:
        # update if this is the first time the invitation was opened
        party.invitation_opened = datetime.datetime.utcnow()
        party.save()
    if request.method == 'POST':
        
        for response in _parse_invite_params(request.POST):
            guest = Guest.objects.get(pk=response.guest_pk)
            # We changed the paramter in the Guest model to party_name
            assert guest.party_name == party
            guest.is_attending = response.is_attending
            guest.meal = response.meal
            guest.save()
            # Added logic. Revisit this. 
            if caboose_farm == True:
                try:
                    guest.arrival_date = request.POST.get('arrival_date')
                    guest.save()
                except Exception:
                    guest.arrival_date = datetime.datetime.utcnow()
                    guest.save()
            else:
                pass        
        if request.POST.get('comments'):
            comments = request.POST.get('comments')
            party.comments = comments if not party.comments else '{}; {}'.format(party.comments, comments)
        party.is_attending = party.any_guests_attending
        party.save()
        return HttpResponseRedirect(reverse('rsvp-confirm', args=[invite_id]))
    return render(request, template_name='guests/invitation.html', context={
        # Check settings.py for these variables. 
        'site_url' : settings.WEDDING_WEBSITE_URL,
        'couple_name': settings.BRIDE_AND_GROOM,
        'wedding_location': settings.WEDDING_LOCATION,
        'wedding_date': settings.WEDDING_DATE,
        'ceremony_start' : settings.CEREMONY_START,
        'ceremony_address': settings.CEREMONY_ADDRESS,
        'map_url': settings.CEREMONY_MAP,
        # Some of the wedding party stayed at an AirBnB called Caboose Farm. 
        'caboose_farm_name': settings.CABOOSE_FARM_NAME, 
        'caboose_farm_map' : settings.CABOOSE_FARM_MAP, 
        'caboose_farm_address': settings.CABOOSE_FARM_ADDRESS,
        'party': party,
        'party_category': party.category,
        'meals': MEALS,
        # Added a caboose_farm boolean that will show the arrival date field to select invitees. 
        'caboose_farm': caboose_farm,
    }) 


InviteResponse = namedtuple('InviteResponse', ['guest_pk', 'is_attending', 'meal'])


def confirmation(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    caboose_farm = Guest.objects.filter(party_name=party, caboose_farm=True)
    #arrival_date = Guest.objects.filter(party_name=party, arrival_date__gte=datetime.date(2122, 6, 16)).first()
    arrival_date = Guest.objects.filter(party_name=party, arrival_date__gte=datetime.datetime.combine(datetime.date(2122, 6, 16), datetime.datetime.min.time())).first()
    return render(request, template_name='guests/confirmation.html', context={
            # Check settings.py for these variables. 
            'site_url' : settings.WEDDING_WEBSITE_URL,
            'couple_name': settings.BRIDE_AND_GROOM,
            'wedding_location': settings.WEDDING_LOCATION,
            'wedding_date': settings.WEDDING_DATE,
            'map_url': settings.CEREMONY_MAP,
            'ceremony_address': settings.CEREMONY_ADDRESS,
            'ceremony_start' : settings.CEREMONY_START,
            'caboose_farm_map' : settings.CABOOSE_FARM_MAP, 
            'caboose_farm_address': settings.CABOOSE_FARM_ADDRESS,
            'caboose_farm_name' : settings.CABOOSE_FARM_NAME,
            'party': party,
            'party_category': party.category,
            'meals': MEALS,
            # Added a caboose_farm boolean that will show the arrival date field to select invitees. 
            'caboose_farm': caboose_farm,
            # For the static invitation
            'arrival_date' : arrival_date,
        })


def _parse_invite_params(params):
    responses = {}
    for param, value in params.items():
        if param.startswith('attending'):
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['attending'] = True if value == 'yes' else False
            responses[pk] = response
        elif param.startswith('meal'):
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['meal'] = value
            responses[pk] = response

    for pk, response in responses.items():
        yield InviteResponse(pk, response['attending'], response.get('meal', None))


def rsvp_confirm(request, invite_id=None):
    party = guess_party_by_invite_id_or_404(invite_id)
    return render(request, template_name='guests/rsvp_confirmation.html', context={
        'couple_name': settings.BRIDE_AND_GROOM,
        'wedding_location': settings.WEDDING_LOCATION,
        'party': party,
        'support_email': settings.DEFAULT_WEDDING_REPLY_EMAIL,
    })


@login_required
def invitation_email_preview(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    context = get_invitation_context(party)
    return render(request, INVITATION_TEMPLATE, context)
 

@login_required
def invitation_email_test(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    #send_invitation_email(party, recipients=[settings.DEFAULT_WEDDING_TEST_EMAIL])
    send_invitation_email(party, recipients=party.guest_emails)
    return HttpResponse('Sent invite to ' + str(party))


# This duplicates the send all function in invitation.py
@login_required
def send_all_invitations(request):
    mark_as_sent = Party.objects.filter(invitation_sent=None)
    party = Party.in_default_order().filter(is_invited=True, invitation_sent=None, invitation_opened=None).exclude(is_attending=False)
    for recipient in party:
        send_invitation_email(recipient, test_only=False)
        if mark_as_sent:
            party.invitation_sent = datetime.datetime.now()
            party.update()
    return HttpResponse('Sent all the invitations!')


@login_required
def wipe_guests(request):
    guests = Party.objects.all().delete()
    return HttpResponse('All guests deleted')

def save_the_date_random(request):
    template_id = list(SAVE_THE_DATE_CONTEXT_MAP.keys())[0]
    #template_id = random.choice(SAVE_THE_DATE_CONTEXT_MAP.keys())
    return save_the_date_preview(request, template_id)


def save_the_date_preview(request, template_id):
    context = get_save_the_date_context(template_id)
    context['email_mode'] = False
    return render(request, SAVE_THE_DATE_TEMPLATE, context=context)


@login_required
def test_email(request, template_id):
    context = get_save_the_date_context(template_id)
    send_save_the_date_email(context, [settings.DEFAULT_WEDDING_TEST_EMAIL])
    return HttpResponse('sent!')


def rsvp_forgot(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # This field is for spam blocking. If a bot fills it, then the message doesn't send. 
        message = request.POST.get('message')
        try:
            recipient = Guest.objects.filter(email__exact = email)[0]
            email_address = recipient.email
            party = Party.objects.filter(guest = recipient)[0]
            link = party.invitation_id
            party_category = party.category
            resend_invite(email_address, link, party_category, message)
        except Exception:
            email_address = email
            gate_crashers(email_address, message)
            pass      
    return render(request, template_name='guests/forgot.html', context={
        'couple_name': settings.BRIDE_AND_GROOM,
        'response': "If your email address is on the guest list, you will get a fresh invitation." })

def _base64_encode(filepath):
    with open(filepath, "rb") as image_file:
        return base64.b64encode(image_file.read())

def which_url(request):
    website_urls = settings.WEDDING_WEBSITE_URL
    
    
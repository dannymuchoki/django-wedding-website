from email.mime.image import MIMEImage
import os
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.http import Http404
from django.template.loader import render_to_string
from guests.models import Party, Guest, MEALS

INVITATION_TEMPLATE = 'guests/email_templates/invitation.html'


def guess_party_by_invite_id_or_404(invite_id):
    try:
        return Party.objects.get(invitation_id=invite_id)
    except Party.DoesNotExist:
        if settings.DEBUG:
            # in debug mode allow access by ID
            return Party.objects.get(id=int(invite_id))
        else:
            raise Http404()

# Each guest gets a unique code and invite
def guest_by_code_or_404(guest_code):
    try:
        return Guest.objects.get(guest_code = guest_code)
    except Guest.DoesNotExist:
        if settings.DEBUG:
            # in debug mode allow access by ID
            return Guest.objects.all()
        else:
            raise Http404()


def get_invitation_context(party):
    couple_name = settings.BRIDE_AND_GROOM
    return {
        'title': "Lion's Head",
        'main_image': 'bride-groom.jpg',
        'couple_name': couple_name,
        'wedding_date' : settings.WEDDING_DATE,
        'main_color': '#fff3e8',
        'font_color': '#fff',
        'page_title':  str(party.name + " You're Invited!"),
        'preheader_text': "You are invited!",
        'invitation_id': party.invitation_id,
        'party': party,
        'meals': MEALS,
    }


def send_invitation_email(party, test_only=False, recipients=None):
    if recipients is None:
        recipients = party.guest_emails
    if not recipients:
        print ('===== WARNING: no valid email addresses found for {} ====='.format(party))
        return

    # Changes the email at the invitation's footer. The URLs can be a list in settings.py. Change the categories here. 
    def Site_URL():
        if party.category == 'Lisette':
            site_url = settings.WEDDING_WEBSITE_URL[0]
        elif party.category == 'Danny':
            site_url = settings.WEDDING_WEBSITE_URL[1]
        else: 
            site_url = settings.WEDDING_WEBSITE_URL[2]
        return site_url
    
    context = get_invitation_context(party)
    context['email_mode'] = True 
    context['site_url'] = Site_URL()                # URL changes depending on the party's category.     
    context['couple'] = settings.BRIDE_AND_GROOM
    context['party_category'] = party.category
    template_html = render_to_string(INVITATION_TEMPLATE, context=context)
    template_text = "You're invited to {}'s wedding. To view this invitation, visit {} in any browser.".format(
        settings.BRIDE_AND_GROOM,
        reverse('invitation', args=[context['invitation_id']])
    )
    subject = "You're invited"
    # https://www.vlent.nl/weblog/2014/01/15/sending-emails-with-embedded-images-in-django/
    msg = EmailMultiAlternatives(subject, template_text, settings.DEFAULT_WEDDING_FROM_EMAIL, recipients,
                                 cc=settings.WEDDING_CC_LIST,
                                 reply_to=[settings.DEFAULT_WEDDING_REPLY_EMAIL])
    msg.attach_alternative(template_html, "text/html")
    msg.mixed_subtype = 'related'
    for filename in (context['main_image'], ):
        attachment_path = os.path.join(os.path.dirname(__file__), 'static', 'invitation', 'images', filename)
        with open(attachment_path, "rb") as image_file:
            msg_img = MIMEImage(image_file.read())
            msg_img.add_header('Content-ID', '<{}>'.format(filename))
            msg.attach(msg_img)

    print ('sending invitation to {} ({})'.format(party.name, ', '.join(recipients)))
    if not test_only:
        msg.send()


def send_all_invitations(test_only, mark_as_sent):
    to_send_to = Party.in_default_order().filter(is_invited=True, invitation_sent=None).exclude(is_attending=False)
    for party in to_send_to:
        send_invitation_email(party, test_only=test_only)
        if mark_as_sent:
            party.invitation_sent = datetime.now()
            party.save()


def send_reminders(party):
    # Send reminders to people who haven't responded to the invite
    to_send_to = Party.in_default_order().filter(is_invited=True, invitation_sent=True, invitation_opened=True, is_attending=None)
    for party in to_send_to:
        send_invitation_email(party, test_only=test_only)

def resend_invite(email_address, link, party_category, message):
    # Spam protection. If a bot enters a value in message, it will be ignored.
    if len(message) == 0:
        # This re-sends the invite link to anyone who forgot. 
        subject, from_email, to = 'Your invitation link', settings.DEFAULT_WEDDING_FROM_EMAIL, email_address
        if party_category == "Danny":
            text_content = 'Hey - sorry to hear you lost the RSVP link. Here it is again: https://danny.wedding/invite/{}'.format(link)
            html_content = '<p>Hey - </p> <p> Sorry to hear you lost the RSVP link. Here it is again: https://danny.wedding/invite/{}</p>'.format(link)
        elif party_category == "Lisette":
            text_content = 'Hey - sorry to hear you lost the RSVP link. Here it is again: https://lisette.wedding/invite/{}'.format(link)
            html_content = '<p>Hey - </p> <p> Sorry to hear you lost the RSVP link. Here it is again: https://lisette.wedding/invite/{}</p>'.format(link)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print("It sent!")
    else:
        print(message + " is not sent")


def gate_crashers(email_address, message):
    subject, from_email, to = str(email_address) + ' asked for a link', settings.DEFAULT_WEDDING_FROM_EMAIL, settings.DEFAULT_WEDDING_FROM_EMAIL
    text_content = "{} is trying to gatecrash.".format(email_address)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.send()
 
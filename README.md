# A Wedding Website and Invitation + Guest Management System built in Django. 

## The Website

This was originally a project by [Cory Zue](http://www.coryzue.com/contact/) that I forked and used for my own wedding.
You can find [a longer writeup on this project here](https://www.placecard.me/blog/django-wedding-website/).

## What was included in the original package?

Cory's original work included:

- A responsive, single-page traditional wedding website
- A complete guest management application
- Email framework for sending save the dates
- Email framework for invitations and built in RSVP system
- Guest dashboard

## Danny added a couple of things

- The ability to upload your guest list via the dashboard using a comma delimited file (.csv)
- The ability to download your guest list via the dashboard, also in .csv.
- Each guest gets a unique numeric code. I used it for security authentication purposes to keep out gatecrashers.
- Template updates for more DRY-ness (you don't have to scour the templates to change the couple's names).
- Made the secret key more resilient (i.e. hid it in an `.env` file)
- A view that resends RSVP links to guests who forgot/lost them.

### The "Standard" Wedding Website

The standard wedding website is a responsive, single-page, twitter bootstrap-based site (using a modified version of
[this theme](https://blackrockdigital.github.io/startbootstrap-creative/)).

It is completely customizable to your needs and the content is laid out in standard django templates. By default it includes:

- A "hero" splash screen for a photo
- A mobile-friendly top nav with scrollspy
- A photo/hover navigation pane
- Configurable content sections for every aspect of your site that you want
- A set of different styles you can use for different sections

![Hero Section of Wedding Website](https://raw.githubusercontent.com/dannymuchoki/django-wedding-website/master/screenshots/hero-page.png)

### Forgot your RSVP?

Guests who lose their RSVP can get it resent by visiting `/forgot` and entering their email address. If the email address is on the guest list,
the system re-sends the guest's invitation. 

### Guest dashboard

You can access the dashboard via `/dashboard/` from an account with admin access. Your other guests won't be able to see it.

Originally, you could upload the guest list via the console. My guest list was always fluctuating so I added an option to upload
guests via a comma delimited file (.csv) in the dashboard view.

#### Adding guests
![Wedding Dashboard](https://raw.githubusercontent.com/dannymuchoki/django-wedding-website/master/screenshots/wedding-dashboard-1.png)

You can make a `.csv` file pretty easily in Excel or OpenOffice. The column headers for your .csv file should be:

```
Party, First Name, Last Name, Type, Is Child?, Category, Invite Now?, Email, Caboose Farm?, Arrival Date

```
Look in `guests/tests/data` for sample file formats. 

`Party`, `First Name`, and `Last Name` are the only columns that are strictly mandatory. You can customize how to populate your dashboard via `views.py`. I recommend changing the Guest and Party models to suit your data collection needs. 


### Viewing/downloading your guest list
![Wedding Dashboard](https://raw.githubusercontent.com/dannymuchoki/django-wedding-website/master/screenshots/wedding-dashboard-2.png)

Each guest added will be included in the guest list. You can quickly download a .csv spreadsheet of your guests. 

#### Guest management
![Wedding Dashboard](https://raw.githubusercontent.com/dannymuchoki/django-wedding-website/master/screenshots/wedding-dashboard-3.png)

After your invitations go out you can use the guest dashboard to see how many people have RSVP'd, everyone who still
has to respond, people who haven't selected a meal, etc. It's a great way of tracking your big picture numbers in terms of how many guests to expect.

## Models

The original code included two data models - the `Party` and the `Guest`. In addition to modifying these models, I added a third `UploadedGuestList` model to manage my uploaded guest list spreadsheets. This allows me to access past guest lists in the admin. 

#### Party model

The `Party` model allows you to group your guests together for things like sending a single invitation to a couple.
You can also add parties that you're not sure you're going to invite using the `is_invited` field, which works great for sending tiered invitations.
There's also a field to track whether the party is invited to the rehearsal dinner.

#### Guest model

The `Guest` model contains all of your individual guests.
In addition to standard name/email it has fields to represent whether the guest is a child (for kids meals/pricing differences),
and, after sending invitations, marking whether the guest is attending and what meal they are having.

#### UploadGuestList model (for .csv imports). 

The guest list can be imported and exported via excel (.csv) either in command line or in the dashboard.
This allows you to build your guest list in Excel and get it into the system in a single step.
It also lets you export the data to share with others or for whatever else you need.

For the command line option, see the `import_guests` management command for more details and `guests/tests/data` for sample file formats.

### Save the Dates

The app comes with a built-in cross-client and mobile-friendly email template for save the dates (see `save_the_date.html`).

You can create multiple save the dates and send them out either randomly or by `Party` type (useful if you want to send formal
invitations to some people and more playful ones to others).

See `save_the_date.py` and `SAVE_THE_DATE_CONTEXT_MAP` for customizing your save the dates.

### Invitations and RSVPs

The app also comes with a built-in invitation system.
The template is similar to the save-the-date template, however in addition to the standard invitation content it includes:

- A built in tracking pixel to know whether someone has opened the email or not
- Unique invitation URLs for each party with pre-populated guest names ([example](http://rownena-and.coryzue.com/invite/b2ad24ec5dbb4694a36ef4ab616264e0/))
- Online RSVP system with meal selection and validation

### Purge your guest list

Visiting `/wipeguests` will quickly and instantly wipe your guest list if you need to start all over again. I do recommend downloading it from the Guest List first. 

### Other details

You can easily hook up Google analytics by editing the tracking ID in `google-analytics.html`.

## Installation

As of writing this in 2023, this was developed for Python 3 and Django 3.12.3 (LTS).

Make a [virtual environment](https://docs.python.org/3/library/venv.html)! Then just install requirements, migrate, and runserver to get started:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Environment files are your friend

This version heavily relies on a local `.env` file referenced in `settings.py`. [Learn more about environment variables here](https://pypi.org/project/python-dotenv/). Environment variables are also crucial in running this on the cloud, as well as keeping secret things secret (like your secret key).  

## Customization

I recommend forking this project and just manually modifying it by hand to replace everything with what you want.
Searching for the text on a page in the repository is a great way to find where something lives.

### Sending email

This [thread on stack overflow](https://stackoverflow.com/questions/6367014/how-to-send-email-via-django)
is a good starting place for learning how to connect to a real mail service. I recommend Sendgrid.

This application uses Django's email framework for sending mail.
You need to modify the `EMAIL_HOST`, `EMAIL_PORT` and other associated variables in `settings.py` or, ideally, your  in order
to hook it into a real server. **MAKE SURE TO STORE THESE SETTINGS IN AN ENVIRONMENT VARIABLE!**   

### Email addresses

To customize the email addresses, see the `DEFAULT_WEDDING_FROM_EMAIL` and
`DEFAULT_WEDDING_REPLY_EMAIL` variables in `settings.py`.
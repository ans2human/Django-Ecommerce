from django.contrib.staticfiles import finders

result = finders.find('mail_templates/email.html')
searched_locations = finders.searched_locations
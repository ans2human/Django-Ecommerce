from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from .models import EmailTemplate



def add_to_portfolio_mail(request):
    qs = EmailTemplate.objects.get(email_type="WM")
    html_content = qs.email_template
    html_file = str(os.path.join(settings.EMAIL_TEMP,
                                 "mail_templates/email.html"))
    print(html_file)
    file = open(html_file, 'w+')
    file.write(html_content)
    file.close()
    subject = qs.email_template_name
    from_email = settings.EMAIL_HOST_USER
    body = render_to_string(
        "mail_templates/email.html",
        {
            'user': request.user.get_full_name,
            'body': "we're glad that you chose us for trading! We strive to cater all your trading needs"
        }
    )
    email = request.user.email
    send_mail(f'Welcome {request.user.first_name}',
              subject, from_email, [email], html_message=body,)
    open(html_file, 'w').close()
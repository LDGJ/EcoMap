# -*- coding: utf-8 -*-
"""Module contains usefull functions."""
import logging
import logging.config
import os
import random
import string
import smtplib

from urlparse import urlparse
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CONF_PATH = os.path.join(os.environ['CONFROOT'], 'log.conf')


def random_password(length):
    """Generates randow string. Contains lower- and uppercase letters.
       :params: length - length of string
       :return: string"""
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


def get_logger():
    """function for configuring default logger object
    from standard logging library
        Returns:
            configured logger object.
        Usage:
            import this method to your
            module and call it.
            then define a new logger object as usual
    """
    return logging.config.fileConfig(CONF_PATH)


class Singleton(type):
    """
    using a Singleton pattern to work with only one possible instance of Pool
    """
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


def parse_url(url_to_parse, get_arg=None, get_path=None):
    """Function helps to parse url and splits parts of urls.
    :param url_to_parse: input url
    :param get_arg: [optional]
    :param get_path: [optional]
    :return: parsed url contains path
    """
    url = urlparse(url_to_parse)
    if get_arg:
        return url.path.split('/')[-1]
    if get_path:
        return '/'.join(url.path.split('/')[:-1])
    return '?'.join((url.path, url.query)) if url.query else url.path


def send_email(email_type, configs, args):
    """Sends email."""
    msg = MIMEMultipart('alternative')
    complete_email = os.path.join(os.environ['CONFROOT'],
                                  'email_template.html')

    if email_type is 'registration':
        email_body = os.path.join(os.environ['CONFROOT'],
                                  'registration_email_template.html')
        msg['Subject'] = Header('Реєстрація на ecomap.org', 'utf-8')
    elif email_type is 'password_restore':
        email_body = os.path.join(os.environ['CONFROOT'],
                                  'restore_password_template.html')
        msg['Subject'] = Header('Відновлення паролю до ecomap.org', 'utf-8')
    elif email_type is 'daily_report':
        make_template(args)
        args = ''
        email_body = os.path.join(os.environ['CONFROOT'],
                                  'new_template.html')
        msg['Subject'] = Header('звіт адміністратора на ecomap.org', 'utf-8')

    html = None
    html_body = None
    with open(complete_email, 'rb') as template:
        html = template.read().decode('utf-8')

    with open(email_body, 'rb') as template:
        html_body = template.read().decode('utf-8')
        html_body = html_body % tuple(args)

    html_formatted = html % html_body
    msg['From'] = configs[2]
    msg['To'] = configs[3]
    htmltext = MIMEText(html_formatted, 'html', 'utf-8')
    msg.attach(htmltext)

    server = smtplib.SMTP_SSL('smtp.gmail.com')
    server.login(configs[0], configs[1])
    server.sendmail('admin@ecomap.com', configs[3],
                    msg.as_string())
    server.quit()


def make_template(data):
    with open((os.path.join(os.environ['CONFROOT'],
              "new_template.html")), "w") as html:
        html.write('')
        mes = '<h1>Жоден з користувачів пароль не змінював.</h1>'
        table_head = """<table>
            <tr>
                <th>користувач</th>
                <th>mail</th>
                <th>number request</th>
                <th>time</th>
            </tr>
        """
        table_row = """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%d</td>
                <td>%d</td>
            </tr>
        """
        if data:
            html.write(table_head)
            for x in data:
                html.write(table_row % (x[1].encode('utf-8'),
                                        x[2].encode('utf-8'),
                                        int(x[3]),
                                        int(x[0])))
            else:
                html.write('</table>')
        else:
            html.write(mes)


def admin_stats_email(data=None):
    """Sends email to new created users.
       :params: app_name - app's login
                app_key - app's key
                name - user name
                surname - user surname
                email - user email
                password - user password
    """
    TEMPLATE_PATH = os.path.join(os.environ['CONFROOT'],
                                 'admin_stats_template.html')

    with open(TEMPLATE_PATH, 'rb') as template:
        html = template.read()

    mes = 'message noone changed </body>'
    table_head = """<table>
        <tr>
            <th>користувач</th>
            <th>mail</th>
            <th>number request</th>
        </tr>
    """
    table_row = """
        <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%d</td>
        </tr>
            """
    if data:
        html += table_head
        for x in data:
            html += table_row % (x[1].encode('utf-8'),
                                 x[2].encode('utf-8'),
                                 int(x[3]))
        else:
            html += '</table></body>'
    else:
        html += mes

    html_decoded = html
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header('звіт адміністратора на ecomap.org', 'utf-8')

    # htmltext = MIMEText(html_decoded, 'html', 'utf-8')

    # msg.attach(htmltext)
    msg['Subject'] = 'звіт за добу'
    msg['From'] = 'admin@ecomap.com'
    msg['To'] = 'vadime.padalko@gmail.com'

    # with app.app_context():
    #     msg.body = render_template(template + '.txt')
    #     msg.html = render_template('jinja_template.html', data=data)
    #     # mail.send(msg)

    return msg


# def admin_stats_email2(data=None):
#     """Sends email to new created users.
#        :params: app_name - app's login
#                 app_key - app's key
#                 name - user name
#                 surname - user surname
#                 email - user email
#                 password - user password
#     """
#     msg = MIMEMultipart('alternative')
#     msg['Subject'] = Header('звіт адміністратора на ecomap.org', 'utf-8')
#
#     with app.app_context():
#         msg.html = render_template('jinja_template.html', data=data)
#
#     htmltext = MIMEText(msg.html, 'html', 'utf-8')
#
#     msg.attach(htmltext)
#     msg['Subject'] = 'звіт за добу'
#     msg['From'] = 'admin@ecomap.com'
#     msg['To'] = 'vadime.padalko@gmail.com'
#     return msg

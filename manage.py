def init_django():
    import django
    from django.conf import settings

    if settings.configured:
        return

    settings.configure(
        INSTALLED_APPS=[
            'db',
        ],
        DATABASES = {
        'default': {
        'ENGINE': 'engine for your dbms',
        'NAME': 'name of your db',
        'USER': 'your username',
        'PASSWORD': 'your password',
        'HOST': 'host adress',
        'PORT': 'port number',
            }
        }
    )
    django.setup()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    init_django()
    execute_from_command_line()

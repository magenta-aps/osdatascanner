from django.core.exceptions import ImproperlyConfigured, ValidationError
import email_validator


def get_serializer(model_class):
    """
    Return the serializer class that corresponds to the given model class.
    """
    serializer_class = getattr(model_class, 'serializer_class', None)
    if not serializer_class:
        raise ImproperlyConfigured(
            f"No serializer found for {model_class.__name__}. "
            "Please define a serializer for this model."
        )
    return serializer_class


# Don't check mail deliverability; we don't care about that
# (email addresses might be disabled, and UPNs aren't necessarily
# email addresses anyway)
email_validator.CHECK_DELIVERABILITY = False


def validate_mail(value):
    # By default, this runs with allow_smtputf8=True, which allows internationalized addresses -
    # f.e. emails with "æøå" in them. Django's EmailField and its default validator don't.
    # So, it's preferred to opt for a CharField & this validator.
    try:
        email_validator.validate_email(value)
    # We're only doing this to avoid throwing a library exception and instead
    # throw something that f.e. the Django-admin can handle.
    except Exception as e:
        raise ValidationError(e)

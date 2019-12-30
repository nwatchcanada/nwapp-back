from django.core.files.base import ContentFile
import base64
import six
import uuid


def get_content_file_from_base64_string(data, filename):
    """
    Function will convert the string and filename parameter and return a
    `ContentFile` object.

    Special thanks:
    (1) https://github.com/tomchristie/django-rest-framework/pull/1268
    (2) https://stackoverflow.com/a/39587386
    """
    # Check if this is a base64 string
    if isinstance(data, six.string_types):
        # Check if the base64 string is in the "data:" format
        if 'data:' in data and ';base64,' in data:
            # Break out the header from the base64 content
            header, data = data.split(';base64,')

        # Try to decode the file. Return validation error if it fails.
        try:
            decoded_file = base64.b64decode(data)
        except TypeError:
            print("Failed conversion.")
            return None

        # Convert it to the content file.
        data = ContentFile(decoded_file, name=filename)
    return data

import boto3
from boto3.exceptions import Boto3Error
from flask_babel import _
from app import app


def translate(text, source_language, dest_language):
    if 'AWS_ACCESS_KEY_ID' not in app.config or \
            not app.config['AWS_ACCESS_KEY_ID'] or \
            'AWS_SECRET_ACCESS_KEY' not in app.config or \
            not app.config['AWS_SECRET_ACCESS_KEY'] or \
            'AWS_DEFAULT_REGION' not in app.config or \
            not app.config['AWS_DEFAULT_REGION']:
        return _('Error: the translation service is not configured.')
    translate = boto3.client('translate')
    response = translate.translate_text(Text=text,
                                        SourceLanguageCode=source_language,
                                        TargetLanguageCode=dest_language)
    return response.get('TranslatedText')

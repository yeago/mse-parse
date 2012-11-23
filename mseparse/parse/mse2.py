import zipfile
import datetime
import yaml
import re
from ..utils.fix_unicode import fix_unicode
from django.utils.html import strip_tags


def cardblob_to_dict(blob):
    blob = blob.replace('\n\t\t', 'RETURN')
    spec = {}
    for line in blob.split('\n'):
        line = line.strip()
        if line:
            field, value = line.split(':', 1)
            if value is None or value.strip() == '':
                continue
            spec[field] = value.replace('RETURN', '\r\n\r\n').replace('COLON', ':').strip()
    return normalize_rows(spec)


def normalize_rows(spec):
    EXEMPT = ['super type', 'sub type', 'power', 'toughness']  # Not sure what these would be multiline for
    multiline_keys = {}
    for key in spec.keys():
        match = re.match('(.+?) \d', key)
        if match and match.groups():
            match = match.groups(0)[0]
            if match in EXEMPT:
                continue
            if not match in multiline_keys:
                multiline_keys[match] = []
            multiline_keys[match].append(key)

    respec = spec.copy()
    for key, keys in multiline_keys.items():
        tokens = []
        if spec.get(key):
            tokens.append(spec[key])
        tokens.extend([spec.get(k) for k in keys if spec.get(k)])
        respec[key] = "RETURN".join(tokens)
    return respec


def separate_sections(set_file):
    set_file = fix_unicode(set_file)
    set_file = unicode(set_file, errors='ignore')
    set_file = strip_tags(set_file)
    set_file = set_file.split('keyword:',)[0]
    cardsplit = lambda x: '%scardCOLON%s' % x.groups(0)
    set_file = re.sub('(.+?)card:(.*)', cardsplit, set_file)
    card_blobs = set_file.split('card:')
    set_blob = card_blobs.pop(0)

    """
    Some cleanup of set blob
    -We don't care about colons beyond the second tab level
    -Second level tabs usually just need to be in the same value
    -Wrap values in quotes
    """
    set_blob = re.sub('\t\t(.*?):(.*)', lambda x: '\t\t%sCOLON%s' % (
                                x.groups(0)[0], x.groups(0)[1]), set_blob)
    set_blob = set_blob.replace('\n\t\t', 'RETURN')
    set_blob = re.sub('\t([^:]+?):(.*)', lambda x: '\t%s: "%s"' % (
                    x.groups(0)[0], x.groups(0)[1]), set_blob)
    return set_blob, card_blobs


def parse_setfile(set_file):
    set_blob, card_blobs = separate_sections(set_file)
    set_info = yaml.load(set_blob.replace('\t', '     '))
    cards = []
    for blob in card_blobs:
        spec = cardblob_to_dict(blob)
        respec = {}
        respec.update(spec)
        for key, value in spec.items():
            if value and value == str(value):
                respec[key] = value.replace('RETURN', '\r\n\r\n').replace('COLON', ':')
        cards.append(respec)
    return set_info, cards


def unzip_mse(mse_file):
    return zipfile.ZipFile(mse_file.file, 'r')


def set_data(zfile):
    return parse_setfile(zfile.open('set').read())


def image_data(zfile, name):
    for fname in zfile.namelist():
        if 'image' in fname and fname == name:
            return zfile.open(fname)


def update_setmodel_from_spec(instance, set_info):
    try:
        instance.name = set_info['set info']['title']
    except KeyError:
        instance.name = 'MSE Set %s' % datetime.date.today()

    try:
        instance.description = set_info['set info']['description']
    except KeyError:
        instance.description = 'Imported from MSE'
    return instance


def power_toughness(card_spec):
    if card_spec.get('power') and card_spec.get('toughness'):
        return '%s/%s' % (card_spec['power'], card_spec['toughness'])


def update_cardmodel_from_spec(instance, card_spec):
    #  Set info needed for image
    ATTR_MAP = {
        'name': 'name',
        'type': 'super type',
        'rarity': 'rarity',
        'artist': 'illustrator',
        'subtype': 'sub type',
        'flavour_text': 'flavor text',
        'attribution': 'copyright',
        'rules': 'rule text',
    }

    LAMBDA_MAP = {
        'power_toughness': power_toughness,
        'rarity': lambda x: (x.get('rarity') or '').lower(),
        'mana_cost': lambda x: ('%s' % (x.get('casting cost') or '')) or None,
    }

    for tapped_key, mse_key in ATTR_MAP.items():
        mse_value = card_spec.get(mse_key)
        if mse_value:
            mse_value = mse_value.replace('RETURN', '\r\n\r\n').strip()
        setattr(instance, tapped_key, mse_value or None)

    for tapped_key, mse_callable in LAMBDA_MAP.items():
        mse_value = mse_callable(card_spec)
        if mse_value:
            mse_value = mse_value.replace('RETURN', '\r\n\r\n').strip()
        setattr(instance, tapped_key, mse_value or None)
    return instance

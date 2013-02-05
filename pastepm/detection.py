from pastepm.config import config
from pastepm.lib.pyclassifier import Classifier

c = Classifier.from_data(open(config.get('pyclassifier', 'file')))
language_ext_pairs = c.get_classes()

def language_detect(code):
    return c.identify(code)

def get_language_from_extension(extension):
    for language, ext in language_ext_pairs:
        if ext == extension: return language.lower()

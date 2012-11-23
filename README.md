from .mse import unzip_mse, set_data
from zipfile import BadZipfile

try:
    self._zipfile = unzip_mse(mse_file_obj)
    self._set_spec, self._card_specs = set_data(self._zipfile)
except BadZipFile:
    raise ValueError("Couldn't parse")

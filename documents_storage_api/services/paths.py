import pathlib
import os
master_path = os.getcwd()

MEDIA_FILES_PATH = pathlib.Path(master_path, "data/media_files")
TEMP_PATH = pathlib.Path(master_path, "data/temp")
EXTRACTED_TAR_FILE_PATH = pathlib.Path(TEMP_PATH, "import")
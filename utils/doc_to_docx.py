from datetime import datetime
import os.path
import re

from doc2docx import convert


def convert_docs_to_docx(file_paths, save_folder):
    now = datetime.now()
    folder_name = now.strftime("%Y-%m-%d_%H %M %S")

    save_location = os.path.join(os.path.abspath(save_folder), folder_name)

    os.makedirs(save_location)
    for i in enumerate(file_paths):
        doc = file_paths[i]
        extension = os.path.splitext(doc)[1].lstrip(".")
        if extension == "doc":
            os.rename(doc, os.path.join(save_location, os.path.basename(doc)))




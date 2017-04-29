import os
import random
import shutil
import string
import zipfile
from distutils.dir_util import copy_tree as cp
from distutils.dir_util import remove_tree as rm


def zip_dir(path, ziph):
    for root, dirs, files in os.walk(path):
        relative_root = root.replace(path, "")
        for f in files:
            ziph.write(os.path.join(root, f), os.path.join(relative_root, f))


project_directory = "/home/dev/Documents/python-sandbox/awswcrawler"
project_code_directory = project_directory + "/awswcrawler"

venv_dir = project_directory + "/venv"

tmp_root_dir = "/tmp"
building_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
building_dir = tmp_root_dir + "/app_build_" + building_id

if os.path.exists(building_dir):
    os.removedirs(building_dir)

os.mkdir(building_dir)

shutil.copytree(project_code_directory, building_dir + "/awswcrawler")
cp(venv_dir + "/lib/python2.7/site-packages", building_dir)

app_file_path = 'app.zip'

zipf = zipfile.ZipFile(app_file_path, 'w', zipfile.ZIP_DEFLATED)
zip_dir(building_dir, zipf)
zipf.close()

rm(building_dir)

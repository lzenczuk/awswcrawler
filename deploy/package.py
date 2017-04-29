import os
import random
import shutil
import string
import zipfile
from distutils.dir_util import copy_tree as cp
from distutils.dir_util import remove_tree as rm


def _zip_dir(path, ziph):
    for root, dirs, files in os.walk(path):
        relative_root = root.replace(path, "")
        for f in files:
            ziph.write(os.path.join(root, f), os.path.join(relative_root, f))


def package_app(app_zip_file_name, build_folder, venv_folder, *code_folders):
    if not os.path.exists(build_folder):
        os.mkdir(build_folder)

    build_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    inner_build_folder = build_folder + "/build_" + build_id
    app_code_folder = inner_build_folder + "/app_code"

    if os.path.exists(inner_build_folder):
        os.removedirs(inner_build_folder)

    os.mkdir(inner_build_folder)
    os.mkdir(app_code_folder)

    for cf in code_folders:
        package_name = cf.split("/")[-1]
        shutil.copytree(cf, app_code_folder + "/" + package_name)

    cp(venv_folder + "/lib/python2.7/site-packages", app_code_folder)

    app_file_path = inner_build_folder + '/' + app_zip_file_name

    zipf = zipfile.ZipFile(app_file_path, 'w', zipfile.ZIP_DEFLATED)
    _zip_dir(app_code_folder, zipf)
    zipf.close()

    shutil.copy(app_file_path, build_folder)
    rm(inner_build_folder)

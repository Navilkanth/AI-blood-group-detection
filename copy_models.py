
import shutil
import os

def copy_file(src, dst):
    try:
        shutil.copy2(src, dst)
        print(f"Copied {src} to {dst}")
    except Exception as e:
        print(f"Failed to copy {src}: {e}")

src_malaria = r"c:\Users\navin\Downloads\bd classification\Malaria-master\Malaria-master\model.h5"
dst_malaria = r"c:\Users\navin\Downloads\bd classification\backend\models_integrated\malaria_model.h5"

src_cancer = r"c:\Users\navin\Downloads\bd classification\Blood-Cancer-Detection-CNN-master\Blood-Cancer-Detection-CNN-master\mymodel.h5"
dst_cancer = r"c:\Users\navin\Downloads\bd classification\backend\models_integrated\cancer_model.hdf5"

os.makedirs(os.path.dirname(dst_malaria), exist_ok=True)

copy_file(src_malaria, dst_malaria)
copy_file(src_cancer, dst_cancer)

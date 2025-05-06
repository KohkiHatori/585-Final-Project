import os
import random
import shutil

# Set source and destination folder paths
source_folder = '/Users/kohkihatori/Downloads/img_align_celeba'
destination_folder = '/Users/kohkihatori/Downloads/faces'

# Make sure destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# List all files in the source folder
all_files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]

# Pick 100 random files (or fewer if not enough files)
files_to_move = random.sample(all_files, min(100, len(all_files)))

# Move files
for file_name in files_to_move:
    src_path = os.path.join(source_folder, file_name)
    dst_path = os.path.join(destination_folder, file_name)
    shutil.move(src_path, dst_path)

print(f"Moved {len(files_to_move)} files.")

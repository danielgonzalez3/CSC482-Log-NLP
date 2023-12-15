import tarfile
import gzip
import csv
import os
import re
import shutil

TAR_FILE_PATH = 'ref_data/travis-ci-logs.tar'
EXTRACT_PATH = 'data'

def log_java_errors(file_path):
    java_num_regex = r"(.java:\d+:.*)"
    id = os.path.splitext(file_path)[0]
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            matches = [line.strip() for line in lines if re.search(java_num_regex, line)]

            with open('global_logs.csv', mode='a', newline='') as log_file:
                writer = csv.writer(log_file)
                for match in matches:
                    writer.writerow([id, match])
        return "Log entries added to global_logs.csv"
    except Exception as e:
        return str(e)

def extract_gz(gz_path, extract_to=None):
    """
    Extracts a .gz file.

    :param gz_path: Path to the .gz file.
    :param extract_to: File path to extract to. If None, the same name as the .gz file will be used, without the .gz extension.
    """
    if extract_to is None:
        extract_to = gz_path[:-3]  # Remove .gz extension

    with gzip.open(gz_path, 'rb') as f_in:
        with open(extract_to, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    print(f'Extracted all files in {gz_path}')
    os.remove(gz_path)

def extract_tar(tar_path, extract_path='data'):
    """
    Extracts a tar file.

    :param tar_path: Path to the tar file.
    :param extract_path: Directory where to extract the files.
    """
    with tarfile.open(tar_path, 'r') as tar:
        tar.extractall(path=extract_path)
        print(f'Extracted all files in {tar_path} to {extract_path}')

    for root, dirs, files in os.walk(extract_path):
        for file in files:
            if file.endswith('.txt.gz'):
                file_path = os.path.join(root, file)
                extract_gz(file_path) 


def main():
    if os.path.exists(EXTRACT_PATH):
        print(f"Extraction path {EXTRACT_PATH} already exists. Skipping extraction.")
    else:
        extract_tar(TAR_FILE_PATH, EXTRACT_PATH)
    if not os.path.exists('global_logs.csv'):
        with open('global_logs.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "LOG"])
    for root, dirs, files in os.walk(EXTRACT_PATH):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                log_java_errors(file_path)
                print(f'Extracted logs in {file_path}')
    
if __name__ == "__main__":
    main()

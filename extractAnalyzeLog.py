import zipfile
import csv
import os
import re

def fetchLogs(texts, name):
    log_regex = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) (INFO|ERROR|WARN|DEBUG|TRACE).*?(?=\d{4}-\d{2}-\d{2}T|\Z)"

    with open('global_logs.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        for text in texts:
            matches = re.finditer(log_regex, text, re.DOTALL)
            for match in matches:
                print(name)
                print(match.group(2))
                print(match.group(0))
                writer.writerow([name, match.group(2), match.group(0)])
    
def extract_and_analyze_zip(file_path):
    texts = []
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        # extract all the contents into a temporary directory
        temp_dir = f"/tmp/tmp_{file_path}"
        zip_ref.extractall(temp_dir)

        # iterate through the files and directories in the extracted folder
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith('.txt'):
                    with open(file_path, 'r') as text_file:
                        texts.append(text_file.read())
    return texts


def main():
    # add headers
    with open('global_logs.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "TYPE", "LOG"])
    
    for file in os.listdir("data/"):
        if file.endswith(".zip"):
            file_path = os.path.join("data/", file)
            print("checking:" + file)
            texts = extract_and_analyze_zip(file_path)
            fetchLogs(texts, file)

if __name__ == "__main__":
    main()

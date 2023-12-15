import sys
import spacy
import re
import pandas as pd

nlp = spacy.load('en_core_web_sm')
df = pd.read_csv('svo.csv')

def clean_error(text):
    pattern = r"(WARNING \|)|(ERROR   \|)|(WARNING:)"
    match = re.search(pattern, text)

    if match:
        return text.split("|")[1]
    else:
        return text

def extract_variables(text):
    pattern = r'logs_([a-zA-Z0-9-]+)-([a-zA-Z0-9-]+)-(\d+)-([a-fA-F0-9]+)\.zip'

    match = re.match(pattern, text)

    if match:
        owner = match.group(1)
        repo = match.group(2)
        run_id = match.group(3)
        commit_hash = match.group(4)

        return {
            'owner': owner,
            'repo': repo,
            'run_id': run_id,
            'commit_hash': commit_hash
        }
    else:
        return None

def create_github_commit_link(variables):
    owner = variables['owner']
    repo = variables['repo']
    commit_hash = variables['commit_hash']
    
    github_commit_link = f'https://github.com/{owner}/{repo}/commit/{commit_hash}'
    return github_commit_link
    
def searchSVO(text):
    tok = nlp(text)
    global_count = 0
    global_id = 0
    for index, row in df.iterrows():
        id = row['ID']
        svos = row['SVOs']
        
        tmp_count = 0
        for t in tok:
            tmp_count += svos.count(t.text)
        if (tmp_count > global_count):
            global_count = tmp_count
            global_id = id
    return global_count, global_id

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py filename")
        sys.exit(1)
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as file:
            content = file.read()
            text = clean_error(content)
            count, id = searchSVO(text)
            content = extract_variables(id)
            github_link = create_github_commit_link(content)
            print(f"From {count} SVO matches, here is the link to a commit where the builds matched the errors provided:")
            print(github_link)
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

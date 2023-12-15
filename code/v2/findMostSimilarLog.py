import tkinter as tk
from tkinter import simpledialog
from tkinter import scrolledtext
import pandas as pd
import ast
import numpy as np
import sys
import re
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

id_to_repo = {
    1129565: "spring-projects/spring-boot",
    132351: "square/okhttp",
    1501298: "apache/storm",
    1504827: "prestodb/presto",
    1512319: "jcabi/jcabi-github",
    1889385: "thrau/jarchivelib",
    2026694: "JabRef/jabref",
    2036767: "crate/crate",
    2136677: "google/iosched",
    2853863: "ReactiveX/RxAndroid",
    2964082: "SpongePowered/SpongeAPI",
    297539: "wordpress-mobile/WordPress-Android",
    380237: "openmicroscopy/openmicroscopy",
    407298: "Netflix/Hystrix",
    487759: "JakeWharton/butterknife",
    78264: "square/retrofit"
}


df = pd.read_csv('merged_global_logs_embeddings_2.csv', nrows=100)
df['embeddings'] = df['embeddings'].apply(lambda x: np.array(ast.literal_eval(x)))

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def preprocess_log(log):
    log = re.sub(r'/[^ ]+', '', log)
    log = log.lower()
    return log

def get_bert_embeddings(log_message):
    inputs = tokenizer(log_message, return_tensors='pt', truncation=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

def find_most_similar(embeddings, query_embedding):
    similarities = cosine_similarity(embeddings, query_embedding)
    most_similar_index = similarities.argmax()
    most_similar_score = similarities.max()
    return most_similar_index, most_similar_score

def find_similar_logs(query_log):    
    preprocessed_query_log = preprocess_log(query_log)

    query_embedding = get_bert_embeddings(preprocessed_query_log)
    
    all_embeddings = np.stack(df['embeddings'].values)

    most_similar_index, most_similar_score = find_most_similar(all_embeddings, query_embedding.reshape(1, -1))

    most_similar_log_info = df.iloc[most_similar_index]['ID']
    
    id_part, log_number = most_similar_log_info.split('/')[1:3]
    id_part = int(id_part) # convert ID to int

    repo = id_to_repo.get(id_part, "Unknown repository")

    if repo != "Unknown repository":
        gh_url = f"https://github.com/{repo}"
    else:
        gh_url = "Repository not found in the mapping"
    
    result = f"\nThe most similar Workflow ID is {id_part}, which belongs to {gh_url}\n\n"
    result += f"build number: {log_number}\n\n"
    result += f"similarity score: {most_similar_score}"
    return result

def create_gui():
    root = tk.Tk()
    root.title("System Log Glossary Search (SLGS)")

    def on_submit():
        log_message = log_message_entry.get("1.0", tk.END).strip()
        results = find_similar_logs(log_message)
        result_display.delete(1.0, tk.END)
        result_display.insert(tk.INSERT, results)

    tk.Label(root, text="Enter Log Message:").pack()
    log_message_entry = tk.Text(root, height=5, width=50)
    log_message_entry.pack()

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.pack()

    result_display = scrolledtext.ScrolledText(root, height=10, width=50)
    result_display.pack()

    root.mainloop()

def main():
    create_gui()

if __name__ == "__main__":
    main()
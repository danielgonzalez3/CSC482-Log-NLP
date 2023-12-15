import pandas as pd
import ast
import numpy as np
import re
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

SAMPLE_SIZE = 5000
df = pd.read_csv('merged_global_logs_embeddings.csv', nrows=SAMPLE_SIZE)
df['embeddings'] = df['embeddings'].apply(lambda x: np.array(ast.literal_eval(x)))

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
    most_similar_score = similarities.max()
    return most_similar_score

def find_similar_score(query_log):    
    preprocessed_query_log = preprocess_log(query_log)

    query_embedding = get_bert_embeddings(preprocessed_query_log)
    
    all_embeddings = np.stack(df['embeddings'].values)

    most_similar_score = find_most_similar(all_embeddings, query_embedding.reshape(1, -1))

    return most_similar_score

def main():
    SELECTION = int(SAMPLE_SIZE/2)
    sample_df = pd.read_csv('merged_global_logs.csv', nrows=SAMPLE_SIZE)
    random_entries = sample_df.sample(n=SELECTION)
    random_entries.to_csv('random_global_logs.csv', index=False)

    print(f"Selected {SELECTION} random entries.")
    total_score = 0
    for _, row in random_entries.iterrows():
        log_message = row['LOG']
        similarity_score = find_similar_score(log_message)
        total_score += similarity_score
    
    average_similarity_score = total_score / len(random_entries)
    print(f"Average similarity score: {average_similarity_score:.4f}")

if __name__ == "__main__":
    main()
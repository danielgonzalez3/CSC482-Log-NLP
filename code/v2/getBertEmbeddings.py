import pandas as pd
import re
from transformers import BertTokenizer, BertModel
import time

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def preprocess_log(log):
    log = re.sub(r'/[^ ]+', '', log)
    log = log.lower()
    return log

# generate embeddings using BERT
def get_bert_embeddings(log_message):
    inputs = tokenizer(log_message, return_tensors='pt', truncation=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()


def main():
    df = pd.read_csv('merged_global_logs.csv')
    df['embeddings'] = None

    print(f"Loaded {len(df)} log entries from the CSV file.")

    output_filename = 'merged_global_logs_embeddings.csv'

    # iterate over the DataFrame and process each log
    for index, row in df.iterrows():
        start_time = time.time()

        # preprocess the log
        preprocessed_log = preprocess_log(row['LOG'])
        df.at[index, 'preprocessed_log'] = preprocessed_log

        # generate embeddings
        embedding = get_bert_embeddings(preprocessed_log)[0]
        df.at[index, 'embeddings'] = embedding.tolist()

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Processed log {index+1}/{len(df)} (Time taken: {elapsed_time:.2f} seconds)")

    df.to_csv(output_filename, index=False)

    print(f"Embeddings saved to {output_filename}")

if __name__ == "__main__":
    main()

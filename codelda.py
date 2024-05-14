import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def progress_bar(progress, total):
    percent = 100 * (progress / total)
    bar = "█" * int(percent // 2) + "-" * (50 - int(percent // 2))
    print(f"\r|{bar}| {percent:.2f}%", end="\r")

# Initialize the filtered papers CSV file
output_file = r'D:\Capstone\filtered_output.csv'
header = ['id', 'title', 'year', 'author_name', 'author_org', 'author_id',
          'n_citation', 'doc_type', 'reference_count', 'references',
          'venue_id', 'venue_name', 'venue_type', 'doi', 'keyword',
          'volume', 'issue', 'publisher', 'weight', 'indexed_keyword',
          'inverted_index']

# Open the output CSV file in write mode
with open(output_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Write the header to the output file
    writer.writerow(header)

    # Preprocess the data
    def preprocess_text(text):
        tokens = text.split(';')
        tokens = [token.strip().lower() for token in tokens]
        return tokens

    # Create a document-term matrix
    vectorizer = CountVectorizer()

    # Train LDA model
    num_topics = 5  # Define the number of topics
    lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42)

    # Open the input CSV file
    with open(r'D:\Capstone\output.csv', 'r', newline='', encoding='utf-8') as input_file:
        reader = csv.reader(input_file)
        next(reader)  # Skip the header

        # Get the total number of records
        total_records = 4894081

        # Process each record
        for progress, row in enumerate(reader, 1):
            # Access the 'keyword' column
            keyword = row[14]  # Assuming the 'keyword' field is at index 14

            # Preprocess the keyword
            processed_keywords = preprocess_text(keyword)
            processed_keywords_text = ' '.join(processed_keywords)

            # Check if the processed text is empty
            if processed_keywords_text:
                # Create a document-term matrix
                dtm = vectorizer.fit_transform([processed_keywords_text])

                # Train LDA model
                lda_model.fit(dtm)

                # Get the topic assignment
                topic_assignment = lda_model.transform(dtm).argmax(axis=1)[0]

                # Filter papers related to CS topic
                if topic_assignment == 0:  # Define the topic number related to computer science
                    # Write the filtered paper to the output file
                    writer.writerow(row)

            # Update progress bar
            progress_bar(progress, total_records)

    # Print progress bar completion
    progress_bar(total_records, total_records)
    print()

# Output the completion message
print(f"Filtered papers flushed to {output_file}")

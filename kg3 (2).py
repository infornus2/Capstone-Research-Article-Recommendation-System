from neo4j import GraphDatabase
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# Neo4j configuration
uri = "bolt://localhost:7687"
username = "neo4j"
password = "capstone73_2"

# Directory where CSV files are stored
csv_directory = "output_directory"

# Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to process a batch of data and insert into Neo4j
def process_batch(tx, batch_data):
    for data in batch_data:
        paper_data, venue_data, author_data, keyword_data = data

        # Debugging output
        #print("Venue Name:", venue_data['venue_name'].strip())
        if(venue_data['venue_name'].strip()!=""):
            # Create or merge the Venue node
            tx.run("""
                MERGE (venue:Venue {id: $venue_id})
                ON CREATE SET venue.name = $venue_name, venue.type = $venue_type
            """, venue_id=venue_data['venue_id'], venue_name=venue_data['venue_name'].strip(), venue_type=venue_data['venue_type'])

        # Create the Paper node
        tx.run("""
            CREATE (paper:Paper {id: $id, title: $title, year: $year, n_citation: $n_citation,
                                 doc_type: $doc_type, reference_count: $reference_count,
                                 doi: $doi})
        """, **paper_data)

        # Create the PUBLISHED_IN relationship
        tx.run("""
            MATCH (paper:Paper {id: $paper_id})
            MATCH (venue:Venue {id: $venue_id})
            MERGE (paper)-[:PUBLISHED_IN]->(venue)
        """, paper_id=paper_data['id'], venue_id=venue_data['venue_id'])

        # Process authors
        for author_name, author_id, author_org in author_data:
            if pd.notna(author_name) and pd.notna(author_id) and pd.notna(author_org):
                tx.run("""
                    MERGE (author:Author {id: $author_id})
                    ON CREATE SET author.name = $author_name, author.organization = $author_org
                """, author_name=author_name, author_id=author_id, author_org=author_org)

                tx.run("""
                    MATCH (paper:Paper {id: $paper_id})
                    MATCH (author:Author {id: $author_id})
                    MERGE (author)-[:AUTHORED]->(paper)
                """, paper_id=paper_data['id'], author_id=author_id)

        # Create Keyword nodes and relationships
        for keyword in keyword_data:
            tx.run("""
                MERGE (keyword:Keyword {name: $keyword})
            """, keyword=keyword)

            tx.run("""
                MATCH (paper:Paper {id: $paper_id})
                MATCH (keyword:Keyword {name: $keyword})
                MERGE (paper)-[:HAS_KEYWORD]->(keyword)
            """, paper_id=paper_data['id'], keyword=keyword)

# Function to process a CSV file and return batches of data
def process_csv_file(file_path):
    df = pd.read_csv(file_path, encoding='utf-8')

    batch_size = 50  # Adjust the batch size as needed
    num_rows = df.shape[0]
    batches = []

    for i in range(0, num_rows, batch_size):
        batch_df = df.iloc[i:i + batch_size]
        batch_data = []

        for _, row in batch_df.iterrows():
            paper_data = row[['id', 'title', 'year', 'n_citation', 'doc_type', 'reference_count', 'doi']].to_dict()
            venue_data = row[['venue_id', 'venue_name', 'venue_type']].to_dict()
            
            # Handle author data
            author_names = row['author_name'].split(';') if isinstance(row['author_name'], str) else []
            author_ids = row['author_id'].split(';') if isinstance(row['author_id'], str) else []
            author_orgs = row['author_org'].split(';') if isinstance(row['author_org'], str) else []
            author_data = list(zip(author_names, author_ids, author_orgs))

            keyword_data = row['keyword'].split(';') if isinstance(row['keyword'], str) else []

            batch_data.append((paper_data, venue_data, author_data, keyword_data))

        batches.append(batch_data)

    return batches

# Inside the process_csv_files_in_parallel function
def process_csv_files_in_parallel(files):
    for file_path in files:
        batches = process_csv_file(file_path)
        
        # Initialize a new driver instance for each thread
        thread_driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            for batch in batches:
                executor.submit(process_batch, thread_driver.session(), batch)
        
        # Close the driver instance after processing the file
        thread_driver.close()
        
        print(f"Processed {file_path}")



if __name__ == "__main__":
    csv_files = [os.path.join(csv_directory, filename) for filename in os.listdir(csv_directory) if filename.startswith("output_") and filename.endswith(".csv")]
    
    num_threads = min(8, len(csv_files))  # Adjust the number of threads as needed
    files_per_thread = len(csv_files) // num_threads
    file_chunks = [csv_files[i:i + files_per_thread] for i in range(0, len(csv_files), files_per_thread)]
    
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(process_csv_files_in_parallel, file_chunks)
    
    print("Data insertion into Neo4j completed.")

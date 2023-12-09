#flask run --host=0.0.0.0 --port=5001

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import hashlib
import csv
from neo4j import GraphDatabase
import secrets
from flask_paginate import Pagination
import math

app = Flask(__name__, template_folder='')

# Generate a secret key
secret_key = secrets.token_hex(16)
app.secret_key = secret_key

# Define the connection parameters
uri = "bolt://localhost:7687"
username = "neo4j"
password = "capstone73_2"

# Pagination settings
PER_PAGE = 9

def get_pagination_info(page, total_count):
    return Pagination(page=page, per_page=PER_PAGE, total=total_count, css_framework="bootstrap4")

def load_domain_names():
    domain_names = []
    with open('Domain30.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            domain_names.append(row[0])
    return domain_names

def none_common(paper,contri):
    print({paper[i]: contri[i] for i in range(len(contri))})
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            res=[]
            for i in range(len(contri)):
                query=(
                    "MATCH (p1:Paper)"
                    "WHERE p1.id = $papers "
                    "MATCH (p2:Paper)"
                    "WHERE p2 <> p1 "
                    "WITH p1, p2, gds.similarity.euclideanDistance(p1.embedding, p2.embedding) as distance "
                    "ORDER BY distance "
                    "LIMIT $num "
                    "RETURN p2.title AS paper_title, p2.doc_type AS paper_type, p2.id AS paper_id,[(p2)<-[:AUTHORED]-(a:Author) | a.name] AS author_name,[(p2)-[:PUBLISHED_IN]->(v:Venue) | v.name] AS venue_name,p2.author_community AS author_community, p2.keyword_community AS keyword_community, p2.venue_community AS venue_community , distance as Distance"
                )        
                result1 = session.run(query, papers=paper[i], num=contri[i])
                intermediate = result1.data()
                res+=intermediate

    return res


def intention_recom(query_result,l):
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            paper = list(query_result)

            query = (
                "MATCH (p:Paper)"
                "WHERE p.id IN $paper "
                "RETURN p.id AS paper_id,p.author_community AS author_community, p.venue_community AS venue_community, p.keyword_community AS keyword_community;"
            )
            result = session.run(query, paper=paper)
            res = result.data()
            
            # Initialize dictionaries to store common IDs and counts
            author_ids = {}
            #apid=[]
            venue_ids = {}
            #vpid=[]
            keyword_ids = {}
            #kpid=[]

            combined_dict={0:[],1:[],2:[]}

            for entry in res:
                author_id = entry['author_community']
                venue_id= entry['venue_community']
                keyword_id = entry['keyword_community']
                pid=entry['paper_id']

                if author_id in author_ids:
                    author_ids[author_id] += 1
                    #apid.append(query_result[pid])
                    combined_dict[0].append(query_result[pid])
                else:
                    author_ids[author_id] = 1

                if venue_id in venue_ids:
                    venue_ids[venue_id] += 1
                    #vpid.append(query_result[pid])
                    combined_dict[1].append(query_result[pid])
                else:
                    venue_ids[venue_id] = 1

                if keyword_id in keyword_ids:
                    keyword_ids[keyword_id] += 1
                    #kpid.append(query_result[pid])
                    combined_dict[2].append(query_result[pid])
                else:
                    keyword_ids[keyword_id] = 1

            # Find the most common ID and the count for each type of community
            common_author_id = -1 if max(author_ids.values()) == 1 else max(author_ids, key=author_ids.get)
            common_venue_id = -1 if max(venue_ids.values()) == 1 else max(venue_ids, key=venue_ids.get)
            common_keyword_id = -1 if max(keyword_ids.values()) == 1 else max(keyword_ids, key=keyword_ids.get)

            # Create the result dictionary with tuples
            r = {
                'author_community': (common_author_id, author_ids[common_author_id] if common_author_id != -1 else 0),
                'venue_community': (common_venue_id, venue_ids[common_venue_id] if common_venue_id != -1 else 0),
                'keyword_community': (common_keyword_id, keyword_ids[common_keyword_id] if common_keyword_id != -1 else 0)
            }

            # Find the largest second value in the tuples
            max_second_value = max(t[1] for t in r.values())

            # Divide the second value in each tuple by the largest second value
            result = {key: (value[0], round(value[1] / max_second_value,2)) for key, value in r.items()}

            print(result)
            #print("Papers IDS in same author community:",apid)
            #print("Papers IDS in same venue community:",vpid)
            #print("Papers IDS in same keyword community:",kpid)

            print(combined_dict)

            # Calculating no. of recommendations

            n=10 #FIX TOTAL NO. OF RECOMMENDATIONS

            target_value = (-1, 0.0)
            check = all(value == target_value for value in result.values())
            if check:
                contri=[]
                while(sum(contri)<10):
                    x=10-sum(contri)
                    for i in query_result:
                        contri.append(math.ceil((query_result[i]/l)*x))
                
                res=none_common(paper,contri)
            
            else:
                # Calculating no. of recommendations
                total=0
                frac=[0,0,0]
                while(total<10):
                    n=10-total
                    for i in range(len(result)):
                        frac[i]+=math.ceil(((result[list(result.keys())[i]][1]*(sum(combined_dict[i])))/l)*n)
                    total=sum(frac)
                
                print(total)
                print(frac)
                """
                
                n=10
                total=0
                frac=[0,0,0]
                while(total<10):
                    n=10-total
                    for i in range(len(result)):
                        frac[i]+=math.ceil((result[list(result.keys())[i]][1]/l)*n)
                        total+=math.ceil((result[list(result.keys())[i]][1]/l)*n)
                """
                print(total)
                print(frac)

                res=[]

                # retrieving recommendations
                for i in range(len(frac)):
                    if frac[i]==0:
                        continue
                    query=(
                        "MATCH (p1:Paper)"
                        "WHERE p1.id IN $papers "
                        "MATCH (p2:Paper)"
                        "WHERE p2 <> p1 AND (CASE $community WHEN 'author_community' THEN p1.author_community = p2.author_community=$comm_id WHEN 'venue_community' THEN p1.venue_community = p2.venue_community=$comm_id WHEN 'keyword_community' THEN p1.keyword_community = p2.keyword_community=$comm_id ELSE FALSE END)"
                        "WITH p1, p2, gds.similarity.euclideanDistance(p1.embedding, p2.embedding) as distance " 
                        "ORDER BY distance "
                        "LIMIT $num "
                        "RETURN p2.title AS paper_title, p2.doc_type AS paper_type, p2.id AS paper_id,[(p2)<-[:AUTHORED]-(a:Author) | a.name] AS author_name,[(p2)-[:PUBLISHED_IN]->(v:Venue) | v.name] AS venue_name,p2.author_community AS author_community, p2.keyword_community AS keyword_community, p2.venue_community AS venue_community , distance as Distance"
                    )
                    result1 = session.run(query, papers=paper, community=list(result.keys())[i], comm_id=result[list(result.keys())[i]][0], num=frac[i])
                    intermediate = result1.data()
                    res+=intermediate
            

            res_list = [i for n, i in enumerate(res) if i not in res[:n]] #remove duplicates

            for i in res_list:
                x = i['author_name']
                i['author_name'] = ', '.join(x)
                i['venue_name']=i['venue_name'][0]
                print(i['paper_id'],end='\t')
                print(i['author_community'],end='\t')
                print(i['venue_community'],end='\t')
                print(i['keyword_community'],end='\t')
                print(i['Distance'])

            return(res_list)


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password_hash=?", (username, password_hash))
        user_id = cursor.fetchone()

        if user_id:
            session['user_id'] = user_id[0]
            #print(type(user_id[0]))
            cursor.execute("SELECT paper_id,activity_type FROM user_interests WHERE user_id=?", (str(user_id[0]),))
            query_result = cursor.fetchall()
            unique_values = {}

            for first_term, second_term in query_result:
                if first_term not in unique_values:
                    # If the first term is not in the dictionary, add it with the second term
                    unique_values[first_term] = second_term
                else:
                    # If the first term is already in the dictionary, update the second term if it's higher
                    if second_term > unique_values[first_term]:
                        unique_values[first_term] = second_term

            # Convert the dictionary back to a list of tuples
            #query_result = [(key, value) for key, value in unique_values.items()]
            

            if not unique_values:
                cursor.execute("SELECT domain FROM users WHERE id=?", (user_id[0],))
                selected_domains = cursor.fetchall()
                selected_domains = [item[0] for item in selected_domains]
                conn.close()
                return redirect(url_for('index', param=', '.join(selected_domains)))
            
            else:
                print(unique_values)
                # Convert the list elements to integers
                #paper = [int(item) for item in paper]
                l=sum(unique_values.values())
                res=intention_recom(unique_values,l)
                #print(res)
                cursor.execute('''
                            UPDATE user_interests
                            SET login = 1
                            WHERE user_id = ? AND login = 0;
                        ''', (str(user_id[0]),))

                conn.commit()
                conn.close()
                return render_template("recom.html", nodes=res)               
            

        else:
            conn.close()
            return "Invalid username or password. Please try again."
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        selected_domains = request.form.getlist('domain')

        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "Username already exists. Please choose another username."
        else:
            cursor.execute("INSERT INTO users (username, password_hash, domain) VALUES (?, ?, ?)",
                           (username, password_hash, ', '.join(selected_domains)))
            conn.commit()
            conn.close()

            return redirect(url_for('login'))
    domain_names = load_domain_names()
    return render_template("register.html", domain_names=domain_names)

def get_nodes(selected_domains):
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            query = (
                "MATCH (p:Paper)-[:HAS_KEYWORD]->(k:Keyword) "
                "WHERE k.name IN $selected_domains "
                "WITH p, COUNT(DISTINCT k) AS keywordCount, size($selected_domains) AS totalKeywords "
                "WHERE keywordCount <= totalKeywords "
                "RETURN p.title AS paper_title,p.doc_type AS paper_type, p.id AS paper_id,[(p)<-[:AUTHORED]-(a:Author) | a.name] AS author_name,[(p)-[:PUBLISHED_IN]->(v:Venue)|v.name]AS venue_name "
                "ORDER BY keywordCount DESC "
                "LIMIT 50"
            )
            result = session.run(query, selected_domains=selected_domains)
            res = result.data()
            #print(res)
            for i in res:
                x = i['author_name']
                i['author_name'] = ', '.join(x)
                i['venue_name']=i['venue_name'][0]
            return res

@app.route("/index", methods=['GET'])
def index():
    selected_domains = request.args.get('param')
    selected_domains = selected_domains.split(',')
    selected_domains = [d.strip() for d in selected_domains]
    nodes = get_nodes(selected_domains)

    # Calculate the total number of items
    total_items = len(nodes)

    # Get the current page from the query parameters
    page = request.args.get('page', type=int, default=1)

    # Calculate start and end indices for pagination
    start = (page - 1) * PER_PAGE
    end = page * PER_PAGE

    # Slice the data to display the current page's items
    nodes_to_display = nodes[start:end]


    # Use the get_pagination_info function to create a Pagination object
    pagination = get_pagination_info(page, total_items)
    
    return render_template("index.html", nodes=nodes_to_display, pagination=pagination)

@app.route("/mark_interest", methods=['POST'])
def mark_interest():
    if request.method == 'POST':
        try:
            paper_id = request.form['paper_id']
            user_id = session.get('user_id')
            activity_type = request.form['activity_type']

            a={"Download":1.0,"Read":0.5,"Summary":0.25}

            if user_id is None:
                return jsonify(success=False, message="User not authenticated")

            connection = sqlite3.connect('user.db')
            cursor = connection.cursor()

            cursor.execute('DELETE FROM user_interests WHERE user_id = ? AND login=1', (user_id,))


            
            cursor.execute('''
                INSERT INTO user_interests (user_id, paper_id, activity_type,login) VALUES (?, ?, ?, ?)
            ''', (user_id, int(paper_id), a[activity_type],0))

            connection.commit()
            connection.close()

            return jsonify(success=True)
        except Exception as e:
            print(f"Error marking interest: {str(e)}")
            return jsonify(success=False, message="An error occurred while marking interest")

    return jsonify(success=False, message="Invalid request")

# Modify your existing perform_search function to consider the new parameters
def perform_search(search_term, search_author, search_venue, search_title):
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            # Initialize the query variable
            query = ""
            print(search_author)
            print(search_venue)
            print(search_title)
            print(search_term, search_author, search_venue, search_title)
            # Adjust the query based on the selected checkboxes
            if search_author=='true':
                print("in author")
                query = (
                    "MATCH (paper)<-[r:AUTHORED]-(author)"
                    "WHERE toLower(author.name) CONTAINS toLower($search_term)"
                    "WITH paper, COLLECT(author.name) AS authors "
                    "RETURN paper.id AS paper_id, paper.title AS paper_title, paper.doc_type AS paper_type, authors AS authors,[(paper)-[:PUBLISHED_IN]->(v:Venue)|v.name] AS venue_name"
                )
            elif search_venue=='true':
                print("in venue")
                query = (
                    "MATCH (venue)<-[r:PUBLISHED_IN]-(paper)<-[r1:AUTHORED]-(author)"
                    "WHERE toLower(venue.name) CONTAINS toLower($search_term)"
                    "WITH paper, COLLECT(author.name) AS authors "
                    "RETURN paper.id AS paper_id, paper.title AS paper_title, paper.doc_type AS paper_type, authors AS authors,[(paper)-[:PUBLISHED_IN]->(v:Venue)|v.name] AS venue_name"
                )
                
            elif search_title=='true':
                print("in title")
                query = (
                    "MATCH (paper)<-[r:AUTHORED]-(author)"
                    "WHERE toLower(paper.title) CONTAINS toLower($search_term)"
                    "WITH paper, COLLECT(author.name) AS authors "
                    "RETURN paper.id AS paper_id, paper.title AS paper_title, paper.doc_type AS paper_type, authors AS authors,[(paper)-[:PUBLISHED_IN]->(v:Venue)|v.name] AS venue_name"
                )
            else:
                # Use the base query if no checkboxes are selected
                print("in else")

            # Execute the query
            result = session.run(query, search_term=search_term)
            res = result.data()

            for i in res:
                # Check if the 'author_name' key is present in the dictionary
                if 'author_name' in i:
                    x = i['author_name']
                    i['author_name'] = ', '.join(x)
                else:
                    i['author_name'] = ''  # Set a default value if 'author_name' is not present

                i['venue_name'] = i.get('venue_name', [''])[0]  # Set a default value for 'venue_name'

            return res
        
@app.route("/search", methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        
        search_author = request.form['search_author']   
        search_venue = request.form['search_venue']
        search_title = request.form['search_title']

        search_results = perform_search(search_term, search_author, search_venue, search_title)
        return jsonify(results=search_results)  # Return the results as JSON
    return render_template("search_results.html")



# Modify your existing perform_search function to consider the new parameters


if __name__ == "__main__":
    app.run(debug=False)

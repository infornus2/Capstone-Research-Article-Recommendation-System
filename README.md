
# Project Title

Research Article Recommendation System using Graph  Database


Our project aims to revolutionize research paper recommendation systems by leveraging the power of graph-based methodologies. Unlike traditional approaches that rely solely on metadata like author names and keywords, our system employs a sophisticated knowledge graph. By harnessing GraphSAGE and Community Detection algorithms within a framework like Neo4J, we uncover intricate relationships among study fields, subjects, and concepts. This enables us to offer context-aware recommendations that transcend conventional boundaries, providing researchers with fresh perspectives and cutting-edge insights. Through our innovative approach, we strive to enhance the efficiency and effectiveness of the scientific community by streamlining the process of accessing pertinent information from the ever-expanding landscape of knowledge.




## Run Locally

Clone the project

```bash
  git clone https://github.com/roslynpius/Capstone-Research-Article-Recommendation-System.git
```

Go to the project directory

```bash
  cd project-directory
```
get dataset


It runs the csv file and splits it

```bash
  python split(1).py
```
It segregates the data into domain and only cs domain is taken into consideration

```bash
  python codelda.py
```

It makes the knowledge graph from the data

```bash
  python kg3(2).py
```


## Video

![App Screenshot](https://github.com/roslynpius/Capstone-Research-Article-Recommendation-System/blob/main/73_Demo.mp4)


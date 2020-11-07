# Smash Data
Python code to query smash.gg database and process matchups.  
Integrated with Elasticsearch for easy kibana visualizations. 

# Setup:
1. Install Elasticsearch: Follow [these instructions](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html).
2. Create an index labeled `events-test`: 
```
PUT event-data
{
  "mappings": {
    "properties": {
      "timestamp": {
        "type": "date"
      }
    }
  }
}
```
3. Run the `main.py` file to begin indexing  

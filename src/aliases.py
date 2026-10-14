"""Alias lists used by the Silver layer. Keys are lowercase."""

# raw city (lowercase, brackets removed) -> canonical city
CITY_ALIASES = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "bangalore rural": "Bengaluru",
    "bangalore/bengaluru": "Bengaluru",
    "bengaluru/bangalore": "Bengaluru",
    "bengaluru / bangalore": "Bengaluru",
    "bangalore / bengaluru": "Bengaluru",
    "gurgaon": "Gurugram",
    "gurugram": "Gurugram",
    "new delhi": "Delhi",
    "delhi ncr": "Delhi",
    "delhi / ncr": "Delhi",
    "mumbai suburban": "Mumbai",
    "bombay": "Mumbai",
    "calcutta": "Kolkata",
    "madras": "Chennai",
    "poona": "Pune",
    "secunderabad": "Hyderabad",
    "hyderabad / secunderabad": "Hyderabad",
    "trivandrum": "Thiruvananthapuram",
    "cochin": "Kochi",
    "vizag": "Visakhapatnam",
    "mysore": "Mysuru",
    "baroda": "Vadodara",
    "pondicherry": "Puducherry",
    "remote": "Remote",
    "work from home": "Remote",
    "wfh": "Remote",
    "remote work": "Remote",
}

# raw skill (lowercase, trimmed) -> canonical skill key (lowercase)
SKILL_ALIASES = {
    "ms excel": "excel", "microsoft excel": "excel", "advanced excel": "excel",
    "excel advanced": "excel",
    "powerbi": "power bi", "power-bi": "power bi", "microsoft power bi": "power bi",
    "ms power bi": "power bi", "power bi desktop": "power bi",
    "tableau desktop": "tableau",
    "postgres": "postgresql", "postgre sql": "postgresql",
    "my sql": "mysql",
    "ms sql server": "sql server", "microsoft sql server": "sql server",
    "mssql": "sql server", "ms sql": "sql server",
    "structured query language": "sql",
    "py spark": "pyspark", "apache spark": "spark",
    "apache airflow": "airflow", "apache kafka": "kafka",
    "mongo db": "mongodb", "elastic search": "elasticsearch",
    "big query": "bigquery",
    "ml": "machine learning", "dl": "deep learning",
    "ai": "artificial intelligence", "nlp": "natural language processing",
    "scikit learn": "scikit-learn", "sklearn": "scikit-learn",
    "tensor flow": "tensorflow", "py torch": "pytorch",
    "gcp": "google cloud platform", "google cloud": "google cloud platform",
    "amazon web services": "aws", "aws cloud": "aws",
    "ms azure": "azure", "microsoft azure": "azure",
    "js": "javascript", "node js": "node.js", "nodejs": "node.js",
    "reactjs": "react", "react js": "react", "react.js": "react",
    "py": "python", "python programming": "python", "python 3": "python",
    "python3": "python", "python scripting": "python",
    "r programming": "r", "r language": "r",
    "data visualisation": "data visualization", "visualization": "data visualization",
    "data analytics": "data analysis",
    "etl tools": "etl", "big data analytics": "big data",
    "data warehouse": "data warehousing", "datawarehouse": "data warehousing",
    "ms office": "ms office", "microsoft office": "ms office",
    "statistical analysis": "statistics", "stats": "statistics",
}

# canonical key -> display name (anything missing gets first letter capitalised)
SKILL_DISPLAY = {
    "python": "Python", "sql": "SQL", "mysql": "MySQL", "postgresql": "PostgreSQL",
    "sql server": "SQL Server", "nosql": "NoSQL", "mongodb": "MongoDB",
    "aws": "AWS", "azure": "Azure", "google cloud platform": "Google Cloud Platform",
    "power bi": "Power BI", "tableau": "Tableau", "excel": "Excel", "looker": "Looker",
    "pyspark": "PySpark", "spark": "Spark", "hadoop": "Hadoop", "kafka": "Kafka",
    "airflow": "Airflow", "dbt": "dbt", "snowflake": "Snowflake",
    "databricks": "Databricks", "bigquery": "BigQuery", "etl": "ETL",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch", "scikit-learn": "scikit-learn",
    "llm": "LLM", "r": "R", "scala": "Scala", "java": "Java", "c++": "C++",
    "c#": "C#", ".net": ".NET", "javascript": "JavaScript", "node.js": "Node.js",
    "react": "React", "html": "HTML", "css": "CSS", "git": "Git", "docker": "Docker",
    "linux": "Linux", "elasticsearch": "Elasticsearch", "ms office": "MS Office",
    "ci/cd": "CI/CD",
}

# junk tags removed before aliasing
SKILL_STOPLIST = {"", "not available", "basic", "other", "others", "na", "n/a", "none"}
# ---- additions (round 2)
CITY_ALIASES.update({
    "temp. wfh - kolkata": "Kolkata",
    "north goa": "Goa",
    "south goa": "Goa",
})
SKILL_DISPLAY.update({"sap": "SAP"})

# Generic Naukri tags that are not specific skills; kept in the data but flagged.
SKILL_GENERIC = {
    "analytical", "data", "coding", "development", "management", "operations",
    "monitoring", "healthcare", "computer science", "cloud", "backend",
    "consulting", "analytics", "business analyst",
}

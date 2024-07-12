import json
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.request

import pandas as pd
import requests

import streamlit as st

st.title("DuckDB-NSQL-7B Demo")


def format_xpt_data(file_path):
    """
    Read an XPT file and convert byte string columns to regular strings.
    
    Args:
    file_path (str): The path to the XPT file.
    
    Returns:
    pd.DataFrame: The formatted DataFrame.
    """
    # Read the .xpt file
    df = pd.read_sas(file_path)

    # Convert byte string columns to regular strings
    for column in df.columns:
        if df[column].dtype == object:  # Check if column type is object
            df[column] = df[column].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)

    return df

df = format_xpt_data('./data/adadas.xpt')

PROMPT_TEMPLATE = """### Instruction:\n{instruction}\n\n### Input:\n{input}\n### Question:\n{question}\n\n### Response (use duckdb shorthand if possible):\n"""
INSTRUCTION_TEMPLATE = """Your task is to generate valid duckdb SQL to answer the following question{has_schema}"""  # noqa: E501
ERROR_MESSAGE = ":red[ Quack! Much to our regret, SQL generation has gone a tad duck-side-down.\nThe model is currently not able to craft a correct SQL query for this request. \nSorry my duck friend. ]\n\n:red[If the question is about your own database, make sure to set the correct schema. Otherwise, try to rephrase your request. ]\n\n```sql\n{sql_query}\n```\n\n```sql\n{error_msg}\n```"
STOP_TOKENS = ["###", ";", "--", "```"]

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.


def generate_prompt(question, schema):
    input = ""
    if schema:
        # Lowercase types inside each CREATE TABLE (...) statement
        for create_table in re.findall(
                r"CREATE TABLE [^(]+\((.*?)\);", schema, flags=re.DOTALL | re.MULTILINE
        ):
            for create_col in re.findall(r"(\w+) (\w+)", create_table):
                schema = schema.replace(
                    f"{create_col[0]} {create_col[1]}",
                    f"{create_col[0]} {create_col[1].lower()}",
                )
        input = """Here is the database schema that the SQL query will run on:\n{schema}\n""".format(  # noqa: E501
            schema=schema
        )
    prompt = PROMPT_TEMPLATE.format(
        instruction=INSTRUCTION_TEMPLATE.format(
            has_schema="." if schema == "" else ", given a duckdb database schema."
        ),
        input=input,
        question=question,
    )
    return prompt


def generate_sql_azure(question, schema):
    prompt = generate_prompt(question, schema)
    start = time.time()

    data={
        "input_data": {
            "input_string": [prompt],
            "parameters":{
                "top_p": 0.9,
                "temperature": 0.1,
                "max_new_tokens": 200,
                "do_sample": True
            }
        }
    }
    body = str.encode(json.dumps(data))

    url = 'https://motherduck-eu-west2-xbdfd.westeurope.inference.ml.azure.com/score'
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ st.secrets['azure_ai_token']), 'azureml-model-deployment': 'motherduckdb-duckdb-nsql-7b-v-1' }
    req = urllib.request.Request(url, body, headers)
    raw_resp = urllib.request.urlopen(req)
    resp = json.loads(raw_resp.read().decode("utf-8"))[0]["0"]
    sql_query = resp[len(prompt):]
    print(time.time()-start)
    return sql_query


def validate_sql(query, schema):
    try:
        # Define subprocess
        process = subprocess.Popen(
            [sys.executable, './validate_sql.py', query, schema],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Get output and potential parser, and binder error message
        stdout, stderr = process.communicate(timeout=0.5)
        if stderr:
            error_message = stderr.decode('utf8').split("\n")
            # skip traceback
            if len(error_message) > 3:
                error_message = "\n".join(error_message[3:])
            return False, error_message
        return True, ""
    except subprocess.TimeoutExpired:
        process.kill()
        # timeout reached, so parsing and binding was very likely successful
        return True, ""


expander = st.expander("Customize Schema (Optional)")
expander.markdown(
    "If you DuckDB database is `database.duckdb`, execute this query in your terminal to get your current schema:"
)
expander.markdown(
    """```bash\necho ".schema" | duckdb database.duckdb | sed 's/(/(\\n    /g' | sed 's/, /,\\n    /g' | sed 's/);/\\n);\\n/g'\n```""",
)

# Input field for text prompt
default_schema = """

"""


schema = expander.text_area("Current schema:", value=default_schema, height=500)

# Input field for text prompt
text_prompt = st.text_input(
    "What DuckDB SQL query can I write for you?", value="Read a CSV file from test.csv"
)

if text_prompt:
    sql_query = generate_sql_azure(text_prompt, schema)
    valid, msg = validate_sql(sql_query, schema)
    if not valid:
        st.markdown(ERROR_MESSAGE.format(sql_query=sql_query, error_msg=msg))
    else:
        st.markdown(f"""```sql\n{sql_query}\n```""")

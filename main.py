from rich.console import Console
import sql_metadata
import rich_click
import sqlparse
import openai
import rich
import time
import json
import os

console = Console()
console.clear()

api_key = os.environ.get("API_KEY")
if not api_key:
    print("API_KEY not set in .env")
    exit(1)

client = openai.OpenAI(api_key=api_key)

ANNOTATED_FILE = os.environ.get("ANNOTATED_FILE")
if not ANNOTATED_FILE:
    console.print("ANNOTATED_FILE not set in .env\nDefault: annotated.json")
    ANNOTATED_FILE = "annotated.json"

def annotate_queries():
    global ANNOTATED_FILE
    global client

    DATA_FILE = os.environ.get("DATA_FILE")
    if not DATA_FILE:
        console.print("DATA_FILE not set in .env\nDefault: queries.json")
        DATA_FILE = "queries.json"

    with open(DATA_FILE) as f:
        data = json.loads(f.read())

    annotated_data = []

    for i, query in enumerate(data):
        console.print(f"[bold #87C3AA]{i} [#308673]/ [#87C3AA]{len(data)}\n")

        console.print(f"[bold #C7E8D3]{query["question"]}[/bold #C7E8D3]\n")
        console.print(sqlparse.format(query["sql"], reindent=True, keyword_case='upper'), highlight=False)
        completion = client.chat.completions.create(
          model="gpt-4o",
          messages=[
            {"role": "system", "content": "For the following Natural Language description of a SQL query, please list the topics involved in the query. We are looking for topics that a column in the database might correspond to. Please give the answer as solely a comma separated, with no spaces after the commas, list of topics in as they appear in the input."},
            {"role": "user", "content": f"Natural Lanauge: {query['question']}"},
          ]
        )

        topics = completion.choices[0].message.content

        assert(topics is not None)
        console.print(f"[bold #C7E8D3]{topics}\n")
        annotated_data.append({
            "question": query["question"],
            "sql": query["sql"],
            "topics": topics.split(",")
        })

        # write as we go, in case of interruption
        # data (for now) is small enough where no performance hit

        assert(ANNOTATED_FILE is not None)
        with open(ANNOTATED_FILE, "w") as f:
            f.write(json.dumps(annotated_data, indent=4))

        console.clear()

    console.print("Done annotating queries.")
    time.sleep(2) 
    console.clear()
    

def map_queries():
    global ANNOTATED_FILE
    global client

    MAPPED_FILE = os.environ.get("MAPPED_FILE")
    if not MAPPED_FILE:
        console.print("MAPPED_FILE not set in .env\nDefault: mapped.json")
        MAPPED_FILE = "mapped.json"

    assert(ANNOTATED_FILE is not None)
    if not os.path.exists(ANNOTATED_FILE):
        console.print("Please run --annotate first.")
        exit(1)

    with open(ANNOTATED_FILE) as f:
        data = json.loads(f.read())

    mapping = []

    for i, query in enumerate(data):
        console.print(f"[bold #87C3AA]{i} [#308673]/ [#87C3AA]{len(data)}\n")

        console.print(f"[bold #C7E8D3]{query["question"]}[/bold #C7E8D3]\n")
        console.print(sqlparse.format(query["sql"], reindent=True, keyword_case='upper'), highlight=False)
        console.print(f"\n[bold #C7E8D3]{query["topics"]}\n")

        metadata = sql_metadata.Parser(query["sql"])
        try:
            mapping.append({"progress": "unprocessed"})
            columns = metadata.columns + metadata.columns_aliases_names

            completion = client.chat.completions.create(
              model="gpt-4o",
              messages=[
                {"role": "system", "content": "The following will give four sections of (1) natural language (2) SQL query (3) natural language concepts (4) columns of interest in the SQL query. Your job is to give a mapping of natural language concepts to columns of interest in the sql query. it might be the case that there is more than one column per concept, and rarely the same column of interest may be used in multiple concepts. Answer EXACTLY as a single json map where the concept is the key as a string and the value is a list of columns of interest as strings. Give as plaintext and do NOT wrap in a code block. Make sure to give a mapping for each concept if possible, and use exact values as given. If needed use the SQL query itself as well as the original natural language description to help you."},
                {"role": "user", "content": f"Natural Language: {query['question']}\nSQL: {query['sql']}\nConcepts: {query['topics']}\nColumns: {columns}"},
              ]
            )

            strmap = completion.choices[0].message.content
            assert(strmap is not None)

            mapping[-1] = {"progress": strmap}
            mapping[-1] = json.loads(strmap)
        except:
            console.print("[red]Error parsing SQL[/red]")
            time.sleep(2)

        with open(MAPPED_FILE, "w") as f:
            f.write(json.dumps(mapping, indent=4))

        console.clear()

    console.print("Done mapping queries.")
    time.sleep(2)


#######
# CLI #
#######

@rich_click.command()
@rich_click.option(
    "--annotate",
    is_flag=True,
    default=False,
    help="Annotate the queries with topics. Run FIRST before mapping."
)
@rich_click.option(
    "--map",
    is_flag=True,
    default=False,
    help="Map topics to columns. Make sure to run --annotate first."
)
def main(annotate, map):
    """CLI Utility to map topics to columns in NL - SQL pairs"""

    if not annotate and not map:
        print("Please specify --annotate or --map. Run with --help for more info.")
        exit(1)

    if annotate:
        annotate_queries()
    if map:
        map_queries()

if __name__ == '__main__':
    main()


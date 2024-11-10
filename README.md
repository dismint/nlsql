<div align="center">
  
# NLSQL [![Email](https://img.shields.io/badge/EMAIL-mintjjc%40gmail.com-93BFCF?style=flat&logoSize=auto&labelColor=EEE9DA)](mailto:mintjjc@gmail.com)

[Overview](#overview) • [Implementation](#implementation)

</div>

# Overview 🗺️

This project aims to map natural language to its SQL counterpart by associating topics in NL to columns in SQL. The project is built entirely using Python 3 and was run in an x86-64 Linux development environment. The project should run locally cross platform. To develop locally, make sure to catch up on the dependencies:

```bash
# install dependencies from requirements.txt

pip install -r requirements.txt
```

The project makes use of a `.env` file to set environment variables, including the sensitive OpenAI api key. The following are the available options for the `.env` file. The `API_KEY` is the only field that must be set, all other fields will be set to the shown values by default.

```bash
API_KEY        = <API_KEY>
DATA_FILE      = queries.json
ANNOTATED_FILE = annotated.json
MAPPED_FILE    = mapped.json
```

# Implementation 🔬

NLSQL consists of two main steps, which can be selected from the CLI. They can run independently, but `annotate` must be run to generate a `annotated.json` before `map` can be used.

<div align="center">
  
![](imgs/cli.png)

</div>

## Annotation

The first step is to create topics from the natural language of each query. The objective is to locate ideas that would map to columns in the actual SQL database. We use `gpt-4o` to automatically transform `queries.json` into `annotated.json`, which contains an additional field per entry which is a list of topics. The file can be manually verified after generated.

```json
[
  {
    "question": "What is the current building key, building street address, city, state, and postal code of the history department?",
    "sql": "SELECT DISTINCT d.FCLT_BUILDING_KEY, e.BUILDING_STREET_ADDRESS, d.CITY, d.STATE, d.POSTAL_CODE FROM FCLT_BUILDING_ADDRESS d JOIN FCLT_ROOMS a ON a.FCLT_BUILDING_KEY = d.FCLT_BUILDING_KEY JOIN FCLT_ORG_DLC_KEY b ON a.FCLT_ORGANIZATION_KEY = b.FCLT_ORGANIZATION_KEY JOIN MASTER_DEPT_HIERARCHY c ON b.DLC_KEY = c.DLC_KEY JOIN BUILDINGS e ON e.BUILDING_KEY = d.FCLT_BUILDING_KEY WHERE lower(c.DLC_NAME) = lower('History') AND d.ADDRESS_PURPOSE = 'STREET';",
    "topics": [
      "building key",
      "building street address",
      "city",
      "state",
      "postal code"
    ]
  },
  {
    "question": "Show the unique activity titles, locations, term start date, and supervisor name for all independent activities, sorted by the ascending order of start date.",
    "sql": "SELECT DISTINCT a.activity_title, d.session_location, c.term_start_date, b.person_name AS Leader FROM iap_subject_detail a JOIN iap_subject_person b ON a.iap_subject_person_key = b.iap_subject_person_key JOIN academic_terms_all c ON c.term_code = a.term_code JOIN iap_subject_session d ON a.iap_subject_session_key = d.iap_subject_session_key WHERE b.person_role = 'Activity leader' ORDER BY term_start_date ASC;",
    "topics": [
      "activity titles",
      "locations",
      "term start date",
      "supervisor name"
    ]
  }
]
```

## Mapping

The final step is to map the generated topics to their respective column(s) in the SQL query. The topics are the same from the previous step, and the columns are generated from the result of parsing with the [`sql_metadata`](https://pypi.org/project/sql_metadata/) library, which provides a variety of information from columns and their aliases to tables and subqueries.

If the query is well formatted SQL, the library will be able to easily parse it into its columns. However there is at one current entry in the dataset that cannot parse due to the usage of RegEx (INDEX 11)

The results are again run with `gpt-4o` to pair them appropriately. Verification can be done on the output file as described below.

## Final Output

The final output is generated as a JSON file that contains a list of mappings from topics to columns in the same order as they were given in the input query.

```json
[
  {
    "building key": ["FCLT_BUILDING_ADDRESS.FCLT_BUILDING_KEY"],
    "building street address": ["BUILDINGS.BUILDING_STREET_ADDRESS"],
    "city": ["FCLT_BUILDING_ADDRESS.CITY"],
    "state": ["FCLT_BUILDING_ADDRESS.STATE"],
    "postal code": ["FCLT_BUILDING_ADDRESS.POSTAL_CODE"]
  },
  {
    "activity titles": ["iap_subject_detail.activity_title"],
    "locations": ["iap_subject_session.session_location"],
    "term start date": [
      "academic_terms_all.term_start_date",
      "term_start_date"
    ],
    "supervisor name": ["iap_subject_person.person_name", "Leader"]
  }
]
```

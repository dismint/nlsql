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

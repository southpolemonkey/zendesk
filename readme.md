# Zendesk bot

Zendesk code challenge

## Description

A minimal app to query data with an interactive shell. The `zendesk` module is implemented in command design pattern with a decouple architecture where connects backend and frontend logic through processor.

The app supports yaml configuration which enables users to easily declare new relationships.

## Get Started

Clone the repo first


### Running with Docker

```
make build
make run
```
You should now enter the shell 

```
 _____                  __          __      __          __ 
/__  /  ___  ____  ____/ /__  _____/ /__   / /_  ____  / /_
  / /  / _ \/ __ \/ __  / _ \/ ___/ //_/  / __ \/ __ \/ __/
 / /__/  __/ / / / /_/ /  __(__  ) ,<    / /_/ / /_/ / /_  
/____/\___/_/ /_/\__,_/\___/____/_/|_|  /_.___/\____/\__/  
                                                           

  Commands:
      help                                Show help information
      clear                               Clear terminal
      quit                                Exit the shell

      load                                Load data 
      search                              Enter interactive query mode
      search <entity> <field> <value>     e.g. search tickets submitter_id 71    
      show db                             List all tables 
      show table                          List all fields are supported for searching
      


```

### Running from source

Required python version: >3.8
```
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Using `setuptool` 

You can also use setuptool to install which come with an executable `zbot`
```
python -m venv venv && source venv/bin/activate
pip install -e .
```

```
(shell)$ zbot 
...
```


## Usage

Declare new tables in `config.yaml`. User should provide corrsponding json fields under `zendesk/resources/<table_name>.json` 

```yaml
tables:
  <table_name>:
    primary_key: <field_name>
    index:
      - <field_name>
    # optional, external fields are retrieved when querying  <table_name>  
    external_fields: 
      - external_table_name: <table_name>
        external_table_key: <field_name>
        local_table_key: <field_name>
        required_fields:
          - field: <field_name>
            alias: <alias_name>
```

## Development Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
```

Run test cases
```
make test
```

## Project Structure

```bash
zendesk/
  db.py             Containers Database, Table and Index class. Table class implements Index which enables 
                    fast access to the elements. 
  model.py          Contains data model class
  processor.py      Contains class handling incoming user requests
  utilies           helper functions
  zendesk_bot       frontend logic
tests               
logs                
app.py              entrypoint
```


## Assumptions
- The db loads data by default from `zendesk/resourcs/<table_name>.json` with table_name declared in `config.yaml`  
- Current versiono supports single field as primary key only whereas composite is not supported yet.
- The search supports two type of match 
  - Exact value match
  - If field contains a list, entire field is returned once search value matches any keywords in the list. e.g. `search tickets tags a` will match the record contains `tags:['a','b','c']` 
- The app assume data can be loaded into memory and so query result is returned in a list. Although often not the case in real world application, **lazy load techniques** e.g. generator can be used to handle the senario if needed. Also python built-in `json.load()` method does not support an iterator interface, third-party package e.g. [ijson](https://pypi.org/project/ijson/) can be used under certain use cases.
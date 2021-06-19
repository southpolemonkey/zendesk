# Zendesk bot


## Get Started

Clone the repo first 

```
git clone https://github.com/southpolemonkey/zendesk.git && cd zendesk
``` 

To run the app, choose one of the methods blow

1) Docker (Suggested)

```
make build
make run
```
You are now inside the shell 

```
 _____                  __          __      __          __ 
/__  /  ___  ____  ____/ /__  _____/ /__   / /_  ____  / /_
  / /  / _ \/ __ \/ __  / _ \/ ___/ //_/  / __ \/ __ \/ __/
 / /__/  __/ / / / /_/ /  __(__  ) ,<    / /_/ / /_/ / /_  
/____/\___/_/ /_/\__,_/\___/____/_/|_|  /_.___/\____/\__/  
                                                           

Command: : help

    Commands:
        help
        search
        search <entity> <field> <value>
        load
        quit
        fields
    
```

2) Running locally. The app is developed in python 3.8.5 so make sure you have python >3.8 installed. 
```
python -m venv venv && source venv/bin/activate
pip install -r requirements
python app.py
```

3) The last method is to install the package and run with command `zbot`
```
python -m venv venv && source venv/bin/activate
pip install -e .
```

```
(shell)$ zbot 
 _____                  __          __      __          __ 
/__  /  ___  ____  ____/ /__  _____/ /__   / /_  ____  / /_
  / /  / _ \/ __ \/ __  / _ \/ ___/ //_/  / __ \/ __ \/ __/
 / /__/  __/ / / / /_/ /  __(__  ) ,<    / /_/ / /_/ / /_  
/____/\___/_/ /_/\__,_/\___/____/_/|_|  /_.___/\____/\__/  
     
```


## Project Structure

```bash
zendesk/
  db.py             Containers Database, Table and Index class. Table implements index to enable 
                    fast access to the elements. 
  model.py          Contains data model class for users, tickers and organizations
  processor.py      Contains class handling incoming user requests
  utilies           helper functions
  zendesk_bot       Interactive part

app.py              entrypoint to zendesk_bot
```


## Assumptions

# jedeschule-api

API for the jedeschule.de project

Deployed at https://jedeschule.codefor.de/

API-Documentation at https://jedeschule.codefor.de/docs


## Setup
Before you start, make sure to have a postgres database running and accepting connections.

The database should be in the latest migration state as per the 
migrations in the [jedeschule-scraper repository](https://github.com/datenschule/jedeschule-scraper).

In order to run the application locally in development mode, execute the following commands.
```bash
#(optional) create a virtual enviornment
export DATABASE_URL=<YOUR_DB_CONFIG> # e.g. postgres://postgres@0.0.0.0:5432/jedeschule
pip install -r requirements.txt
pip install uvicorn
uvicorn app.main:app --reload
```
This will start a server which automatically restarts on file changes.
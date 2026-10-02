# Jira

## Description

Various scripts for working with Jira tickets.

## Specific Requirements

- Having a `.env` file defining the following variables:

JIRA_URL
JIRA_EMAIL
JIRA_TOKEN

## Scripts

### [compile_countries_in_countries.py](compile_countries_in_countries.py)

Scans the given ticket IDs and compiles the set of country codes referenced across them.

### [compile_locales_in_countries.py](compile_locales_in_countries.py)

Scans the given ticket IDs and compiles the set of locale codes referenced across them.

### [export_subtask_statuses.py](export_subtask_statuses.py)

Exports the status of every subtask under the given parent tickets to an Excel file.

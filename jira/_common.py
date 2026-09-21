import os
import sys

from dotenv import load_dotenv
from jira import JIRA
from mtlogger import logger

load_dotenv()

def get_jira_url():
  return os.getenv('JIRA_URL')

def get_jira_email():
  return os.getenv('JIRA_EMAIL')

def get_jira_token():
  return os.getenv('JIRA_TOKEN')

def get_jira_vars():
  jira_url = get_jira_url()
  jira_email = get_jira_email()
  jira_token = get_jira_token()

  if not all([jira_url, jira_email, jira_token]):
    logger.error('Missing required JIRA environment variables:')
    logger.error('  - JIRA_URL')
    logger.error('  - JIRA_EMAIL')
    logger.error('  - JIRA_TOKEN')
    sys.exit(1)

  return jira_url, jira_email, jira_token

def get_jira_client():
  jira_url, jira_email, jira_token = get_jira_vars()

  try:
    client = JIRA(server=jira_url, basic_auth=(jira_email, jira_token))
    logger.success(f'Connected to {jira_url}')
    return client
  except Exception as ex:
    logger.error(f'Failed to connect to {jira_url}: {ex}')
    sys.exit(1)

import os
import re
import sys
import threading

from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from jira import JIRA
from jira.resources import Issue
from mtlogger import logger
from tqdm import tqdm

load_dotenv()

_jira_client = None
_jira_client_lock = threading.Lock()

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
  global _jira_client

  if _jira_client is not None:
    return _jira_client

  with _jira_client_lock:
    if _jira_client is not None:
      return _jira_client

    jira_url, jira_email, jira_token = get_jira_vars()

    try:
      _jira_client = JIRA(server=jira_url, basic_auth=(jira_email, jira_token))
      logger.debug(f'Connected to {jira_url}')
      return _jira_client
    except Exception as ex:
      logger.error(f'Failed to connect to {jira_url}: {ex}')
      sys.exit(1)

def find_in_issue_ids(issue_ids: list[str], pattern: re.Pattern):
  combined = set()

  with ThreadPoolExecutor() as executor:
    futures = {executor.submit(fetch_and_find_in_issue, issue_id, pattern): issue_id for issue_id in issue_ids}

    for future in tqdm(as_completed(futures), total=len(issue_ids), desc='Processing issues', unit='issue'):
      matches = future.result()
      if matches:
        combined.update(matches)

  return combined

def fetch_and_find_in_issue(issue_id: str, pattern: re.Pattern):
  try:
    issue = get_jira_client().issue(issue_id.strip())
  except Exception as ex:
    logger.error(f'Failed to fetch {issue_id}: {ex}')
    return None

  return find_in_issue(issue, pattern)

def find_in_issue(issue: Issue, pattern: re.Pattern):
  text = f'{issue.fields.summary or ""}\n{issue.fields.description or ""}'
  matches = set(pattern.findall(text))
  logger.log(f'{issue.key}:\n  [{", ".join(sorted(matches))}]\n')

  return matches

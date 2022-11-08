import fire
import logging

from configManager import ConfigManager
from customLogger import CustomLogger
from seafile import Seafile
from ldapClient import LdapClient

import requests

def main(config="/etc/seafile/ldapsync.yml", v=False, vv=False):
# Setup Logger
  logger = CustomLogger('[Seafile - LDAPSync]')

  if (v):
    logger.setLevel(logging.INFO)

  if (vv):
    logger.setLevel(logging.DEBUG)

  # Load Config
  config = ConfigManager(logger, config).config

  # Connect seafile
  seafile = Seafile(logger, config["seafile"])
  seafile.refreshAccessToken()

  # Connect ldap
  ldap = LdapClient(logger, config["ldap"])
  
  groups = seafile.fetchGroups()
  ldap_accounts = ldap.fetchAccounts()

  for group in groups:
    group_member = []
    group_member_emails = []
    for account_key in ldap_accounts:
        account = ldap_accounts[account_key]
        if "memberOf" in account and group["name"] in account["memberOf"]:
            group_member.append(account)
            group_member_emails.append(account["mail"])

    seafile.addGroupMember(group["id"], group_member_emails)

if __name__ == '__main__':
    fire.Fire(main)
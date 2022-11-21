import fire
import logging

from configManager import ConfigManager
from customLogger import CustomLogger
from seafile import Seafile
from ldapClient import LdapClient

import requests


def checkIfMemberOf(memberOf: str, groupName: str, account, group_members, group_member_emails, seafile_member_emails, group_member_emails_new, logger) -> bool:
  if groupName in memberOf:
    group_members.append(account)
    group_member_emails.append(account["mail"])

    if account["mail"] not in seafile_member_emails:
      logger.debug(" ---> Adding account " + account["cn"])
      group_member_emails_new.append(account["mail"])

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

  admin_email = config["seafile"]["admin"] 
  only_sync_admingroups = config["seafile"]["only_sync_admingroups"]

  logger.info("Syncing Groups...")

  for group in groups:
    logger.debug("Processing group " + group["name"])

    if (only_sync_admingroups and group["owner"] != admin_email):
      logger.debug("Only Admingroupsync is enabled, skipping ...")
      continue

    # Fetching a list of all members of a group in seafile
    seafile_member_emails = seafile.fetchGroupMembers(group["id"])
    seafile_member_emails = list(map(lambda member: member["email"], seafile_member_emails))

    group_members = []
    group_member_emails = []
    group_member_emails_new = []

    for account_key in ldap_accounts:
        account = ldap_accounts[account_key]

        if "memberOf" in account:
            if (isinstance(account["memberOf"], str)):
              checkIfMemberOf(account["memberOf"], group["name"], account, group_members, group_member_emails, seafile_member_emails, group_member_emails_new, logger)
            
            else:
              for memberOf in account["memberOf"]:
                if checkIfMemberOf(memberOf, group["name"], account, group_members, group_member_emails, seafile_member_emails, group_member_emails_new, logger):
                              continue

    for member in seafile_member_emails:
      if member != admin_email and member not in group_member_emails:
        logger.debug(" ---> Removing member " + member)
        seafile.removeGroupMember(group["id"], member)

    seafile.addGroupMember(group["id"], group_member_emails_new)

if __name__ == '__main__':
    fire.Fire(main)

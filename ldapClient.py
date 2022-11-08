import ldap

from logging import Logger

from interfaces.ldapConfig import LdapConfig

class LdapClient:
    def __init__(self, logger: Logger, settings: LdapConfig):
        self.logger = logger
        self.server = settings["server"]
        self.base = settings["base"]
        self.people = settings["people"]
        self.ldapserver = ldap.initialize(self.server)
        return

    def fetchAccounts(self):
        ldap_accounts = {}

        account_search = self.ldapserver.search_s(self.people, ldap.SCOPE_SUBTREE, '(objectClass=inetOrgPerson)', ['uid', 'cn', 'memberof', 'mail'])
        for dn,entry in account_search:
            for key in entry:
                if len(entry[key]) == 1:
                    entry[key] = entry[key][0].decode('utf-8')
                else:
                    entry[key] = list(map(lambda elem: elem.decode('utf-8'), entry[key]))

            ldap_accounts[entry['uid']] = entry
        return ldap_accounts
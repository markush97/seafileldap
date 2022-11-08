from interfaces.seafileConfig import SeafileConfig
from logging import Logger

import requests

class Seafile:
    def __init__(self, logger: Logger, settings: SeafileConfig):
        self.logger = logger
        self.username = settings["username"]
        self.password = settings["password"]
        self.server = settings["server"]
        return

    def refreshAccessToken(self):
        response = requests.post(self.server + "/api2/auth-token/", json = {'password': self.password, 'username': self.username})
        self.token = response.json()["token"]
        self.authHeader = {'Authorization': 'Token ' + self.token}
        return self.token

    def fetchGroups(self):
        response = requests.get(self.server + "/api/v2.1/admin/groups/", headers=self.authHeader)
        groups = response.json()["groups"]
        return groups

    def fetchGroupMembers(self, groupId: int):
        response = requests.get(self.server + "/api/v2.1/admin/groups/" + str(groupId) + "/members/", headers=self.authHeader)
        members = response.json()["members"]
        return members

    def addGroupMember(self, groupId: int, memberEmails):
        members = []

        for email in memberEmails:
            members.append(('email', (None, email)))

        response = requests.post(self.server + "/api/v2.1/admin/groups/" + str(groupId) + "/members/", headers=self.authHeader, files=members)
    
    def removeGroupMember(self, groupId: int, memberEmail: str):
        response = requests.delete(self.server + "/api/v2.1/admin/groups/" + str(groupId) + "/members/" + str(memberEmail), headers=self.authHeader)

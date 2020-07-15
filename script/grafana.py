from grafana_api.grafana_api import GrafanaClientError, GrafanaBadInputError
from grafana_api.grafana_face import GrafanaFace
from .config import *
from .helpers import *

grafana_api = ""
configuration = ""


def setup_grafana():
    global grafana_api, configuration
    configuration = config()
    grafana_api = GrafanaFace(
        auth=configuration.GRAFANA_AUTH,
        host=configuration.GRAFANA_URL
    )


def delete_team_by_name(name):
    """
    Deletes a team with a given name.
    :param name: The name if the Team to be deleted.
    :return: Returns True if the team to be deleted existed, returns False if it did not.
    """
    team_data = grafana_api.teams.get_team_by_name(name)
    if len(team_data) > 0:
        for data_set in team_data:
            grafana_api.teams.delete_team(data_set["id"])
        return True
    return False


def create_team(name, mail):
    """
    Creates a team with the given name and mail.
    :param name: The name of the team.
    :param mail: The mail of the team.
    :return: The API response.
    """
    return grafana_api.teams.add_team({
        "name": name,
        "mail": mail
    })


def create_user_with_random_pw(user):
    """
    Creates a user from a dictionary resembling a user. Generates a random alphanumerical String as password.
    :param user: The dictionary off of which the user should be created.
    """
    grafana_api.admin.create_user({
        "login": user["login"],
        "password": get_random_alphanumerical(),
        "OrgId": 1
    })


def delete_user_by_login(login):
    """
    Deletes the user with the given login.
    :param login: The login of the user to be deleted.
    :return: The response of the api.
    """
    if not login == "admin":
        return grafana_api.admin.delete_user(grafana_api.users.find_user(login)["id"])
    return False


def create_folder(folder_name, folder_uuid):
    """
    Creates a folder with a given name and uuid. Returns the api-response if the folder was create successfully.
    If an error occurs, false is returned.
    :param folder_name: The name of the folder to be created.
    :param folder_uuid: The uuid of the folder to be created.
    :return: The api-response if the folder was create successfully. If an error occurs, false is returned.
    """
    try:
        return grafana_api.folder.create_folder(folder_name, folder_uuid)
    except GrafanaClientError:
        return False


def add_user_to_team(login, team):
    """
    Adds the user with the given login to the team with the given name.
    :param login: The login of the user to be added to the team.
    :param team: The team the user should be added to.
    """
    try:
        grafana_api.teams.add_team_member(get_id_of_team(team), get_id_by_login(login))
    except GrafanaBadInputError:
        return False


def get_members_of_team(team):
    """
    Returns an array containing all members of the team carrying the given name. Each user is represented by a
    dictionary consisting of "name", "email" and "login"
    :param team: The name of the team the members should be returned of.
    :return: An array containing all users as described above.
    """
    result = []
    users = grafana_api.teams.get_team_members(grafana_api.teams.get_team_by_name(team)[0]["id"])
    if users is not None:
        for user in users:
            result.append({"login": user["login"]})
    return result


def remove_member_from_team(grafana_team, user_login):
    grafana_api.teams.remove_team_member(get_id_of_team(grafana_team), get_id_by_login(user_login))


def login_taken(login):
    """
    Checks if a given grafana-login is already taken. Returns True if the login is taken.
    :param login: the grafana-login which should be checked.
    :return: True if the grafana-login is already taken, False if the login is available.
    """
    try:
        grafana_api.users.find_user(login)
        return True
    except GrafanaClientError:
        return False


def get_id_by_login(login):
    """
    Returns the id of a grafana-login.
    :param login: the grafana-login the id should be returned from.
    :return: The id of the given login.
    """
    return grafana_api.users.find_user(login)["id"]


def exists_folder(uid):
    """
    Checks if a folder with the given uid exists in grafana.
    :param uid: The uid of the folder that should be checked.
    :return: Returns True if the folder exists, otherwise False is returned.
    """
    try:
        grafana_api.folder.get_folder(uid)
        return True
    except GrafanaClientError:
        return False


def get_id_of_team(team):
    """
    Returns the id of the grafana team with the given name.
    :param team: The name of the grafana team.
    :return: The id of the grafana team with the given name. Returns False if the Team does not exist.
    """
    teams = grafana_api.teams.get_team_by_name(team)
    if len(teams) < 1:
        return False
    return teams[0]["id"]


def update_folder_permissions(folder_id, permissions):
    """
    Sets the given permissions for the folder found under the given id
    """
    grafana_api.folder.update_folder_permissions(folder_id, {"items": permissions})


def get_all_teams():
    """
    Returns all teams present in the connected grafana instance.
    """
    return grafana_api.teams.search_teams()


def get_all_users():
    """
    Returns all users present in the connected grafana instance.
    """
    user_logins = []
    users = grafana_api.users.search_users()
    if users is not None:
        for user in users:
            user_logins.append({"login": user["login"]})
    return user_logins

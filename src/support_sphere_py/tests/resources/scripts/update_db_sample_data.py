import csv
import datetime
import uuid

from pathlib import Path

from support_sphere.models.public import (UserProfile, People, Cluster, PeopleGroup, Household,
                                          RolePermission, UserRole, UserCaptainCluster)
from support_sphere.models.auth import User
from support_sphere.repositories.auth import UserRepository
from support_sphere.repositories.base_repository import BaseRepository
from support_sphere.repositories.public import UserProfileRepository, UserRoleRepository, PeopleRepository
from support_sphere.repositories import supabase_client

from support_sphere.models.enums import AppRoles, AppPermissions, OperationalStatus

import logging

logger = logging.getLogger(__name__)


def populate_user_details():
    """
        This utility function populates your local supabase database tables with sample data entries.
    """

    all_households = BaseRepository.select_all(Household)

    file_path = Path("./support_sphere_py/tests/resources/data/sample_data.csv")
    with file_path.open(mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            user_profile = None
            if bool(eval(row['has_profile'])):
                # Create a auth.user with encrypted_password (ONLY FOR LOCAL TESTING)
                supabase_client.auth.sign_up({"email": row['email'], "password": row['username']})
                supabase_client.auth.sign_out()
                user: User = UserRepository.find_by_email(row['email'])

                # Create a user profile
                profile = UserProfile(username=row['username'], user=user)
                UserProfileRepository.add(profile)
                user_profile = UserProfileRepository.find_by_username(row['username'])

                user_role = UserRole(user_profile=user_profile, role=AppRoles.USER)
                BaseRepository.add(user_role)

            # Create People Entry
            person_detail = People(given_name=row['given_name'], family_name=row['family_name'],
                                   is_safe=bool(eval(row['is_safe'])), needs_help=bool(eval(row['needs_help'])),
                                   accessibility_needs=bool(eval(row['accessibility_needs'])),
                                   user_profile=user_profile)

            person = PeopleRepository.add(person_detail)

            # Create a PeopleGroup Entry
            people_group = PeopleGroup(people=person, household=all_households[-1])
            BaseRepository.add(people_group)
    logger.info("Database Populated Successfully")


def populate_cluster_and_household_details():
    # Creating entries in 'Cluster' and 'Household' table.
    cluster = Cluster(name="Cluster1")
    BaseRepository.add(cluster)
    all_clusters = BaseRepository.select_all(Cluster)

    household = Household(cluster=all_clusters[-1], name="Household1")
    BaseRepository.add(household)


def authenticate_user_signup_signin_signout_via_supabase():
    # The password is stored in an encrypted format in the auth.users table
    response_sign_up = supabase_client.auth.sign_up({"email": "zeta@abc.com", "password": "zetazeta"})
    supabase_client.auth.sign_out()
    response_sign_in = supabase_client.auth.sign_in_with_password({"email": "zeta@abc.com", "password": "zetazeta"})
    supabase_client.auth.sign_out()


def update_user_permissions_roles_by_cluster():
    role_1 = RolePermission(role=AppRoles.ADMIN, permission=AppPermissions.OPERATIONAL_EVENT_READ)
    role_2 = RolePermission(role=AppRoles.ADMIN, permission=AppPermissions.OPERATIONAL_EVENT_CREATE)
    role_3 = RolePermission(role=AppRoles.COM_ADMIN, permission=AppPermissions.OPERATIONAL_EVENT_CREATE)
    role_4 = RolePermission(role=AppRoles.COM_ADMIN, permission=AppPermissions.OPERATIONAL_EVENT_READ)
    role_5 = RolePermission(role=AppRoles.SUBCOM_AGENT, permission=AppPermissions.OPERATIONAL_EVENT_READ)

    BaseRepository.add(role_1)
    BaseRepository.add(role_2)
    BaseRepository.add(role_3)
    BaseRepository.add(role_4)
    BaseRepository.add(role_5)

    user_profile = UserProfileRepository.find_by_username('adamabacus')
    user_role = UserRoleRepository.find_by_user_profile_id(user_profile.id)
    user_role.role = AppRoles.SUBCOM_AGENT
    BaseRepository.add(user_role)

    all_clusters = BaseRepository.select_all(Cluster)
    cluster_role = UserCaptainCluster(cluster=all_clusters[-1], user_role=user_role)
    BaseRepository.add(cluster_role)

    user_profile = UserProfileRepository.find_by_username('bethbodmas')
    user_role = UserRoleRepository.find_by_user_profile_id(user_profile.id)
    user_role.role = AppRoles.COM_ADMIN
    BaseRepository.add(user_role)


def test_app_mode_status_update():
    response_sign_in = supabase_client.auth.sign_in_with_password(
        {"email": "beth.bodmas@example.com", "password": "bethbodmas"})

    user_profile = UserProfileRepository.find_by_username('bethbodmas')
    supabase_client.table("operational_events").insert({"id": str(uuid.uuid4()),
                                                        "created_by": str(user_profile.id),
                                                        "created_at": datetime.datetime.now().isoformat(),
                                                        "status": OperationalStatus.EMERGENCY.name}).execute()

    supabase_client.table("operational_events").insert({"id": str(uuid.uuid4()),
                                                        "created_by": str(user_profile.id),
                                                        "created_at": datetime.datetime.now().isoformat(),
                                                        "status": OperationalStatus.TEST.name}).execute()

    supabase_client.table("operational_events").insert({"id": str(uuid.uuid4()),
                                                        "created_by": str(user_profile.id),
                                                        "created_at": datetime.datetime.now().isoformat(),
                                                        "status": OperationalStatus.NORMAL.name}).execute()
    supabase_client.auth.sign_out()


def test_unauthorized_app_mode_update():
    try:
        response_sign_in = supabase_client.auth.sign_in_with_password(
            {"email": "adam.abacus@example.com", "password": "adamabacus"})
        user_profile = UserProfileRepository.find_by_username('adamabacus')
        supabase_client.table("operational_events").insert({"id": str(uuid.uuid4()),
                                                            "created_by": str(user_profile.id),
                                                            "created_at": datetime.datetime.now().isoformat(),
                                                            "status": OperationalStatus.EMERGENCY.name}).execute()
    except Exception as ex:
        logger.info(ex)
        logger.info("[CORRECT BEHAVIOUR]: User Denied Access for missing AUTHz.")
    finally:
        supabase_client.auth.sign_out()


if __name__ == '__main__':

    authenticate_user_signup_signin_signout_via_supabase()
    populate_cluster_and_household_details()
    populate_user_details()
    update_user_permissions_roles_by_cluster()
    test_app_mode_status_update()
    test_unauthorized_app_mode_update()

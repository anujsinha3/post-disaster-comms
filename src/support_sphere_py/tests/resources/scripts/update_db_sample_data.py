import csv
import yaml
from pathlib import Path
from supabase import create_client, Client

from support_sphere.models.public import UserProfile, People, Cluster, PeopleGroup, Household
from support_sphere.models.auth import User
from support_sphere.repositories.auth import UserRepository
from support_sphere.repositories.base_repository import BaseRepository
from support_sphere.repositories.public import UserProfileRepository, PeopleRepository

import logging

logger = logging.getLogger(__name__)


def populate_user_details(supabase: Client):
    """
        This utility function populates your local supabase database tables with sample data entries.
    """

    all_households = BaseRepository.select_all(Household)

    file_path = Path("./src/support_sphere_py/tests/resources/data/sample_data.csv")
    with file_path.open(mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            user_profile = None
            if bool(eval(row['has_profile'])):

                # Create a auth.user with encrypted_password (ONLY FOR LOCAL TESTING)
                supabase.auth.sign_up({"email": row['email'], "password": row['username']})
                supabase.auth.sign_out()
                user: User = UserRepository.find_by_email(row['email'])

                # Create a user profile
                profile = UserProfile(username=row['username'], user=user)
                UserProfileRepository.add(profile)
                user_profile = UserProfileRepository.find_by_username(row['username'])

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


def get_supabase_client() -> Client:

    # Setting up the supabase client for python
    file_path = Path("./deployment/values.dev.yaml")
    with file_path.open(mode='r') as file:
        config = yaml.safe_load(file)
        url = config['studio']['environment']['SUPABASE_PUBLIC_URL']
        key = config['secret']['jwt']['anonKey']

    supabase: Client = create_client(url, key)
    return supabase


def authenticate_user_signup_signin_signout_via_supabase(supabase: Client):

    # The password is stored in an encrypted format in the auth.users table
    response_sign_up = supabase.auth.sign_up({"email": "zeta@abc.com", "password": "zetazeta"})
    logger.info(response_sign_up)
    supabase.auth.sign_out()
    response_sign_in = supabase.auth.sign_in_with_password({"email": "zeta@abc.com", "password": "zetazeta"})
    logger.info(response_sign_in)
    supabase.auth.sign_out()


if __name__ == '__main__':

    supabase = get_supabase_client()

    authenticate_user_signup_signin_signout_via_supabase(supabase)
    populate_cluster_and_household_details()
    populate_user_details(supabase)
    


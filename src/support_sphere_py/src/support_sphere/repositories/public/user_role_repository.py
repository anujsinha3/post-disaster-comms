import uuid
from typing import Optional

from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from support_sphere.models.public import UserRole
from support_sphere.repositories.base_repository import BaseRepository


class UserRoleRepository(BaseRepository):


    @classmethod
    def select_all(cls) -> list[UserRole]:
        """
        Retrieves all `UserRole` records from the database.

        Returns
        -------
        list[UserRole]
            A list of all `UserRole` records.
        """
        return super().select_all(UserRole)

    @staticmethod
    def find_by_user_profile_id(user_profile_id: uuid.uuid4, fetch_user_profile: bool = False) -> Optional[UserRole]:
        """
        Finds a `UserRole` record by the associated `user_profile_id` with optional eager loading of the related `UserProfile`.

        Parameters
        ----------
        user_profile_id : str
            The `user_profile_id` alias (public.user_profiles.id) to search for in the `UserRole` model.
        fetch_user_profile : bool, optional
            Whether to fetch the related `UserProfile` entity (default is False).

        Returns
        -------
        Optional[UserRole]
            The `UserRole` object if found, otherwise None.
        """
        with Session(UserRoleRepository.repository_engine) as session:
            statement = UserRoleRepository._build_search_query(fetch_user_profile)
            statement = statement.where(UserRole.user_profile_id == user_profile_id)
            user_profile = session.exec(statement).one_or_none()
            return user_profile

    @staticmethod
    def _build_search_query(fetch_user_profile: bool = False):
        """
        Builds a SQL query to search for `UserRole` records with optional eager loading of the `UserProfile`.

        Parameters
        ----------
        fetch_user_profile : bool, optional
            Whether to eagerly load the related `UserProfile` entity (default is False).

        Returns
        -------
        sqlalchemy.sql.Select
            A query object ready to be executed for searching `UserRole` records.
        """
        statement = select(UserRole)
        # Add eager loading options based on flags
        statement = statement.options(joinedload(UserRole.user_profile)) if fetch_user_profile else statement

        return statement

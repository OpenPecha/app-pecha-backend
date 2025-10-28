import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from jose import JWTError
from jose.exceptions import JWTClaimsError
from jwt import ExpiredSignatureError
from starlette import status
from uuid import uuid4
from typing import List

from pecha_api.plans.authors.plan_authors_service import (
    validate_and_extract_author_details,
    get_author_details,
    update_author_info,
    get_authors,
    update_social_profiles,
    get_selected_author_details,
    get_plans_by_author,
    _get_author_details_by_id,
    _get_author_social_profile
)
from pecha_api.plans.authors.plan_authors_model import Author, AuthorSocialMediaAccount
from pecha_api.plans.authors.plan_authors_response_models import (
    AuthorInfoResponse,
    AuthorInfoRequest,
    SocialMediaProfile,
    AuthorsResponse
)
from pecha_api.users.users_enums import SocialProfile
from pecha_api.error_contants import ErrorConstants
import jose


class TestValidateAndExtractAuthorDetails:
    """Test cases for validate_and_extract_author_details function."""

    @patch('pecha_api.plans.authors.plan_authors_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_authors_service.get_author_by_email')
    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_success(
        self, 
        mock_validate_token, 
        mock_get_author_by_email, 
        mock_session_local
    ):
        """Test successful token validation and author extraction."""
        # Arrange
        token = "valid_token"
        expected_payload = {"email": "test@example.com"}
        expected_author = MagicMock(spec=Author)
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_validate_token.return_value = expected_payload
        mock_get_author_by_email.return_value = expected_author

        # Act
        result = validate_and_extract_author_details(token)

        # Assert
        assert result == expected_author
        mock_validate_token.assert_called_once_with(token)
        mock_get_author_by_email.assert_called_once_with(db=mock_db_session, email="test@example.com")

    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_missing_email(
        self, 
        mock_validate_token
    ):
        """Test token validation when email is missing from payload."""
        # Arrange
        token = "token_without_email"
        mock_validate_token.return_value = {"name": "test_user"}  # No email field

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_none_email(
        self, 
        mock_validate_token
    ):
        """Test token validation when email is None in payload."""
        # Arrange
        token = "token_with_none_email"
        mock_validate_token.return_value = {"email": None}

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_expired_signature_error(
        self, 
        mock_validate_token
    ):
        """Test handling of ExpiredSignatureError from jwt library."""
        # Arrange
        token = "expired_token"
        mock_validate_token.side_effect = ExpiredSignatureError("Token has expired")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_jose_expired_signature_error(
        self, 
        mock_validate_token
    ):
        """Test handling of jose.ExpiredSignatureError."""
        # Arrange
        token = "expired_token"
        mock_validate_token.side_effect = jose.ExpiredSignatureError("Token has expired")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_jwt_claims_error(
        self, 
        mock_validate_token
    ):
        """Test handling of JWTClaimsError."""
        # Arrange
        token = "invalid_claims_token"
        mock_validate_token.side_effect = JWTClaimsError("Invalid claims")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_value_error(
        self, 
        mock_validate_token
    ):
        """Test handling of ValueError."""
        # Arrange
        token = "invalid_token"
        mock_validate_token.side_effect = ValueError("Invalid token format")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_jwt_error(
        self, 
        mock_validate_token
    ):
        """Test handling of JWTError."""
        # Arrange
        token = "jwt_error_token"
        mock_validate_token.side_effect = JWTError("JWT error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_authors_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_authors_service.get_author_by_email')
    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_database_error(
        self, 
        mock_validate_token, 
        mock_get_author_by_email, 
        mock_session_local
    ):
        """Test handling of database session error."""
        # Arrange
        token = "valid_token"
        expected_payload = {"email": "test@example.com"}
        mock_validate_token.return_value = expected_payload
        mock_session_local.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_and_extract_author_details(token)

        assert str(exc_info.value) == "Database connection error"

    @patch('pecha_api.plans.authors.plan_authors_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_authors_service.get_author_by_email')
    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_author_not_found(
        self, 
        mock_validate_token, 
        mock_get_author_by_email, 
        mock_session_local
    ):
        """Test handling when author is not found in database."""
        # Arrange
        token = "valid_token"
        expected_payload = {"email": "nonexistent@example.com"}
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_validate_token.return_value = expected_payload
        mock_get_author_by_email.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "User not found"

    @patch('pecha_api.plans.authors.plan_authors_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_authors_service.get_author_by_email')
    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_logging_debug_called(
        self, 
        mock_validate_token, 
        mock_get_author_by_email, 
        mock_session_local
    ):
        """Test that logging.debug is called for exceptions."""
        # Arrange
        token = "invalid_token"
        mock_validate_token.side_effect = ValueError("Invalid token format")

        # Act & Assert
        with patch('pecha_api.plans.authors.plan_authors_service.logging.debug') as mock_logging:
            with pytest.raises(HTTPException):
                validate_and_extract_author_details(token)
            
            mock_logging.assert_called_once_with("exception: Invalid token format")

    @patch('pecha_api.plans.authors.plan_authors_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_authors_service.get_author_by_email')
    @patch('pecha_api.plans.authors.plan_authors_service.validate_token')
    def test_validate_and_extract_author_details_database_session_context_manager(
        self, 
        mock_validate_token, 
        mock_get_author_by_email, 
        mock_session_local
    ):
        """Test that database session is properly used as context manager."""
        # Arrange
        token = "valid_token"
        expected_payload = {"email": "test@example.com"}
        expected_author = MagicMock(spec=Author)
        mock_db_session = MagicMock()
        mock_session_context = MagicMock()
        mock_session_context.__enter__.return_value = mock_db_session
        mock_session_local.return_value = mock_session_context
        mock_validate_token.return_value = expected_payload
        mock_get_author_by_email.return_value = expected_author

        # Act
        result = validate_and_extract_author_details(token)

        # Assert
        assert result == expected_author
        mock_session_local.assert_called_once()
        mock_session_context.__enter__.assert_called_once()
        mock_session_context.__exit__.assert_called_once()
        mock_get_author_by_email.assert_called_once_with(db=mock_db_session, email="test@example.com")


class TestDataFactory:
    """Factory class for creating test data objects."""
    
    @staticmethod
    def create_mock_author(
        author_id=None,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        bio="Test bio",
        image_url="test-image.jpg",
        social_accounts=None
    ) -> MagicMock:
        """Create a mock Author object with specified attributes."""
        mock_author = MagicMock(spec=Author)
        mock_author.id = author_id or uuid4()
        mock_author.first_name = first_name
        mock_author.last_name = last_name
        mock_author.email = email
        mock_author.bio = bio
        mock_author.image_url = image_url
        mock_author.social_media_accounts = social_accounts or []
        return mock_author
    
    @staticmethod
    def create_mock_social_account(
        platform_name="FACEBOOK",
        profile_url="https://facebook.com/johndoe"
    ) -> MagicMock:
        """Create a mock AuthorSocialMediaAccount object."""
        mock_account = MagicMock(spec=AuthorSocialMediaAccount)
        mock_account.platform_name = platform_name
        mock_account.profile_url = profile_url
        return mock_account
    
    @staticmethod
    def create_author_info_request(
        firstname="John",
        lastname="Doe",
        image_url="https://s3.amazonaws.com/bucket/test-image.jpg",
        bio="Updated bio",
        social_profiles=None
    ) -> AuthorInfoRequest:
        """Create an AuthorInfoRequest object."""
        if social_profiles is None:
            social_profiles = [
                SocialMediaProfile(
                    account=SocialProfile.FACEBOOK,
                    url="https://facebook.com/johndoe"
                )
            ]
        
        return AuthorInfoRequest(
            firstname=firstname,
            lastname=lastname,
            image_url=image_url,
            bio=bio,
            social_profiles=social_profiles
        )


class TestGetAuthors:
    """Test cases for get_authors function."""
    
    @patch('pecha_api.plans.authors.plan_authors_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_authors_service.get_all_authors')
    @patch('pecha_api.plans.authors.plan_authors_service.generate_presigned_access_url')
    @patch('pecha_api.plans.authors.plan_authors_service.get')
    @patch('pecha_api.plans.authors.plan_authors_service._get_author_social_profile')
    @pytest.mark.asyncio
    async def test_get_authors_success(
        self,
        mock_get_social_profile,
        mock_get_config,
        mock_generate_presigned_url,
        mock_get_all_authors,
        mock_session_local
    ):
        """Test successful retrieval of all authors."""
        # Arrange
        bucket_name = "test-bucket"
        presigned_url = "https://s3.amazonaws.com/test-bucket/test-image.jpg"
        
        mock_social_account = TestDataFactory.create_mock_social_account()
        mock_authors = [
            TestDataFactory.create_mock_author(social_accounts=[mock_social_account]),
            TestDataFactory.create_mock_author(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com"
            )
        ]
        
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_get_all_authors.return_value = mock_authors
        mock_get_config.return_value = bucket_name
        mock_generate_presigned_url.return_value = presigned_url
        mock_get_social_profile.return_value = [
            SocialMediaProfile(account=SocialProfile.FACEBOOK, url="https://facebook.com/johndoe")
        ]
        
        # Act
        result = await get_authors()
        
        # Assert
        assert isinstance(result, AuthorsResponse)
        assert len(result.authors) == 2
        assert result.skip == 0
        assert result.limit == 20
        assert result.total == 2
        
        # Verify first author
        first_author = result.authors[0]
        assert first_author.id == mock_authors[0].id
        assert first_author.firstname == mock_authors[0].first_name
        assert first_author.lastname == mock_authors[0].last_name
        assert first_author.email == mock_authors[0].email
        assert first_author.bio == mock_authors[0].bio
        assert first_author.image_url == presigned_url
        
        # Verify function calls
        mock_get_all_authors.assert_called_once_with(db=mock_db_session)
        mock_get_config.assert_called_with("AWS_BUCKET_NAME")
        assert mock_generate_presigned_url.call_count == 2
    
    @patch('pecha_api.plans.authors.plan_authors_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_authors_service.get_all_authors')
    @patch('pecha_api.plans.authors.plan_authors_service.generate_presigned_access_url')
    @patch('pecha_api.plans.authors.plan_authors_service.get')
    @patch('pecha_api.plans.authors.plan_authors_service._get_author_social_profile')
    @pytest.mark.asyncio
    async def test_get_authors_empty_list(
        self,
        mock_get_social_profile,
        mock_get_config,
        mock_generate_presigned_url,
        mock_get_all_authors,
        mock_session_local
    ):
        """Test get_authors when no authors exist."""
        # Arrange
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_get_all_authors.return_value = []
        
        # Act
        result = await get_authors()
        
        # Assert
        assert isinstance(result, AuthorsResponse)
        assert len(result.authors) == 0
        assert result.skip == 0
        assert result.limit == 20
        assert result.total == 0
        
        mock_get_all_authors.assert_called_once_with(db=mock_db_session)


class TestGetAuthorDetails:
    """Test cases for get_author_details function."""
    
    @patch('pecha_api.plans.authors.plan_authors_service.generate_presigned_access_url')
    @patch('pecha_api.plans.authors.plan_authors_service.get')
    @patch('pecha_api.plans.authors.plan_authors_service._get_author_social_profile')
    @patch('pecha_api.plans.authors.plan_authors_service.validate_and_extract_author_details')
    @pytest.mark.asyncio
    async def test_get_author_details_success(
        self,
        mock_validate_and_extract,
        mock_get_social_profile,
        mock_get_config,
        mock_generate_presigned_url
    ):
        """Test successful retrieval of author details."""
        # Arrange
        token = "valid_token"
        bucket_name = "test-bucket"
        presigned_url = "https://s3.amazonaws.com/test-bucket/test-image.jpg"
        
        mock_social_account = TestDataFactory.create_mock_social_account()
        mock_author = TestDataFactory.create_mock_author(
            social_accounts=[mock_social_account]
        )
        social_profiles = [
            SocialMediaProfile(account=SocialProfile.FACEBOOK, url="https://facebook.com/johndoe")
        ]
        
        mock_validate_and_extract.return_value = mock_author
        mock_get_social_profile.return_value = social_profiles
        mock_get_config.return_value = bucket_name
        mock_generate_presigned_url.return_value = presigned_url
        
        # Act
        result = await get_author_details(token)
        
        # Assert
        assert isinstance(result, AuthorInfoResponse)
        assert result.id == mock_author.id
        assert result.firstname == mock_author.first_name
        assert result.lastname == mock_author.last_name
        assert result.email == mock_author.email
        assert result.bio == mock_author.bio
        assert result.image_url == presigned_url
        assert result.social_profiles == social_profiles
        
        # Verify function calls
        mock_validate_and_extract.assert_called_once_with(token=token)
        mock_get_social_profile.assert_called_once_with(author=mock_author)
        mock_get_config.assert_called_once_with("AWS_BUCKET_NAME")
        mock_generate_presigned_url.assert_called_once_with(
            bucket_name=bucket_name,
            s3_key=mock_author.image_url
        )


class TestUpdateSocialProfiles:
    """Test cases for update_social_profiles function."""
    
    def test_update_social_profiles_add_new_profile(self):
        """Test adding new social media profiles."""
        # Arrange
        author_id = uuid4()
        mock_author = TestDataFactory.create_mock_author(author_id=author_id)
        mock_author.social_media_accounts = []
        
        social_profiles = [
            SocialMediaProfile(
                account=SocialProfile.FACEBOOK,
                url="https://facebook.com/johndoe"
            )
        ]
        
        # Act
        update_social_profiles(mock_author, social_profiles)
        
        # Assert
        assert len(mock_author.social_media_accounts) == 1
        new_account = mock_author.social_media_accounts[0]
        assert new_account.author_id == author_id
        assert new_account.platform_name == "FACEBOOK"
        assert new_account.profile_url == "https://facebook.com/johndoe"
    
    def test_update_social_profiles_update_existing_profile(self):
        """Test updating existing social media profiles."""
        # Arrange
        author_id = uuid4()
        existing_account = TestDataFactory.create_mock_social_account(
            platform_name="FACEBOOK",
            profile_url="https://facebook.com/oldjohndoe"
        )
        mock_author = TestDataFactory.create_mock_author(
            author_id=author_id,
            social_accounts=[existing_account]
        )
        
        social_profiles = [
            SocialMediaProfile(
                account=SocialProfile.FACEBOOK,
                url="https://facebook.com/newjohndoe"
            )
        ]
        
        # Act
        update_social_profiles(mock_author, social_profiles)
        
        # Assert
        assert len(mock_author.social_media_accounts) == 1
        existing_account.profile_url = "https://facebook.com/newjohndoe"
    
    def test_update_social_profiles_empty_list(self):
        """Test update_social_profiles with empty social profiles list."""
        # Arrange
        mock_author = TestDataFactory.create_mock_author()
        mock_author.social_media_accounts = []
        
        # Act
        update_social_profiles(mock_author, [])
        
        # Assert
        assert len(mock_author.social_media_accounts) == 0
    
    def test_update_social_profiles_none_list(self):
        """Test update_social_profiles with None social profiles."""
        # Arrange
        mock_author = TestDataFactory.create_mock_author()
        mock_author.social_media_accounts = []
        
        # Act
        update_social_profiles(mock_author, None)
        
        # Assert
        assert len(mock_author.social_media_accounts) == 0


class TestUpdateAuthorInfo:
    """Test cases for update_author_info function."""
    
    @patch('pecha_api.plans.authors.plan_authors_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_authors_service.update_author')
    @patch('pecha_api.plans.authors.plan_authors_service.update_social_profiles')
    @patch('pecha_api.plans.authors.plan_authors_service.Utils.extract_s3_key')
    @patch('pecha_api.plans.authors.plan_authors_service.validate_and_extract_author_details')
    @pytest.mark.asyncio
    async def test_update_author_info_success(
        self,
        mock_validate_and_extract,
        mock_extract_s3_key,
        mock_update_social_profiles,
        mock_update_author,
        mock_session_local
    ):
        """Test successful author info update."""
        # Arrange
        token = "valid_token"
        s3_key = "test-image.jpg"
        
        mock_author = TestDataFactory.create_mock_author()
        updated_author = TestDataFactory.create_mock_author(
            first_name="Updated John",
            last_name="Updated Doe"
        )
        author_info_request = TestDataFactory.create_author_info_request()
        
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_validate_and_extract.return_value = mock_author
        mock_extract_s3_key.return_value = s3_key
        mock_update_author.return_value = updated_author
        
        # Act
        result = await update_author_info(token, author_info_request)
        
        # Assert
        assert result == updated_author
        assert mock_author.first_name == author_info_request.firstname
        assert mock_author.last_name == author_info_request.lastname
        assert mock_author.bio == author_info_request.bio
        assert mock_author.image_url == s3_key
        
        # Verify function calls
        mock_validate_and_extract.assert_called_once_with(token=token)
        mock_extract_s3_key.assert_called_once_with(presigned_url=author_info_request.image_url)
        mock_db_session.add.assert_called_once_with(mock_author)
        mock_update_social_profiles.assert_called_once_with(
            author=mock_author,
            social_profiles=author_info_request.social_profiles
        )
        mock_update_author.assert_called_once_with(db=mock_db_session, author=mock_author)
    
    @patch('pecha_api.plans.authors.plan_authors_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_authors_service.update_author')
    @patch('pecha_api.plans.authors.plan_authors_service.update_social_profiles')
    @patch('pecha_api.plans.authors.plan_authors_service.Utils.extract_s3_key')
    @patch('pecha_api.plans.authors.plan_authors_service.validate_and_extract_author_details')
    @patch('pecha_api.plans.authors.plan_authors_service.logging.error')
    @pytest.mark.asyncio
    async def test_update_author_info_database_error(
        self,
        mock_logging_error,
        mock_validate_and_extract,
        mock_extract_s3_key,
        mock_update_social_profiles,
        mock_update_author,
        mock_session_local
    ):
        """Test update_author_info when database operation fails."""
        # Arrange
        token = "valid_token"
        s3_key = "test-image.jpg"
        
        mock_author = TestDataFactory.create_mock_author()
        author_info_request = TestDataFactory.create_author_info_request()
        
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_validate_and_extract.return_value = mock_author
        mock_extract_s3_key.return_value = s3_key
        mock_update_author.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_author_info(token, author_info_request)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Internal Server Error"
        
        # Verify rollback was called
        mock_db_session.rollback.assert_called_once()
        mock_logging_error.assert_called_once_with("Failed to update user info: Database error")


class TestGetSelectedAuthorDetails:
    """Test cases for get_selected_author_details function."""
    
    @patch('pecha_api.plans.authors.plan_authors_service.generate_presigned_access_url')
    @patch('pecha_api.plans.authors.plan_authors_service.get')
    @patch('pecha_api.plans.authors.plan_authors_service._get_author_social_profile')
    @patch('pecha_api.plans.authors.plan_authors_service._get_author_details_by_id')
    @pytest.mark.asyncio
    async def test_get_selected_author_details_success(
        self,
        mock_get_author_by_id,
        mock_get_social_profile,
        mock_get_config,
        mock_generate_presigned_url
    ):
        """Test successful retrieval of selected author details."""
        # Arrange
        author_id = uuid4()
        bucket_name = "test-bucket"
        presigned_url = "https://s3.amazonaws.com/test-bucket/test-image.jpg"
        
        mock_author = TestDataFactory.create_mock_author(author_id=author_id)
        social_profiles = [
            SocialMediaProfile(account=SocialProfile.FACEBOOK, url="https://facebook.com/johndoe")
        ]
        
        mock_get_author_by_id.return_value = mock_author
        mock_get_social_profile.return_value = social_profiles
        mock_get_config.return_value = bucket_name
        mock_generate_presigned_url.return_value = presigned_url
        
        # Act
        result = await get_selected_author_details(author_id)
        
        # Assert
        assert isinstance(result, AuthorInfoResponse)
        assert result.id == mock_author.id
        assert result.firstname == mock_author.first_name
        assert result.lastname == mock_author.last_name
        assert result.email == mock_author.email
        assert result.bio == mock_author.bio
        assert result.image_url == presigned_url
        assert result.social_profiles == social_profiles
        
        # Verify function calls
        mock_get_author_by_id.assert_called_once_with(author_id=author_id)
        mock_get_social_profile.assert_called_once_with(author=mock_author)


class TestGetPlansByAuthor:
    """Test cases for get_plans_by_author function."""
    
    @patch('pecha_api.plans.authors.plan_authors_service.convert_plan_model_to_dto')
    @patch('pecha_api.plans.authors.plan_authors_service.load_plans_from_json')
    @patch('pecha_api.plans.authors.plan_authors_service._get_author_details_by_id')
    @patch('pecha_api.plans.authors.plan_authors_service.PlansResponse')
    @pytest.mark.asyncio
    async def test_get_plans_by_author_success(
        self,
        mock_plans_response,
        mock_get_author_by_id,
        mock_load_plans,
        mock_convert_plan
    ):
        """Test successful retrieval of plans by author."""
        # Arrange
        author_id = uuid4()
        author_id_str = str(author_id)
        
        mock_author = TestDataFactory.create_mock_author(author_id=author_id)
        
        # Mock plan objects
        mock_plan1 = MagicMock()
        mock_plan1.status = "PUBLISHED"
        mock_plan1.author.id = author_id_str
        
        mock_plan2 = MagicMock()
        mock_plan2.status = "DRAFT"
        mock_plan2.author.id = author_id_str
        
        mock_plan3 = MagicMock()
        mock_plan3.status = "PUBLISHED"
        mock_plan3.author.id = str(uuid4())  # Different author
        
        mock_plans_listing = MagicMock()
        mock_plans_listing.plans = [mock_plan1, mock_plan2, mock_plan3]
        
        mock_plan_dto = MagicMock()
        mock_response = MagicMock()
        
        mock_get_author_by_id.return_value = mock_author
        mock_load_plans.return_value = mock_plans_listing
        mock_convert_plan.return_value = mock_plan_dto
        mock_plans_response.return_value = mock_response
        
        # Act
        result = await get_plans_by_author(author_id, skip=0, limit=20)
        
        # Assert
        assert result == mock_response
        
        # Verify function calls
        mock_get_author_by_id.assert_called_once_with(author_id=author_id)
        mock_load_plans.assert_called_once()
        mock_convert_plan.assert_called_once_with(mock_plan1)
        mock_plans_response.assert_called_once_with(
            plans=[mock_plan_dto],
            skip=0,
            limit=20,
            total=1
        )
    
    @patch('pecha_api.plans.authors.plan_authors_service.convert_plan_model_to_dto')
    @patch('pecha_api.plans.authors.plan_authors_service.load_plans_from_json')
    @patch('pecha_api.plans.authors.plan_authors_service._get_author_details_by_id')
    @patch('pecha_api.plans.authors.plan_authors_service.PlansResponse')
    @pytest.mark.asyncio
    async def test_get_plans_by_author_pagination(
        self,
        mock_plans_response,
        mock_get_author_by_id,
        mock_load_plans,
        mock_convert_plan
    ):
        """Test pagination in get_plans_by_author."""
        # Arrange
        author_id = uuid4()
        author_id_str = str(author_id)
        
        mock_author = TestDataFactory.create_mock_author(author_id=author_id)
        
        # Create multiple published plans for the same author
        mock_plans = []
        for i in range(5):
            mock_plan = MagicMock()
            mock_plan.status = "PUBLISHED"
            mock_plan.author.id = author_id_str
            mock_plans.append(mock_plan)
        
        mock_plans_listing = MagicMock()
        mock_plans_listing.plans = mock_plans
        
        mock_plan_dto = MagicMock()
        mock_response = MagicMock()
        
        mock_get_author_by_id.return_value = mock_author
        mock_load_plans.return_value = mock_plans_listing
        mock_convert_plan.return_value = mock_plan_dto
        mock_plans_response.return_value = mock_response
        
        # Act
        result = await get_plans_by_author(author_id, skip=2, limit=2)
        
        # Assert
        assert result == mock_response
        
        # Verify function calls
        mock_get_author_by_id.assert_called_once_with(author_id=author_id)
        mock_load_plans.assert_called_once()
        # Verify convert_plan was called for the paginated plans (5 total plans)
        assert mock_convert_plan.call_count == 5
        mock_plans_response.assert_called_once_with(
            plans=[mock_plan_dto, mock_plan_dto],  # 2 plans after pagination
            skip=2,
            limit=2,
            total=5
        )


class TestGetAuthorDetailsById:
    """Test cases for _get_author_details_by_id function."""
    
    @patch('pecha_api.plans.authors.plan_authors_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_authors_service.get_author_by_id')
    @pytest.mark.asyncio
    async def test_get_author_details_by_id_success(
        self,
        mock_get_author_by_id,
        mock_session_local
    ):
        """Test successful retrieval of author by ID."""
        # Arrange
        author_id = uuid4()
        mock_author = TestDataFactory.create_mock_author(author_id=author_id)
        
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_get_author_by_id.return_value = mock_author
        
        # Act
        result = await _get_author_details_by_id(author_id)
        
        # Assert
        assert result == mock_author
        mock_get_author_by_id.assert_called_once_with(db=mock_db_session, author_id=author_id)


class TestGetAuthorSocialProfile:
    """Test cases for _get_author_social_profile function."""
    
    @patch('pecha_api.plans.authors.plan_authors_service.get_social_profile')
    def test_get_author_social_profile_success(
        self,
        mock_get_social_profile
    ):
        """Test successful conversion of author social profiles."""
        # Arrange
        mock_social_accounts = [
            TestDataFactory.create_mock_social_account("FACEBOOK", "https://facebook.com/johndoe"),
            TestDataFactory.create_mock_social_account("X_COM", "https://x.com/johndoe")
        ]
        mock_author = TestDataFactory.create_mock_author(social_accounts=mock_social_accounts)
        
        mock_get_social_profile.side_effect = [SocialProfile.FACEBOOK, SocialProfile.X_COM]
        
        # Act
        result = _get_author_social_profile(mock_author)
        
        # Assert
        assert len(result) == 2
        
        assert result[0].account == SocialProfile.FACEBOOK
        assert result[0].url == "https://facebook.com/johndoe"
        
        assert result[1].account == SocialProfile.X_COM
        assert result[1].url == "https://x.com/johndoe"
        
        # Verify function calls
        assert mock_get_social_profile.call_count == 2
        mock_get_social_profile.assert_any_call(value="FACEBOOK")
        mock_get_social_profile.assert_any_call(value="X_COM")
    
    @patch('pecha_api.plans.authors.plan_authors_service.get_social_profile')
    def test_get_author_social_profile_empty(
        self,
        mock_get_social_profile
    ):
        """Test _get_author_social_profile with no social accounts."""
        # Arrange
        mock_author = TestDataFactory.create_mock_author(social_accounts=[])
        
        # Act
        result = _get_author_social_profile(mock_author)
        
        # Assert
        assert len(result) == 0
        mock_get_social_profile.assert_not_called()

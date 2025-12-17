from google.oauth2 import service_account
from googleapiclient.discovery import build
import structlog
from .google_api_retrier import GoogleApiRetrier
from googleapiclient.errors import HttpError


logger = structlog.get_logger("import_services")


class GoogleWorkspaceClient:
    """
    Initializes and authenticates with the Google Admin SDK using a service account and provides
    access to Directory API endpoints for organizational units, users, and groups.
    """

    # https://developers.google.com/workspace/admin/directory/v1/guides/authorizing
    SCOPES = [
        "https://www.googleapis.com/auth/admin.directory.orgunit.readonly",
        "https://www.googleapis.com/auth/admin.directory.user.readonly",
        "https://www.googleapis.com/auth/admin.directory.user.alias.readonly",
        "https://www.googleapis.com/auth/admin.directory.customer.readonly"
    ]

    def __init__(self, service_account_info, admin_email):
        self._service_account_info = service_account_info
        self._admin_email = admin_email
        self.customer_id = None
        self.directory = None

        # Create retrier instance for all API calls
        self.retrier = GoogleApiRetrier(max_tries=5, base=1, ceiling=5)

        if not self._admin_email:
            raise ValueError("Delegated admin email is required but not provided.")

    @property
    def service_account_info(self):
        return self._service_account_info

    @property
    def admin_email(self):
        return self._admin_email

    def authenticate(self):
        """Authenticate with Google Workspace and determine customer_id."""
        credentials = service_account.Credentials.from_service_account_info(
            self._service_account_info,
            scopes=self.SCOPES,
        )

        delegated_credentials = credentials.with_subject(self._admin_email)
        self.directory = build("admin", "directory_v1", credentials=delegated_credentials)

        logger.info("Attempting to fetch customer_id")

        try:
            # Use retrier for API call
            customer_info = self.retrier.run(
                lambda: self.directory.customers().get(customerKey='my_customer').execute()
            )
            self.customer_id = customer_info.get('id')
            logger.info("Fetched customer_id via customers.get", customer_id=self.customer_id)
        except HttpError as e:
            if e.resp.status == 403:
                logger.info("Insufficient permissions for customers.get, using fallback")

                if self._admin_email.endswith(".gserviceaccount.com"):
                    raise ValueError(
                        "Service account email cannot be used to resolve customer_id"
                    )

                user_info = self.retrier.run(
                    lambda: self.directory.users().get(userKey=self._admin_email).execute()
                )
                self.customer_id = user_info.get("customerId")
            else:
                raise

        logger.info("Successfully authenticated",
                    admin_email=self._admin_email,
                    customer_id=self.customer_id)

    def list_organizational_units(self):  # noqa - Cognitive complexity is too high
        """
        Fetch all organizational units from Google Workspace with automatic retry.

        Returns:
            List of dictionaries representing each organizational unit.
        """
        all_ous = []
        page_token = None

        while True:
            params = {
                "customerId": self.customer_id,
                "type": "all",
            }
            if page_token:
                params["pageToken"] = page_token

            # Use retrier for API call - bind params to avoid closure issues (B023)
            response = self.retrier.run(
                lambda p=params.copy(): self.directory.orgunits().list(**p).execute()  # noqa: B006
            )

            for ou in response.get("organizationUnits", []):
                all_ous.append(ou)

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        # Check if root OU needs to be fetched separately
        has_root = any(ou.get("orgUnitPath") == "/" for ou in all_ous)
        # NOTE: Google Admin SDK does not reliably include the root OU
        # in orgunits().list(type="all") for all domains.
        # To guarantee a complete OU tree, we explicitly fetch the root OU when missing.
        if not has_root:
            try:
                response = self.retrier.run(
                    lambda: self.directory.orgunits().get(
                        customerId=self.customer_id,
                        orgUnitPath="/"
                    ).execute()
                )

                # Handle both structures
                if "organizationUnits" in response:
                    root_candidates = response["organizationUnits"]
                else:
                    root_candidates = [response]

                for root_ou in root_candidates:
                    if root_ou.get("orgUnitPath") == "/" and "orgUnitId" in root_ou:
                        all_ous.insert(0, root_ou)
                        logger.info("Manually added root OU")
                        break
                else:
                    logger.warning("No valid root OU found in fallback response")

            except Exception as e:
                logger.error(
                    "Failed to fetch root OU",
                    error=str(e),
                    customer_id=self.customer_id
                )
                raise

        logger.info("Total OUs fetched", count=len(all_ous))
        return all_ous

    def list_users(self):
        """
        Fetch all users from Google Workspace with automatic retry.

        Yields:
            Dictionaries representing each user.
        """
        page_token = None

        while True:
            params = {
                "customer": self.customer_id,
                "maxResults": 500,
                "orderBy": "givenName",
                "projection": "full"
            }
            if page_token:
                params["pageToken"] = page_token

            # Use retrier for API call
            response = self.retrier.run(
                lambda p=params.copy(): self.directory.users().list(**p).execute()  # noqa: B006
            )

            yield from response.get("users", [])

            page_token = response.get("nextPageToken")
            if not page_token:
                break

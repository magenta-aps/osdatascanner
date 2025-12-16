from google.oauth2 import service_account
from googleapiclient.discovery import build
import structlog

logger = structlog.get_logger("import_services")


class GoogleWorkspaceClient:
    """
    Initializes and authenticates with the Google Admin SDK using a service account and provides
    access to Directory API endpoints for organizational units, users, and groups.
    """

    # https://developers.google.com/workspace/admin/directory/v1/guides/authorizing
    SCOPES = [
        "https://www.googleapis.com/auth/admin.directory.group.readonly",
        "https://www.googleapis.com/auth/admin.directory.orgunit.readonly",
        "https://www.googleapis.com/auth/admin.directory.user.readonly",
        "https://www.googleapis.com/auth/admin.directory.user.alias.readonly"
    ]

    def __init__(self, service_account_info, admin_email):
        self._service_account_info = service_account_info
        self._admin_email = admin_email
        self.customer_id = None
        self.directory = None

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

        logger.warning("No customer_id provided — attempting to auto-detect via Directory API")

        try:
            # Primary attempt, call customer.get('my_customer')
            customer_info = self.directory.customers().get(customerKey='my_customer').execute()
            self.customer_id = customer_info.get('id')
            logger.info("Fetched customer_id via customers.get", customer_id=self.customer_id)
        except Exception as e:
            logger.warning("Could not fetch customer_id via customers.get", error=str(e))
            # If admin email is a service account, fallback is not allowed
            if self._admin_email.endswith(".gserviceaccount.com"):
                raise ValueError(
                    "Service account email cannot be used to resolve customer_id. "
                    "Set 'delegated_admin_email' or 'customer_id'.")

            # Fallback using user profile
            user_info = self.directory.users().get(userKey=self._admin_email).execute()
            self.customer_id = user_info.get("customerId")
            logger.info("Fetched customer_id via user profile", customer_id=self.customer_id)

        logger.info("Impersonating admin", admin_email=self._admin_email)

    def list_organizational_units(self):  # noqa - Cognitive complexity
        """
        Fetch all organizational units from Google Workspace.

        Yields:
            Dictionaries representing each organizational unit.
        """
        all_ous = []
        ou_index = {}
        page_token = None

        try:
            while True:
                params = {
                    "customerId": self.customer_id,
                    "type": "all",
                }
                if page_token:
                    params["pageToken"] = page_token

                response = self.directory.orgunits().list(**params).execute()
                for ou in response.get("organizationUnits", []):
                    all_ous.append(ou)
                    ou_index[ou["orgUnitId"]] = ou
                page_token = response.get("nextPageToken")
                if not page_token:
                    break
        except Exception as e:
            logger.error("Error fetching organizational units", error=str(e))
            raise

        # Now check if the root OU was included
        has_root = any(ou.get("orgUnitPath") == "/" for ou in all_ous)
        if not has_root:
            try:
                response = self.directory.orgunits().get(
                    customerId=self.customer_id,
                    orgUnitPath="/"
                ).execute()

                # Handle both structures: either single OU or a list wrapper
                if "organizationUnits" in response:
                    root_candidates = response["organizationUnits"]
                else:
                    root_candidates = [response]

                for root_ou in root_candidates:
                    if root_ou.get("orgUnitPath") == "/" and "orgUnitId" in root_ou:
                        all_ous.insert(0, root_ou)
                        ou_index[root_ou["orgUnitId"]] = root_ou
                        logger.info("Manually added root OU", ou=root_ou)
                        break
                else:
                    logger.warning("No valid root OU found in fallback response", response=response)

            except Exception as e:
                logger.warning("Failed to fetch root OU", error=str(e))

        logger.info("Total OUs fetched (with root): " + str(len(all_ous)))
        return all_ous

    # https://developers.google.com/workspace/admin/directory/v1/quickstart/python
    def list_users(self):

        page_token = None
        while True:
            try:
                params = {
                    "customer": self.customer_id,
                    "maxResults": 500,
                    "orderBy": "givenName"
                }
                if page_token:
                    params["pageToken"] = page_token
                response = self.directory.users().list(**params).execute()
                yield from response.get("users", [])
                page_token = response.get("nextPageToken")
                if not page_token:
                    break
            except Exception as e:
                logger.error("Error fetching users", error=str(e))
                raise

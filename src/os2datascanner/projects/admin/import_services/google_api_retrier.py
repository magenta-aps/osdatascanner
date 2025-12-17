from googleapiclient.errors import HttpError
from ....engine2.utilities.backoff import ExponentialBackoffRetrier
import json


class GoogleApiRetrier(ExponentialBackoffRetrier):
    """
    A GoogleApiRetrier handles transient errors from Google API calls
    with exponential backoff, similar to WebRetrier but for googleapiclient.

    Handles:
    - 429 Too Many Requests (rate limiting)
    - 5xx server errors (500, 502, 503, 504)
    - 403 with quotaExceeded or rateLimitExceeded
    """

    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
    RETRYABLE_REASONS = {"quotaExceeded", "rateLimitExceeded", "userRateLimitExceeded"}

    def __init__(self, **kwargs):
        # Default to reasonable retry parameters if not specified
        kwargs.setdefault('max_tries', 5)
        kwargs.setdefault('base', 1)
        kwargs.setdefault('ceiling', 5)
        super().__init__(**kwargs)

    def _should_retry(self, ex):
        """Check if this is a retryable Google API error."""
        if not isinstance(ex, HttpError):
            return False

        # Check status code
        if ex.resp.status in self.RETRYABLE_STATUS_CODES:
            return True

        # Check Google-specific error reasons (e.g., quota exceeded)
        # Google API errors are in the response content as JSON
        try:
            error_content = json.loads(ex.content.decode('utf-8'))
            errors = error_content.get('error', {}).get('errors', [])
            for error in errors:
                if isinstance(error, dict) and error.get('reason') in self.RETRYABLE_REASONS:
                    return True
        except (ValueError, KeyError, AttributeError, TypeError):
            # If we can't parse the error, don't retry based on reason
            pass

        return False

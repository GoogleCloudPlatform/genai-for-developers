# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import hmac
from google.cloud import secretmanager
from google.api_core.gapic_v1.client_info import ClientInfo
from google.api_core.exceptions import NotFound, PermissionDenied

from .constants import USER_AGENT

def validate_api_key(api_key: str):
    """Validates an API key against the stored API key from Secret Manager.

    Args:
        api_key: The API key to validate.

    Returns:
        True if the API key is valid, False otherwise.
    """
    devai_api_key = get_secret_value("DEVAI_API_KEY")

    if api_key is None or api_key == "" or devai_api_key is None:
        return False

    return is_valid_api_key(api_key, devai_api_key)

def is_valid_api_key(passed_key, stored_key):
  """Compares an API key securely using hmac.compare_digest().

  Args:
      passed_key: The API key to check, provided by the user.
      stored_key: The API key to validate against, retrieved from secure storage.

  Returns:
      True if the keys match, False otherwise.
  """
  return hmac.compare_digest(passed_key.encode('utf-8'), stored_key.encode('utf-8'))


def ensure_env_variable(var_name):
    """Ensures an environment variable is set.

    Args:
        var_name: The name of the environment variable to check.

    Returns:
        The value of the environment variable.

    Raises:
        EnvironmentError: If the environment variable is not set.
    """
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    return value

def get_secret_value( secret_id: str) -> str:
    """Retrieves a secret value from Google Secret Manager.

    Args:
        secret_id: The ID of the secret to retrieve.

    Returns:
        The secret value as a string, or None if the secret is not found or the user lacks permission.
    
    Raises:
        EnvironmentError: if PROJECT_ID is not defined.
        Exception: For any other unexpected error when getting the secret from the secret manager.
    """    
    try:
        project_id = ensure_env_variable('PROJECT_ID')
        logging.info("PROJECT_ID:", project_id)

        client = secretmanager.SecretManagerServiceClient(
        client_info=ClientInfo(user_agent=USER_AGENT)
        )
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        try:
            response = client.access_secret_version(name=name)
            payload = response.payload.data.decode("utf-8")
            logging.info(f"Successfully retrieved secret ID: {secret_id} in project {project_id}")
            return payload
        
        except PermissionDenied as e:
            logging.warning(f"Insufficient permissions to access secret {secret_id} in project {project_id}: {e}")
            return None
        
        except NotFound:
            logging.info(f"Secret ID not found: {secret_id} in project {project_id}")
            return None
        
        except Exception as e:  # Catching a broader range of potential errors
            logging.error(f"An unexpected error occurred while retrieving secret '{secret_id}': {e}")
            return None
    
    except EnvironmentError as e:
        logging.error(e)

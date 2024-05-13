# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound
from google.api_core.gapic_v1.client_info import ClientInfo
import logging

USER_AGENT = "cloud-solutions/genai-for-developers-v1.1"

def ensure_env_variable(var_name):
    """Ensure an environment variable is set."""
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    return value

def get_access_secret( secret_id: str) -> str:
    try:
        project_id = ensure_env_variable('PROJECT_ID')
        logging.info("PROJECT_ID:", project_id)
    except EnvironmentError as e:
        logging.error(e)
  
    client = secretmanager.SecretManagerServiceClient(
        client_info=ClientInfo(user_agent=USER_AGENT)
    )

    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    try:
        response = client.access_secret_version(name=name)
        payload = response.payload.data.decode("utf-8")
        logging.info(f"ID: {secret_id} in project {project_id}")
        return payload
    except NotFound:
        logging.info(f"ID not found: {secret_id} in project {project_id}")
        return None

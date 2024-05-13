from google.cloud import secretmanager
from google.api_core.exceptions import NotFound
from google.api_core.gapic_v1.client_info import ClientInfo
import logging
 
def get_access_secret(project_id: str, secret_id: str, user_agent: str) -> str:

    client = secretmanager.SecretManagerServiceClient(
        client_info=ClientInfo(user_agent=user_agent)
    )

    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    try:
        response = client.access_secret_version(name=name)
        payload = response.payload.data.decode("utf-8")
        logging.info(f"ID: {secret_id} in project {project_id}")
        return payload
    except NotFound:
        logging.error(f"ID not found: {secret_id} in project {project_id}")
        return None

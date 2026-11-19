import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MAX_RETRIES = int(os.getenv("MAX_RETRIES"))

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN is missing from .env")

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}

def github_request(method, endpoint, **kwargs):
    url = f"https://api.github.com{endpoint}"

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=15,
                **kwargs
            )

            response.raise_for_status()

            return response.json()

        except (
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError
                ) as e:

                    if attempt == MAX_RETRIES - 1:
                        return {"error": f"GitHub connection failed: {str(e)}"}

                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            if status_code == 401:
                return "GitHub authentication failed. Check your access token."

            elif status_code == 403:
                return "GitHub access forbidden. Check your token permissions or rate limit."

            elif status_code == 404:
                return "GitHub resource not found."

            else:
                return f"GitHub HTTP error: {status_code}"

        except requests.exceptions.RequestException as e:
            return f"GitHub request failed: {e}"

        except ValueError:
            return "GitHub returned an invalid JSON response."

    return None

import json
from datetime import datetime
import os
import requests


def main():
    try:
        url = f"https://api.github.com/repos/{os.getenv('GITHUB_ORG_ID')}/{os.getenv('GITHUB_REPOSITORY_NAME')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}/jobs"
        payload = {}
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f"Bearer {os.getenv('GITHUB_TOKEN')}",
            'User-Agent': 'github-build-stats/1.0'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        res = response.text
        data = res.read()
        obj = json.loads(data.decode("utf-8"))
        datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        for row in obj['jobs']:
            for step in range(len(row['steps'])):
                if row['steps'][step]['status'] == "completed":
                    datetime_obj1 = datetime.strptime(row['steps'][step]['started_at'], datetime_format)
                    datetime_obj2 = datetime.strptime(row['steps'][step]['completed_at'], datetime_format)
                    time_difference = datetime_obj2 - datetime_obj1
                    if time_difference.total_seconds() != 0.0:
                        print(row['steps'][step]["name"])
                        print(f"This step took: {time_difference.total_seconds()} seconds")

    except Exception as e:
        print("An exception occurred:", e)
        exit(1)


if __name__ == "__main__":
    main()

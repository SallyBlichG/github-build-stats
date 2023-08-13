import http.client
import json
import os
from datetime import datetime
from google.cloud import bigquery


def main():
    get_build_state_github()


def get_build_state_github():
    try:
        conn = http.client.HTTPSConnection("api.github.com")
        payload = ''
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f"Bearer {os.getenv('GITHUB_TOKEN')}",
            'User-Agent': 'github-build-stats/1.0'
        }
        conn.request("GET",
                     f"/repos/{os.getenv('GITHUB_ORG_ID')}/{os.getenv('GITHUB_REPOSITORY_NAME')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}/jobs",
                     payload, headers)
        res = conn.getresponse()
        data = res.read()
        obj = json.loads(data.decode("utf-8"))
        datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        json_object_bq_data = []
        for row in obj['jobs']:
            workflow_name = row['workflow_name']
            job_name = (row['name']).replace("\\", "")
            url = row['html_url']
            for step in range(len(row['steps'])):
                if row['steps'][step]['status'] == "completed":
                    datetime_started_at = datetime.strptime(row['steps'][step]['started_at'], datetime_format)
                    datetime_completed_at = datetime.strptime(row['steps'][step]['completed_at'], datetime_format)
                    time_difference = datetime_completed_at - datetime_started_at
                    if time_difference.total_seconds() != 0.0:
                        print(row['steps'][step]["name"])
                        print(f"This step took: {time_difference.total_seconds()} seconds")
                        bq_data = {'timestamp': (datetime_started_at.isoformat()),
                                'workflow_name': workflow_name, 'job_name': job_name,
                                'step_name': row['steps'][step]["name"], 'total_time': time_difference.total_seconds(), 'url': url}
                        json_object_bq_data.append(bq_data)
        write_stats_to_bq(json_object_bq_data)
    except Exception as e:
        print("An exception occurred:", e)
        exit(1)


def write_stats_to_bq(json_object_bq_data):
    try:
        client = bigquery.Client.from_service_account_json(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
        bq_details = f"{os.getenv('GOOGLE_PROJECT_NAME')}.{os.getenv('BQ_DATASET')}.{os.getenv('BQ_TABLE')}"
        errors = client.insert_rows_json(bq_details, json_object_bq_data)
        if not errors:
            print("New rows have been added")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))

    except Exception as e:
        print("An exception occurred:", e)
        exit(1)


if __name__ == "__main__":
    main()

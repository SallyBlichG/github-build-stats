import http.client
import json
import os
from datetime import datetime
import pytz
from google.cloud import bigquery


def main():
    getBuildStatsGithub()


def getBuildStatsGithub():
    try:
        conn = http.client.HTTPSConnection("api.github.com")
        # http.client.HTTPSConnection.debuglevel = 1
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
        json_object = []
        for row in obj['jobs']:
            workflow_name = row['workflow_name']
            job_name = (row['name']).replace("\\", "")
            for step in range(len(row['steps'])):
                if row['steps'][step]['status'] == "completed":
                    datetime_obj1 = datetime.strptime(row['steps'][step]['started_at'], datetime_format)
                    datetime_obj2 = datetime.strptime(row['steps'][step]['completed_at'], datetime_format)
                    time_difference = datetime_obj2 - datetime_obj1
                    if time_difference.total_seconds() != 0.0:
                        print(row['steps'][step]["name"])
                        print(f"This step took: {time_difference.total_seconds()} seconds")
                        data = {'timestamp': (datetime_obj1.astimezone(pytz.timezone("UTC+3")).isoformat()),
                                'workflow_name': workflow_name, 'job_name': job_name,
                                'step_name': row['steps'][step]["name"], 'total_time': time_difference.total_seconds()}
                        json_object.append(data)
        writeStatsToBQ(json_object)
    except Exception as e:
        print("An exception occurred:", e)
        exit(1)


def writeStatsToBQ(json_object):
    try:
        client = bigquery.Client.from_service_account_json(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
        table_id = f"{os.getenv('GOOGLE_PROJECT_NAME')}.{os.getenv('BQ_DATASET')}.{os.getenv('BQ_TABLE')}"
        errors = client.insert_rows_json(table_id, json_object)
        if not errors:
            print("New rows have been added")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))

    except Exception as e:
        print("An exception occurred:", e)
        exit(1)


if __name__ == "__main__":
    main()

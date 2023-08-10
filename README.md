# Build Stats: Gather action stats & push it to BigQuery

This GitHub Action automates the process of gathering statistics from a specific run and pushing the collected data to a Google BigQuery table.

## Usage

1. Create a service account key in Google Cloud Platform (GCP) with the necessary permissions to write to your BigQuery dataset.

2. Add the service account key as a secret in your GitHub repository settings. Name the secret `GOOGLE_APPLICATION_CREDENTIALS`.

3. Provide a BigQuery dataset, BigQuery table, and the project name in GCP, as inputs: `BQ_DATASET`, `BQ_TABLE`, `GOOGLE_PROJECT_NAME`.

4. Provide a `GITHUB_TOKEN`, as an input with repo access.

5. Preferably, this action should be the last one, scheduled after all other jobs. You can utilize the `needs` keyword to achieve this.

## Getting Started

Example workflow:

    build-stats:

      name: Build Stats
      runs-on: ubuntu-latest
      needs: [last_job]
    
      steps:
      - name: Get Github Build Stats for current run
        uses: SallyBlichG/github-build-stats@main
        with: 
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_ORG_ID: owner\organization id
          GOOGLE_PROJECT_NAME: google_project_name
          BQ_DATASET: bq_data_set
          BQ_TABLE: github_action_stats
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS }}


## Inputs
All inputs are required!

`GITHUB_TOKEN`: GitHub token to access the build stats. Repo access should be good enough

`GITHUB_ORG_ID`: The organization \ owner id where your repository is located. It might be your username, company name, etc

`GITHUB_REPOSITORY_NAME`: The repository name that we with to get stats from its workflow. Default value is the current repository name, `${{ github.event.repository.name }}`

`GITHUB_RUN_ID`: The run id that we wish to get stats from. Default value is the current run, `${{ github.run_id }}`

`BQ_DATASET`: Big query dataset

`BQ_TABLE`: Big query table

`GOOGLE_PROJECT_NAME`: Google project name (GCP)

`GOOGLE_APPLICATION_CREDENTIALS`: Google credentials (GCP), should be the service account
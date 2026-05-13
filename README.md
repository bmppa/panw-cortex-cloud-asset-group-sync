# Cortex Cloud Dynamic Asset Group Sync

Automates the creation and update of Dynamic Asset Groups in [Palo Alto Networks Cortex Cloud](https://www.paloaltonetworks.com/cortex/cloud) using the public API.

The script:

* Retrieves onboarded cloud accounts from one or more onboarding instances
* Builds dynamic membership predicates automatically
* Creates or updates Dynamic Asset Groups
* Supports multiple asset groups in a single execution
* Supports secure API key handling using environment variables
* Works well with:

  * GitHub Actions
  * AWS Lambda
  * Cron jobs
  * CI/CD pipelines

---

# Features

* Dynamic Asset Group automation
* Multi-instance onboarding support
* Multi-group processing
* Automatic account deduplication
* GitHub Actions compatible
* Secure secret handling
* Supports:

  * `ACCOUNT`
  * `ORGANIZATION`
  * `TENANT`

---

# Requirements

## Python Version

* Python 3.8+

---

# Dependencies

Install required Python package:

```bash id="u0zh5m"
pip install requests
```

Or create a `requirements.txt`:

```text id="v8n17d"
requests
```

Install:

```bash id="jlwmqb"
pip install -r requirements.txt
```

---

# Configuration

The script uses:

* `config.json` for non-sensitive configuration
* Environment variable for the API key

---

# Example config.json

```json
{
    "fqdn": "https://api-xdr.xdr.us.paloaltonetworks.com",
    "api_key_id": "YOUR_API_KEY_ID",

    "asset_groups": [
        {
            "mode": "create",
            "instance_ids": "instance-id-1",
            "group_id": "",
            "group_name": "AWS Production",
            "group_description": "Production AWS Accounts"
        },

        {
            "mode": "update",
            "instance_ids": "instance-id-2",
            "group_id": "1234",
            "group_name": "AWS Development",
            "group_description": "Development AWS Accounts"
        }
    ]
}
```

---

# Configuration Parameters

## Global Configuration

| Parameter    | Description          |
| ------------ | -------------------- |
| `fqdn`       | Cortex Cloud API URL |
| `api_key_id` | Cortex API Key ID    |

---

## Asset Group Configuration

| Parameter           | Description                         |
| ------------------- | ----------------------------------- |
| `mode`              | `create` or `update`                |
| `instance_ids`      | One nboarding instance ID           |
| `group_id`          | Required for update mode            |
| `group_name`        | Asset Group name                    |
| `group_description` | Asset Group description             |

---

# Environment Variable

The script requires the API key value to be provided via environment variable:

```text
API_KEY_VALUE
```

---

# Export Environment Variable

## Linux / macOS

```bash
export API_KEY_VALUE="YOUR_API_KEY_VALUE"
```

---

## Windows PowerShell

```powershell id="v4d87v"
$env:API_KEY_VALUE="YOUR_API_KEY_VALUE"
```

---

# Running the Script

```bash
python3 asset-group-sync.py
```

---

# How It Works

The script performs the following steps:

1. Loads `config.json`
2. Retrieves cloud accounts from each onboarding instance
3. Filters supported account types:

   * ACCOUNT
   * ORGANIZATION
   * TENANT
4. Deduplicates account IDs
5. Builds Dynamic Asset Group membership predicates
6. Creates or updates the Asset Group

---

# Example Membership Predicate

Generated automatically:

```json
{
  "AND": [
    {
      "OR": [
        {
          "SEARCH_FIELD": "xdm.asset.realm",
          "SEARCH_TYPE": "EQ",
          "SEARCH_VALUE": "123456789012"
        }
      ]
    }
  ]
}
```

---

# Example Output

```
=== Cortex Cloud Dynamic Asset Group Sync ===

✅ Loaded configuration from 'config.json'

✅ Fetched 24 accounts.
✅ Total unique accounts: 24

===================================================
🚀 Processing Asset Group
===================================================
Mode: update
Group Name: AWS Production
Description: Production AWS Accounts
Total Realms: 24

Status Code: 200
Response:
{"reply":"success"}
```

---

# GitHub Actions Example

Create:

```text
.github/workflows/xdr-sync.yml
```

Example workflow:

```yaml
name: Cortex Cloud Asset Group Sync

on:
  schedule:
    - cron: "*/5 * * * *"

  workflow_dispatch:

jobs:

  sync-asset-groups:

    runs-on: ubuntu-latest

    env:
      API_KEY_VALUE: ${{ secrets.API_KEY_VALUE }}

    steps:

      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set Up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Dependencies
        run: |
          pip install requests

      - name: Run Script
        run: |
          python asset-group-sync.py
```

---

# GitHub Secrets

Configure in:

```text
Repository
→ Settings
→ Secrets and variables
→ Actions
```

Create:

| Secret          | Description    |
| --------------- | -------------- |
| `API_KEY_VALUE` | Cortex API Key |

---

# Supported Automation Platforms

The script can run on:

* GitHub Actions
* Amazon Web Services Lambda
* Jenkins
* GitLab CI/CD
* Cron
* Kubernetes CronJobs
* Azure DevOps

---

# Troubleshooting

## Config File Not Found

Error:

```text
❌ Config file 'config.json' not found.
```

Verify:

* File exists
* Correct filename
* Correct working directory

---

## Invalid JSON

Error:

```text
❌ Failed to load config file
```

Validate JSON syntax:

```bash
python -m json.tool config.json
```

---

## API Authentication Failure

Verify:

* API Key ID
* `API_KEY_VALUE`
* Correct FQDN
* API permissions

---

## No Accounts Returned

Verify:

* Correct onboarding instance IDs
* Cloud accounts are onboarded
* API access permissions

---

# Security Recommendations

## Recommended

* Store API keys in:

  * GitHub Secrets
  * AWS Secrets Manager
  * Vault
  * Environment variables

---

## Avoid

* Hardcoding secrets in Git repositories
* Storing API keys in `config.json`

---

# Disclaimer

Test in a non-production environment before deploying to production systems.

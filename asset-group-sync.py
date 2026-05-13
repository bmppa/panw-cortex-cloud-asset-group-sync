import requests
import json
import os
import sys

CONFIG_FILE = "config.json"

def load_config_file():
    """Loads configuration from config.json"""

    if not os.path.exists(CONFIG_FILE):
        print(f"\n❌ Config file '{CONFIG_FILE}' not found.")
        sys.exit(1)

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        print(f"\n✅ Loaded configuration from '{CONFIG_FILE}'")

        # Remove trailing slash from FQDN
        config["fqdn"] = config["fqdn"].rstrip("/")

        return config

    except Exception as e:
        print(f"\n❌ Failed to load config file: {e}")
        sys.exit(1)


def get_realms_via_api(fqdn, instance_id, headers):
    """Fetches all account IDs from the parent organization."""

    url = f"{fqdn}/public_api/v1/cloud_onboarding/get_accounts"

    payload = {
        "request_data": {
            "instance_id": instance_id
        }
    }

    realm_list = []

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"\n❌ API Error: {response.status_code}")
            print(response.text)
            return []

        try:
            response_json = response.json()

        except Exception:
            print("\n❌ Response was not valid JSON.")
            print(response.text)
            return []

        data_list = response_json.get('reply', {}).get('DATA', [])

        realm_list = [
            item.get('cloud_account_id')
            for item in data_list
            if item.get('account_type') in ['ACCOUNT', 'ORGANIZATION', 'TENANT']
        ]

        print(f"\n✅ Fetched {len(realm_list)} accounts.")

    except Exception as e:
        print(f"\n❌ Exception while retrieving accounts: {e}")

    return realm_list


def sync_asset_group(global_config, asset_group):
    """
    Creates or updates a Cortex Cloud Dynamic Asset Group.
    """

    headers = {
        "x-xdr-auth-id": global_config["api_key_id"],
        "Authorization": os.environ["API_KEY_VALUE"],
        "Content-Type": "application/json"
    }

    all_realms = set()

    # Support both string and list for instance_ids
    instance_ids = asset_group["instance_ids"]

    if isinstance(instance_ids, str):
        instance_ids = [instance_ids]

    # Retrieve realms from all instance IDs
    for instance_id in instance_ids:

        realms = get_realms_via_api(
            global_config["fqdn"],
            instance_id,
            headers
        )

        all_realms.update(realms)

    if not all_realms:
        print(f"\n❌ No accounts found for group: {asset_group['group_name']}")
        return

    print(f"\n✅ Total unique accounts: {len(all_realms)}")

    # Build realm filters
    realm_filters = [
        {
            "SEARCH_FIELD": "xdm.asset.realm",
            "SEARCH_TYPE": "EQ",
            "SEARCH_VALUE": realm
        }
        for realm in sorted(all_realms)
    ]

    # Membership predicate
    membership_predicate = {
        "AND": [
            {
                "OR": realm_filters
            }
        ]
    }

    # Determine action
    action = asset_group["mode"].lower()

    if action not in ["create", "update"]:
        print(f"\n❌ Invalid mode: {action}")
        return

    endpoint_url = (
        f"{global_config['fqdn']}/public_api/v1/asset-groups/{action}"
    )

    if action == "update":

        if not asset_group["group_id"]:
            print("\n❌ group_id is required for update mode.")
            return

        endpoint_url += f"/{asset_group['group_id']}"

    # Payload
    payload = {
        "request_data": {
            "asset_group": {
                "group_name": asset_group["group_name"],
                "group_type": "Dynamic",
                "group_description": asset_group["group_description"],
                "membership_predicate": membership_predicate
            }
        }
    }

    print("\n===================================================")
    print(f"🚀 Processing Asset Group")
    print("===================================================")
    print(f"Mode: {action}")
    print(f"Group Name: {asset_group['group_name']}")
    print(f"Description: {asset_group['group_description']}")
    print(f"Total Realms: {len(all_realms)}")

    try:
        response = requests.post(
            endpoint_url,
            headers=headers,
            json=payload
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:\n{response.text}")

    except Exception as e:
        print(f"\n❌ Exception while performing operation: {e}")


if __name__ == "__main__":

    print("\n=== Cortex Cloud Dynamic Asset Group Sync ===")

    config = load_config_file()

    # Process all asset groups
    for asset_group in config["asset_groups"]:

        sync_asset_group(config, asset_group)

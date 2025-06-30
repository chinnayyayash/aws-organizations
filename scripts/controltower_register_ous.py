import boto3
import time
import botocore.exceptions

org = boto3.client("organizations")
ct = boto3.client("controltower")

CONTROL_BASELINE_NAME = "AWSControlTowerBaseline"
IDENTITY_BASELINE_NAME = "IdentityCenterBaseline"
BASELINE_VERSION = "4.0"
WAIT_MINUTES = 10  # Wait time in minutes between enable operations

# Step 1: Get Root OU ID
def get_root_id():
    return org.list_roots()["Roots"][0]["Id"]

# Step 2: Recursively fetch all OUs, including nested child OUs
def get_all_ous(parent_id, all_ous=None):
    if all_ous is None:
        all_ous = []
    paginator = org.get_paginator("list_organizational_units_for_parent")
    for page in paginator.paginate(ParentId=parent_id):
        for ou in page["OrganizationalUnits"]:
            all_ous.append({
                "Name": ou["Name"],
                "Id": ou["Id"],
                "Arn": ou["Arn"]
            })
            get_all_ous(ou["Id"], all_ous)
    return all_ous

# Step 3: Get list of enabled OUs
def get_enabled_ou_ids():
    enabled_ids = set()
    retries = 0
    while retries < 5:
        try:
            paginator = ct.get_paginator("list_enabled_baselines")
            for page in paginator.paginate():
                for baseline in page["enabledBaselines"]:
                    arn = baseline["targetIdentifier"]
                    if arn.startswith("arn:aws:organizations"):
                        ou_id = arn.split("/")[-1].lower()
                        enabled_ids.add(ou_id)
            return enabled_ids
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ThrottlingException":
                wait_time = 2 ** retries
                print(f"⏳ Throttled. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                retries += 1
            else:
                raise
    raise Exception("Too many throttling errors while fetching enabled baselines")

# Step 4: Get ARNs for control and identity baselines
def get_baseline_arns():
    control_arn = None
    identity_arn = None
    for b in ct.list_baselines()["baselines"]:
        if b["name"] == CONTROL_BASELINE_NAME:
            control_arn = b["arn"]
        elif b["name"] == IDENTITY_BASELINE_NAME:
            identity_arn = b["arn"]
    return control_arn, identity_arn

def get_enabled_identity_baseline_arn(identity_arn):
    for page in ct.get_paginator("list_enabled_baselines").paginate():
        for b in page["enabledBaselines"]:
            if b["baselineIdentifier"] == identity_arn:
                return b["arn"]
    return None

# Step 5: Simulated wait for one operation to complete
def wait_for_operation_simulated(operation_id):
    print(f"⏳ Waiting {WAIT_MINUTES} minutes for operation {operation_id} to complete...")
    for i in range(WAIT_MINUTES):
        print(f"   → Minute {i + 1}/{WAIT_MINUTES}...")
        time.sleep(60)
    print(f"✅ Done waiting for {operation_id}. Proceeding to next OU.")

# Main logic
def main():
    print("🔍 Fetching all OUs including parent and nested children...")
    root_id = get_root_id()
    all_ous = get_all_ous(root_id)

    control_arn, identity_arn = get_baseline_arns()
    identity_enabled_arn = get_enabled_identity_baseline_arn(identity_arn)

    if not control_arn or not identity_enabled_arn:
        print("❌ Could not find required baseline ARNs. Exiting.")
        return

    SKIP_OU_NAMES = {"security", "exceptions", "suspended"}
    enabled_ou_ids = get_enabled_ou_ids()

    for ou in all_ous:
        ou_name = ou["Name"].strip().lower()
        ou_id = ou["Id"].lower()
        ou_arn = ou["Arn"]

        if ou_name in SKIP_OU_NAMES:
            print(f"🚫 Skipping OU by name: {ou_name} ({ou_id})")
            continue

        if ou_id in enabled_ou_ids:
            print(f"✅ Already enabled: {ou_name} ({ou_id})")
            continue

        print(f"🚀 Enabling baseline for OU: {ou_name} ({ou_id})")
        try:
            response = ct.enable_baseline(
                baselineIdentifier=control_arn,
                baselineVersion=BASELINE_VERSION,
                targetIdentifier=ou_arn,
                parameters=[
                    {
                        "key": "IdentityCenterEnabledBaselineArn",
                        "value": identity_enabled_arn
                    }
                ]
            )
            operation_id = response.get("operationIdentifier")
            if operation_id:
                wait_for_operation_simulated(operation_id)

        except ct.exceptions.ValidationException as ve:
            print(f"⚠️ Cannot enable baseline for OU '{ou_name}' — reason: {ve}")
        except Exception as e:
            print(f"❌ Unexpected error for OU {ou_name} ({ou_id}): {e}")

if __name__ == "__main__":
    main()
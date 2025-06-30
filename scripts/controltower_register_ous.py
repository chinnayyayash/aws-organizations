import boto3
import time

org = boto3.client("organizations")
ct = boto3.client("controltower")

CONTROL_BASELINE_NAME = "AWSControlTowerBaseline"
IDENTITY_BASELINE_NAME = "IdentityCenterBaseline"
BASELINE_VERSION = "4.0"

# Step 1: Get Root OU ID
def get_root_id():
    return org.list_roots()["Roots"][0]["Id"]

# Step 2: Recursively fetch all OUs, including parent and all child OUs
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
            # 🔁 Recursively get nested child OUs
            get_all_ous(ou["Id"], all_ous)
    return all_ous

# Step 3: Get list of already enabled OUs
def get_enabled_ou_ids():
    enabled_ids = set()
    paginator = ct.get_paginator("list_enabled_baselines")
    for page in paginator.paginate():
        for baseline in page["enabledBaselines"]:
            arn = baseline["targetIdentifier"]
            if arn.startswith("arn:aws:organizations"):
                ou_id = arn.split("/")[-1].lower()
                enabled_ids.add(ou_id)
    return enabled_ids

# Step 4: Get baseline ARNs
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

# Step 5: Wait for any active operations to finish
def wait_for_no_active_operations():
    while True:
        operations = ct.list_operations()["operations"]
        active = [op for op in operations if op["status"] in ("IN_PROGRESS", "QUEUED")]
        if not active:
            return
        print(f"⏳ Waiting for {len(active)} active operation(s) to complete...")
        time.sleep(30)

# Step 6: Wait for specific operation to complete
def wait_for_operation(operation_id):
    print(f"⏳ Waiting for operation {operation_id} to complete...")
    while True:
        response = ct.get_operation(operationIdentifier=operation_id)
        status = response["operation"]['status']
        if status == "SUCCEEDED":
            print(f"✅ Operation {operation_id} completed successfully.")
            break
        elif status == "FAILED":
            print(f"❌ Operation {operation_id} failed.")
            break
        else:
            print(f"🕒 Operation status: {status}. Retrying in 30s...")
            time.sleep(30)

# Main logic
def main():
    print("🔍 Fetching all OUs including parent and nested children...")
    root_id = get_root_id()
    all_ous = get_all_ous(root_id)

    enabled_ou_ids = get_enabled_ou_ids()
    control_arn, identity_arn = get_baseline_arns()
    identity_enabled_arn = get_enabled_identity_baseline_arn(identity_arn)

    if not control_arn or not identity_enabled_arn:
        print("❌ Could not find required baseline ARNs. Exiting.")
        return

    # 🔐 Define OU names to skip (case-insensitive)
    SKIP_OU_NAMES = {"security", "exceptions", "suspended"}

    for ou in all_ous:
        ou_name = ou["Name"]
        ou_id = ou["Id"].lower()
        ou_arn = ou["Arn"]

        # Step 2: Skip specific OU names (case-insensitive match)
        if ou_name.strip().lower() in SKIP_OU_NAMES:
            print(f"🚫 Skipping OU by name: {ou_name} ({ou_id})")
            continue

        # Step 3: Skip already-enabled OUs
        if ou_id in enabled_ou_ids:
            print(f"✅ Already enabled: {ou_name} ({ou_id})")
            continue

        # Step 4: Wait for previous operations to finish
        wait_for_no_active_operations()

        # Step 5: Enable baseline
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
                wait_for_operation(operation_id)

        except ct.exceptions.ValidationException as ve:
            print(f"⚠️ Cannot enable baseline for OU '{ou_name}' — reason: {ve}")
        except Exception as e:
            print(f"❌ Unexpected error for OU {ou_name} ({ou_id}): {e}")

if __name__ == "__main__":
    main()
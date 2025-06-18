#!/
bin/bash

set -euo pipefail

echo "🔍 Fetching root OU ID..."
ROOT_ID=$(aws organizations list-roots --query "Roots[0].Id" --output text)

echo "🔍 Fetching Control Tower baseline ARN..."
BASELINE_ARN=$(aws controltower list-baselines \
 --query "baselines[?name=='AWSControlTowerBaseline'].arn" --output text)

if [[ -z "$BASELINE_ARN" ]]; then
 echo "❌ Error: No baseline found."
 exit 1
fi

function register_nested_ous() {
 local parent_id=$1

 CHILD_OUS=$(aws organizations list-organizational-units-for-parent \
 --parent-id "$parent_id" \
 --query "OrganizationalUnits[*].Id" --output text)

 for ou_id in $CHILD_OUS; do
 ou_arn=$(aws organizations describe-organizational-unit \
 --organizational-unit-id "$ou_id" \
 --query "OrganizationalUnit.Arn" --output text)

 echo "🔁 Registering OU: $ou_arn"
 aws controltower enable-baseline \
 --baseline-identifier "$BASELINE_ARN" \
 --baseline-version current \
 --target-identifier "$ou_arn" || echo "⚠️ Already governed or failed: $ou_arn"

 register_nested_ous "$ou_id"
 done
}

echo "🚀 Starting recursive registration from root OU..."
register_nested_ous "$ROOT_ID"
echo "✅ Registration complete."
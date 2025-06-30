# This file defines local variables for the AWS Organization structure.
locals {
  root_id = data.aws_organizations_organization.org.roots[0].id
}

# Define the list of OU names
locals {
  product_line_dev_ous = [
    "Sandbox",
    "Dev",
    "Test",
    "PreProd",
    "Prod"
  ]
}

# Create direct children under ProductLineTenants → APAC, AMER, Default
locals {
  direct_children = ["APAC", "AMER", "Default"]
}

# Under APAC → create Tier1, Tier2, Tier3
locals {
  apac_children = ["Tier1", "Tier2", "Tier3"]
}

# Under Tier1 → create NonProd, Prod
locals {
  tier1_children = ["NonProd", "Prod"]
}


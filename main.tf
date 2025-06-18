# 3. Create missing top-level OUs
resource "aws_organizations_organizational_unit" "product_line_development" {
  name      = "ProductLineDevelopment"
  parent_id = local.root_id
}

resource "aws_organizations_organizational_unit" "product_line_tenants" {
  name      = "ProductLineTenants"
  parent_id = local.root_id
}

resource "aws_organizations_organizational_unit" "suspended" {
  name      = "Suspended"
  parent_id = local.root_id
}

resource "aws_organizations_organizational_unit" "infrastructure" {
  name      = "Infrastructure"
  parent_id = local.root_id
}

resource "aws_organizations_organizational_unit" "exceptions" {
  name      = "Exceptions"
  parent_id = local.root_id
}

resource "aws_organizations_organizational_unit" "security_tooling" {
  name      = "SecurityTooling"
  parent_id = local.root_id
}

resource "aws_organizations_organizational_unit" "policy_staging" {
  name      = "PolicyStaging"
  parent_id = local.root_id
}

# 4. Nested OUs under ProductLineDevelopment
resource "aws_organizations_organizational_unit" "product_line_dev_children" {
  for_each  = toset(local.product_line_dev_ous)
  name      = each.value
  parent_id = aws_organizations_organizational_unit.product_line_development.id
}

# 5. Nested OUs under ProductLineTenants
resource "aws_organizations_organizational_unit" "direct_ous" {
  for_each  = toset(local.direct_children)
  name      = each.value
  parent_id = aws_organizations_organizational_unit.product_line_tenants.id
}

resource "aws_organizations_organizational_unit" "apac_ous" {
  for_each  = toset(local.apac_children)
  name      = each.value
  parent_id = aws_organizations_organizational_unit.direct_ous["APAC"].id
}

resource "aws_organizations_organizational_unit" "tier1_ous" {
  for_each  = toset(local.tier1_children)
  name      = each.value
  parent_id = aws_organizations_organizational_unit.apac_ous["Tier1"].id
}
# 1. Create top-level OUs through Organizations
resource "aws_organizations_organizational_unit" "product_line_development" {
  name      = "ProductLineDevelopment"
  parent_id = local.root_id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_organizations_organizational_unit" "aft_management" {
  name      = "AFTManagement"
  parent_id = local.root_id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_organizations_organizational_unit" "product_line_tenants" {
  name      = "ProductLineTenants"
  parent_id = local.root_id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_organizations_organizational_unit" "suspended" {
  name      = "Suspended"
  parent_id = local.root_id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_organizations_organizational_unit" "infrastructure" {
  name      = "Infrastructure"
  parent_id = local.root_id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_organizations_organizational_unit" "exceptions" {
  name      = "Exceptions"
  parent_id = local.root_id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_organizations_organizational_unit" "security_tooling" {
  name      = "SecurityTooling"
  parent_id = local.root_id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_organizations_organizational_unit" "policy_staging" {
  name      = "PolicyStaging"
  parent_id = local.root_id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_organizations_organizational_unit" "sandbox" {
  name      = "Sandbox"
  parent_id = local.root_id
  lifecycle {
    prevent_destroy = true
  }
}

# 2. Nested OUs under ProductLineDevelopment
resource "aws_organizations_organizational_unit" "product_line_dev_children" {
  for_each  = toset(local.product_line_dev_ous)
  name      = each.value
  parent_id = aws_organizations_organizational_unit.product_line_development.id
  lifecycle {
    prevent_destroy = true
  }
}

# 3. Nested OUs under ProductLineTenants
resource "aws_organizations_organizational_unit" "direct_ous" {
  for_each  = toset(local.direct_children)
  name      = each.value
  parent_id = aws_organizations_organizational_unit.product_line_tenants.id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_organizations_organizational_unit" "apac_ous" {
  for_each  = toset(local.apac_children)
  name      = each.value
  lifecycle {
    prevent_destroy = true
  }
  parent_id = aws_organizations_organizational_unit.direct_ous["APAC"].id
}

resource "aws_organizations_organizational_unit" "tier1_ous" {
  for_each  = toset(local.tier1_children)
  name      = each.value
  parent_id = aws_organizations_organizational_unit.apac_ous["Tier1"].id
  lifecycle {
    prevent_destroy = true
  }
}
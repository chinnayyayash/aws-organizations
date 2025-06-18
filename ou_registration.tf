# First set execute permissions on the script
resource "null_resource" "set_script_permissions" {
  provisioner "local-exec" {
    command = "chmod +x ${path.module}/scripts/register_all_ous.sh"
  }
}

# Then run the main script
resource "null_resource" "register_ous_with_controltower" {
  provisioner "local-exec" {
    command = "${path.module}/scripts/register_all_ous.sh"
  }

  triggers = {
    always_run = timestamp()
  }

  # Combine all dependencies in a single depends_on block
  depends_on = [
    null_resource.set_script_permissions,
    aws_organizations_organizational_unit.product_line_development,
    aws_organizations_organizational_unit.product_line_tenants,
    aws_organizations_organizational_unit.suspended,
    aws_organizations_organizational_unit.infrastructure,
    aws_organizations_organizational_unit.exceptions,
    aws_organizations_organizational_unit.security_tooling,
    aws_organizations_organizational_unit.policy_staging,
    aws_organizations_organizational_unit.product_line_dev_children,
    aws_organizations_organizational_unit.direct_ous,
    aws_organizations_organizational_unit.apac_ous,
    aws_organizations_organizational_unit.tier1_ous
  ]
}
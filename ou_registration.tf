resource "null_resource" "register_ous_with_controltower" {
 provisioner "local-exec" {
    command = "${path.module}/scripts/register_all_ous.sh"
 }

 triggers = {
    always_run = "${timestamp()}"
 }

 depends_on = [
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

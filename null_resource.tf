resource "null_resource" "register_ous" {
  provisioner "local-exec" {
    command = "python3 ${path.module}/scripts/controltower_register_ous.py"
  }

#   triggers = {
#     always_run = timestamp()
#   }
}
resource "aws_ssm_parameter" "watermark" {
  name  = "/scant/watermark"
  type  = "String"
  value = "{\"lastKnownID\": 0}"

  lifecycle {
    ignore_changes = [value]
  }
}

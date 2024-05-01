# Scant

Deploy with

```powershell
$Env:SCANT_TF_BUCKET = Read-Host
# Set AWS credentials

npm run build
npm run pack

Set-Location ./infrastructure
terraform init -backend-config="bucket=${Env:SCANT_TF_BUCKET}"
terraform apply
```

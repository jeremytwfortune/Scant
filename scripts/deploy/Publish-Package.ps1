[CmdletBinding()]
param(
	[Parameter(Mandatory)]
	[string]$RepositoryUri
)

Connect-ECRRepository

docker build -t scant .
docker tag scant:latest ${RepositoryUri}:latest
docker push ${RepositoryUri}:latest

Push-Location "$PSScriptRoot\..\..\infrastructure"
& terraform apply
Pop-Location

Update-LMFunctionCode -FunctionName "scant-scanner" -ImageUri ${RepositoryUri}:latest

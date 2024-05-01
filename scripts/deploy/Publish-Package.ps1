[CmdletBinding()]
param()

$Env:POETRY_VIRTUALENVS_IN_PROJECT = "true"

$distFolder = "$PSScriptRoot\..\..\dist"
$venvFolder = "$PSScriptRoot\..\..\.venv"
$publishFolder = "$PSScriptRoot\..\..\publish"
$distFolder, $publishFolder | ForEach-Object {
	Remove-Item -Recurse $_ -ErrorAction SilentlyContinue
	New-Item -ItemType Directory -Path $_ -Force
}
Remove-Item -Recurse $venvFolder -ErrorAction SilentlyContinue

poetry install --without dev
poetry run pip install `
	--platform manylinux2014_x86_64 `
	--target=.venv/lib/python3.12/site-packages `
	--python-version 3.12 `
	--only-binary=:all: `
	--upgrade `
	cryptography==41.0.7

Copy-Item -Recurse "$PSScriptRoot\..\..\scant\" $distFolder
Copy-Item -Recurse "$venvFolder\lib\site-packages\*" $distFolder
Copy-Item -Recurse "$venvFolder\lib\python3.12\site-packages\*" $distFolder -Force

Compress-Archive -Path "$distFolder\*" -DestinationPath "$publishFolder\dist.zip" -Force

Push-Location "$PSScriptRoot\..\..\infrastructure"
& terraform apply
Pop-Location

$ErrorActionPreference = 'Stop'
$codexCommand = Get-Command codex -ErrorAction Stop
$manifestPath = Join-Path $PSScriptRoot 'plugins\lenovo-computer-use\.mcp.json'
$serverConfig = (Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json).mcpServers.lenovo_desktop
if (-not (Test-Path -LiteralPath $serverConfig.command)) {
    throw 'Configured Python executable is missing. Check the private MCP manifest.'
}
if (-not (Test-Path -LiteralPath $serverConfig.args[1])) {
    throw 'The plugin source has moved. Update the private MCP manifest before installing.'
}
& $codexCommand.Source plugin marketplace add $PSScriptRoot --json
if ($LASTEXITCODE -ne 0) { throw 'Local marketplace registration failed.' }
& $codexCommand.Source plugin add 'lenovo-computer-use@lenovo-local' --json
if ($LASTEXITCODE -ne 0) { throw 'Plugin installation failed.' }
Write-Host 'Installed. Restart the desktop app, then use a new chat or /mcp to verify.'

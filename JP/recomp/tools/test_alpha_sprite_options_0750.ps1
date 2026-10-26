# JP0750: ROM-free executable source-contract test of private launcher switches.
# Execute the ACTUAL unmodified helper AST extracted from Launch-Alpha.ps1.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$source=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\release\alpha\Launch-Alpha.ps1')).Path
$errors=$null; $tokens=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile(
 $source,[ref]$tokens,[ref]$errors)
if ($errors.Count) {throw ($errors|Out-String)}
$fn=$ast.Find({
 param($node)
 $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
 $node.Name -eq 'Get-CviiiSpriteLaunchOptions'
},$true)
if (-not $fn) {throw 'Private launcher lacks source-backed sprite option selection'}
Invoke-Expression $fn.Extent.Text
$content=Get-Content -LiteralPath $source -Raw
if ($content -notmatch 'OverrideStable \(\$PSBoundParameters\.ContainsKey\(''StableSprites''\)\)' -or
    $content -notmatch 'OverrideUnlimited \(\$PSBoundParameters\.ContainsKey\(''UnlimitedSprites''\)\)' -or
    $content -match '\$gameArgs=@\(\$romPath.*--stable-sprites') {
 throw 'Launcher must forward only user-requested presentation overrides'
}
function RequireArgs {
 param([string]$Name,[string[]]$Actual,[string[]]$Expected)
 if (($Actual -join '|') -cne ($Expected -join '|')) {
  throw ('Bad '+$Name+': ['+($Actual -join ',')+'] expected ['+($Expected -join ',')+']')
 }
}
$default=@(Get-CviiiSpriteLaunchOptions -Edition Enhanced -UnlimitedSprites $false -StableSprites $false -OverrideUnlimited $false -OverrideStable $false)
RequireArgs 'saved config unchanged' $default @()
$enabled=@(Get-CviiiSpriteLaunchOptions -Edition Enhanced -UnlimitedSprites $false -StableSprites $true -OverrideUnlimited $false -OverrideStable $true)
RequireArgs 'explicit stable on' $enabled @('--stable-sprites','1')
$disabled=@(Get-CviiiSpriteLaunchOptions -Edition Enhanced -UnlimitedSprites $false -StableSprites $false -OverrideUnlimited $false -OverrideStable $true)
RequireArgs 'explicit stable off' $disabled @('--stable-sprites','0')
$unlimited=@(Get-CviiiSpriteLaunchOptions -Edition Enhanced -UnlimitedSprites $true -StableSprites $false -OverrideUnlimited $true -OverrideStable $false)
RequireArgs 'unlimited on' $unlimited @('--unlimited-sprites','1')
$original=@(Get-CviiiSpriteLaunchOptions -Edition Original -UnlimitedSprites $true -StableSprites $true -OverrideUnlimited $true -OverrideStable $true)
RequireArgs 'Original safe' $original @('--unlimited-sprites','0','--stable-sprites','0')
$both=@(Get-CviiiSpriteLaunchOptions -Edition Enhanced -UnlimitedSprites $true -StableSprites $true -OverrideUnlimited $true -OverrideStable $true)
RequireArgs 'explicitly both' $both @('--unlimited-sprites','1','--stable-sprites','1')
Write-Host 'PASS JP0750 actual Windows launcher preserves persisted sprite options and explicit override controls'
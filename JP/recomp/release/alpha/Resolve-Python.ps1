# JP0607 - robust Windows Python interpreter discovery.
# Dot-source from the private builder, native launcher and QA capture tools.
# Do not confuse Windows' Microsoft Store App Execution Alias with Python.
function Test-CviiiPython {
 param(
  [Parameter(Mandatory=$true)][string]$Executable,
  [string[]]$Prefix=@()
 )
 if (-not (Get-Command $Executable -ErrorAction SilentlyContinue)) { return $false }
 try {
  & $Executable @Prefix -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' *> $null
  return ($LASTEXITCODE -eq 0)
 } catch { return $false }
}

function Resolve-CviiiPython {
 foreach ($probe in @(
     @{Executable='py';Prefix=@('-3')},
     @{Executable='python';Prefix=@()},
     @{Executable='python3';Prefix=@()}
 )) {
  if (Test-CviiiPython -Executable $probe.Executable -Prefix $probe.Prefix) {
   return [pscustomobject]@{
    Executable=[string]$probe.Executable
    Prefix=[string[]]$probe.Prefix
   }
  }
 }
 throw ('No working Python 3.10+ interpreter was found. Windows may be '+
   'using the Microsoft Store python.exe App Execution Alias, which '+
   'is not a real interpreter. Install Python 3 from '+
   'https://www.python.org/downloads/windows/ (include the Python '+
   'launcher or add Python to PATH). Verify "py -3 --version" or '+
   '"python --version" in a NEW terminal. In Windows Settings > '+
   'Apps > Advanced app settings > App execution aliases, disable '+
   'python.exe/python3.exe aliases if they intercept the real Python.')
}

function Invoke-CviiiPython {
 param(
  [Parameter(Mandatory=$true)][string]$Script,
  [string[]]$Arguments=@()
 )
 $interpreter=Resolve-CviiiPython
 $argv=@($interpreter.Prefix) + @($Script) + @($Arguments)
 & $interpreter.Executable @argv
 if ($LASTEXITCODE -ne 0) {
  throw ('Python failed (exit '+$LASTEXITCODE+'), script: '+$Script)
 }
}

param(
    [string]$BackendRoot = '',
    [string]$FrontendRoot = '',
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = 'Stop'

$script:AllProcesses = @()
$script:KillIds = [System.Collections.Generic.HashSet[int]]::new()

function Get-ProjectConfig {
    param([string]$Root)

    if (-not $Root) { return $null }

    $configPath = Join-Path $Root '.re-project.json'
    if (Test-Path -LiteralPath $configPath) {
        try {
            return Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
        }
        catch {
            return $null
        }
    }

    return $null
}

function Resolve-ConfigPath {
    param([string]$Root, [string]$Value)

    if ([System.IO.Path]::IsPathRooted($Value)) {
        return $Value
    }

    return Join-Path $Root $Value
}

function Has-MainPy {
    param([string]$Root)

    return $Root -and (Test-Path -LiteralPath (Join-Path $Root 'main.py'))
}

function Has-ViteConfig {
    param([string]$Root)

    if (-not $Root) { return $false }

    return (Test-Path -LiteralPath (Join-Path $Root 'vite.config.js')) -or
           (Test-Path -LiteralPath (Join-Path $Root 'vite.config.ts')) -or
           (Test-Path -LiteralPath (Join-Path $Root 'package.json'))
}

function Find-BackendRoot {
    param([string]$Start)

    if (-not $Start) { return '' }

    $config = Get-ProjectConfig -Root $Start
    if ($config -and $config.backend) {
        $candidate = Resolve-ConfigPath -Root $Start -Value $config.backend
        if (Has-MainPy -Root $candidate) {
            return $candidate
        }
    }

    if (Has-MainPy -Root $Start) {
        return $Start
    }

    $directories = Get-ChildItem -LiteralPath $Start -Directory -ErrorAction SilentlyContinue
    foreach ($directory in $directories) {
        if (Has-MainPy -Root $directory.FullName) {
            return $directory.FullName
        }
    }

    $parent = Split-Path -Parent $Start
    if ($parent -and $parent -ne $Start) {
        $parentDirectories = Get-ChildItem -LiteralPath $parent -Directory -ErrorAction SilentlyContinue
        foreach ($directory in $parentDirectories) {
            if (Has-MainPy -Root $directory.FullName) {
                return $directory.FullName
            }
        }
    }

    return ''
}

function Find-FrontendRoot {
    param([string]$Start, [string]$Backend)

    if ($Start -and (Test-Path -LiteralPath (Join-Path $Start 'package.json'))) {
        return $Start
    }

    if ($Backend) {
        $config = Get-ProjectConfig -Root $Backend
        if ($config -and $config.frontend) {
            $candidate = Resolve-ConfigPath -Root $Backend -Value $config.frontend
            if (Has-ViteConfig -Root $candidate) {
                return $candidate
            }
        }
    }

    if ($Start) {
        $directories = Get-ChildItem -LiteralPath $Start -Directory -ErrorAction SilentlyContinue
        foreach ($directory in $directories) {
            if (Has-ViteConfig -Root $directory.FullName) {
                return $directory.FullName
            }
        }
    }

    return ''
}

function Add-ProcessTree {
    param([int]$ProcessId)

    if ($ProcessId -le 0) { return }
    if (-not $script:KillIds.Add($ProcessId)) { return }

    $children = $script:AllProcesses | Where-Object { $_.ParentProcessId -eq $ProcessId }
    foreach ($child in $children) {
        Add-ProcessTree -ProcessId ([int]$child.ProcessId)
    }
}

function Add-PortOwnerTree {
    param([int]$Owner)

    if ($Owner -le 0) { return }

    Add-ProcessTree -ProcessId $Owner

    $current = $script:AllProcesses | Where-Object { $_.ProcessId -eq $Owner } | Select-Object -First 1
    if ($current) {
        $parent = [int]$current.ParentProcessId
        if ($parent -gt 0) {
            Add-ProcessTree -ProcessId $parent
        }
    }
}

function Stop-ProjectProcesses {
    $script:AllProcesses = Get-CimInstance Win32_Process
    $script:KillIds = [System.Collections.Generic.HashSet[int]]::new()

    foreach ($port in @($BackendPort, $FrontendPort)) {
        $owners = @(
            Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
                Where-Object { $_.LocalPort -eq $port } |
                Select-Object -ExpandProperty OwningProcess -Unique
        )

        foreach ($owner in $owners) {
            Add-PortOwnerTree -Owner ([int]$owner)
        }
    }

    $script:KillIds |
        Sort-Object -Descending |
        ForEach-Object {
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
        }

    Start-Sleep -Seconds 2
}

function Start-Backend {
    param([string]$Root, [int]$Port)

    if (-not (Has-MainPy -Root $Root)) {
        Write-Host "Backend root not found: $Root"
        return $false
    }

    $python = Join-Path $Root '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python)) {
        $command = Get-Command python -ErrorAction SilentlyContinue
        if (-not $command) {
            Write-Host "Python not found for backend root: $Root"
            return $false
        }
        $python = $command.Source
    }

    $backendOut = Join-Path $Root 'uvicorn_stdout.log'
    $backendErr = Join-Path $Root 'uvicorn_stderr.log'

    Start-Process -FilePath $python `
        -ArgumentList @('-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', "$Port", '--reload') `
        -WorkingDirectory $Root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $backendOut `
        -RedirectStandardError $backendErr | Out-Null

    return $true
}

function Start-Frontend {
    param([string]$Root, [int]$Port)

    if (-not (Has-ViteConfig -Root $Root)) {
        Write-Host "Frontend root not found: $Root"
        return $false
    }

    $vite = Join-Path $Root 'node_modules\vite\bin\vite.js'
    if (Test-Path -LiteralPath $vite) {
        $node = (Get-Command node -ErrorAction SilentlyContinue).Source
        if (-not $node) {
            $node = 'node.exe'
        }

        $frontendOut = Join-Path $Root 'vite_stdout.log'
        $frontendErr = Join-Path $Root 'vite_stderr.log'

        Start-Process -FilePath $node `
            -ArgumentList @($vite, '--host', '127.0.0.1', '--port', "$Port") `
            -WorkingDirectory $Root `
            -WindowStyle Hidden `
            -RedirectStandardOutput $frontendOut `
            -RedirectStandardError $frontendErr | Out-Null

        return $true
    }

    $npm = (Get-Command npm.cmd -ErrorAction SilentlyContinue).Source
    if (-not $npm) {
        Write-Host "Vite entry or npm not found in frontend root: $Root"
        return $false
    }

    $frontendOut = Join-Path $Root 'vite_stdout.log'
    $frontendErr = Join-Path $Root 'vite_stderr.log'

    Start-Process -FilePath $npm `
        -ArgumentList @('run', 'dev', '--', '--host', '127.0.0.1', '--port', "$Port") `
        -WorkingDirectory $Root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $frontendOut `
        -RedirectStandardError $frontendErr | Out-Null

    return $true
}

function Wait-ForHttp {
    param([string]$Url)

    for ($i = 0; $i -lt 15; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            return $response.StatusCode
        }
        catch {
            Start-Sleep -Milliseconds 500
        }
    }

    return $null
}

$startPath = if ($BackendRoot) { $BackendRoot } else { (Get-Location).Path }
$config = Get-ProjectConfig -Root $startPath

if ($config -and $config.backendPort -and $BackendPort -eq 8000) {
    $BackendPort = [int]$config.backendPort
}
if ($config -and $config.frontendPort -and $FrontendPort -eq 5173) {
    $FrontendPort = [int]$config.frontendPort
}

$resolvedBackend = if ($BackendRoot) {
    $BackendRoot
}
else {
    Find-BackendRoot -Start $startPath
}

if (-not $resolvedBackend) {
    Write-Host 'No FastAPI backend found in the current project.'
    exit 1
}

$resolvedFrontend = if ($FrontendRoot) {
    $FrontendRoot
}
else {
    Find-FrontendRoot -Start $startPath -Backend $resolvedBackend
}

Stop-ProjectProcesses

Write-Host "Backend: $resolvedBackend"
Write-Host "Frontend: $resolvedFrontend"
Write-Host 'Starting backend and frontend...'

Start-Backend -Root $resolvedBackend -Port $BackendPort
if ($resolvedFrontend) {
    Start-Frontend -Root $resolvedFrontend -Port $FrontendPort
}
else {
    Write-Host 'No frontend root detected; backend started only.'
}

$backendStatus = Wait-ForHttp -Url "http://127.0.0.1:$BackendPort/openapi.json"
$frontendStatus = if ($resolvedFrontend) {
    Wait-ForHttp -Url "http://127.0.0.1:$FrontendPort/my"
}
else {
    $null
}

if ($backendStatus -ne 200) {
    Write-Host "Backend status: $backendStatus"
    Get-Content -Tail 30 (Join-Path $resolvedBackend 'uvicorn_stderr.log') -ErrorAction SilentlyContinue
    exit 1
}

if ($resolvedFrontend -and $frontendStatus -ne 200) {
    Write-Host "Frontend status: $frontendStatus"
    Get-Content -Tail 30 (Join-Path $resolvedFrontend 'vite_stderr.log') -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Backend ready: http://127.0.0.1:$BackendPort"
if ($resolvedFrontend) {
    Write-Host "Frontend ready: http://localhost:$FrontendPort"
}

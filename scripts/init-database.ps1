# 执行 database/init.sql（密码从 backend/.env 读取）
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$envFile = Join-Path $root "backend\.env"
$sqlFile = Join-Path $root "database\init.sql"

if (-not (Test-Path $envFile)) {
    Write-Error "未找到 backend\.env，请先复制 backend\.env.example 为 .env 并填写 DB_PASSWORD"
    exit 1
}

$dbPassword = $null
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*DB_PASSWORD\s*=\s*(.+)\s*$') {
        $dbPassword = $matches[1].Trim()
    }
}
if (-not $dbPassword) {
    Write-Error "backend\.env 中未找到 DB_PASSWORD"
    exit 1
}

$mysqlCandidates = @(
    "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe",
    "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
)
$mysql = $mysqlCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $mysql) {
    Write-Error "未找到 mysql.exe，请确认 MySQL 已安装并在 PATH 中"
    exit 1
}

& $mysql -u root "-p$dbPassword" -e "source $($sqlFile -Replace '\\','/')"
Write-Host "数据库 init.sql 执行完成。"

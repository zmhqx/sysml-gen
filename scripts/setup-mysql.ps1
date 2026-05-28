# 初始化并启动 MySQL 8.4（与 backend/.env 中密码 Baiyu0713@ 一致）
$ErrorActionPreference = "Stop"
$basedir = "C:\Program Files\MySQL\MySQL Server 8.4"
$datadir = "C:\ProgramData\MySQL\MySQL Server 8.4\Data"
# 配置文件放在无空格路径，避免 mysqld 启动失败
$iniPath = Join-Path $PSScriptRoot "my.ini"
$serviceName = "MySQL84"
$rootPassword = "Baiyu0713@"

$mysqld = Join-Path $basedir "bin\mysqld.exe"
$mysql = Join-Path $basedir "bin\mysql.exe"

New-Item -ItemType Directory -Force -Path (Split-Path $datadir) | Out-Null
New-Item -ItemType Directory -Force -Path $datadir | Out-Null

if (-not (Test-Path (Join-Path $datadir "mysql"))) {
    Write-Host "正在初始化数据目录..."
    & $mysqld --initialize-insecure --datadir="$datadir" --basedir="$basedir"
}

@"
[mysqld]
basedir=$basedir
datadir=$datadir
port=3306
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

[client]
port=3306
default-character-set=utf8mb4
"@ | Set-Content -Path $iniPath -Encoding ASCII

$existing = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if (-not $existing) {
    Write-Host "正在注册 Windows 服务 $serviceName ..."
    & $mysqld --install $serviceName --defaults-file="$iniPath"
}

$svc = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($svc.Status -ne 'Running') {
    Write-Host "正在启动服务..."
    Start-Service $serviceName
    Start-Sleep -Seconds 3
}

Write-Host "正在设置 root 密码..."
& $mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$rootPassword'; FLUSH PRIVILEGES;"
Write-Host "MySQL 已就绪。root 密码: $rootPassword"

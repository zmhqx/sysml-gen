# 后端 API 一键演示（需先启动 uvicorn）
$base = "http://127.0.0.1:8000/api/v1"
$ErrorActionPreference = "Stop"

function Invoke-Api {
    param($Method, $Uri, $Body = $null, $Token = $null, $Form = $null)
    $headers = @{}
    if ($Token) { $headers["Authorization"] = "Bearer $Token" }
    $params = @{ Method = $Method; Uri = $Uri; Headers = $headers }
    if ($Body) { $params["Body"] = ($Body | ConvertTo-Json); $params["ContentType"] = "application/json" }
    if ($Form) { $params["Form"] = $Form }
    Invoke-RestMethod @params
}

Write-Host "1. 健康检查..."
Invoke-RestMethod "http://127.0.0.1:8000/health"

Write-Host "2. 注册用户 demo / 密码 Demo123456..."
try {
    Invoke-Api POST "$base/auth/register" @{ username = "demo"; password = "Demo123456"; full_name = "演示用户" }
} catch { Write-Host "  (用户可能已存在，跳过)" }

Write-Host "3. 登录..."
$login = Invoke-Api POST "$base/auth/login" @{ username = "demo"; password = "Demo123456" }
$token = $login.access_token
Write-Host "  已获取 access_token"

Write-Host "4. 将 demo 设为 manager（需 MySQL 已执行）..."
$mysql = "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"
& $mysql -u root "-pBaiyu0713@" -e "UPDATE sysmldocgen.users SET role='manager' WHERE username='demo';" 2>$null

Write-Host "5. 创建项目..."
$proj = Invoke-Api POST "$base/projects" @{ name = "演示项目"; description = "脚本演示" } -Token $token
$pid = $proj.id
Write-Host "  项目 ID: $pid"

$jsonPath = Join-Path $env:TEMP "demo-model.json"
@'
{"elements":[{"element_id":"REQ-1","element_name":"需求示例","element_type":"Requirement","parent_element_id":"","description":"演示"}],"relationships":[]}
'@ | Set-Content $jsonPath -Encoding UTF8

Write-Host "6. 上传并解析模型..."
$boundary = [System.Guid]::NewGuid().ToString()
# 使用 curl 更可靠地上传文件
$uploadOut = curl.exe -s -X POST "$base/models/upload" `
    -H "Authorization: Bearer $token" `
    -F "project_id=$pid" `
    -F "file=@$jsonPath" `
    -F "auto_parse=true" `
    -F "run_async=false" `
    -F "import_mode=replace"
$model = $uploadOut | ConvertFrom-Json
$mid = $model.id
Write-Host "  模型 ID: $mid  parse_status: $($model.parse_status)"

Write-Host "7. 查看元素..."
$els = Invoke-Api GET "$base/models/$mid/elements" -Token $token
Write-Host "  元素数量: $($els.Count)"

Write-Host "8. 创建模板并生成文档..."
$tpl = Invoke-Api POST "$base/templates" @{
    name = "演示模板"; template_type = "说明"
    content = "<h1>{{ model_name }}</h1><ul>{% for e in elements %}<li>{{ e.name }}</li>{% endfor %}</ul>"
} -Token $token
$doc = Invoke-Api POST "$base/documents/generate" @{
    project_id = $pid; model_id = $mid; template_id = $tpl.id
} -Token $token
Write-Host "  文档 ID: $($doc.id) status: $($doc.status)"

Write-Host "`n演示完成。打开 http://localhost:8000/docs 可继续手动操作。"

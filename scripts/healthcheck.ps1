# SOC Log Lab - Health Check Script
# Returns HTTP status code of the application

param(
    [string]$Url = "http://127.0.0.1:8000",
    [int]$Timeout = 10
)

try {
    $request = [System.Net.WebRequest]::Create($Url)
    $request.Timeout = $Timeout * 1000
    $response = $request.GetResponse()
    $statusCode = [int]$response.StatusCode
    $response.Close()

    if ($statusCode -eq 200) {
        Write-Host "[HEALTH] Application is RUNNING (HTTP $statusCode)" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "[HEALTH] Application returned HTTP $statusCode" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "[HEALTH] Application is DOWN: $_" -ForegroundColor Red
    exit 2
}

$secret = "shiprocket_secret_familybookstore_2026"
$payload = '{"event":"ORDER_SHIPPED","awb":"1234567890","order_id":"FB123","status":"shipped","current_status":"SHIPPED"}'

# Generate signature
$hmac = New-Object System.Security.Cryptography.HMACSHA256
$hmac.Key = [Text.Encoding]::UTF8.GetBytes($secret)
$signature = [BitConverter]::ToString($hmac.ComputeHash([Text.Encoding]::UTF8.GetBytes($payload))).Replace('-','').ToLower()

Write-Host "Generated signature: $signature"

# Send request
try {
    $response = Invoke-WebRequest -Uri "https://resources-yellow-associates-dual.trycloudflare.com/webhook/shiprocket/" -Method POST -Headers @{
        "Content-Type" = "application/json"
        "anx-api-key" = $signature
    } -Body $payload -UseBasicParsing
    
    Write-Host "SUCCESS: $($response.Content)"
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
}
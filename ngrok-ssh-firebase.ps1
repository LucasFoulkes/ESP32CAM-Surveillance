# Function to check internet connectivity
function Test-InternetConnection {
    try {
        $response = Invoke-RestMethod -Uri "https://www.google.com" -Method Head -TimeoutSec 5
        return $true
    }
    catch {
        return $false
    }
}

# Function to update Firebase with the forwarding address
function Update-Firebase($forwardingAddress) {
    $firebaseUrl = "https://sshrelay-23b2e-default-rtdb.firebaseio.com/vr001.json"
    $data = @{
        "forwarding_address" = $forwardingAddress
    }
    Invoke-RestMethod -Method Put -ContentType "application/json" -Body ($data | ConvertTo-Json) -Uri $firebaseUrl
}

$ngrokRunning = $false

while ($true) {
    # Check internet connectivity
    if (Test-InternetConnection) {
        if (-not $ngrokRunning) {
            # Kill previous ngrok processes
            Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Stop-Process

            # Start ngrok tunnel in the foreground
            Start-Process -FilePath "ngrok" -ArgumentList "tcp 22"
            Start-Sleep -Seconds 10 # Wait for ngrok to initialize

            # Fetch ngrok tunnel address from the local ngrok API
            try {
                $ngrokData = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels"
                $ngrokAddress = $ngrokData.tunnels[0].public_url

                # Update Firebase with the ngrok address
                Update-Firebase $ngrokAddress
                Write-Output "Ngrok address sent to Firebase: $ngrokAddress"

                $ngrokRunning = $true
            }
            catch {
                Write-Output "Failed to fetch ngrok address or update Firebase."
            }
        }
    }
    else {
        Write-Output "No internet connection. Retrying in 30 seconds..."
        $ngrokRunning = $false
    }

    # Wait for 30 seconds before checking again
    Start-Sleep -Seconds 30
}
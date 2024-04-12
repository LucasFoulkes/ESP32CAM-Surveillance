# Function to run Python script
function Run-PythonScript {
    Start-Process -FilePath "python" -ArgumentList "C:\Path\To\my_python_script.py"
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

                # Run Python script
                Run-PythonScript

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

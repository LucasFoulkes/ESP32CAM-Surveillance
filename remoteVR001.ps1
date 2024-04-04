# Function to retrieve the forwarding address from Firebase
function Get-ForwardingAddress {
    $firebaseUrl = "https://sshrelay-23b2e-default-rtdb.firebaseio.com/vr001.json"
    $response = Invoke-RestMethod -Uri $firebaseUrl
    return $response.forwarding_address
}

# Function to extract the hostname and port from the forwarding address
function Get-HostnameAndPort($forwardingAddress) {
    $match = $forwardingAddress -match 'tcp://(\S+):(\d+)'
    if ($match) {
        $hostname = $matches[1]
        $port = $matches[2]
        return $hostname, $port
    }
    else {
        throw "Invalid forwarding address format."
    }
}

# Function to establish an SSH connection
function Connect-SSH($hostname, $port) {
    ssh -p $port administrator@$hostname
}

# Main script
try {
    # Retrieve the forwarding address from Firebase
    $forwardingAddress = Get-ForwardingAddress

    # Extract the hostname and port from the forwarding address
    $hostname, $port = Get-HostnameAndPort $forwardingAddress

    # Establish the SSH connection
    Connect-SSH $hostname $port
}
catch {
    Write-Output "An error occurred: $_"
}
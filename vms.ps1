
$logs_dirs = @(".\logs", ".\logs\errors", ".\logs\json")

foreach ($dir in $logs_dirs){
    if (!(Test-Path -Path $dir -PathType Container)) {
        New-Item -Path $dir -ItemType Directory | Out-Null
    }    
}


$vms = Get-VM
$vm_data = @()
$pcname = $env:COMPUTERNAME

foreach ($vm in $vms) {
    $adapters_data = @()

    foreach ($adapter in $vm.NetworkAdapters) {
        $adapter_info = [PSCustomObject]@{
            "mac" = $adapter.MacAddress
            "vlan" = ($adapter | Get-VMNetworkAdapterVlan).AccessVlanId
        }
        $adapters_data += $adapter_info
    }

    $vm_info = [PSCustomObject]@{
        "vm_id" = $vm.VMId
        "name" = $vm.Name
        "uptime" = [int]$vm.Uptime.TotalSeconds
        "adapters" = $adapters_data

    }
    $vm_data += $vm_info
}

$json = @{
    "name" = $pcname
    "vms" = $vm_data
} | ConvertTo-Json  -Depth 4

$response = Invoke-WebRequest http://inventory.local/api/v1/vms/ -Method 'POST' -Body $json -ContentType 'application/json; charset=utf-8'

if (!$response.StatusCode){
    $Error[0].Exception.Message | Out-File -FilePath ".\logs\errors\$($pcname).json"
    $json | Set-Content -Path ".\logs\json\$($pcname).json"
} 
else{
    $json | Set-Content -Path ".\logs\json\$($pcname).json"
}
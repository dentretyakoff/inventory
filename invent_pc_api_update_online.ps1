$ErrorActionPreference = "Stop"


function get_data_send_to_api ($pc){
    # $pcname
    $pcname = $pc.name
    $last_logon_timestamp = $pc.lastLogonTimestamp
    $last_logon_timestamp = [datetime]::FromFileTime([Int64]::Parse($last_logon_timestamp)).ToString('yyyy-MM-ddTHH:mm') # 2023-09-29T12:30

    $json = @{
        pc_name = $pcname
        online_date = $last_logon_timestamp
    } | ConvertTo-Json

    # $json
    $response = Invoke-WebRequest http://inventory.local/api/v1/comps/ -Method 'PATCH' -Body $json -ContentType 'application/json; charset=utf-8'


    if (!$response.StatusCode){
        $Error[0].Exception.Message | Out-File -FilePath ".\logs\errors\$($pcname)_update_online.json"
        $json | Set-Content -Path ".\logs\json\$($pcname)_update_online.json"
    } 
    else{
        $json | Set-Content -Path ".\logs\json\$($pcname)_update_online.json"
    }
}

$logs_dirs = @(".\logs", ".\logs\errors", ".\logs\json")

foreach ($dir in $logs_dirs){
    if (!(Test-Path -Path $dir -PathType Container)) {
        New-Item -Path $dir -ItemType Directory | Out-Null
    }    
}

$comps = Get-ADComputer -Properties lastLogonTimestamp -Filter * -SearchBase "OU=Компьютеры домена,DC=company,DC=local" | Where-Object {($_.enabled -eq $true) -and ($_.DistinguishedName -notlike "*OU=Промышленные компьютеры,*")}

$current_date = Get-Date -Format 'dd.MM.yyyy-HHmmss'


foreach ($comp in $comps){
    try {
        get_data_send_to_api $comp
    }
    catch {
        "$pc`t$($Error[0].Exception.Message)" | Add-Content ".\logs\errors\$($current_date)_update_online.log"
    }
}

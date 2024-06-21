$ErrorActionPreference = "Stop"

  
  #List of Manufacture Codes that could be pulled from WMI and their respective full names. Used for translating later down.
  $ManufacturerHash = @{ 
    "AAC" =	"AcerView";
    "ACI" = "Asus";
    "ACR" = "Acer";
    "AOC" = "AOC";
    "AIC" = "AG Neovo";
    "APP" = "Apple Computer";
    "AST" = "AST Research";
    "AUO" = "Asus";
    "BNQ" = "BenQ";
    "CMO" = "Acer";
    "CPL" = "Compal";
    "CPQ" = "Compaq";
    "CPT" = "Chunghwa Pciture Tubes, Ltd.";
    "CTX" = "CTX";
    "DEC" = "DEC";
    "DEL" = "Dell";
    "DPC" = "Delta";
    "DWE" = "Daewoo";
    "EIZ" = "EIZO";
    "ELS" = "ELSA";
    "ENC" = "EIZO";
    "EPI" = "Envision";
    "FCM" = "Funai";
    "FUJ" = "Fujitsu";
    "FUS" = "Fujitsu-Siemens";
    "GSM" = "LG Electronics";
    "GWY" = "Gateway 2000";
    "HEI" = "Hyundai";
    "HIT" = "Hyundai";
    "HSL" = "Hansol";
    "HTC" = "Hitachi/Nissei";
    "HWP" = "HP";
    "IBM" = "IBM";
    "ICL" = "Fujitsu ICL";
    "IVM" = "Iiyama";
    "KDS" = "Korea Data Systems";
    "LEN" = "Lenovo";
    "LGD" = "Asus";
    "LPL" = "Fujitsu";
    "MAX" = "Belinea"; 
    "MEI" = "Panasonic";
    "MEL" = "Mitsubishi Electronics";
    "MS_" = "Panasonic";
    "NAN" = "Nanao";
    "NEC" = "NEC";
    "NOK" = "Nokia Data";
    "NVD" = "Fujitsu";
    "OPT" = "Optoma";
    "PHL" = "Philips";
    "REL" = "Relisys";
    "SAN" = "Samsung";
    "SAM" = "Samsung";
    "SBI" = "Smarttech";
    "SGI" = "SGI";
    "SNY" = "Sony";
    "SRC" = "Shamrock";
    "SUN" = "Sun Microsystems";
    "SEC" = "Hewlett-Packard";
    "TAT" = "Tatung";
    "TOS" = "Toshiba";
    "TSB" = "Toshiba";
    "VSC" = "ViewSonic";
    "ZCM" = "Zenith";
    "UNK" = "Unknown";
    "_YV" = "Fujitsu";
      }   


function get_data_send_to_api ($pcname){
    $pcname
    #Takes each monitor object found and runs the following code:
    $monitors = @()
    foreach ($Monitor in Get-WmiObject -ComputerName $pcname -Namespace "root\WMI" -Class "WMIMonitorID" -ErrorAction SilentlyContinue) {
      
        #Grabs respective data and converts it from ASCII encoding and removes any trailing ASCII null values
        If ($Monitor.UserFriendlyName -ne $null -and [System.Text.Encoding]::ASCII.GetString($Monitor.UserFriendlyName) -ne $null) {
            $Mon_Model = ([System.Text.Encoding]::ASCII.GetString($Monitor.UserFriendlyName)).Replace("$([char]0x0000)","")
        } else {
            $Mon_Model = $null
        }
        $Mon_Serial_Number = ([System.Text.Encoding]::ASCII.GetString($Monitor.SerialNumberID)).Replace("$([char]0x0000)","")
        $Mon_Manufacturer = ([System.Text.Encoding]::ASCII.GetString($Monitor.ManufacturerName)).Replace("$([char]0x0000)","")
      
        #Sets a friendly name based on the hash table above. If no entry found sets it to the original 3 character code
        $Mon_Manufacturer_Friendly = $ManufacturerHash.$Mon_Manufacturer
        If ($Mon_Manufacturer_Friendly -eq $null) {
        $Mon_Manufacturer_Friendly = $Mon_Manufacturer
        }

        $monitors += @(@{
            manufacturer = $Mon_Manufacturer_Friendly
            model = $Mon_Model
            serial_number = $Mon_Serial_Number
        })

    }


    #имя файла для записи информации
    $cpu_name = (Get-WmiObject -ComputerName $pcname win32_processor).Name
    $motherboard = (Get-WmiObject -ComputerName $pcname win32_baseboard).Manufacturer + " " + (Get-WmiObject -ComputerName $pcname win32_baseboard).Product
    $MEM = Get-WmiObject -ComputerName $pcname Win32_PhysicalMemory
    $DD = Get-WmiObject -ComputerName $pcname Win32_DiskDrive | Where-Object {$_.MediaType -ne "Removable Media"}
    $sys = (Get-WmiObject -ComputerName $pcname -class Win32_OperatingSystem).Caption
    $sys_arch = (Get-WmiObject -ComputerName $pcname Win32_ComputerSystem).systemtype
    $last_user = ((Get-WMIObject -ComputerName $pcname Win32_ComputerSystem -ErrorAction SilentlyContinue).Username -split "\\")[1]

    # Получение веб камеры
    $web_camera = (Get-WmiObject -ComputerName $pcname Win32_PnPEntity | Where-Object {$_.Service -eq 'usbvideo'}).Name -join ";"
    if (!$web_camera){
        $web_camera = '-'
    }
    
    # Получение департамента
    if ($last_user){
        $department = (Get-ADUser $last_user -Properties department).Department
    }
    if (!$department){
        $department = '-'
    }

    #оперативная память
    $ozu = @()
    foreach($memory in $MEM) {
        $ozu += @(@{
            model = $memory.Manufacturer
            capacity = $memory.Capacity / [math]::Pow(1024,3)
            serial_number = $memory.SerialNumber
        })
    }
    #диски
    $disk_info = @()
    foreach($disk in $DD) {
        $disk_info += @(@{
            model = $disk.Model
            capacity = [math]::Truncate($disk.Size / [math]::Pow(1024,3))
            serial_number = $disk.SerialNumber
        })
    }

    $json = @{
        pc_name = $pcname
        win_ver = $sys
        os_arch = $sys_arch
        cpu = $cpu_name
        motherboard = $motherboard
        rams = $ozu
        disks = $disk_info
        monitors = $monitors
        web_camera = $web_camera
        department = $department
    }| ConvertTo-Json

    $response = Invoke-WebRequest http://inventory.local/api/v1/comps/ -Method 'POST' -Body $json -ContentType 'application/json; charset=utf-8'


    if (!$response.StatusCode){
        $Error[0].Exception.Message | Out-File -FilePath ".\logs\errors\$($pcname).json"
        $json | Set-Content -Path ".\logs\json\$($pcname).json"
    } 
    else{
        $json | Set-Content -Path ".\logs\json\$($pcname).json"
    }
}

$logs_dirs = @(".\logs", ".\logs\errors", ".\logs\json")

foreach ($dir in $logs_dirs){
    if (!(Test-Path -Path $dir -PathType Container)) {
        New-Item -Path $dir -ItemType Directory | Out-Null
    }    
}

$Comp = (Get-ADComputer -Filter * -SearchBase "OU=Компьютеры домена,DC=company,DC=local" | Where-Object {($_.enabled -eq $true) -and ($_.DistinguishedName -notlike "*OU=Технические компьютеры,*")}).name
$CompOnline = ($Comp | ForEach-Object {Test-Connection -ComputerName $_ -Count 1 -AsJob} | Get-Job | Receive-Job -Wait | Select-Object @{Name='ComputerName';Expression={$_.Address}},@{Name='Reachable';Expression={if ($_.StatusCode -eq 0) { $true } else { $false }}} | Where-Object {$_.Reachable -eq "True"}).ComputerName | Sort-Object

$CurrentDate = Get-Date -Format 'dd.MM.yyyy-HHmmss'
$startTime = Get-Date
$report_file = ".\logs\report_$($CurrentDate).log"


@"
##############################################
## Время запуска: $($startTime.ToLongTimeString())
## Получено компьютеров из AD: $($Comp.Count)
## Онлайн компьютеров: $($CompOnline.Count)
"@ | Add-Content $report_file


foreach ($pc in $CompOnline){
    try {
        get_data_send_to_api $pc
        $comp_successful += 1
    }
    catch {
        "$pc`t$($Error[0].Exception.Message)" | Add-Content ".\logs\errors\$($CurrentDate).log"
        $comp_error += 1
    }
}

$endTime = Get-Date
$executionTime = $endTime - $startTime

$hours = [math]::floor($executionTime.TotalHours)
$minutes = $executionTime.Minutes
$seconds = $executionTime.Seconds

@"
## Успешно опрошено: $($comp_successful)
## Ошибок при опросе: $($comp_error)
## Время остановки: $($endTime.ToLongTimeString())
## Скрипт выполнился за: $($hours):$($minutes):$($seconds)
##############################################
"@ | Add-Content $report_file

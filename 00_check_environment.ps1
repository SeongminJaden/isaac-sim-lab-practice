# 확인할 Sim Python 실행 파일 경로다.
param([string]$Python = 'C:\isaac-course\simenv\Scripts\python.exe')
# 점검 도중 발생한 PowerShell 오류를 중단한다.
$ErrorActionPreference = 'Stop'
# Windows 버전 정보를 조회한다.
$os = Get-CimInstance Win32_OperatingSystem
# 물리 메모리를 포함한 PC 정보를 조회한다.
$computer = Get-CimInstance Win32_ComputerSystem
# RAM 바이트 수를 GiB로 변환한다.
$ram = [math]::Round($computer.TotalPhysicalMemory / 1GB, 1)
# Lab 설치에 필요한 긴 경로 설정을 읽기만 한다.
$longPaths = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem').LongPathsEnabled
# OS·RAM·긴 경로 설정을 화면에 표시한다.
Write-Host "OS: $($os.Caption) / RAM: $ram GiB / LongPathsEnabled: $longPaths"
# 수업은 Windows 11을 대상으로 한다.
if ($os.Caption -notmatch 'Windows 11') { Write-Warning 'Course target: Windows 11 x64.' }
# 32 GB보다 작은 메모리 구성을 경고한다.
if ($ram -lt 31) { Write-Warning 'Isaac Sim 6.1 minimum RAM: 32 GB.' }
# 긴 경로가 꺼져 있으면 설치 안내를 확인하게 한다.
if ($longPaths -ne 1) { Write-Warning 'Enable Windows long paths before installing Isaac Lab. See README.' }
# NVIDIA 드라이버의 진단 도구가 있는지 확인한다.
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    # GPU 이름·드라이버·VRAM을 조회한다.
    & nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    # 진단 명령 자체의 실패를 검사한다.
    if ($LASTEXITCODE -ne 0) { throw 'nvidia-smi failed. Check the NVIDIA driver.' }
# 도구가 없으면 드라이버 확인이 필요하다고 안내한다.
} else { Write-Warning 'nvidia-smi not found. Check the NVIDIA driver.' }
# 드라이브별 남은 공간을 GiB로 표시한다.
Get-PSDrive -PSProvider FileSystem | Select-Object Name,@{N='FreeGiB';E={[math]::Round($_.Free/1GB,1)}}
# Python 환경이 이미 있으면 패키지와 CUDA 접근을 확인한다.
if (Test-Path -LiteralPath $Python) {
    # Python·Sim·Torch 버전과 GPU 사용 가능 여부를 출력한다.
    & $Python -c "import sys,importlib.metadata as m; print(sys.version); print('isaacsim',m.version('isaacsim')); import torch; print('torch',torch.__version__,'CUDA',torch.version.cuda,'GPU available',torch.cuda.is_available())"
    # DLL 차단이나 패키지 누락을 점검 실패로 알린다.
    if ($LASTEXITCODE -ne 0) { throw 'Python package check failed. Check the selected environment.' }
# 설치 전이라면 환경을 먼저 준비해야 한다고 안내한다.
} else { Write-Host 'Isaac Python not found yet. Install first, or pass -Python with its full path.' }
# 진단 출력만으로 렌더링이나 물리 성공을 보장하지 않는다.
Write-Host 'This checks prerequisites only; it does not prove RTX rendering or simulation works.'

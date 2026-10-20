# 새 Sim 가상환경 경로를 받는다. Lab 환경은 별도다.
param([string]$Environment = 'C:\isaac-course\simenv')
# PowerShell 명령 실패 시 중단한다.
$ErrorActionPreference = 'Stop'
# 기존 환경은 덮어쓰지 않는다.
if (Test-Path -LiteralPath $Environment) { throw "Already exists: $Environment. Use the existing installation or choose a new -Environment." }
# Python Launcher가 없으면 Python 설치 안내를 따른다.
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'Install Python 3.12 x64 with the Python launcher first.' }
# 수업 기준 Python 3.12를 검사한다.
& py -3.12 -c "import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize('P') == 8"
# 버전 점검이 실패하면 환경을 만들지 않는다.
if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 is required.' }
# 시스템 Python과 분리된 가상환경을 만든다.
& py -3.12 -m venv $Environment
# 환경 생성 실패를 검사한다.
if ($LASTEXITCODE -ne 0) { throw 'Failed to create the virtual environment.' }
# 이후 패키지는 새 환경의 Python으로만 설치한다.
$python = Join-Path $Environment 'Scripts\python.exe'
# 최신 wheel을 설치할 수 있도록 pip를 준비한다.
& $python -m pip install --upgrade pip
# pip 준비 오류를 검사한다.
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
# CUDA 13용 PyTorch 2.11을 설치한다.
& $python -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu130
# PyTorch 설치 실패를 검사한다.
if ($LASTEXITCODE -ne 0) { throw 'CUDA PyTorch installation failed.' }
# Isaac Sim 6.1 본체와 확장 캐시를 설치한다.
& $python -m pip install 'isaacsim[all,extscache]==6.1.0.0' --extra-index-url https://pypi.nvidia.com
# Sim 설치 오류를 무시하고 실행하지 않는다.
if ($LASTEXITCODE -ne 0) { throw 'Isaac Sim installation failed. Read the first error above.' }
# 설치된 패키지의 의존성 충돌을 검사한다.
& $python -m pip check
# 검사 실패를 설치 성공으로 표시하지 않는다.
if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
# 완료된 환경의 실행 파일 위치를 알린다.
Write-Host "Installed. Launch: & '$Environment\Scripts\isaacsim.exe'"
# 첫 실행의 약관은 사용자가 직접 확인한다.
Write-Host 'Read and respond to the NVIDIA license prompt on first launch.'

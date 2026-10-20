#!/usr/bin/env bash
# Ubuntu 24.04 x86_64용 Sim 6.1 전용 환경을 만든다. Lab의 .venv와는 별도다.
set -euo pipefail # 설치 단계 중 하나라도 실패하면 중단한다.
env_dir="${1:-$HOME/pa-course/.venv-isaacsim}" # 첫 인자로 새 환경 경로를 바꿀 수 있다.
(($# <= 1)) || { echo 'Usage: bash 01_install_sim.sh [new-environment-path]' >&2; exit 2; } # 남는 인자를 무시하지 않는다.
[[ ! -e "$env_dir" ]] || { echo "Already exists: $env_dir" >&2; exit 1; } # 기존 환경을 덮어쓰지 않는다.
python3.12 -c 'import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize("P") == 8' # Python 버전과 64비트를 검사한다.
python3.12 -m venv "$env_dir" # 시스템 Python과 분리된 가상환경을 만든다.
python="$env_dir/bin/python" # 이후 명령은 이 환경의 Python만 사용한다.
"$python" -m pip install --upgrade pip # wheel 설치에 사용할 pip를 준비한다.
"$python" -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu130 # CUDA 13 빌드를 설치한다.
"$python" -m pip install 'isaacsim[all,extscache]==6.1.0.0' --extra-index-url https://pypi.nvidia.com # Sim과 확장 캐시를 설치한다.
"$python" -m pip check # 의존성 충돌이 있으면 성공으로 표시하지 않는다.
printf 'Installed. Launch: %s/bin/isaacsim\n' "$env_dir" # 실행 파일 위치를 알려준다.
printf '%s\n' 'Read and respond to the NVIDIA license prompt on first launch.' # 약관은 사용자가 확인한다.

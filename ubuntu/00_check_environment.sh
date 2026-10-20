#!/usr/bin/env bash
# Ubuntu 버전, GPU, 메모리, Python 환경을 확인한다. 시뮬레이션 성공 검사는 아니다.
set -euo pipefail # 예상하지 않은 명령 실패를 숨기지 않는다.
cat /etc/os-release # 설치된 배포판 이름과 버전을 보여준다.
uname -m # PC x86_64인지 확인한다. 이 안내는 Jetson용이 아니다.
free -h # 사용 가능한 시스템 메모리를 확인한다.
df -h "$HOME" # 가상환경과 학습 로그를 저장할 디스크 여유를 확인한다.
python3.12 --version # 수업 기준 Python이 설치되어 있는지 확인한다.
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader # GPU 모델, 드라이버, VRAM을 출력한다.
if grep -qi microsoft /proc/sys/kernel/osrelease; then # WSL에서도 nvidia-smi만 성공할 수 있으므로 구분한다.
    echo 'WSL: CUDA visibility does not validate Isaac Sim RTX rendering.' # 네이티브 Ubuntu GPU 검증과 혼동하지 않는다.
fi
echo 'Prerequisites only. Run the exercises to validate rendering and physics.' # 실제 실습 실행이 별도로 필요하다.

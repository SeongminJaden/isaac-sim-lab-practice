#!/usr/bin/env bash
# Ubuntu에서 공통 Python 물리·카메라 예제를 지정한 Sim 환경으로 실행한다.
set -euo pipefail # 명령 실패와 미정의 변수 사용을 중단한다.
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd) # 호출한 터미널이 아닌 스크립트 위치에서 경로를 구한다.
python="${ISAAC_PYTHON:-$HOME/pa-course/.venv-isaacsim/bin/python}" # Workstation 사용자는 ISAAC_PYTHON에 python.sh를 지정한다.
example="${1:-}" # 첫 인자는 실행할 예제 번호다.
case "$example" in # 허용된 두 예제만 실행한다.
    01) script=01_drop_cubes.py ;; # 질량별 낙하와 높이 CSV 실습이다.
    02) script=02_camera_capture.py ;; # RGB·깊이 촬영 실습이다.
    *) echo 'Usage: bash run_sim.sh 01|02 [example options]' >&2; exit 2 ;; # 누락이나 오타를 거부한다.
esac
shift # 예제 번호를 제거하고 나머지 인자는 Python 예제로 넘긴다.
[[ -x "$python" ]] || { echo "Executable Isaac Python not found: $python" >&2; exit 1; } # 설치 경로를 확인한다.
exec "$python" "$root/examples/$script" "$@" # 공백과 옵션을 보존하고 Python의 종료 코드를 전달한다.

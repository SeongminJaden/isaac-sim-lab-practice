# 8 GB 소형 실습 설정

Isaac Sim 6.1의 공식 최소 VRAM은 16 GB이다. 이 자료의 8 GB 설정은 메모리 사용량을 낮추기 위한 출발점이며 실행 보장이 아니다.

- 물리 예제: 화면 640×360, 안티앨리어싱 끄기, 단일 GPU.
- 카메라 예제: RGB·깊이 320×240, 카메라 1개, 상자 5개.
- Isaac Lab: Cartpole 환경 1개부터 실행. 성공하면 메모리를 확인하면서 늘린다.
- 창 없이 실행해도 Isaac Sim의 NVIDIA GPU 요구는 유지된다.
- VirtualBox의 VMSVGA는 NVIDIA GPU가 아니다. VM에서 패키지 설치가 끝나도 Isaac Sim 렌더링·학습의 성공을 의미하지 않는다.

공식 요구 사항: https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html

Windows에서 WinError 4551이 발생하면 오류에 표시된 DLL과 Windows Code Integrity 기록을 확인한다. 앱 제어 정책의 차단은 해상도나 환경 수를 낮춰 해결되는 문제가 아니며, 해당 소프트웨어 실행이 허용되는 PC 환경이 필요하다.

## WSL 사용 범위

WSL2는 CUDA 계산을 지원하지만, CUDA 사용 가능 여부만으로 Isaac Sim의 RTX 렌더링이 가능하다고 판단할 수 없다. NVIDIA는 WSL2의 GPU·RTX 제한으로 Isaac Sim 컨테이너를 지원하지 않는다고 안내한다. 이 자료의 Ubuntu 명령은 NVIDIA GPU를 직접 사용하는 Ubuntu 24.04 PC를 기준으로 한다. WSL을 동일한 실행 환경으로 안내하지 않는다.

- CUDA on WSL: https://docs.nvidia.com/cuda/wsl-user-guide/index.html
- NVIDIA의 WSL2 지원 답변: https://forums.developer.nvidia.com/t/is-it-possible-to-run-isaac-sim-in-wsl2/349609/2

CPU 보상 계산 예제는 Isaac Sim을 불러오지 않으므로 Python 3.12만 있는 WSL에서도 실행할 수 있다. 이는 Isaac Sim이나 Isaac Lab GPU 실행 검증을 대신하지 않는다.

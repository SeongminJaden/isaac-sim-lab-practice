"""공통 장면 함수. SimulationApp을 만든 뒤에만 import한다."""
from datetime import datetime  # 실행별 결과 폴더에 시각을 붙인다.
from pathlib import Path  # Windows·Ubuntu 경로 차이를 처리한다.
import omni.usd  # 현재 USD 장면에 접근한다.
from pxr import Gf, UsdGeom, UsdLux, UsdPhysics  # 수학, 형상, 조명, 물리 스키마다.


def output_directory(label):  # 이전 결과를 덮어쓰지 않는 실행 폴더를 만든다.
    path = Path(__file__).resolve().parents[1] / "outputs" / f"{label}_{datetime.now():%Y%m%d_%H%M%S_%f}"  # 마이크로초까지 구분한다.
    path.mkdir(parents=True, exist_ok=False)  # 같은 이름이 이미 있으면 덮어쓰기 대신 실패한다.
    return path  # 호출자가 CSV나 이미지를 저장할 위치를 돌려준다.


def make_box(stage, path, position, size, color, mass=None):  # mass가 있으면 움직이는 강체, 없으면 고정 충돌체다.
    box = UsdGeom.Cube.Define(stage, path)  # 지정한 USD 경로에 정육면체를 정의한다.
    box.CreateSizeAttr(1.0)  # 기준 변 길이를 1로 정한다.
    box.AddTranslateOp().Set(Gf.Vec3d(*position))  # 중심 위치를 m 단위로 지정한다.
    box.AddScaleOp().Set(Gf.Vec3f(*size))  # 축별 배율이 곧 각 변의 길이가 된다.
    box.CreateDisplayColorAttr([Gf.Vec3f(*color)])  # RGB 0~1 색을 설정한다.
    UsdPhysics.CollisionAPI.Apply(box.GetPrim())  # 다른 충돌체와 접촉할 수 있게 한다.
    if mass is not None:  # 질량을 준 물체만 동역학 계산 대상으로 만든다.
        UsdPhysics.RigidBodyAPI.Apply(box.GetPrim())  # 중력과 힘에 따라 움직이는 강체 속성을 부여한다.
        UsdPhysics.MassAPI.Apply(box.GetPrim()).CreateMassAttr(mass)  # 질량을 kg 단위로 지정한다.
    return box  # 필요하면 호출자가 추가 속성을 설정할 수 있다.


def create_scene(gravity=9.81):  # 바닥과 조명을 갖춘 최소 장면을 만든다.
    stage = omni.usd.get_context().get_stage()  # SimulationApp이 만든 현재 장면을 사용한다.
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)  # z축이 위쪽이도록 정한다.
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)  # 장면 길이 1을 실제 1 m로 해석한다.
    stage.SetDefaultPrim(UsdGeom.Xform.Define(stage, "/World").GetPrim())  # 모든 물체의 기준 루트를 정의한다.
    physics = UsdPhysics.Scene.Define(stage, "/World/Physics")  # 중력을 설정할 물리 장면을 만든다.
    physics.CreateGravityDirectionAttr(Gf.Vec3f(0.0, 0.0, -1.0))  # 중력이 -z 방향으로 작용한다.
    physics.CreateGravityMagnitudeAttr(gravity)  # 중력 가속도 크기를 지정한다.
    make_box(stage, "/World/Floor", (0, 0, -0.1), (8, 8, 0.2), (0.4, 0.4, 0.4))  # 윗면 z=0인 고정 바닥이다.
    UsdLux.DomeLight.Define(stage, "/World/Light").CreateIntensityAttr(1000.0)  # 장면을 비출 환경광이다.
    return stage  # 예제가 물체와 카메라를 추가할 수 있게 반환한다.


def point_camera(stage, path, eye, target):  # eye에서 target을 바라보는 USD 카메라 자세를 계산한다.
    transform = Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye), Gf.Vec3d(*target), Gf.Vec3d(0, 0, 1)).GetInverse()  # 뷰 행렬의 역행렬은 카메라의 세계 변환이다.
    camera = UsdGeom.Xformable(stage.GetPrimAtPath(path))  # 기존 카메라의 변환 인터페이스를 얻는다.
    camera.ClearXformOpOrder()  # 이전 변환이 중복 적용되지 않게 순서를 비운다.
    camera.AddTransformOp().Set(transform)  # USD 카메라의 로컬 -z축이 target을 향하도록 적용한다.

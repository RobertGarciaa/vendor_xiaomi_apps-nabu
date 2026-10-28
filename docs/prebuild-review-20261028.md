# 앱 의존성·권한 수정 및 반영 — 2026-10-28

대상은 현재 PixelOS의 vendor/xiaomi/apps-nabu다. ROM 빌드와 out 산출물 검사는
사용자가 수행하는 user 빌드 이후로 미룬다.

## 수정

- Notes product privapp allowlist에 SCHEDULE_EXACT_ALARM을 추가했다. 현재 플랫폼은
  signature|privileged 권한 목록을 강제하므로 플랫폼 서명만으로 누락을 무시할 수 없다.
  maxSdkVersion=28인 과거 전화/계정 권한은 현재 활성 권한에서 제외해 검사한다.
- Notes/Creation에서 실제 공급하지 않는 필수 micloud-sdk uses-library를 제거했다.
  지원하는 API는 기존 앱 로컬 shim이 처리하며 클라우드 서비스는 제공하지 않는다.
- Android 패키지 아래의 MIUI 전용 API용 호환 클래스를 추가했다:
  MiuiConfiguration, MiuiSettings.System, MiuiDisplayMetrics, MiuiMultiWindowUtils,
  MiuiCompositionSamplingListener. AOSP 설정·화면 밀도·지원하지 않는 MIUI 서비스의
  부재를 반영한다. MIUI 네이티브 화면 샘플러를 이식한 것은 아니며 콜백을 위조하지 않는다.
  GraphicBuffer 선언은 컴파일 전용이고 APK에는 포함하지 않는다.
- Pad 5 OS1.0.6.0의 device_features/nabu.xml을 새 원본 pin으로 추가해 두 APK의
  assets/nabu_features.xml에 동봉했다. 앞선 FeatureParser는 이 자산이 없어서 실패했다.
  nabu/ staging prefix는 --nabu-dump를 사용한다. 기존 shuntian 입력도 계속 검증한다.
- 추출 시 기존 proprietary 트리를 지우지 않고 검증된 입력만 파일별로 원자 교체한다.
  생성 APK와 무관한 파일을 보존한다.
- Notes도 shim 입력을 필수로 받는다. coverage 검사는 클래스·전체 메서드/필드 descriptor,
  상속 및 android.* 아래 MIUI API를 구분한다. 생성자는 상속으로 충족하지 않는다.
  원본에서 제거된 build-retained annotation은 실행 클래스 의존성으로 취급하지 않는다.
- 생성 기록을 checkout 상대경로 schema 2로 바꿔 저장소 이동 후에도 검증할 수 있게 했다.
  ROM에 포함된 SDK의 ZIP 정렬/서명 도구를 fallback으로 지원한다. source SDK의
  apksigner는 JAR 경로를 직접 사용한다.

## 검증과 생성물

세 APK를 재생성·플랫폼 서명하고 verify-apps.py로 APK 서명/정렬, 원본 assets/native 보존,
리소스 ID와 한국어 구성, manifest 차단, Notes 특권 권한 목록, shim/feature asset,
생성 기록 입력 해시를 검사했다. 원본 pin은 6개다.

새 Android 호환 클래스는 공개 SDK와 compile-only GraphicBuffer 선언으로 javac/D8
컴파일했다. 변경하지 않은 기존 shim은 앞선 소스 해시가 일치하는 DEX를 재사용해 통합했다.
현재 framework.jar를 이용해 전체 shim을 새로 컴파일한 결과로 주장하지 않는다.
Notes/Creation의 앱 smali와 통합 shim 사이 정확한 외부 MIUI descriptor 검사에 누락이 없다.
회귀 시험은 manifest/리소스/중복 클래스/정확한 shim descriptor 등 10개다.

원본·파생 APK와 .build.json은 기존 방침대로 Git에서 제외한다. 실제 체크아웃의 ignored
proprietary/ported에 검증된 파생 APK와 기록을 반영한다. 다른 체크아웃에서는 README의
원본 추출/빌드 절차가 필요하다.

## 남은 확인


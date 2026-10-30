# OPlus Documents — nabu / Android 17

## 원본과 재현

- 공여 덤프: `1a4fab824a49403ba6754efdf8585196`, OPD2514, Android 17 / SDK 37.
- 입력: `my_stock/del-app/OplusDocumentsReader/OplusDocumentsReader.apk`.
- 패키지: `andes.oplus.documentsreader`, 17.1.32 / 17001032, minSdk 35 / targetSdk 37.
- SHA256: `60c014d6b5526664302400b0a4e6add870623e71b8d41f5db1e3c906a393bb6b`.
- 원본과 생성 APK/JNI는 `proprietary/`에만 두고 커밋하지 않는다.
- import → build → verify 명령은 README 참고. 원본 불일치 시 가져오기를 거부한다.
- `.build.json`은 원본·패치·호환 Java·빌드 도구·DEX·완성 APK 해시를 기록한다.

## 호환 변경

원본 매니페스트·리소스·assets·네이티브 바이트는 보존한다.
원본 8 DEX 중 classes.dex/classes6.dex에만 명시적 패치를 적용하며,
classes9.dex에 앱 로컬 호환 타입 5개를 추가한다.

1. `SlitsScreenHelper.onCreate`: PixelOS에 없는
   `com.itgsa.opensdk.wm.MultiWindowTrigger` 생성 대신 원본의 OEM 기능 미지원
   콜백을 사용한다. 편집기 시작 시 발생한 NoClassDefFoundError를 해결한다.
   Android 자체 분할 화면 기능을 전역 비활성화하는 변경은 아니다.
2. `emo.simpletext.control.u`: BaseInputConnection 조합·확정 처리 중 TextWatcher가
   Editable을 재초기화하던 재진입을 깊이 카운터로 막는다.
   한글 첫 글자가 `ㅅㅏ`처럼 분리되던 현상을 수정한다.
   예외 경로에서도 카운터를 복구하며 입력 문자열을 기록하거나 강제 정규화하지 않는다.
3. `OplusBuild`/`VERSION`: 지원하지 않는 OEM API 버전은 0.
   `OplusFeatureConfigManager`: 실제 ro.build.characteristics의 tablet만 매핑.
   `OplusSystemProperties`: 실제 AOSP 속성과 호출자 기본값을 사용한다.
   `OplusUsbEnvironment`: 실제 공유 저장소·마운트된 USB 볼륨을 조회한다.
   nabu에는 SD 슬롯이 없으므로 별도 SD 경로는 null이다.

기기 브랜드 변경, 프레임워크/Settings 수정, 전역 OEM 프레임워크 설치는 없다.

## 설치·권한·부팅 영향

- `product/app/OplusDocuments`, 플랫폼 서명, arm64 전용, dexpreopt 비활성.
- JNI 14개는 LOCAL_PREBUILT_JNI_LIBS로 앱 전용 설치한다. PRODUCT_COPY_FILES에
  ELF를 복사하거나 /system/lib64·/vendor/lib64에 전역으로 넣지 않는다.
- APK native는 AArch64 ELF이며 직접 DT_NEEDED는 APK 내부 또는 Android 표준 라이브러리다.
  선택적 dlopen의 liblcmm·libwgram 등은 전체 기능 검증 전이다.
- 매니페스트에 sharedUserId·persistent가 없고 priv-app으로 설치하지 않는다.
  privapp-permissions 허용 목록이나 새 sepolicy·VINTF·init 서비스는 추가하지 않는다.
- 파일 접근은 사용자가 모든 파일 액세스를 허용하는 기존 UI 흐름을 유지한다.
  승인 없이 권한을 강제 부여하지 않는다.
- 원본 OEM 권한 요청과 서비스 선언은 유지한다. OEM 계정·AI·클라우드·비공개 저장소
  연동이 제공된다는 뜻은 아니며, 해당 기능을 사용할 경우 별도 검증이 필요하다.
- 두 uses-library(androidx.window.extensions/sidecar)는 required=false다.
- 서명기가 ZIP 정렬을 바꾸지 않도록 --alignment-preserved true를 사용하고,
  최종 서명 APK의 16KB ZIP 정렬을 검사한다. 이는 모든 ELF의 16KB 페이지 호환성
  증명과는 다르다. nabu 실기기 실행과 최종 ROM ABI 검증을 구분한다.

## 확인 범위 — 2026-10-30

| 항목 | 결과 |
| --- | --- |
| 앱 시작·한국어 태블릿 홈 | 실기기 확인 |
| 모든 파일 액세스 | 사용자 직접 허용 |
| Word 저장 후 재열기 | 수정본에서 사용자 정상 확인 |
| 새 Word 한글 조합 | 수정본에서 사용자 정상 확인 |
| APK 서명·16KB ZIP 정렬·중복 클래스·원본 페이로드 | 검증 도구 통과 |
| 표·발표·PDF·글꼴 선택·OTG | 개별 실기기 미검증 |
| 한국어 전체 번역 | 미완료. 원본 한국어 리소스를 유지하며 일부 중국어 fallback 존재 |
| ROM 내장 부팅·최종 SELinux/VINTF/ABI/용량 | 다음 제품 빌드 결과와 실기기에서 확인 필요 |

앱 실행 성공을 전체 ROM 또는 미사용 기능 검증 완료로 해석하지 않는다.
기존 메모·Creation의 소스와 생성 도구는 변경하지 않는다.

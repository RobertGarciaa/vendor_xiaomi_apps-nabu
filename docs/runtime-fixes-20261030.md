# Creation 첫 실행 수정 — 2026-10-30

샤오미 보안센터의 SYSTEM_PERMISSION_DECLARE_NEW Activity 부재 경로를 로컬 동의
화면으로 연결했다. 사용자가 동의했을 때만 결과 코드 1을 반환한다. 명시적 light theme로
글자 대비를 유지하고 Android 권한을 자동 부여하지 않는다.

클라우드 설정 객체는 lifecycle 참조를 위해 유지하되 pref_micloud를 setVisible(false)로 숨긴다.
사용자는 홈 진입·그림 생성·저장·호환펜 입력·클라우드 항목 제거를 확인했다.

Creation은 Android.mk APPS prebuilt와 LOCAL_PREBUILT_JNI_LIBS로 원본 JNI 15개를
앱 전용 lib/arm64에 설치한다. APK 준비 후 tools/prepare-native.py를 실행한다.
ELF를 PRODUCT_COPY_FILES로 복사하지 않으며 전역 product/lib64에도 중복 배치하지 않는다.
데이터 유지 업데이트의 JNI 추출 확인과 최종 ROM 이미지의 JNI 설치 검증은 구분한다.

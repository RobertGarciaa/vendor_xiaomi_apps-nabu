# Pad 5 (nabu) stock apps for PixelOS Android 17

샤오미 패드5용 메모, Xiaomi Creation과 OPlus 문서 편집기를 이식합니다.
메모·Creation 원본은 shuntian HyperOS 4 / Android 17 덤프의 고정된 입력입니다.
문서 편집기는 별도의 OnePlus Pad 4 제공 덤프에서 추출합니다.

| 앱 | 패키지 | 버전 | 설치 위치 |
| --- | --- | --- | --- |
| 메모 | `com.miui.notes` | 3.2.7.4 | `product/priv-app/MIUINotes` |
| Xiaomi Creation | `com.miui.creation` | 4.1.6 | `product/app/Creation` |
| OPlus 문서 | `andes.oplus.documentsreader` | 17.1.32 | `product/app/OplusDocuments` |

MIUI 의존성은 앱 로컬 shim으로 제공합니다. 태블릿 여부는 시스템 속성에서 읽고,
클라우드·계정 서비스는 제공하지 않습니다. 원본 native/asset을 유지하며 한국어
리소스와 필요한 매니페스트·호환 코드를 앱 안에 포함합니다.

## 준비와 검증

```sh
python3 tools/extract-sources.py --dump /path/to/shuntian-dump --nabu-dump /path/to/nabu-dump
python3 tools/build-shims.py --rom-root /path/to/pixelos --app-smali /path/to/notes-smali --keep /path/to/shim-build
python3 tools/build-notes.py --rom-root /path/to/pixelos --shim-smali /path/to/shim-build/smali
python3 tools/build-creation.py --rom-root /path/to/pixelos --shim-smali /path/to/shim-build/smali
python3 tools/prepare-native.py
python3 tools/verify-apps.py --rom-root /path/to/pixelos
```

원본·생성 APK·앱 전용 JNI는 `proprietary/` 안에 두며 Git에서 제외합니다.
Creation의 앱 전용 JNI는 native 준비 도구로 생성합니다. 최종 이미지 용량과 실행은
제품 빌드 및 실기기로 확인합니다.

세부 기록:

| 문서 | 내용 |
| --- | --- |
| `docs/dependencies.md` | 앱별 외부 의존성과 shim 범위 |
| `docs/korean.md` | 한국어 리소스와 번역 검사 |
| `docs/prebuild-review-20261028.md` | 프리빌트 검토 기록 |
| `docs/codex-review-20261027.md` | 초기 코드 검토 |
| `docs/runtime-fixes-20261030.md` | Creation 첫 실행 수정 |
| `docs/uses-library-20261031.md` | APK uses-library 선언과 검사 |

## OPlus 문서 편집기

```sh
python3 tools/import-oplus-docs.py --dump /path/to/oneplus-pad4-dump
python3 tools/build-oplus-docs.py --rom-root /path/to/pixelos
python3 tools/verify-oplus-docs.py --rom-root /path/to/pixelos
```

별도의 원본 APK는 `oplus-docs/source.json`의 SHA256으로 확인합니다.
빌드 시 앱 전용 JNI 14개와 `.build.json`도 생성합니다.
`apps.mk`를 상속하면 기본 포함됩니다. 제외하려면 상속 전에
`TARGET_ENABLE_OPLUS_DOCS := false`를 지정하세요.
`TARGET_ENABLE_XIAOMI_APPS := false`는 문서 앱도 함께 제외합니다.

Word 저장·재열기 및 한글 조합은 사용자 실기기에서 확인했습니다.
표·발표·PDF 및 OEM 부가 기능은 검증 전이며 한국어 번역도 일부 누락돼 있습니다.
ROM 내장 후 최종 권한·SELinux·파티션 검증은 별도로 필요합니다.
패치·의존성과 검증 범위는 [문서 편집기 포팅 기록](docs/oplus-documents-port.md)을 참고하세요.

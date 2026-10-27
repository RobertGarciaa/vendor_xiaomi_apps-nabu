# Pad 5 (nabu) stock apps for PixelOS Android 17

샤오미 패드5용 메모와 Xiaomi Creation을 이식합니다.
원본은 shuntian HyperOS 4 / Android 17 덤프의 고정된 입력입니다.

| 앱 | 패키지 | 버전 | 설치 위치 |
| --- | --- | --- | --- |
| 메모 | `com.miui.notes` | 3.2.7.4 | `product/priv-app/MIUINotes` |
| Xiaomi Creation | `com.miui.creation` | 4.1.6 | `product/app/Creation` |

MIUI 의존성은 앱 로컬 shim으로 제공합니다. 태블릿 여부는 시스템 속성에서 읽고,
클라우드·계정 서비스는 제공하지 않습니다. 원본 native/asset을 유지하며 한국어
리소스와 필요한 매니페스트·호환 코드를 앱 안에 포함합니다.

## 준비와 검증

```sh
python3 tools/extract-sources.py --dump /path/to/shuntian-dump --nabu-dump /path/to/nabu-dump
python3 tools/build-shims.py --rom-root /path/to/pixelos --app-smali /path/to/notes-smali --keep /path/to/shim-build
python3 tools/build-notes.py --rom-root /path/to/pixelos --shim-smali /path/to/shim-build/smali
python3 tools/build-creation.py --rom-root /path/to/pixelos --shim-smali /path/to/shim-build/smali
python3 tools/verify-apps.py --rom-root /path/to/pixelos
```

원본·생성 APK·앱 전용 JNI는 `proprietary/` 안에 두며 Git에서 제외합니다.
Creation의 앱 전용 JNI는 native 준비 도구로 생성합니다. 최종 이미지 용량과 실행은
제품 빌드 및 실기기로 확인합니다. 세부 의존성과 번역은 `docs/`를 참고하세요.

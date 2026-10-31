# APK uses-library 선언 — 2026-10-31

## 문제

빌드가 `Creation`의 사용 라이브러리 검사에서 멈췄다.

```
error: mismatch or misordering in the <uses-library> tags between the build
system and the manifest:
    - optional libraries in build system: []
                 vs. in the manifest: [org.apache.http.legacy,
                    androidx.window.extensions, androidx.window.sidecar]
```

Android 17은 APK 매니페스트의 `<uses-library>`와 빌드 시스템의 선언이 일치하는지
검사하고, 다르면 빌드를 중단한다. 스톡 APK는 세 라이브러리를 `required=false`로
선언하는데, 이 트리의 모듈 정의에는 목록이 비어 있었다.

## 범위

이 검사는 `dex_preopt`가 켜진 APK에만 적용된다고 보고 넘길 뻔했지만, 실제 규칙이
생성되는지 확인하니 세 앱이 모두 걸려 있었다.

| 앱 | 경로 | 검사 규칙 |
|---|---|---|
| Creation | `Android.mk` (BUILD_PREBUILT) | `obj/APPS/Creation_intermediates/enforce_uses_libraries.status` |
| MIUINotes | `Android.bp` (`android_app_import`) | `m.114-MIUINotes_android_common.verify_uses_libraries` |
| MiSound | `dolby-nabu/Android.bp` | `m.115-MiSound_android_common.verify_uses_libraries` |

빌드는 `Creation`에서 먼저 멈췄을 뿐, `MIUINotes`와 `MiSound`도 같은 오류로
실패한다. 각 앱의 실제 빌드 명령을 그대로 실행해 확인했다.

```
=== MIUINotes  FAIL  [org.apache.http.legacy, com.miui.system, ...]
=== MiSound    FAIL  [com.miui.core, androidx.window.extensions, androidx.window.sidecar]
```

## 해결

두 경로의 처리 방식이 다르다.

### Make 경로 (Creation)

`LOCAL_OPTIONAL_USES_LIBRARIES`에 매니페스트와 같은 순서로 적는다. 이 변수는
`PRODUCT_PACKAGES`로 필터링되므로, 이 ROM에 모듈이 없는 이름을 적어도 검사 인자로
넘어가지 않는다.

### Soong 경로 (MIUINotes, MiSound)

`android_app_import`의 `optional_uses_libs`에 매니페스트 전체를 순서대로 적는다.
Soong은 `OtherModuleExists`로 걸러 존재하는 것만 CLC에 넣고, 나머지는
`missing_optional_uses_libs`로 검사기에 넘긴다. 따라서 `com.miui.system`이나
`com.miui.core`처럼 이 ROM에 없는 라이브러리도 매니페스트 그대로 선언하면 된다.

`enforce_uses_libs: false`로 검사를 끄는 방법도 있지만, 그러면 나중에 매니페스트가
바뀌어도 알 수 없으므로 쓰지 않았다.

## 재발 방지

`tools/verify-apps.py`가 각 APK의 `uses-library-not-required` 목록과 `Android.bp`의
`optional_uses_libs`를 비교한다. 선언에서 한 항목만 빼도 잡아낸다.

```
MIUINotes: optional_uses_libs ['com.miui.system', ...] does not match the
manifest [...]; Soong rejects this in verify_uses_libraries
```

## 검증

- 세 앱의 실제 `manifest_check` 명령을 재구성해 실행 → 모두 exit 0
- `python3 tools/verify-apps.py --rom-root ...` → PASS
- `bpfmt -d` → 두 저장소 모두 OK

전체 ROM 빌드는 사용자가 다시 수행한다.

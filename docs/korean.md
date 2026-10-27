# 한국어 번역

이 포팅은 사용자에게 보이는 모든 메뉴·안내·설명을 한국어로 제공하는 것을
목표로 한다. 다만 음력·천간·지지처럼 **데이터 자체가 중국 문화권 표기**인
항목은 원본을 유지한다.

## 범위

| 앱 | 기본 문자열 | 기존 한국어 | 추가 번역 | 비고 |
| --- | --- | --- | --- | --- |
| 메모 | 2,852 | 2,297 | **118** | 나머지는 음력/간지/규제 문구 |
| Creation | 927 | 671 | **5** | 중국 규제 신고 문구 |




## 원본 유지 항목

다음 접두사로 시작하는 키는 번역 대상에서 제외하고 원본 값을 유지한다.

| 접두사 | 내용 |
| --- | --- |
| `chinese_day_` | 음력 일자 (초하루, 초이틀 …) |
| `chinese_digit_` | 한자 숫자 |
| `chinese_leap_` | 윤달 |
| `chinese_month` | 음력 월 이름 |
| `chinese_symbol_animals_` | 십이지 동물 |
| `heavenly_stems_` | 천간 (갑·을·병 …) |
| `earthly_branches_` | 지지 (자·축·인 …) |
| `lunar_chinese_` | 음력 명절 |
| `solar_chinese_` | 양력 명절 |
| `calendar_date_picker` | 달력 위젯 라벨 |
| `fmt_chinese_date` | 중국식 날짜 서식 |

규제 신고 문구 5개(`setting_algorithm_filing_*`, `setting_algorithm_name_text`,
`setting_filing_text`)는 라벨만 한국어로 옮기고 **신고번호는 원본 그대로**
둔다. 번호는 실제 등록번호라 바꾸면 표시가 틀린 정보가 된다.

## 형식 인자

`%1$s`, `%d`, `%%` 같은 형식 인자는 원문과 개수·순서가 정확히 일치해야 한다.
`tools/check-translations.py`가 이를 강제한다. 실제로 다음 항목들이 이 검사에서
걸려 수정되었다.

| 키 | 문제 | 수정 |
| --- | --- | --- |
| `import_uploading` | `%1$s` 누락 | `%1$s 업로드 중` |
| `llm_image_describe_multi` | `%d` 누락 | `이 %d장의 이미지 내용을 설명해 주세요` |
| `note_source_label` | `%1$s`, `%2$s` 누락 | `%1$s · 출처 %2$s` |
| `sync_all_done` | `%1$d`, `%2$d` 누락 | `노트 %1$d개, 할 일 %2$d개 동기화 완료` |
| `sync_notes_and_todos_unsync` | `%1$d`, `%2$d` 누락 | `노트 %1$d개, 할 일 %2$d개가 아직 동기화되지 않았습니다` |
| `repeat_mode_set_item_month_detail_day` | 원문에 인자 없음 | `일` (코드가 숫자를 붙임) |

## 표 형식

`translations/*.tsv`는 `<키><TAB><값>` 한 줄 형식이다.
값 안에 실제 개행을 넣을 수 없으므로 `\n`, `\t`, `\\` 이스케이프를 쓴다.
자세한 규칙은 [FORMAT.md](../translations/FORMAT.md)에 있다.

## 검증

```sh
# 앱별 번역 표 검사
python3 tools/check-translations.py \
    --strings /path/to/decoded/MIUINotes/res/values/strings.xml \
    --tsv translations/notes-ko.tsv \
    --complete-from /path/to/required-keys.txt

# 빌드 결과 종합 검사 (중국어 잔존 포함)
python3 tools/verify-apps.py --rom-root /path/to/pixelos
```

`verify-apps.py`는 번역 표와 빌드된 APK를 함께 검사해
중국어가 남은 키가 있으면 실패한다. 허용 목록은 규제 신고 문구 5개뿐이다.

## 한계


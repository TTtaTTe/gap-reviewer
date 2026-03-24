#!/usr/bin/env python3
"""
검토보고서 DOCX 생성기 (v2)
JSON 데이터를 받아 전문 스타일의 Word 문서를 생성합니다.

사용법:
    python generate_docx.py <input_json_path> <output_docx_path>
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# shared 모듈 import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "shared"))
from docx_styles import (
    create_document, add_cover_page, add_toc, add_heading, add_paragraph,
    add_checklist_item, create_table, add_header_footer, set_run_font,
    COLOR_NAVY, COLOR_CHARCOAL, COLOR_BODY, COLOR_GRAY
)


def generate_docx(data, output_path):
    """검토보고서 DOCX 생성"""
    doc = create_document()

    report = data.get("report", {})
    items = data.get("items", [])
    phase1_history = data.get("phase1_history", [])

    inst_file = report.get("instruction_file", "-")
    deliv_file = report.get("deliverable_file", "-")

    # ── 표지 ──
    add_cover_page(
        doc,
        title="지시서-작업물 대조 검토 보고서",
        subtitle=f"{inst_file} vs {deliv_file}",
        date_str=datetime.now().strftime("%Y년 %m월 %d일"),
        author="Deliverable Gap Reviewer",
        classification="내부용",
        version="v1.0"
    )

    # ── 목차 ──
    add_toc(doc)

    # ── 머리글/꼬리글 ──
    add_header_footer(doc, header_text="지시서-작업물 대조 검토 보고서")

    # ── 1. 개요 ──
    add_heading(doc, "1. 개요", level=1)

    overview_rows = [
        ["지시서 파일", inst_file],
        ["작업물 파일", deliv_file],
        ["Phase 1 분석 신뢰도", f"{report.get('phase1_score', '-')} / 10.0"],
        ["Phase 2 종합 점수", f"{report.get('phase2_overall_score', '-')} / 10.0"],
    ]
    create_table(doc, ["항목", "내용"], overview_rows, col_widths=[5, 11])

    add_heading(doc, "요약", level=3)
    summary_rows = [
        ["충족 (10.0)", str(report.get("fulfilled_count", 0))],
        ["대부분충족 (7.0~9.9)", str(report.get("partial_high_count", 0))],
        ["부분충족 (4.0~6.9)", str(report.get("partial_count", 0))],
        ["미흡 (1.0~3.9)", str(report.get("insufficient_count", 0))],
        ["누락 (0.0)", str(report.get("missing_count", 0))],
    ]
    create_table(doc, ["상태", "항목 수"], summary_rows, col_widths=[6, 4])

    # ── 2. 항목별 대조 결과 ──
    add_heading(doc, "2. 항목별 대조 결과", level=1)

    detail_headers = ["#", "분류", "요구항목", "R1", "R2", "최종", "상태", "태그"]
    detail_rows = []
    for item in items:
        tag = item.get("tag") or "-"
        status_map = {
            "fulfilled": "충족", "mostly_fulfilled": "대부분충족",
            "partial": "부분충족", "insufficient": "미흡", "missing": "누락"
        }
        status = status_map.get(item.get("status", ""), item.get("status", ""))
        tag_map = {"common": "공통", "reference": "참고"}
        tag_display = tag_map.get(tag, tag) if tag != "-" else "-"

        detail_rows.append([
            str(item.get("id", "")),
            item.get("category", ""),
            item.get("requirement", ""),
            str(item.get("score_r1", "")),
            str(item.get("score_r2", "")),
            str(item.get("final_score", "")),
            status,
            tag_display,
        ])

    if detail_rows:
        create_table(
            doc, detail_headers, detail_rows,
            col_widths=[0.8, 2.5, 4, 1.2, 1.2, 1.2, 2, 1.2]
        )

    # ── 3. 보완 필요 체크리스트 ──
    add_heading(doc, "3. 보완 필요 체크리스트", level=1)

    score_groups = [
        ("3-1. 누락 항목 (0.0점)", lambda x: x.get("final_score", 0) == 0.0),
        ("3-2. 미흡 항목 (1.0~3.9점)", lambda x: 1.0 <= x.get("final_score", 0) <= 3.9),
        ("3-3. 부분충족 항목 (4.0~6.9점)", lambda x: 4.0 <= x.get("final_score", 0) <= 6.9),
        ("3-4. 대부분충족 항목 (7.0~9.9점)", lambda x: 7.0 <= x.get("final_score", 0) <= 9.9),
    ]

    for group_title, filter_fn in score_groups:
        group_items = [item for item in items if filter_fn(item)]
        if not group_items:
            continue

        add_heading(doc, group_title, level=2)

        for item in group_items:
            tag = item.get("tag")
            tag_map = {"common": "공통", "reference": "참고"}
            tag_display = tag_map.get(tag) if tag else None

            add_checklist_item(
                doc,
                title=item.get("requirement", ""),
                score=item.get("final_score", 0),
                tag=tag_display,
                current_state=item.get("current_state"),
                suggestion_direction=item.get("suggestion_direction"),
                suggestion_example=item.get("suggestion_example"),
            )

    # ── 4. 충족 항목 ──
    fulfilled_items = [item for item in items if item.get("final_score", 0) >= 10.0]
    if fulfilled_items:
        add_heading(doc, "4. 충족 항목", level=1)
        fulfilled_rows = [
            [str(item.get("id", "")), item.get("category", ""),
             item.get("requirement", ""), str(item.get("final_score", ""))]
            for item in fulfilled_items
        ]
        create_table(
            doc, ["#", "분류", "요구항목", "최종점수"], fulfilled_rows,
            col_widths=[1, 3, 8, 2]
        )

    # ── 5. Phase 1 분석 이력 ──
    add_heading(doc, "5. Phase 1 분석 이력", level=1)
    if phase1_history:
        history_rows = [
            [h.get("round", ""), str(h.get("score", "-"))]
            for h in phase1_history
        ]
        create_table(doc, ["단계", "점수"], history_rows, col_widths=[6, 4])

    doc.save(output_path)
    print(f"DOCX 생성 완료: {output_path}")


def main():
    if len(sys.argv) != 3:
        print("사용법: python generate_docx.py <input_json> <output_docx>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)

    generate_docx(data, sys.argv[2])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
수정본/수정이력 DOCX 생성기 (v2)
gap-fix의 수정 결과를 전문 스타일의 Word 문서로 생성합니다.

사용법:
    # 수정이력 보고서 생성
    python generate_fix_docx.py report <modification_json> <output_docx>

    # 수정본 문서 생성
    python generate_fix_docx.py content <content_md> <output_docx> [cover_json]
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# shared 모듈 import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "shared"))
from docx_styles import (
    create_document, add_cover_page, add_toc, add_heading, add_paragraph,
    create_table, add_header_footer, md_to_docx, set_run_font,
    COLOR_NAVY, COLOR_CHARCOAL, COLOR_BODY, COLOR_GRAY, COLOR_RED, COLOR_GREEN
)


def generate_modification_report(data, output_path):
    """수정이력 보고서 DOCX"""
    doc = create_document()
    log = data.get("modification_log", {})
    modifications = log.get("modifications", [])
    remaining = log.get("remaining_items", [])

    # 표지
    add_cover_page(
        doc,
        title="수정 이력 보고서",
        subtitle=f"원본: {log.get('original_file', '-')}",
        date_str=datetime.now().strftime("%Y년 %m월 %d일"),
        author="Deliverable Gap Fixer",
    )

    # 목차
    add_toc(doc)

    # 머리글/꼬리글
    add_header_footer(doc, header_text="수정 이력 보고서")

    # 1. 개요
    add_heading(doc, "1. 개요", level=1)
    overview_rows = [
        ["검토보고서", log.get("source_json", "-")],
        ["원본 작업물", log.get("original_file", "-")],
        ["수정본 파일", log.get("output_file", "-")],
        ["전체 보완 필요", f"{log.get('total_gaps', 0)}개"],
        ["수정 완료", f"{log.get('fixed_count', 0)}개"],
        ["잔여 항목", f"{log.get('remaining_count', 0)}개"],
    ]
    create_table(doc, ["항목", "내용"], overview_rows, col_widths=[5, 11])

    # 2. 수정 항목 상세
    add_heading(doc, "2. 수정 항목 상세", level=1)
    if modifications:
        for mod in modifications:
            add_heading(
                doc,
                f"#{mod.get('item_id', '')} {mod.get('requirement', '')}",
                level=2
            )

            p = doc.add_paragraph()
            run = p.add_run(f"기존 점수: {mod.get('before_score', 0)}점")
            set_run_font(run, size=10, color=COLOR_RED)

            p = doc.add_paragraph()
            run = p.add_run("수정 내용: ")
            set_run_font(run, size=10, bold=True, color=COLOR_NAVY)
            run = p.add_run(f"{mod.get('action', '')} — {mod.get('description', '')}")
            set_run_font(run, size=10, color=COLOR_BODY)

            if mod.get("cover_source"):
                p = doc.add_paragraph()
                run = p.add_run("출처: ")
                set_run_font(run, size=10, bold=True, color=COLOR_GRAY)
                run = p.add_run(mod["cover_source"])
                set_run_font(run, size=10, color=COLOR_BODY)
    else:
        add_paragraph(doc, "수정된 항목이 없습니다.")

    # 3. 미수정 잔여 항목
    add_heading(doc, "3. 미수정 잔여 항목", level=1)
    if remaining:
        remaining_rows = [
            [
                str(item.get("item_id", "")),
                item.get("requirement", ""),
                str(item.get("final_score", "")),
                item.get("reason", ""),
            ]
            for item in remaining
        ]
        create_table(
            doc, ["#", "요구항목", "점수", "미수정 사유"],
            remaining_rows, col_widths=[1, 5, 1.5, 8]
        )
    else:
        add_paragraph(doc, "모든 보완 필요 항목이 수정되었습니다.")

    # 4. 커버리지 비교
    add_heading(doc, "4. 커버리지 비교", level=1)
    total = log.get("total_gaps", 0)
    fixed = log.get("fixed_count", 0)
    remain = log.get("remaining_count", 0)
    rate = round(fixed / total * 100, 1) if total > 0 else 0

    compare_rows = [
        ["보완 필요 항목", f"{total}개", f"{remain}개"],
        ["커버율", "0%", f"{rate}%"],
    ]
    create_table(doc, ["구분", "수정 전", "수정 후"], compare_rows, col_widths=[5, 5, 5])

    doc.save(output_path)
    print(f"수정이력 DOCX 생성 완료: {output_path}")


def generate_fixed_document(content_md, output_path, cover_data=None):
    """수정본 DOCX (마크다운 → 전문 DOCX)"""
    doc = create_document()

    # 표지 (cover_data가 있으면 사용)
    if cover_data:
        add_cover_page(
            doc,
            title=cover_data.get("title", "수정본"),
            subtitle=cover_data.get("subtitle", "보완 반영"),
            date_str=cover_data.get("date", datetime.now().strftime("%Y년 %m월 %d일")),
            author=cover_data.get("author", ""),
            classification=cover_data.get("classification", ""),
            version=cover_data.get("version", ""),
        )
    else:
        add_cover_page(
            doc,
            title="작업물 수정본",
            subtitle="보완 자료 반영",
            date_str=datetime.now().strftime("%Y년 %m월 %d일"),
            author="Deliverable Gap Fixer",
        )

    # 목차
    add_toc(doc)

    # 머리글/꼬리글
    header_text = cover_data.get("title", "수정본") if cover_data else "수정본"
    add_header_footer(doc, header_text=header_text)

    # 본문 (MD → DOCX 변환)
    md_to_docx(doc, content_md)

    doc.save(output_path)
    print(f"수정본 DOCX 생성 완료: {output_path}")


def main():
    if len(sys.argv) < 4:
        print("사용법:")
        print("  수정이력: python generate_fix_docx.py report <json> <output_docx>")
        print("  수정본:   python generate_fix_docx.py content <md> <output_docx> [cover_json]")
        sys.exit(1)

    mode = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]

    if mode == "report":
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        generate_modification_report(data, output_path)

    elif mode == "content":
        with open(input_path, "r", encoding="utf-8") as f:
            content_md = f.read()

        cover_data = None
        if len(sys.argv) >= 5 and sys.argv[4] != "none":
            with open(sys.argv[4], "r", encoding="utf-8") as f:
                cover_data = json.load(f)

        generate_fixed_document(content_md, output_path, cover_data)

    else:
        print(f"알 수 없는 모드: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()

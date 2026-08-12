import sys
from hybrid_llm_generator import LLMDraftGenerator, RuleRepairEngine
from luc_bat_rules import check_luc_bat_poem_rules

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def main():
    print_header("PHƯƠNG ÁN 2: HỆ THỐNG HYBRID LLM + RULE REPAIR ENGINE (NEURO-SYMBOLIC)")

    draft_gen = LLMDraftGenerator()
    repair_engine = RuleRepairEngine()

    prompts = ["nắng", "trời", "truyện"]

    for idx, prompt in enumerate(prompts, 1):
        print(f"\n" + "-" * 80)
        print(f"=== DEMO THỬ NGHIỆM {idx}: CHỦ ĐỀ GỢI Ý = '{prompt.upper()}' ===")
        print("-" * 80)

        # Step 1: LLM Generative Stage
        raw_draft = draft_gen.generate_draft(prompt)
        print("\n[TẦNG 1: LLM GENERATIVE DRAFT (Bản Thảo Thô Từ LLM - Có Lỗi Thừa/Thiếu Từ & Lệch Vần)]:")
        for line_i, line in enumerate(raw_draft):
            indent = "      " if line_i % 2 == 1 else "   "
            print(f"{indent}{' '.join(line).capitalize()} ({len(line)} từ)")

        raw_eval = check_luc_bat_poem_rules(raw_draft)
        print(f"   ==> Đánh Giá Bản Thảo RAW: {'✓ Đúng Luật' if raw_eval['valid'] else '✗ Lỗi Luật Thơ'}")
        if not raw_eval['valid']:
            for err in raw_eval['errors']:
                print(f"      - {err}")

        # Step 2: Symbolic Rule Repair Stage
        repaired_poem = repair_engine.repair_poem(raw_draft)
        print("\n[TẦNG 2: RULE REPAIR ENGINE (Bài Thơ Đã Được Sửa Lỗi Tự Động 100% Đúng Luật)]:")
        for line_i, line in enumerate(repaired_poem):
            indent = "      " if line_i % 2 == 1 else "   "
            print(f"{indent}{' '.join(line).capitalize()} ({len(line)} từ)")

        final_eval = check_luc_bat_poem_rules(repaired_poem)
        print(f"   ==> Đánh Giá Sau Khi Sửa: {'✓ THỎA MÃN 100% QUY TẮC LỤC BÁT' if final_eval['valid'] else '✗ Có Lỗi'}")

    print_header("HOÀN THÀNH DEMO PHƯƠNG ÁN 2 (NEURO-SYMBOLIC HYBRID)")


if __name__ == "__main__":
    main()

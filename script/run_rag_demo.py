from __future__ import annotations

import sys
from pathlib import Path

# Add src directory to path if needed
src_path = Path(__file__).resolve().parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from core.config import load_settings
from core.utils import read_json


def main() -> None:
    settings = load_settings()
    
    demo_json_path = settings.paths.demo_answers
    b_metrics_path = settings.paths.baseline_metrics
    c_metrics_path = settings.paths.corrupted_metrics
    r_metrics_path = settings.paths.repaired_metrics
    rag_demo_md_path = settings.paths.comparison_report.with_name("rag_demo.md")

    missing = []
    for path, label in [
        (demo_json_path, "Demo answers JSON"),
        (b_metrics_path, "Baseline metrics JSON"),
        (c_metrics_path, "Corrupted metrics JSON"),
        (r_metrics_path, "Repaired metrics JSON"),
    ]:
        if not path.exists():
            missing.append(f"{label} ({path})")

    if missing:
        print("ERROR: Cannot run RAG demo because the following required artifacts are missing:")
        for m in missing:
            print(f"  - {m}")
        print("\nPlease run the pipelines first:")
        print("  1. uv run python script/run_phase1.py")
        print("  2. uv run python script/run_corruption_flow.py")
        sys.exit(1)

    demo_answers = read_json(demo_json_path)
    b_metrics = read_json(b_metrics_path)
    c_metrics = read_json(c_metrics_path)
    r_metrics = read_json(r_metrics_path)

    print("=======================================================================")
    print("                 RAG PIPELINE COMPARISON DEMO                          ")
    print("=======================================================================")
    print(f"Markdown Presentation Path: {rag_demo_md_path}\n")

    print("--- METRICS SUMMARY ---")
    print(f"Retrieval Hit Rate: Baseline={b_metrics.get('retrieval_hit_rate', 0):.4f} | Corrupted={c_metrics.get('retrieval_hit_rate', 0):.4f} | Repaired={r_metrics.get('retrieval_hit_rate', 0):.4f}")
    print(f"Mean Token F1:      Baseline={b_metrics.get('mean_token_f1', 0):.4f} | Corrupted={c_metrics.get('mean_token_f1', 0):.4f} | Repaired={r_metrics.get('mean_token_f1', 0):.4f}")
    print(f"Judge Accuracy:     Baseline={b_metrics.get('judge_accuracy', 0):.4f} | Corrupted={c_metrics.get('judge_accuracy', 0):.4f} | Repaired={r_metrics.get('judge_accuracy', 0):.4f}")
    print(f"Mean Judge Score:   Baseline={b_metrics.get('mean_judge_score', 0):.4f} | Corrupted={c_metrics.get('mean_judge_score', 0):.4f} | Repaired={r_metrics.get('mean_judge_score', 0):.4f}\n")

    print("--- SAMPLE QUESTION COMPARISONS ---")
    for sample in demo_answers:
        qid = sample.get("question_id", "N/A")
        q_text = sample.get("question", "")
        gt = sample.get("ground_truth", "")

        b = sample.get("baseline", {})
        c = sample.get("corrupted", {})
        r = sample.get("repaired", {})

        print(f"\nQuestion [{qid}]: {q_text}")
        print(f"  Ground Truth: {gt[:80]}..." if len(gt) > 80 else f"  Ground Truth: {gt}")
        print(f"  [Baseline]  Docs: {b.get('retrieved_doc_ids')} | Hit: {b.get('retrieval_hit')} | F1: {b.get('token_f1', 0):.4f}")
        print(f"              Ans:  {b.get('answer')}")
        print(f"  [Corrupted] Docs: {c.get('retrieved_doc_ids')} | Hit: {c.get('retrieval_hit')} | F1: {c.get('token_f1', 0):.4f}")
        print(f"              Ans:  {c.get('answer')}")
        print(f"  [Repaired]  Docs: {r.get('retrieved_doc_ids')} | Hit: {r.get('retrieval_hit')} | F1: {r.get('token_f1', 0):.4f}")
        print(f"              Ans:  {r.get('answer')}")

    print("\n=======================================================================")


if __name__ == "__main__":
    main()

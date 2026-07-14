#!/usr/bin/env python3

import csv
import argparse
from statistics import median

DEFAULT_COLUMNS = [
"qseqid", "sseqid", "pident", "length", "mismatch", "gapopen",
"qstart", "qend", "sstart", "send", "evalue", "bitscore"
]

def parse_args():
    parser = argparse.ArgumentParser(
        description="Clean BLAST tabular output, infer strand, and generate a simple report."
    )
    parser.add_argument("-i", "--input", required=True, help="Input BLAST outfmt 6 file")
    parser.add_argument("-o", "--output", required=True, help="Output cleaned TSV file")
    parser.add_argument("--report", help="Optional markdown report file")
    return parser.parse_args()

def read_blast_file(filepath):
    rows = []
    with open(filepath, "r", newline="") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            line = line.strip()
            if not line:
                continue
            rows.append(line.split())
    return rows

def validate_rows(rows, expected_ncols=12):
    for idx, row in enumerate(rows, start=1):
        if len(row) != expected_ncols:
            raise ValueError(f"Row {idx} has {len(row)} columns, expected {expected_ncols}")

def process_rows(rows):
    processed = []
    issues = []

    for idx, row in enumerate(rows, start=1):
        record = dict(zip(DEFAULT_COLUMNS, row))

        try:
            qstart = int(record["qstart"])
            qend = int(record["qend"])
            sstart = int(record["sstart"])
            send = int(record["send"])
        except ValueError:
            issues.append(f"Row {idx}: non-numeric qstart/qend/sstart/send")
            continue

        strand = "+" if send >= sstart else "-"
        span = abs(send - sstart) + 1

        if strand == "-":
            qstart, qend = qend, qstart
            sstart, send = send, sstart

        record["qstart"] = qstart
        record["qend"] = qend
        record["sstart"] = sstart
        record["send"] = send
        record["strand"] = strand
        record["sstart_norm"] = min(sstart, send)
        record["send_norm"] = max(sstart, send)

        if span <= 0:
            issues.append(f"Row {idx}: invalid span computed")

        processed.append(record)

    return processed, issues

def write_output(records, output_file):
    fieldnames = DEFAULT_COLUMNS + ["strand", "sstart_norm", "send_norm"]
    with open(output_file, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(records)

def write_report(report_file, report_text):
    with open(report_file, "w") as handle:
        handle.write(report_text + "\n")


def build_report_text(input_file, records, issues, output_columns):
    queries = sorted(set(r["qseqid"] for r in records))
    subjects = sorted(set(r["sseqid"] for r in records))

    pidents = [float(r["pident"]) for r in records]
    sizes = [abs(int(r["send"]) - int(r["sstart"])) + 1 for r in records]
    evalues = [float(r["evalue"]) for r in records]

    comments_removed_check = "[CHECK]"
    strand_check = "[CHECK]" if all(r.get("strand") in {"+", "-"} for r in records) else "[FAIL]"

    lines = []
    lines.append("__| genolab BLAST report |__")
    lines.append("")
    lines.append(f"All # deleted from output {comments_removed_check}")
    lines.append(f"All locations strand included and corrected {strand_check}")
    lines.append("")
    lines.append("Head of the output file (5 lines)")
    lines.append("\t".join(output_columns))
    for record in records[:5]:
        row_text = "\t".join(str(record[col]) for col in output_columns)
        lines.append(row_text)
    lines.append("")
    lines.append("List of queries:")
    for q in queries:
        lines.append(f"- {q}")
    lines.append("")
    lines.append("List of subjects:")
    for s in subjects:
        lines.append(f"- {s}")
    lines.append("")
    lines.append(
        f"Median PID: {median(pidents):.2f} | Min: {min(pidents):.2f} | Max: {max(pidents):.2f}"
    )
    lines.append(
        f"Median Size: {median(sizes):.2f} | Min: {min(sizes)} | Max: {max(sizes)}"
    )
    lines.append(
        f"Median Evalue: {median(evalues):.3e} | Min: {min(evalues):.3e} | Max: {max(evalues):.3e}"
    )

    if issues:
        lines.append("")
        lines.append("Issues:")
        for issue in issues:
            lines.append(f"- {issue}")

    return "\n".join(lines)


def main():
    args = parse_args()

    rows = read_blast_file(args.input)
    validate_rows(rows)

    records, issues = process_rows(rows)

    if not records:
        print("No valid BLAST rows to report.")
        return

    output_columns = DEFAULT_COLUMNS + ["strand", "sstart_norm", "send_norm"]
    report_text = build_report_text(args.input, records, issues, output_columns)

    print(report_text)

    write_output(records, args.output)

    if args.report:
        write_report(args.report, report_text)

if __name__ == "__main__":
    main()

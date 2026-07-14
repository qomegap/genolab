#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<EOF
Usage:
  genolab dicti -i INPUT.tsv -d DICT.tsv -o OUTPUT.tsv

Description:
  Rename values in the second column (assumed sseqid) of a TSV file
  using a 2-column mapping table.

Options:
  -i    Input file
  -d    Dict file (old_name<TAB>new_name)
  -o    Output file
EOF
}

input=""
dicti=""
output=""

while getopts "i:d:o:h" opt; do
    case "$opt" in
        i) input="$OPTARG" ;;
        d) dicti="$OPTARG" ;;
        o) output="$OPTARG" ;;
        h)
            usage
            exit 0
            ;;
        *)
            usage >&2
            exit 1
            ;;
    esac
done

if [[ -z "$input" || -z "$dicti" || -z "$output" ]]; then
    usage >&2
    exit 1
fi

awk '
BEGIN {
    FS = OFS = "\t"
    renamed = 0
    sseqid_col = 2
}
NR == FNR {
    if ($0 ~ /^#/ || $0 == "") next
    if (NF < 2) next
    if ($1 == "old_name" && $2 == "new_name") next
    map[$1] = $2
    next
}
FNR == 1 {
    # Skip header entirely in output, but do not treat it as data
    # Optionally, do header-based mapping here if you ever want it
    next
}
{
    if (($sseqid_col in map) && map[$sseqid_col] != "") {
        $sseqid_col = map[$sseqid_col]
        renamed++
    } else {
        unmatched[$sseqid_col] = 1
    }

    if ($sseqid_col != "") {
        new_names[$sseqid_col] = 1
    }

    print
}
END {
    n_unmatched = 0
    n_new = 0

    for (x in unmatched) n_unmatched++
    for (x in new_names) n_new++

    print "Assuming BLAST outfmt 6 (extended): sseqid in column 2" > "/dev/stderr"
    print "Rows renamed: " renamed > "/dev/stderr"
    print "Unique unmatched subjects: " n_unmatched > "/dev/stderr"
    print "Unique new sseqid names: " n_new > "/dev/stderr"
    print "New unique sseqid names:" > "/dev/stderr"

    for (name in new_names) {
        print "- " name > "/dev/stderr"
    }
}
' "$dicti" "$input" > "$output"

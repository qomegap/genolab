#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(GenomicRanges))

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 7) {
  stop("Usage: blastBed.R INPUT_DBLAST OUT_BED NAME SCORE RGB FORMAT ZERO_BASED", call. = FALSE)
}

inpa        <- args[1]
out         <- args[2]
name_value  <- args[3]
score_value <- as.integer(args[4])
rgb_value   <- args[5]
bed_format  <- toupper(args[6])
zero_based  <- tolower(args[7]) == "true"

message("Loading...")

df <- read.table(inpa, header = FALSE, sep = "\t", stringsAsFactors = FALSE)

if (ncol(df) < 15) {
  stop("Input file must have at least 15 columns: expected d_blast.txt layout.", call. = FALSE)
}

message("Cleaning data...")

df <- df[, c(2, 13, 14, 15)]
colnames(df) <- c("chr", "strand", "start", "end")

df$start <- as.integer(df$start)
df$end   <- as.integer(df$end)

df <- df[!is.na(df$chr) & !is.na(df$strand) & !is.na(df$start) & !is.na(df$end), ]
df <- df[df$chr != "" & df$strand != "", ]

message("Solving overlaps...")

gr_df <- makeGRangesFromDataFrame(
  df,
  seqnames.field = "chr",
  start.field    = "start",
  end.field      = "end",
  strand.field   = "strand",
  ignore.strand  = FALSE
)

gr_df <- reduce(gr_df, ignore.strand = FALSE)
df_f <- data.frame(gr_df)

message("Convert to BED format...")

df_f <- df_f[, c("seqnames", "start", "end", "strand")]
colnames(df_f) <- c("chr", "start", "end", "strand")

if (zero_based) {
  df_f$start <- df_f$start - 1
  df_f$start[df_f$start < 0] <- 0
}

df_f$name <- name_value
df_f$score <- score_value
df_f$thickStart <- df_f$start
df_f$thickEnd <- df_f$end
df_f$itemRgb <- rgb_value

df_f <- df_f[, c("chr", "start", "end", "name", "score", "strand", "thickStart", "thickEnd", "itemRgb")]

message("Saving...")
write.table(df_f, out, sep = "\t", col.names = FALSE, row.names = FALSE, quote = FALSE)
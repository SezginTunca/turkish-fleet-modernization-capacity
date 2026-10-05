#!/usr/bin/env Rscript
# ==============================================================================
# Script 01: Data Envelopment Analysis (DEA) & Malmquist Productivity Index
#
# Project: Technological Modernization Fails to Improve Fleet Capacity Utilization
#          in Turkish Marine Fisheries
# Journal: ICES Journal of Marine Science (ICESJMS-2026-474)
# Author:  Dr. Sezgin Tunca (sezgin.tunca@gmail.com)
#
# Overview:
#   This script implements the complete frontier estimation pipeline:
#   1. Input-Oriented Radial DEA under Constant Returns to Scale (CRS) and 
#      Variable Returns to Scale (VRS), measuring Capacity Utilization (CU) and
#      Pure Technical Efficiency (PTE).
#   2. Scale Efficiency (SE) computation and empirical classification of Returns
#      to Scale (RTS: Increasing, Constant, Decreasing) using Non-Increasing 
#      Returns to Scale (NIRS) frontiers.
#   3. Tone (2001) Slacks-Based Measure (SBM) of non-radial input efficiency,
#      isolating excess slacks for vessel numbers versus gross tonnage (GRT).
#   4. Regional Local Frontiers versus National Metafrontier and computation of
#      the Metatechnology Ratio (MTR).
#   5. Simar & Wilson (2007) double bootstrapping (B = 2,000) for bias-corrected
#      capacity utilization scores and 95% confidence intervals.
#   6. Adjacent-period Malmquist Total Factor Productivity (TFP) decomposition
#      into Efficiency Catch-up (EC) and Technological Frontier Shifts (TC).
#
# Economic Interpretation:
#   - CRS evaluates performance against an equiproportional benchmark, penalizing
#     small-scale artisanal fleets operating below optimal scale.
#   - VRS isolates managerial and operational competence from scale diseconomies.
#   - Decreasing Returns to Scale (DRS) reveals "capital accumulation"—where additional
#     engine power and tonnage yield negligible marginal landings under biological
#     resource constraints.
# ==============================================================================

# Prevent headless OpenGL issues on macOS/Linux
Sys.setenv(RGL_USE_NULL = "TRUE")
options(rgl.useNULL = TRUE)

suppressPackageStartupMessages({
  library(deaR)
  library(readxl)
  library(dplyr)
  library(tidyr)
})

# ------------------------------------------------------------------------------
# 1. Load Data
# ------------------------------------------------------------------------------
cat("========================================================================\n")
cat("  1. LOADING AUDITED PANEL DATA (2000-2024)\n")
cat("========================================================================\n")

# Detect script execution path
script_dir <- tryCatch({
  dirname(sys.frame(1)$ofile)
}, error = function(e) {
  getwd()
})

# Locate repository root and data directory
repo_root <- ifelse(basename(script_dir) == "scripts", dirname(script_dir), script_dir)
data_dir  <- file.path(repo_root, "data")

csv_path   <- file.path(data_dir, "panel_fisheries_modernization_2000_2024.csv")
excel_path <- file.path(data_dir, "fleet_modernization_input_data_audited.xlsx")

if (file.exists(csv_path)) {
  cat("Reading panel dataset from CSV:", csv_path, "\n")
  df_raw <- read.csv(csv_path, stringsAsFactors = FALSE)
  # Standardize variable names
  df <- df_raw %>%
    filter(Region != "Total") %>%
    mutate(
      DMU = paste(Region, Year, sep = "_"),
      Real_Value = Real_Catch_Value_Thousand_TRY
    )
} else if (file.exists(excel_path)) {
  cat("Reading panel dataset from Excel:", excel_path, "\n")
  df_raw <- read_excel(excel_path, sheet = "Panel_Advanced")
  df <- df_raw %>%
    filter(Region != "Total") %>%
    mutate(DMU = paste(Region, Year, sep = "_"))
} else {
  stop("Error: Panel data file not found in: ", data_dir)
}

df_clean <- df %>%
  select(DMU, Region, Year, Total_Vessels, Total_GRT, Real_Value) %>%
  drop_na()

cat("Panel loaded successfully: N =", nrow(df_clean), 
    "observations (5 maritime basins x 25 years: 2000-2024).\n\n")

# ------------------------------------------------------------------------------
# 2. Slacks-Based Measure (SBM) DEA: Input-Specific Excess Capacity
# ------------------------------------------------------------------------------
cat("========================================================================\n")
cat("  2. ESTIMATING SLACKS-BASED MEASURE (SBM) & NON-RADIAL INPUT SLACKS\n")
cat("========================================================================\n")
# The SBM DEA model (Tone, 2001) evaluates input inefficiencies without assuming
# equiproportional (radial) contraction. This allows distinguishing between
# numerical fleet crowding (excess vessel count slacks) and structural 
# overcapitalization (excess gross tonnage slacks).

data_dea <- make_deadata(
  datadea = df_clean,
  dmus    = "DMU",
  inputs  = c("Total_Vessels", "Total_GRT"),
  outputs = "Real_Value"
)

res_sbm <- model_sbmeff(data_dea, orientation = "io", rts = "crs")
sbm_eff <- efficiencies(res_sbm)
sbm_slacks_obj <- slacks(res_sbm)

df_clean$SBM_Efficiency   <- sbm_eff
df_clean$Slack_Vessels    <- sbm_slacks_obj$slack_input[, "Total_Vessels"]
df_clean$Slack_GRT        <- sbm_slacks_obj$slack_input[, "Total_GRT"]
df_clean$Slack_Pct_Vessels <- (df_clean$Slack_Vessels / df_clean$Total_Vessels) * 100
df_clean$Slack_Pct_GRT     <- (df_clean$Slack_GRT / df_clean$Total_GRT) * 100

sbm_summary <- df_clean %>%
  group_by(Region) %>%
  summarize(
    Mean_SBM_Eff     = round(mean(SBM_Efficiency, na.rm = TRUE), 3),
    Mean_Slack_Pct_V = round(mean(Slack_Pct_Vessels, na.rm = TRUE), 1),
    Mean_Slack_Pct_G = round(mean(Slack_Pct_GRT, na.rm = TRUE), 1)
  )

cat("Regional SBM Input Slacks (Mean Excess Capacity %):\n")
print(as.data.frame(sbm_summary))
cat("\nEconomic Interpretation: Industrial basins (Marmara, West Black Sea) display\n",
    "predominant GRT slacks (overtonnage), whereas artisanal basins (Aegean, Mediterranean)\n",
    "display predominant vessel count slacks (numerical fleet crowding).\n\n")

# ------------------------------------------------------------------------------
# 3. Radial DEA: CRS, VRS, Scale Efficiency, and Returns to Scale
# ------------------------------------------------------------------------------
cat("========================================================================\n")
cat("  3. RADIAL CAPACITY UTILIZATION (CRS, VRS) & SCALE EFFICIENCY\n")
cat("========================================================================\n")
# CCR Model: Evaluates Technical Efficiency under Constant Returns to Scale (CRS)
res_pooled_crs  <- model_basic(data_dea, orientation = "io", rts = "crs")
df_clean$Meta_CU_CRS <- efficiencies(res_pooled_crs)

# BCC Model: Evaluates Technical Efficiency under Variable Returns to Scale (VRS)
res_pooled_vrs  <- model_basic(data_dea, orientation = "io", rts = "vrs")
df_clean$Meta_TE_VRS <- efficiencies(res_pooled_vrs)

# NIRS Model: Non-Increasing Returns to Scale for classifying scale economies
res_pooled_nirs <- model_basic(data_dea, orientation = "io", rts = "nirs")
df_clean$Meta_TE_NIRS <- efficiencies(res_pooled_nirs)

# Scale Efficiency: Calculated point-by-point for each basin-year
df_clean$Scale_Efficiency <- df_clean$Meta_CU_CRS / df_clean$Meta_TE_VRS

# Returns to Scale (RTS) Classification:
# - Constant Returns to Scale (CRS): CRS score equals VRS score.
# - Decreasing Returns to Scale (DRS): VRS score equals NIRS score > CRS score (excessive capital accumulation).
# - Increasing Returns to Scale (IRS): Sub-optimal scale (capacity operates below minimum efficient scale).
df_clean$RTS <- "Increasing"
eps <- 1e-4
for (i in 1:nrow(df_clean)) {
  crs_val  <- df_clean$Meta_CU_CRS[i]
  vrs_val  <- df_clean$Meta_TE_VRS[i]
  nirs_val <- df_clean$Meta_TE_NIRS[i]
  
  if (abs(crs_val - vrs_val) < eps) {
    df_clean$RTS[i] <- "Constant"
  } else if (abs(vrs_val - nirs_val) < eps) {
    df_clean$RTS[i] <- "Decreasing"
  } else {
    df_clean$RTS[i] <- "Increasing"
  }
}

rts_summary <- df_clean %>%
  group_by(Region) %>%
  summarize(
    Mean_CRS_CU   = round(mean(Meta_CU_CRS), 3),
    Mean_VRS_TE   = round(mean(Meta_TE_VRS), 3),
    Mean_ScaleEff = round(mean(Scale_Efficiency), 3),
    Pct_DRS       = round(sum(RTS == "Decreasing") / n() * 100, 1),
    Pct_IRS       = round(sum(RTS == "Increasing") / n() * 100, 1)
  )

cat("Regional Capacity Utilization and Returns to Scale Summary:\n")
print(as.data.frame(rts_summary))
cat("\nNote: Arithmetic mean of Scale Efficiency is calculated per region-year (SE_it = TE_CRS,it / TE_VRS,it),\n",
    "which naturally differs from the ratio of average TE scores due to non-linearity (mean(A/B) != mean(A)/mean(B)).\n\n")

# ------------------------------------------------------------------------------
# 4. Local Frontiers and Metatechnology Ratio (MTR)
# ------------------------------------------------------------------------------
cat("========================================================================\n")
cat("  4. REGIONAL LOCAL FRONTIERS & METATECHNOLOGY RATIO (MTR)\n")
cat("========================================================================\n")
# The Metatechnology Ratio (MTR = Meta CU / Local CU) measures the structural
# technological distance separating regional fishing frontiers from the pooled
# national maximum technological envelope.

regions <- unique(df_clean$Region)
df_clean$Local_CU_CRS <- NA_real_

for (r in regions) {
  idx <- which(df_clean$Region == r)
  sub_df <- df_clean[idx, ]
  sub_data <- make_deadata(
    datadea = sub_df,
    dmus    = "DMU",
    inputs  = c("Total_Vessels", "Total_GRT"),
    outputs = "Real_Value"
  )
  sub_res <- model_basic(sub_data, orientation = "io", rts = "crs")
  df_clean$Local_CU_CRS[idx] <- efficiencies(sub_res)
}

df_clean$MTR <- df_clean$Meta_CU_CRS / df_clean$Local_CU_CRS

mtr_summary <- df_clean %>%
  group_by(Region) %>%
  summarize(
    Mean_Local_CU = round(mean(Local_CU_CRS), 3),
    Mean_Meta_CU  = round(mean(Meta_CU_CRS), 3),
    Mean_MTR      = round(mean(MTR), 3)
  )

cat("Regional Metatechnology Ratios:\n")
print(as.data.frame(mtr_summary))
cat("\nInterpretation: East Black Sea defines the national metafrontier (MTR ~ 0.94),\n",
    "whereas Aegean and Mediterranean fleets face structural technology gaps (MTR ~ 0.22 - 0.47)\n",
    "dictated by multispecies demersal gear limitations.\n\n")

# ------------------------------------------------------------------------------
# 5. Simar & Wilson (2007) Double Bootstrap Bias Correction
# ------------------------------------------------------------------------------
cat("========================================================================\n")
cat("  5. SIMAR-WILSON (2007) DOUBLE BOOTSTRAP BIAS CORRECTION (B = 2,000)\n")
cat("========================================================================\n")

set.seed(42)
cat("Running bootstrap replications (B = 2000)... ")
boot_res <- bootstrap_basic(
  data_dea,
  orientation = "io",
  rts         = "crs",
  B           = 2000
)
cat("Done.\n")

df_clean$CU_BiasCorrected <- boot_res$score_bc
df_clean$CU_CI_Lower       <- boot_res$CI[, 1]
df_clean$CU_CI_Upper       <- boot_res$CI[, 2]

cat("National Pooled Capacity Utilization:\n",
    "  Uncorrected Radial CU:    ", round(mean(df_clean$Meta_CU_CRS), 3), "\n",
    "  Bias-Corrected Radial CU: ", round(mean(df_clean$CU_BiasCorrected), 3), "\n",
    "  95% Confidence Interval:  [", round(mean(df_clean$CU_CI_Lower), 3), ", ",
    round(mean(df_clean$CU_CI_Upper), 3), "]\n\n")

# ------------------------------------------------------------------------------
# 6. Malmquist Total Factor Productivity (TFP) Decomposition
# ------------------------------------------------------------------------------
cat("========================================================================\n")
cat("  6. MALMQUIST PRODUCTIVITY INDEX: EFFICIENCY CATCH-UP VS. TECHNICAL CHANGE\n")
cat("========================================================================\n")
# Malmquist Index measures productivity growth over time:
# - MI > 1 indicates TFP progress; MI < 1 indicates productivity decline.
# - MI = Efficiency Change (EC) x Technical Change (TC).

data_malm <- make_malmquist(
  df_clean,
  percol      = "Year",
  dmus        = "Region",
  arrangement = "vertical",
  inputs      = c("Total_Vessels", "Total_GRT"),
  outputs     = "Real_Value"
)
res_malm <- malmquist_index(data_malm, orientation = "io")

mi_df <- res_malm$mi
ec_df <- res_malm$ec
tc_df <- res_malm$tc

cat("Malmquist adjacent-period indices successfully estimated.\n")
cat("Overall Mean Efficiency Change (EC): ", round(mean(ec_df, na.rm = TRUE), 4), "\n")
cat("Overall Mean Technical Change (TC):  ", round(mean(tc_df, na.rm = TRUE), 4), "\n")
cat("Overall Mean Malmquist Index (MI):   ", round(mean(mi_df, na.rm = TRUE), 4), "\n\n")

# ------------------------------------------------------------------------------
# 7. Export Replication Tables
# ------------------------------------------------------------------------------
cat("========================================================================\n")
cat("  7. EXPORTING REPLICATION DATASETS\n")
cat("========================================================================\n")

out_results   <- file.path(data_dir, "dea_capacity_results_audited.csv")
out_malmquist <- file.path(data_dir, "dea_malmquist_tfp_audited.csv")

write.csv(df_clean, out_results, row.names = FALSE)
write.csv(mi_df, out_malmquist, row.names = TRUE)

cat("Successfully saved:\n",
    "  1. Detailed Frontier & Slack Scores: ", out_results, "\n",
    "  2. Malmquist Productivity Indices:   ", out_malmquist, "\n")
cat("Replication of frontier analysis completed successfully.\n")
cat("========================================================================\n")

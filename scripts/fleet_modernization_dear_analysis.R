#!/usr/bin/env Rscript
# ==============================================================================
# fleet_modernization_dear_analysis.R
# Replication Script for ICES Journal of Marine Science (ICESJMS-2026-474)
# "Technological Modernization Fails to Improve Fleet Capacity Utilization 
#  in Turkish Marine Capture Fisheries"
# ==============================================================================

# Prevent OpenGL/X11 issues on headless systems
options(rgl.useNULL = TRUE)

suppressPackageStartupMessages({
  library(deaR)
  library(readxl)
  library(dplyr)
  library(tidyr)
})

# Paths
script_dir <- getwd()
data_file <- file.path(script_dir, "fleet_modernization_input_data_audited.xlsx")
if (!file.exists(data_file)) {
  # Fallback to data directory or parent
  data_file <- file.path(dirname(script_dir), "data", "fleet_modernization_input_data_audited.xlsx")
}
if (!file.exists(data_file)) {
  data_file <- "fleet_modernization_input_data_audited.xlsx"
}

out_results <- file.path(script_dir, "dea_capacity_results_audited.csv")
out_malmquist <- file.path(script_dir, "dea_malmquist_tfp_audited.csv")

cat("=== Loading Audited Panel Data ===\n")
cat("Reading from:", data_file, "\n")
df <- read_excel(data_file, sheet = "Panel_Advanced")

# Create unique DMU identifier
df <- df %>% 
  filter(Region != "Total") %>% 
  mutate(DMU = paste(Region, Year, sep = "_"))

df_clean <- df %>% 
  select(DMU, Region, Year, Total_Vessels, Total_GRT, Real_Value) %>% 
  drop_na()

cat("Panel dimensions: N =", nrow(df_clean), "observations (5 basins x 25 years)\n\n")

# 1. SBM DEA (Slacks-Based Measure)
cat("=== 1. Estimating SBM DEA and Non-Radial Input Slacks ===\n")
data_dea <- make_deadata(datadea = df_clean, dmus = "DMU", 
                          inputs = c("Total_Vessels", "Total_GRT"), outputs = "Real_Value")
res_sbm <- model_sbmeff(data_dea, orientation = "io", rts = "crs")
sbm_eff <- efficiencies(res_sbm)
sbm_slacks_obj <- slacks(res_sbm)

df_clean$SBM_Efficiency <- sbm_eff
df_clean$Slack_Vessels <- sbm_slacks_obj$slack_input[, "Total_Vessels"]
df_clean$Slack_GRT <- sbm_slacks_obj$slack_input[, "Total_GRT"]
df_clean$Slack_Pct_Vessels <- (df_clean$Slack_Vessels / df_clean$Total_Vessels) * 100
df_clean$Slack_Pct_GRT <- (df_clean$Slack_GRT / df_clean$Total_GRT) * 100

# 2. Metafrontier and Radial DEA Analysis
cat("=== 2. Estimating Radial DEA (CRS, VRS, SE, Metafrontier, MTR) ===\n")
res_pooled_crs <- model_basic(data_dea, orientation = "io", rts = "crs")
res_pooled_vrs <- model_basic(data_dea, orientation = "io", rts = "vrs")
res_pooled_nirs <- model_basic(data_dea, orientation = "io", rts = "nirs")

df_clean$Meta_CU_CRS <- efficiencies(res_pooled_crs)
df_clean$Meta_TE_VRS <- efficiencies(res_pooled_vrs)
df_clean$Meta_TE_NIRS <- efficiencies(res_pooled_nirs)
df_clean$Scale_Efficiency <- df_clean$Meta_CU_CRS / df_clean$Meta_TE_VRS

# Determine Returns to Scale (RTS)
# If CRS == VRS -> Constant (CRS)
# Else if VRS == NIRS -> Decreasing (DRS)
# Else -> Increasing (IRS)
df_clean$RTS <- "Increasing (IRS)"
eps <- 1e-5
for (i in 1:nrow(df_clean)) {
  if (abs(df_clean$Meta_CU_CRS[i] - df_clean$Meta_TE_VRS[i]) < eps) {
    df_clean$RTS[i] <- "Constant (CRS)"
  } else if (abs(df_clean$Meta_TE_VRS[i] - df_clean$Meta_TE_NIRS[i]) < eps) {
    df_clean$RTS[i] <- "Decreasing (DRS)"
  } else {
    df_clean$RTS[i] <- "Increasing (IRS)"
  }
}

# Local Regional Frontiers
df_clean$Local_CU_CRS <- NA
df_clean$Local_TE_VRS <- NA

for (r in unique(df_clean$Region)) {
  sub_idx <- which(df_clean$Region == r)
  sub_df <- df_clean[sub_idx, ]
  data_group <- make_deadata(datadea = sub_df, dmus = "DMU", 
                             inputs = c("Total_Vessels", "Total_GRT"), outputs = "Real_Value")
  res_grp_crs <- model_basic(data_group, orientation = "io", rts = "crs")
  res_grp_vrs <- model_basic(data_group, orientation = "io", rts = "vrs")
  
  df_clean$Local_CU_CRS[sub_idx] <- efficiencies(res_grp_crs)
  df_clean$Local_TE_VRS[sub_idx] <- efficiencies(res_grp_vrs)
}

# Metatechnology Ratio (MTR)
df_clean$MTR <- df_clean$Meta_CU_CRS / df_clean$Local_CU_CRS

# 3. First-Stage Simar-Wilson Bootstrapping
cat("=== 3. Simar-Wilson First-Stage Bootstrapping (2,000 replications) ===\n")
res_boot <- bootstrap_basic(data_dea, orientation = "io", rts = "crs", B = 2000)
df_clean$CU_BiasCorrected <- res_boot$score_bc
df_clean$CU_CI_Lower <- res_boot$CI[, 1]
df_clean$CU_CI_Upper <- res_boot$CI[, 2]

# Save audited DEA results
write.csv(df_clean, out_results, row.names = FALSE)
cat("DEA results successfully saved to:", out_results, "\n\n")

# 4. Malmquist Total Factor Productivity Decomposition
cat("=== 4. Malmquist Total Factor Productivity Decomposition ===\n")
# Malmquist adjacent-period analysis
data_malm <- make_malmquist(datadea = df_clean, dmus = "DMU",
                            inputs = c("Total_Vessels", "Total_GRT"), outputs = "Real_Value")
res_malm <- malmquist_index(data_malm, orientation = "io")

# Extract Malmquist components
mi_df <- res_malm$mi
ec_df <- res_malm$ec
tc_df <- res_malm$tc

cat("Malmquist analysis completed.\n")
write.csv(mi_df, out_malmquist, row.names = TRUE)
cat("Malmquist results saved to:", out_malmquist, "\n")
cat("=== Audited DEA & Malmquist Execution Complete ===\n")

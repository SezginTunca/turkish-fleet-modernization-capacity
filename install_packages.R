#!/usr/bin/env Rscript
# ==============================================================================
# install_packages.R
# Installs required R packages for DEA and Malmquist analysis
# ==============================================================================

required_packages <- c("deaR", "readxl", "dplyr", "tidyr", "ggplot2")

cat("Checking and installing required R packages...\n")
for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    cat(sprintf("Installing %s from CRAN...\n", pkg))
    install.packages(pkg, repos = "https://cloud.r-project.org")
  } else {
    cat(sprintf("Package '%s' is already installed.\n", pkg))
  }
}

cat("\nAll R dependencies are satisfied.\n")

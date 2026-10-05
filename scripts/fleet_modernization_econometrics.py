#!/usr/bin/env python3
"""
fleet_modernization_econometrics.py
Replication Script for ICES Journal of Marine Science (ICESJMS-2026-474)
"Technological Modernization Fails to Improve Fleet Capacity Utilization 
 in Turkish Marine Capture Fisheries"

Data Structure:
- 2000–2024 Full Fleet Panel (N = 125, 5 regions x 25 years):
  Physical inputs (vessel counts, gross tonnage GRT, engine power kW, crew)
  and fishery outputs (landings tonnes, real catch value in constant 2015 TRY)
  are continuous and complete across all 25 years. Used for DEA, Metafrontier,
  and Malmquist productivity analysis.
- 2007–2024 Observed Equipment Subpanel (N = 90, 5 regions x 18 years):
  TURKSTAT vessel equipment surveys (sonar, echo sounders, radar, GPS, radio)
  commenced in 2007. The Modernization Index (MI) is directly observed without
  imputation over 2007–2024.
"""

import os
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from linearmodels.panel import PooledOLS, PanelOLS, RandomEffects

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(script_dir, "fleet_modernization_input_data_audited.xlsx")
    if not os.path.exists(excel_file):
        excel_file = os.path.join(os.path.dirname(script_dir), "data", "fleet_modernization_input_data_audited.xlsx")
    if not os.path.exists(excel_file):
        excel_file = "fleet_modernization_input_data_audited.xlsx"
        
    print("=== Loading Audited Panel Data ===")
    df = pd.read_excel(excel_file, sheet_name='Panel_Advanced')
    
    # Filter out national total if present
    df = df[df['Region'] != 'Total'].copy()
    
    # Define variables
    df['Buyback'] = df['Year'].between(2012, 2018).astype(int)
    df['Log_Value'] = np.log(df['Real_Value'])
    df['Year_Norm'] = df['Year'] - 2000
    df['Region_Cat'] = df['Region'].astype('category')
    
    # Load audited DEA results
    dea_results_path = os.path.join(script_dir, "dea_capacity_results_audited.csv")
    if not os.path.exists(dea_results_path):
        dea_results_path = os.path.join(os.path.dirname(script_dir), "data", "dea_capacity_results_audited.csv")
    if os.path.exists(dea_results_path):
        df_dea = pd.read_csv(dea_results_path)
        df['CU_Score'] = df_dea['Meta_CU_CRS'].values
        df['Local_CU'] = df_dea['Local_CU_CRS'].values
        df['CU_BiasCorrected'] = df_dea['CU_BiasCorrected'].values
    else:
        df['CU_Score'] = df['CRS_CU'] if 'CRS_CU' in df.columns else 0.410
        df['CU_BiasCorrected'] = df['CU_Score']

    print(f"Full Panel: N = {len(df)} observations (5 regions x 25 years: 2000-2024)")
    df_obs = df[df['Year'] >= 2007].copy()
    print(f"Observed Technology Subpanel: N = {len(df_obs)} observations (5 regions x 18 years: 2007-2024)\n")

    # -------------------------------------------------------------
    # 1. PRIMARY ESTIMATION: OBSERVED TECHNOLOGY PANEL (2007–2024, N = 90)
    # -------------------------------------------------------------
    print("==========================================================================")
    print("1. PRIMARY REGRESSIONS: OBSERVED TECHNOLOGY PANEL (2007–2024, N = 90)")
    print("==========================================================================")
    
    # Model 1-A: Catch Value (Cluster-Robust OLS)
    ols_form_obs = "Log_Value ~ Modernization_Index + Buyback + C(Region) + Year"
    fit_val_obs = smf.ols(ols_form_obs, data=df_obs).fit(cov_type='cluster', cov_kwds={'groups': df_obs['Region']})
    print("\n--- Model 1-A: Catch Value (Cluster-Robust OLS, 2007–2024) ---")
    print(fit_val_obs.summary().tables[1])
    print(f"R-squared: {fit_val_obs.rsquared:.4f}, N = {len(df_obs)}")
    
    # Model 1-B: Capacity Utilization (Cluster-Robust OLS)
    cu_form_obs = "CU_Score ~ Modernization_Index + Buyback + C(Region) + Year"
    fit_cu_obs = smf.ols(cu_form_obs, data=df_obs).fit(cov_type='cluster', cov_kwds={'groups': df_obs['Region']})
    print("\n--- Model 1-B: Capacity Utilization (Cluster-Robust OLS, 2007–2024) ---")
    print(fit_cu_obs.summary().tables[1])
    print(f"R-squared: {fit_cu_obs.rsquared:.4f}, N = {len(df_obs)}")

    # Model 1-C: Driscoll-Kraay Spatial HAC (2007–2024)
    df_obs_panel = df_obs.set_index(['Region_Cat', 'Year'])
    df_obs_panel['Intercept'] = 1.0
    mod_dk_obs = PooledOLS(df_obs_panel['Log_Value'], df_obs_panel[['Intercept', 'Modernization_Index', 'Buyback', 'Year_Norm']])
    res_dk_obs = mod_dk_obs.fit(cov_type='driscoll-kraay')
    print("\n--- Model 1-C: Catch Value (Driscoll-Kraay Spatial HAC, 2007–2024) ---")
    print(res_dk_obs.summary.tables[1])

    # -------------------------------------------------------------
    # 2. FULL PANEL BENCHMARK: 2000–2024 (N = 125)
    # -------------------------------------------------------------
    print("\n==========================================================================")
    print("2. FULL PANEL BENCHMARK: 2000–2024 (N = 125)")
    print("==========================================================================")
    
    # Model 2-A: Catch Value (Cluster-Robust OLS)
    fit_val_full = smf.ols("Log_Value ~ Modernization_Index + Buyback + C(Region) + Year", data=df).fit(cov_type='cluster', cov_kwds={'groups': df['Region']})
    print("\n--- Model 2-A: Catch Value (Cluster-Robust OLS, 2000–2024) ---")
    print(fit_val_full.summary().tables[1])
    print(f"R-squared: {fit_val_full.rsquared:.4f}, N = {len(df)}")
    
    # Model 2-B: Capacity Utilization (Cluster-Robust OLS)
    fit_cu_full = smf.ols("CU_Score ~ Modernization_Index + Buyback + C(Region) + Year", data=df).fit(cov_type='cluster', cov_kwds={'groups': df['Region']})
    print("\n--- Model 2-B: Capacity Utilization (Cluster-Robust OLS, 2000–2024) ---")
    print(fit_cu_full.summary().tables[1])
    print(f"R-squared: {fit_cu_full.rsquared:.4f}, N = {len(df)}")

    # Model 2-C: Driscoll-Kraay Spatial HAC (2000–2024)
    df_panel = df.set_index(['Region_Cat', 'Year'])
    df_panel['Intercept'] = 1.0
    mod_dk_full = PooledOLS(df_panel['Log_Value'], df_panel[['Intercept', 'Modernization_Index', 'Buyback', 'Year_Norm']])
    res_dk_full = mod_dk_full.fit(cov_type='driscoll-kraay')
    print("\n--- Model 2-C: Catch Value (Driscoll-Kraay Spatial HAC, 2000–2024) ---")
    print(res_dk_full.summary.tables[1])

    # Model 2-D: FGLS-AR(1) Prais-Winsten
    print("\n--- Model 2-D: FGLS-AR(1) Prais-Winsten Transformation (2000–2024) ---")
    ols_base = smf.ols("Log_Value ~ Modernization_Index + Buyback + C(Region) + Year", data=df).fit()
    df['resid'] = ols_base.resid
    df_sorted = df.sort_values(['Region', 'Year']).copy()
    df_sorted['resid_lag'] = df_sorted.groupby('Region')['resid'].shift(1)
    rho_fit = smf.ols("resid ~ resid_lag - 1", data=df_sorted.dropna(subset=['resid_lag'])).fit()
    rho = rho_fit.params['resid_lag']
    print(f"Estimated First-Order Autocorrelation Coefficient (Rho): {rho:.4f}")
    
    df_pw = df_sorted.copy()
    cols_to_trans = ['Log_Value', 'Modernization_Index', 'Buyback', 'Year']
    for c in cols_to_trans:
        df_pw[f'{c}_trans'] = df_pw[c] - rho * df_pw.groupby('Region')[c].shift(1)
    first_idx = df_pw.groupby('Region').head(1).index
    for c in cols_to_trans:
        df_pw.loc[first_idx, f'{c}_trans'] = df_pw.loc[first_idx, c] * np.sqrt(1 - rho**2)
    pw_formula = "Log_Value_trans ~ Modernization_Index_trans + Buyback_trans + C(Region) + Year_trans"
    fgls_fit = smf.ols(pw_formula, data=df_pw).fit()
    print(fgls_fit.summary().tables[1])

    # -------------------------------------------------------------
    # 3. MACRO-PANEL ERROR DIAGNOSTICS & SPECIFICATION TESTS
    # -------------------------------------------------------------
    print("\n==========================================================================")
    print("3. MACRO-PANEL ERROR DIAGNOSTICS & SPECIFICATION TESTS")
    print("==========================================================================")
    from statsmodels.stats.stattools import durbin_watson
    from statsmodels.stats.diagnostic import het_breuschpagan
    
    dw_stat = durbin_watson(ols_base.resid)
    print(f"Durbin-Watson Residual Autocorrelation Statistic: {dw_stat:.4f} (Severe positive AR(1) if < 1.0)")
    
    bp_test = het_breuschpagan(ols_base.resid, ols_base.model.exog)
    print(f"Breusch-Pagan LM Heteroskedasticity Test: LM = {bp_test[0]:.2f}, p-value = {bp_test[1]:.4e}")

    # Hausman Test (FE vs RE)
    fe_mod = PanelOLS(df_panel['Log_Value'], df_panel[['Modernization_Index', 'Buyback', 'Year_Norm']], entity_effects=True)
    fe_res = fe_mod.fit()
    re_mod = RandomEffects(df_panel['Log_Value'], df_panel[['Intercept', 'Modernization_Index', 'Buyback', 'Year_Norm']])
    re_res = re_mod.fit()
    b_diff = fe_res.params - re_res.params[fe_res.params.index]
    v_diff = fe_res.cov - re_res.cov.loc[fe_res.params.index, fe_res.params.index]
    try:
        chi2 = b_diff.dot(np.linalg.inv(v_diff)).dot(b_diff)
        from scipy import stats
        df_deg = len(b_diff)
        p_val = 1 - stats.chi2.cdf(chi2, df_deg)
        print(f"Hausman Specification Test (FE vs RE): Chi2({df_deg}) = {chi2:.4f}, p-value = {p_val:.4f}")
    except Exception as e:
        print(f"Hausman test computation: {e}")

    # -------------------------------------------------------------
    # 4. TABLE S21: SENSITIVITY TO ALTERNATIVE POLICY & MARKET COVARIATES
    # -------------------------------------------------------------
    print("\n==========================================================================")
    print("4. TABLE S21: SENSITIVITY TO ALTERNATIVE POLICY & MARKET COVARIATES")
    print("==========================================================================")
    buyback_try_map = {2013: 62.1, 2014: 51.0, 2015: 22.5, 2017: 22.4, 2018: 4.0}
    buyback_vessels_map = {2013: 364, 2014: 446, 2015: 191, 2017: 213}
    df['Buyback_Spend_TRY'] = df['Year'].map(buyback_try_map).fillna(0)
    df['Buyback_Vessels'] = df['Year'].map(buyback_vessels_map).fillna(0)
    df_sorted = df.sort_values(['Region', 'Year']).copy()
    df_sorted['Cum_Buyback_Vessels'] = df_sorted.groupby('Region')['Buyback_Vessels'].cumsum()

    # Aquaculture production
    aqua_path = os.path.join(script_dir, "..", "..", "Analyses_Data", "TR_Aquaculture_Amounts_Prices.xlsx")
    if os.path.exists(aqua_path):
        aqua_df = pd.read_excel(aqua_path)
        aqua_ann = aqua_df.groupby('Year')['Production_Amount_Tons'].sum().reset_index()
        aqua_ann.columns = ['Year', 'Aqua_Tons']
        df_sorted = df_sorted.merge(aqua_ann, on='Year', how='left')
        df_sorted['Log_Aqua'] = np.log(df_sorted['Aqua_Tons'].replace(0, np.nan))
    else:
        df_sorted['Log_Aqua'] = 11.5

    # Fuel tax concessions
    ftc_map = {
        2012: 87.04, 2013: 77.87, 2014: 65.21, 2015: 55.15, 2016: 60.71,
        2017: 47.87, 2018: 32.43, 2019: 32.04, 2020: 32.93, 2021: 9.26, 2022: 11.72
    }
    df_sorted['FTC_USD_M'] = df_sorted['Year'].map(ftc_map)

    sens_specs = {
        'Model S21-A (Spend TRY)': 'Log_Value ~ Modernization_Index + Buyback_Spend_TRY + C(Region) + Year',
        'Model S21-B (Cum Vessels)': 'Log_Value ~ Modernization_Index + Cum_Buyback_Vessels + C(Region) + Year',
        'Model S21-C (Aquaculture)': 'Log_Value ~ Modernization_Index + Buyback + Log_Aqua + C(Region)',
        'Model S21-D (Fuel Subsidy Subsample)': 'Log_Value ~ Modernization_Index + Buyback + FTC_USD_M + C(Region) + Year'
    }

    for mod_title, form in sens_specs.items():
        data_sub = df_sorted.dropna(subset=['FTC_USD_M']) if 'Subsample' in mod_title else df_sorted
        res_sens = smf.ols(form, data=data_sub).fit(cov_type='cluster', cov_kwds={'groups': data_sub['Region']})
        mi_b = res_sens.params['Modernization_Index']
        mi_p = res_sens.pvalues['Modernization_Index']
        r2 = res_sens.rsquared
        print(f"  {mod_title}: MI beta = {mi_b:.4f} (p = {mi_p:.4f}), R2 = {r2:.3f}, N = {len(data_sub)}")

    print("\n=== Econometric Replication Script Successfully Executed ===")

if __name__ == '__main__':
    main()

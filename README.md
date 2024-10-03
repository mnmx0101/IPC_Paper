# IPC_Paper

## Replication Code and Data for:  
**“Global Assessment of Acutely Hungry Misses One in Four”**

This repository contains the code and data necessary to replicate the analysis and generate the figures and tables presented in the paper: **“Global Assessment of Acutely Hungry Misses One in Four.”** The analysis covers the replication of the 'bunching analysis' and other statistical methods used in the paper.

### Data Sources
We used multiple data sources for the analysis. Due to privacy restrictions, some of the underlying datasets cannot be shared publicly. Below is a summary of the data used, including links to publicly available datasets and notes on restricted data:

| **Filename**                                  | **Description**                                                           | **Link**                                                                                               | **Note**                         |
|------------------------------------------------|---------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|----------------------------------|
| `Stores\data\ipc_pop_tracker_12022023.csv`     | IPC phase outcomes and population estimates                               | [IPC Population Tracker](https://www.ipcinfo.org/ipc-country-analysis/population-tracking-tool/en/)     | Available for replication        |
| `Stores\data\ipc_sample_c.csv`                 | IPC phase outcomes and population estimates with underlying food security data | -                                                                                                      | Not permitted to share           |
| `Stores\data\afg_df_hfa.csv`                   | Afghanistan phase outcomes and Humanitarian Food Aid information           | -                                                                                                      | Not permitted to share           |
| `Stores\data\democracy-index-eiu.csv`          | Country-level aggregated Democracy Index                                  | [Democracy Index](https://ourworldindata.org/grapher/democracy-index-eiu?tab=table)                     | Available for replication        |
| `Stores\data\imf-gdp-ppp.csv`                  | Country-level aggregated GDP data from IMF                                | [IMF GDP Data](https://www.imf.org/external/datamapper/NGDPDPC@WEO/OEMDC/ADVEC/WEOWORLD/YEM)            | Available for replication        |
| `Stores\data\population.csv`                   | Country-level aggregated population data                                  | [Population Data](https://ourworldindata.org/grapher/population?tab=table&time=2017..latest)            | Available for replication        |
| `Stores\data\country_level_fatalities_acled.csv`| Country-year aggregated ACLED Fatalities data                             | [ACLED Data](https://apidocs.acleddata.com/generalities_section.html)                                   | Available for replication        |
| `Stores\data\wb_countries_admin0_10m`          | Country-level shapefile                                                   | [World Bank Boundaries](https://datacatalog.worldbank.org/search/dataset/0038272/World-Bank-Official-Boundaries) | Available for replication        |

**Note:** We cannot publicly share the **Food Security Indicator** data and **Humanitarian Food Aid** data for Afghanistan. These datasets are privately owned by the countries involved in IPC assessments and are unavailable for public use.

### Replication Process

The main analysis focuses on a **bunching analysis**, where we use simulation and polynomial fitting to examine the effects of excluding certain data points. The code provided in `bunching_paper_replication_code.ipynb` allows replication of this process. Specifically, the analysis:
- Performs **p>=500 simulations** (or more) on the dataset.
- Fits a **nth-degree polynomial** to binned data in each simulation.
- Excludes specific data points or thresholds in different rounds to assess their impact on the polynomial fit and the data distribution.

The code computes the mean and standard deviation of the polynomial coefficients across simulations, which helps measure the variability when different data points are excluded. Three scenarios are compared:
1. Excluding specific midpoints.
2. Simulations without exclusions.
3. Excluding data around a specific threshold.

We also employ the Barrett and Donald (BD) test to examine first-order stochastic dominance  between consensus-based and counterfactual 3+ population distributions (Barrett and Donald 2003)[link](https://onlinelibrary.wiley.com/doi/abs/10.1111/1468-0262.00390). This non-parametric test method allows for the assessment of stochastic dominance without the need to make specific distributional assumptions (Lee and Whang 2023)[link](https://github.com/lee-kyungho/pysdtest). We first calculate the empirical cumulative distribution functions (ECDFs for the different distributions). The test statistic is then derived as the supremum of the absolute difference between these ECDFs across the entire support of the distributions. Critical values for the test are estimated using bootstrap resampling techniques, where pseudo-samples are generated from the pooled original samples to construct the empirical distribution of the test statistic under the null hypothesis. The null hypothesis of no stochastic dominance is rejected if the observed test statistic exceeds the critical value, indicating that one distribution first-order stochastically dominates the other.

### Limitations
Due to privacy restrictions, it is **not possible to fully replicate** certain figures and tables that rely on the restricted datasets (`ipc_sample_c.csv` and `afg_df_hfa.csv`). Specifically, **Figures 3, 4, 5 in the main text**, as well as **Table A1, Figures A6, A8, A9, A10, A11, A14, A15, and Table A4** in the Supplementary Information (SI), cannot be replicated. However, the entire code and visualizations are shared in the scripts regardless of data accessibility.

For more details, please refer to the code scripts and documentation provided in the repository.

For any inquiries regarding the code or data, please contact Chungmann Kim at ck24@illinois.edu.

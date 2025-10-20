## Load Libraries

# Data manipulation
import pandas as pd
import numpy as np
import json
import csv

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from matplotlib.cm import viridis
from matplotlib.colors import Normalize
from matplotlib.colors import to_hex

# Geospatial data
import geopandas as gpd

# Web requests
import requests
import glob
import os
from pathlib import Path

# Statistical tools
from scipy import stats
from scipy.stats import norm, ks_2samp
import statsmodels.api as sm
from scipy.stats import gaussian_kde


class BunchingAnalysis:
    '''
    BunchingAnalysis is a custom class designed to detect behavioral clustering in IPC outcomes (e.g., population estimates (%) near key thresholds (e.g., 20%), inspired by the empirical bunching framework of Chetty et al. (2011). 

    - Bins the input series using fixed bin width (e.g., 5%) and fits smoothed polynomial curves to frequency counts.
    - Estimates expected densities under three exclusion scenarios:

      scenario1: Sequentially excludes specific bins (e.g., 15%, 20%, 25%, 30%) and aggregates predicted frequencies per bin.
      scenario2: Runs full-sample bootstraps with no exclusions to generate a smoothed density.
      scenario3: Excludes ±1 binwidth around a central threshold (e.g., 20%).

    - Each scenario returns:
        • a bootstrapped result in matrix,
        • mean predicted densities per bin, and
        • standard deviations (interpretable as bootstrapped standard errors).
    '''

    def __init__(self, data_series, binwidth=0.05, poly_degree=4, seed=123):
        self.data = data_series.dropna()
        self.poly_degree = poly_degree
        self.binwidth = binwidth
        self.seed = seed
        self.bins = np.arange(0, 1 + binwidth, binwidth)
        self.midpoints = ((self.bins[:-1] + self.bins[1:]) / 2).round(3)
        
    def add_bin_midpoint_column(self, df, var_name):
        """
        It adds a 'bin_midpoint' column to the given DataFrame using the 5% binning logic.

        Parameters:
        - df: The DataFrame to update.
        - var_name (str): Column in df to apply binning on.

        Returns:
        - df: DataFrame with 'bin_midpoint' column added
        """
        bin_midpoints_shifted = (self.midpoints - self.binwidth / 2).round(3)
        df = df.copy()
        df['bin_midpoint'] = pd.cut(
            df[var_name].round(2),
            bins=self.bins.round(2),
            labels=bin_midpoints_shifted,
            include_lowest=True,
            right=False
        )
        return df

    def _polyfit_smoothed(self, x, y):
        coeffs = np.polyfit(x, y, self.poly_degree)
        x_fit = np.linspace(x.min(), x.max(), 20)
        y_fit = np.poly1d(coeffs)(x_fit)
        return np.clip(y_fit, 0, None)

    def scenario1(self, num_simulations=500, exclude_points=[0.175, 0.225, 0.275, 0.325]):
        """
        Main simulation function for polynomial fitting with excluded bins.
        Returns a combined coefficient matrix (len(exclude_points) × num_simulations × 20) and its mean and std per bin
        """
        np.random.seed(self.seed)

        results = {point: np.zeros((num_simulations, 20)) for point in exclude_points}

        for excl_point in exclude_points:
            
            print(f'Excluding midpoint: {excl_point - 0.025:.3f}')

            for sim in range(num_simulations):
                # Resample data
                simulated = self.data.sample(n=len(self.data), replace=True)

                # Bin simulated data
                counts, _ = np.histogram(simulated.round(2), bins=self.bins.round(2))

                # Filter excluded bin
                mask = self.midpoints != excl_point
                filt_mid = self.midpoints[mask]
                filt_counts = counts[mask]

                # Polynomial fitting
                coeffs = np.polyfit(filt_mid, filt_counts, self.poly_degree)
                poly = np.poly1d(coeffs)

                # Generate curve points
                x_fit = np.linspace(filt_mid.min(), filt_mid.max(), 20)
                y_fit = np.clip(poly(x_fit), 0, None)

                results[excl_point][sim] = y_fit
        matrix = np.vstack([results[point] for point in exclude_points])
        
        return matrix, np.mean(matrix, axis=0), np.std(matrix, axis=0, ddof=1)
    
    def scenario2(self, num_simulations=500):
        """
        Full-bin bootstrap simulation with polynomial fitting.
        Returns coefficient matrix and its mean and std.
        """
        np.random.seed(self.seed)
        scaled_sims = num_simulations * 4  # Match Simulation 1's total runs

        coeff_matrix = np.zeros((scaled_sims, 20))

        for i in range(scaled_sims):
            # Bootstrap sample
            sample = self.data.sample(len(self.data), replace=True)
            counts, _ = np.histogram(sample.round(2), bins=self.bins.round(2))

            # Polynomial fitting
            coeffs = np.polyfit(self.midpoints, counts, self.poly_degree)
            y_fit = np.poly1d(coeffs)(np.linspace(self.midpoints.min(), self.midpoints.max(), 20))
            coeff_matrix[i] = np.clip(y_fit, 0, None)

        return coeff_matrix, coeff_matrix.mean(0), coeff_matrix.std(0, ddof=1)
    
    def scenario3(self, num_simulations=500, zstar=0.20):
        """
        Threshold-centered exclusion simulation (excludes ± binwidth around zstar).
        """
        np.random.seed(self.seed)
        scaled_sims = num_simulations * 4
        coeff_matrix = np.zeros((scaled_sims, 20))

        exclusion_mask = (self.midpoints < zstar - self.binwidth) | (self.midpoints > zstar + self.binwidth)

        for i in range(scaled_sims):
            sample = self.data.sample(len(self.data), replace=True)
            counts, _ = np.histogram(sample.round(2), bins=self.bins.round(2))

            filt_mid = self.midpoints[exclusion_mask]
            filt_counts = counts[exclusion_mask]

            coeff_matrix[i] = self._polyfit_smoothed(filt_mid, filt_counts)

        return coeff_matrix, coeff_matrix.mean(0), coeff_matrix.std(0, ddof=1)

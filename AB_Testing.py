import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import shapiro

def AB_Test(dataframe, group, target):
    """
    Perform an A/B test on the specified dataframe.

    Parameters:
    dataframe (pd.DataFrame): DataFrame containing the data
    group (str): Column name indicating the group (A/B)
    target (str): Column name indicating the target metric

    Returns:
    pd.DataFrame: DataFrame containing the test results
    """

    # Ensure the group and target columns are in the dataframe
    if group not in dataframe.columns or target not in dataframe.columns:
        raise ValueError("Specified group or target column not found in the dataframe")

    # Split data into two groups: A and B
    groupA = dataframe[dataframe[group] == "A"][target]
    groupB = dataframe[dataframe[group] == "B"][target]

    # Check if the groups have sufficient data
    if len(groupA) < 30 or len(groupB) < 30:
        raise ValueError("Each group must contain at least 30 samples for the statistical tests to be valid")

    # Assumption: Normality
    normA = shapiro(groupA)[1] >= 0.05
    normB = shapiro(groupB)[1] >= 0.05
    # H0: Distribution is normal (p >= 0.05)
    # H1: Distribution is not normal (p < 0.05)

    # Perform parametric or non-parametric test based on normality assumption
    if normA and normB:
        # Parametric test (t-test)
        leveneTest = stats.levene(groupA, groupB)[1] >= 0.05
        # H0: Variances are equal (p >= 0.05)
        # H1: Variances are not equal (p < 0.05)

        if leveneTest:
            # Equal variances
            ttest = stats.ttest_ind(groupA, groupB, equal_var=True)
        else:
            # Unequal variances
            ttest = stats.ttest_ind(groupA, groupB, equal_var=False)

        test_type = "Parametric"
        homogeneity = "Yes" if leveneTest else "No"
    else:
        # Non-parametric test (Mann-Whitney U)
        ttest = stats.mannwhitneyu(groupA, groupB)
        test_type = "Non-Parametric"
        homogeneity = "N/A"

    # Extract p-value from the test result
    p_value = ttest.pvalue

    # Determine the result of the hypothesis test
    result = "Statistically Significant" if p_value < 0.05 else "Not Statistically Significant"
    summary = "There is a significant difference between the A/B groups." if result == "Statistically Significant" else "There is no significant difference between the A/B groups."

    # Compile the results into a DataFrame
    result_df = pd.DataFrame({
        "Test Type": [test_type],
        "Homogeneity": [homogeneity],
        "AB Hypothesis": [result],
        "p-value": [p_value],
        "Summary": [summary]
    })

    # Return the result DataFrame
    return result_df

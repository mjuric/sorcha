import pandas as pd
import numpy as np
import logging
import sys


def PPMatchPointingToObservations(padain, pointfildb):
    """
    Merges all relevant columns of each observation from the pointing
    database onto the observations dataframe, then drops all observations which are not
    in one of the requested filters and any duplicate columns.

    Parameters:
    -----------
    padain (Pandas dataframe): dataframe of observations.

    pointfildb (Pandas dataframe): dataframe of the pointing database.

    Returns:
    -----------
    res_df (Pandas dataframe): Merged dataframe of observations with pointing
    database, with all superfluous observations dropped.

    """

    # resdf = pd.merge(padain, pointfildb, left_on="FieldID", right_on="FieldID", how="left")

    # certain columns were added to the pointing db dataframe to help with ephemeris generation.
    # they don't need to be included in the result df, so exclude them from the merge.
    pointing_columns_to_skip = ["JD_TDB", "pixels_begin", "pixels_end"]
    for name in ["visit_vector", "pixels", "r_obs", "v_obs", "r_sun", "v_sun"]:
        pointing_columns_to_skip += [ f"{name}_x", f"{name}_y", f"{name}_z" ]

    if True:
        # columns to pick
        cols = list(set(pointfildb.dtype.names) - set(pointing_columns_to_skip))
        pointfildb = pointfildb[cols]

        import numpy.lib.recfunctions as rfn
        resdf = rfn.join_by("FieldID", padain.to_records(), pointfildb, jointype="inner", usemask=False)
        resdf = pd.DataFrame(resdf)
    else:
        pointfildb = pd.DataFrame(pointfildb)
        resdf = pd.merge(
            padain,
            pointfildb.loc[:, ~pointfildb.columns.isin(pointing_columns_to_skip)],
            left_on="FieldID",
            right_on="FieldID",
            how="left",
        )
    resdf['optFilter'] = resdf['optFilter'].str.decode("utf-8")
    print(resdf.dtypes)

    colour_values = resdf.optFilter.unique()
    colour_values = pd.Series(colour_values).dropna()

    resdf = resdf.dropna(subset=["optFilter"]).reset_index(drop=True)

    chktruemjd = np.isclose(resdf["observationStartMJD_TAI"], resdf["FieldMJD_TAI"])

    if not chktruemjd.all():
        logging.error(
            "ERROR: PPMatchPointingToObservations: mismatch in pointing database and pointing output times."
        )
        sys.exit(
            "ERROR:: PPMatchPointingToObservations: mismatch in pointing database and pointing output times."
        )

    resdf = resdf.drop(columns=["observationStartMJD_TAI", "observationId_"])

    return resdf

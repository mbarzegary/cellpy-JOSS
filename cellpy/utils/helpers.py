import logging
import os
import pathlib
import warnings
from copy import deepcopy

import numpy as np
import pandas as pd
from scipy import stats

import cellpy
from cellpy import prms
from cellpy.parameters.internal_settings import (
    get_headers_journal,
    get_headers_summary,
    get_headers_step_table,
    get_headers_normal,
)
from cellpy.readers.cellreader import CellpyCell
from cellpy.utils.batch import Batch

hdr_summary = get_headers_summary()
hdr_steps = get_headers_step_table()
hdr_normal = get_headers_normal()
hdr_journal = get_headers_journal()


def _make_average_legacy(
    frames,
    keys=None,
    columns=None,
    skip_st_dev_for_equivalent_cycle_index=True,
    key_index_bounds=None,
):
    if key_index_bounds is None:
        key_index_bounds = [1, -2]
    hdr_norm_cycle = hdr_summary["normalized_cycle_index"]
    hdr_cum_charge = hdr_summary["cumulated_charge_capacity"]
    cell_id = ""
    not_a_number = np.NaN
    new_frames = []

    if columns is None:
        columns = frames[0].columns

    if keys is not None:
        if isinstance(keys, (list, tuple)):
            cell_id = list(
                set(
                    [
                        "_".join(
                            k.split("_")[key_index_bounds[0] : key_index_bounds[1]]
                        )
                        for k in keys
                    ]
                )
            )[0]
        elif isinstance(keys, str):
            cell_id = keys
    new_frame = pd.concat(frames, axis=1)
    for col in columns:
        number_of_cols = len(new_frame.columns)
        if (
            col in [hdr_norm_cycle, hdr_cum_charge]
            and skip_st_dev_for_equivalent_cycle_index
        ):
            if number_of_cols > 1:
                avg_frame = (
                    new_frame[col].agg(["mean"], axis=1).rename(columns={"mean": col})
                )
            else:
                avg_frame = new_frame[col].copy()

        else:
            new_col_name_mean = col + "_mean"
            new_col_name_std = col + "_std"

            if number_of_cols > 1:
                avg_frame = (
                    new_frame[col]
                    .agg(["mean", "std"], axis=1)
                    .rename(
                        columns={"mean": new_col_name_mean, "std": new_col_name_std}
                    )
                )
            else:
                avg_frame = pd.DataFrame(
                    data=new_frame[col].values, columns=[new_col_name_mean]
                )
                avg_frame[new_col_name_std] = not_a_number
        new_frames.append(avg_frame)
    final_frame = pd.concat(new_frames, axis=1)

    return final_frame, cell_id


def _make_average(
    frames,
    # keys=None,
    columns=None,
    skip_st_dev_for_equivalent_cycle_index=True,
    # key_index_bounds=None,
):

    # if key_index_bounds is None:
    #     key_index_bounds = [1, -2]
    hdr_norm_cycle = hdr_summary["normalized_cycle_index"]
    hdr_cum_charge = hdr_summary["cumulated_charge_capacity"]
    cell_id = ""
    not_a_number = np.NaN
    new_frames = []

    if columns is None:
        columns = frames[0].columns

    # if keys is not None:
    #     if isinstance(keys, (list, tuple)):
    #         cell_id = list(
    #             set(
    #                 [
    #                     "_".join(
    #                         k.split("_")[key_index_bounds[0]:key_index_bounds[1]]
    #                     )
    #                     for k in keys
    #                 ]
    #             )
    #         )[0]
    #     elif isinstance(keys, str):
    #         cell_id = keys
    new_frame = pd.concat(frames, axis=1)
    normalized_cycle_index_frame = pd.DataFrame(index=new_frame.index)
    for col in columns:
        number_of_cols = len(new_frame.columns)
        if col == hdr_norm_cycle and skip_st_dev_for_equivalent_cycle_index:
            if number_of_cols > 1:
                normalized_cycle_index_frame = (
                    new_frame[col]
                    .agg(["mean"], axis=1)
                    .rename(columns={"mean": "equivalent_cycle"})
                )
            else:
                normalized_cycle_index_frame = new_frame[col].copy()

        else:
            new_col_name_mean = "mean"
            new_col_name_std = "std"

            if number_of_cols > 1:
                avg_frame = (
                    new_frame[col].agg(["mean", "std"], axis=1)
                    # .rename(
                    #     columns={"mean": "value"}
                    # )
                )
            else:
                avg_frame = pd.DataFrame(
                    data=new_frame[col].values, columns=[new_col_name_mean]
                )
                avg_frame[new_col_name_std] = not_a_number

            avg_frame = avg_frame.assign(variable=col)
            new_frames.append(avg_frame)

    if not normalized_cycle_index_frame.empty:
        new_frames = [
            pd.concat([normalized_cycle_index_frame, x], axis=1) for x in new_frames
        ]
    final_frame = pd.concat(new_frames, axis=0)
    cols = final_frame.columns.to_list()
    new_cols = []
    for n in ["variable", "mean", "std"]:
        if n in cols:
            new_cols.append(n)
            cols.remove(n)
    cols.extend(new_cols)
    final_frame = final_frame.reindex(columns=cols)
    # return final_frame, cell_id
    return final_frame

def update_journal_cellpy_data_dir(
    pages, new_path=None, from_path="PureWindowsPath", to_path="Path"
):
    """Update the path in the pages (batch) from one type of OS to another.

    I use this function when I switch from my work PC (windows) to my home
    computer (mac).

    Args:
        pages: the (batch.experiment.)journal.pages object (pandas.DataFrame)
        new_path: the base path (uses prms.Paths.cellpydatadir if not given)
        from_path: type of path to convert from.
        to_path: type of path to convert to.

    Returns:
        journal.pages (pandas.DataFrame)

    """
    # TODO: move this to batch?

    if new_path is None:
        new_path = prms.Paths.cellpydatadir

    from_path = getattr(pathlib, from_path)
    to_path = getattr(pathlib, to_path)

    pages.cellpy_file_names = pages.cellpy_file_names.apply(from_path)
    pages.cellpy_file_names = pages.cellpy_file_names.apply(
        lambda x: to_path(new_path) / x.name
    )
    return pages


def make_new_cell():
    """create an empty CellpyCell object."""
    warnings.warn(
        "make_new_cell is deprecated, use CellpyCell.vacant instead", DeprecationWarning
    )
    new_cell = cellpy.cellreader.CellpyCell(initialize=True)
    return new_cell


def add_normalized_cycle_index(summary, nom_cap, column_name=None):
    """Adds normalized cycles to the summary data frame.

    This functionality is now also implemented as default when creating
    the summary (make_summary). However, it is kept here if you would like to
    redo the normalization, for example if you want to use another nominal
    capacity or if you would like to have more than one normalized cycle index.

    Args:
        summary (pandas.DataFrame): data summary
        nom_cap (float): nominal capacity to use when normalizing.
        column_name (str): name of the new column. Uses the name defined in
            cellpy.parameters.internal_settings as default.

    Returns:
        data object now with normalized cycle index in its summary.
    """
    hdr_norm_cycle = hdr_summary["normalized_cycle_index"]
    hdr_cum_charge = hdr_summary["cumulated_charge_capacity_gravimetric"]

    if column_name is None:
        column_name = hdr_norm_cycle

    summary[column_name] = summary[hdr_cum_charge] / nom_cap
    return summary


def add_c_rate(cell, nom_cap=None, column_name=None):
    """Adds C-rates to the step table data frame.

    This functionality is now also implemented as default when creating
    the step_table (make_step_table). However, it is kept here if you would
    like to recalculate the C-rates, for example if you want to use another
    nominal capacity or if you would like to have more than one column with
    C-rates.

    Args:
        cell (CellpyCell): cell object
        nom_cap (float): nominal capacity to use for estimating C-rates.
            Defaults to the nominal capacity defined in the cell object
            (this is typically set during creation of the CellpyData object
            based on the value given in the parameter file).
        column_name (str): name of the new column. Uses the name defined in
            cellpy.parameters.internal_settings as default.

    Returns:
        data object.
    """

    # now also included in step_table
    # TODO: remove this function
    if column_name is None:
        column_name = hdr_steps["rate_avr"]
    if nom_cap is None:
        nom_cap = cell.data.nom_cap

    spec_conv_factor = cell.get_converter_to_specific()
    cell.data.steps[column_name] = abs(
        round(cell.data.steps.current_avr / (nom_cap / spec_conv_factor), 2)
    )

    return cell


def add_areal_capacity(cell, cell_id, journal):
    """Adds areal capacity to the summary."""

    loading = journal.pages.loc[cell_id, hdr_journal["loading"]]

    cell.data.summary[hdr_summary["areal_charge_capacity"]] = (
        cell.data.summary[hdr_summary["charge_capacity"]] * loading / 1000
    )
    cell.data.summary[hdr_summary["areal_discharge_capacity"]] = (
        cell.data.summary[hdr_summary["discharge_capacity"]] * loading / 1000
    )
    return cell


def _remove_outliers_from_summary(s, filter_vals, freeze_indexes=None):
    if freeze_indexes is not None:
        try:
            filter_vals[freeze_indexes] = True
        except IndexError:
            logging.critical(
                f"Could not freeze - missing cycle indexes {freeze_indexes}"
            )

    return s[filter_vals]


def remove_outliers_from_summary_on_window(
    s, window_size=3, cut=0.1, iterations=1, col_name=None, freeze_indexes=None
):
    """Removes outliers based based on neighbours"""
    if col_name is None:
        col = hdr_summary["charge_capacity"]

    else:
        col = hdr_summary[col_name]

    def fractional_std(x):
        return np.std(x) / np.mean(x)

    for j in range(iterations):
        fractional_deviation_series = (
            s[col]
            .rolling(window=window_size, center=True, min_periods=1)
            .apply(fractional_std)
        )
        filter_vals = fractional_deviation_series < cut
        s = s[filter_vals]

    s = _remove_outliers_from_summary(s, filter_vals, freeze_indexes=freeze_indexes)

    return s


def remove_outliers_from_summary_on_nn_distance(
    s, distance=0.7, filter_cols=None, freeze_indexes=None
):
    """Remove outliers with missing neighbours.

    Args:
        s (pandas.DataFrame): summary frame
        distance (float): cut-off (all cycles that have a closest neighbour further apart this number will be removed)
        filter_cols (list): list of column headers to perform the filtering on (defaults to charge and discharge capacity)
        freeze_indexes (list): list of cycle indexes that should never be removed (defaults to cycle 1)

    Returns:
        filtered summary (pandas.DataFrame)

    Returns:

    """
    if filter_cols is None:
        filter_cols = [
            hdr_summary["charge_capacity"],
            hdr_summary["discharge_capacity"],
        ]

    def neighbour_window(y):
        y = y.values
        if len(y) == 1:
            # only included in case the pandas rolling function changes in the future
            return 0.5
        if len(y) == 2:
            return abs(np.diff(y)) / np.mean(y)
        else:
            return min(abs(y[1] - y[0]), abs(y[1] - y[2])) / min(
                np.mean(y[0:1]), np.mean(y[1:])
            )

    s2 = s[filter_cols].copy()

    r = s2[filter_cols].rolling(3, center=True, min_periods=1).apply(neighbour_window)
    filter_vals = (r < distance).all(axis=1)

    s = _remove_outliers_from_summary(s, filter_vals, freeze_indexes=freeze_indexes)

    return s


def remove_outliers_from_summary_on_zscore(
    s, zscore_limit=4, filter_cols=None, freeze_indexes=None
):
    """Remove outliers based on z-score.

    Args:
        s (pandas.DataFrame): summary frame
        zscore_limit (int): remove outliers outside this z-score limit
        filter_cols (list): list of column headers to perform the filtering on (defaults to charge and discharge capacity)
        freeze_indexes (list): list of cycle indexes that should never be removed (defaults to cycle 1)

    Returns:
        filtered summary (pandas.DataFrame)
    """

    if freeze_indexes is None:
        freeze_indexes = [1]

    if filter_cols is None:
        filter_cols = [
            hdr_summary["charge_capacity"],
            hdr_summary["discharge_capacity"],
        ]

    s2 = s[filter_cols].copy()

    filter_vals = (np.abs(stats.zscore(s2)) < zscore_limit).all(axis=1)

    s = _remove_outliers_from_summary(s, filter_vals, freeze_indexes=freeze_indexes)

    return s


def remove_outliers_from_summary_on_value(
    s, low=0.0, high=7_000, filter_cols=None, freeze_indexes=None
):
    """Remove outliers based highest and lowest allowed value

    Args:
        s (pandas.DataFrame): summary frame
        low (float): low cut-off (all cycles with values below this number will be removed)
        high (float): high cut-off (all cycles with values above this number will be removed)
        filter_cols (list): list of column headers to perform the filtering on (defaults to charge and discharge capacity)
        freeze_indexes (list): list of cycle indexes that should never be removed (defaults to cycle 1)

    Returns:
        filtered summary (pandas.DataFrame)

    Returns:

    """
    if filter_cols is None:
        filter_cols = [
            hdr_summary["charge_capacity"],
            hdr_summary["discharge_capacity"],
        ]

    s2 = s[filter_cols].copy()

    filter_vals = ((s2[filter_cols] > low) & (s2[filter_cols] < high)).all(axis=1)

    s = _remove_outliers_from_summary(s, filter_vals, freeze_indexes=freeze_indexes)

    return s


def remove_outliers_from_summary_on_index(s, indexes=None, remove_last=False):
    """Remove rows with supplied indexes (where the indexes typically are cycle-indexes).

    Args:
        s (pandas.DataFrame): cellpy summary to process
        indexes (list): list of indexes
        remove_last (bool): remove the last point

    Returns:
        pandas.DataFrame
    """
    logging.debug("removing outliers from summary on index")
    if indexes is None:
        indexes = []

    selection = s.index.isin(indexes)
    if remove_last:
        selection[-1] = True
    return s[~selection]


def remove_last_cycles_from_summary(s, last=None):
    """Remove last rows after given cycle number"""

    if last is not None:
        s = s.loc[s.index <= last, :]
    return s


def remove_first_cycles_from_summary(s, first=None):
    """Remove last rows after given cycle number"""

    if first is not None:
        s = s.loc[s.index >= first, :]
    return s


def yank_after(b, last=None, keep_old=False):
    """Cut all cycles after a given cycle index number.

    Args:
        b (batch object): the batch object to perform the cut on.
        last (int or dict {cell_name: last index}): the last cycle index to keep
            (if dict: use individual last indexes for each cell).
        keep_old (bool): keep the original batch object and return a copy instead.

    Returns:
        batch object if keep_old is True, else None
    """

    if keep_old:
        b = deepcopy(b)

    if last is None:
        return b

    for cell_number, cell_label in enumerate(b.experiment.cell_names):
        c = b.experiment.data[cell_label]
        s = c.data.summary
        if isinstance(last, dict):
            last_this_cell = last.get(cell_label, None)
        else:
            last_this_cell = last
        s = remove_last_cycles_from_summary(s, last_this_cell)
        c.data.summary = s
    if keep_old:
        return b


def yank_before(b, first=None, keep_old=False):
    """Cut all cycles before a given cycle index number.

    Args:
        b (batch object): the batch object to perform the cut on.
        first (int or dict {cell_name: first index}): the first cycle index to keep
            (if dict: use individual first indexes for each cell).
        keep_old (bool): keep the original batch object and return a copy instead.

    Returns:
        batch object if keep_old is True, else None
    """

    if keep_old:
        b = deepcopy(b)

    if first is None:
        return b

    for cell_number, cell_label in enumerate(b.experiment.cell_names):
        c = b.experiment.data[cell_label]
        s = c.data.summary
        if isinstance(first, dict):
            first_this_cell = first.get(cell_label, None)
        else:
            first_this_cell = first
        s = remove_first_cycles_from_summary(s, first_this_cell)
        c.data.summary = s
    if keep_old:
        return b


def yank_outliers(
    b: Batch,
    zscore_limit=None,
    low=0.0,
    high=7_000.0,
    filter_cols=None,
    freeze_indexes=None,
    remove_indexes=None,
    remove_last=False,
    iterations=1,
    zscore_multiplyer=1.3,
    distance=None,
    window_size=None,
    window_cut=0.1,
    keep_old=False,
):
    """Remove outliers from a batch object.

    Args:
        b (cellpy.utils.batch object): the batch object to perform filtering one (required).
        zscore_limit (int): will filter based on z-score if given.
        low (float): low cut-off (all cycles with values below this number will be removed)
        high (float): high cut-off (all cycles with values above this number will be removed)
        filter_cols (str): what columns to filter on.
        freeze_indexes (list): indexes (cycles) that should never be removed.
        remove_indexes (dict or list): if dict, look-up on cell label, else a list that will be the same for all
        remove_last (dict or bool): if dict, look-up on cell label.
        iterations (int): repeat z-score filtering if `zscore_limit` is given.
        zscore_multiplyer (int): multiply `zscore_limit` with this number between each z-score filtering
            (should usually be less than 1).
        distance (float): nearest neighbour normalised distance required (typically 0.5).
        window_size (int): number of cycles to include in the window.
        window_cut (float): cut-off.

        keep_old (bool): perform filtering of a copy of the batch object
            (not recommended at the moment since it then loads the full cellpyfile).

    Returns:
        if keep_old: new cellpy.utils.batch object.
        else: dictionary of removed cycles
    """

    if keep_old:
        b = deepcopy(b)

    removed_cycles = dict()

    # remove based on indexes and values
    for cell_number, cell_label in enumerate(b.experiment.cell_names):
        logging.debug(f"yanking {cell_label} ")
        c = b.experiment.data[cell_label]
        s = c.data.summary
        before = set(s.index)
        if remove_indexes is not None:
            logging.debug("removing indexes")
            if isinstance(remove_indexes, dict):
                remove_indexes_this_cell = remove_indexes.get(cell_label, None)
            else:
                remove_indexes_this_cell = remove_indexes

            if isinstance(remove_last, dict):
                remove_last_this_cell = remove_last.get(cell_label, None)
            else:
                remove_last_this_cell = remove_last

            s = remove_outliers_from_summary_on_index(
                s, remove_indexes_this_cell, remove_last_this_cell
            )

        s = remove_outliers_from_summary_on_value(
            s,
            low=low,
            high=high,
            filter_cols=filter_cols,
            freeze_indexes=freeze_indexes,
        )

        if distance is not None:
            s = remove_outliers_from_summary_on_nn_distance(
                s,
                distance=distance,
                filter_cols=filter_cols,
                freeze_indexes=freeze_indexes,
            )
            c.data.summary = s

        if window_size is not None:
            s = remove_outliers_from_summary_on_window(
                s,
                window_size=window_size,
                cut=window_cut,
                iterations=iterations,
                freeze_indexes=freeze_indexes,
            )

        removed = before - set(s.index)
        c.data.summary = s
        if removed:
            removed_cycles[cell_label] = list(removed)

    if zscore_limit is not None:
        logging.info("using the zscore - removed cycles not kept track on")
        for j in range(iterations):
            tot_rows_removed = 0
            for cell_number, cell_label in enumerate(b.experiment.cell_names):
                c = b.experiment.data[cell_label]
                n1 = len(c.data.summary)
                s = remove_outliers_from_summary_on_zscore(
                    c.data.summary,
                    filter_cols=filter_cols,
                    zscore_limit=zscore_limit,
                    freeze_indexes=freeze_indexes,
                )
                # TODO: populate removed_cycles
                rows_removed = n1 - len(s)
                tot_rows_removed += rows_removed
                c.data.summary = s
            if tot_rows_removed == 0:
                break
            zscore_limit *= zscore_multiplyer

    if keep_old:
        return b
    else:
        return removed_cycles


def concatenate_summaries(
    b: Batch,
    max_cycle=None,
    rate=None,
    on="charge",
    columns=None,
    column_names=None,
    normalize_capacity_on=None,
    scale_by=None,
    nom_cap=None,
    normalize_cycles=False,
    group_it=False,
    custom_group_labels=None,
    rate_std=None,
    rate_column=None,
    inverse=False,
    inverted=False,
    key_index_bounds=None,
    melt=False,
    cell_type_split_position="auto",
    mode="collector",
) -> pd.DataFrame:
    """Merge all summaries in a batch into a gigantic summary data frame.

    Args:
        b (cellpy.batch object): the batch with the cells.
        max_cycle (int): drop all cycles above this value.
        rate (float): filter on rate (C-rate)
        on (str or list of str): only select cycles if based on the rate of this step-type (e.g. on="charge").
        columns (list): selected column(s) (using cellpy attribute name) [defaults to "charge_capacity_gravimetric"]
        column_names (list): selected column(s) (using exact column name)
        normalize_capacity_on (list): list of cycle numbers that will be used for setting the basis of the
            normalization (typically the first few cycles after formation)
        scale_by (float or str): scale the normalized data with nominal capacity if "nom_cap",
            or given value (defaults to one).
        nom_cap (float): nominal capacity of the cell
        normalize_cycles (bool): perform a normalization of the cycle numbers (also called equivalent cycle index)
        group_it (bool): if True, average pr group.
        custom_group_labels (dict): dictionary of custom labels (key must be the group number/name).
        rate_std (float): allow for this inaccuracy when selecting cycles based on rate
        rate_column (str): name of the column containing the C-rates.
        inverse (bool): select steps that do not have the given C-rate.
        inverted (bool): select cycles that do not have the steps filtered by given C-rate.
        key_index_bounds (list): used when creating a common label for the cells by splitting and combining from
            key_index_bound[0] to key_index_bound[1].
        melt (bool): return frame as melted (long format).
        cell_type_split_position (int | None | "auto"): list item number for creating a cell type identifier
            after performing a split("_") on the cell names (only valid if melt==True). Set to None to not
            include a cell_type col.
        mode (str): set to something else than "collector" to get the "old" behaviour of this function.

    Returns:
        Multi-index ``pandas.DataFrame``

    Notes:
        The returned ``DataFrame`` has the following structure:

        - top-level columns or second col for melted: cell-names (cell_name)
        - second-level columns or first col for melted: summary headers (summary_headers)
        - row-index or third col for melted: cycle number (cycle_index)
        - cell_type on forth col for melted if cell_type_split_position is given

    """

    if mode != "collector":
        warnings.warn(
            "This helper function will be removed shortly", category=DeprecationWarning
        )

    default_columns = [hdr_summary["charge_capacity_gravimetric"]]
    reserved_cell_label_names = ["FC"]
    hdr_norm_cycle = hdr_summary["normalized_cycle_index"]

    if key_index_bounds is None:
        key_index_bounds = [1, -2]

    if columns is None:
        columns = []

    if column_names is None:
        column_names = []

    if isinstance(columns, str):
        columns = [columns]

    if isinstance(column_names, str):
        column_names = [column_names]

    columns = [hdr_summary[name] for name in columns]
    columns += column_names

    if not columns:
        columns = default_columns

    cell_names_nest = []
    group_nest = []
    output_columns = columns.copy()
    frames = []
    keys = []

    if normalize_cycles:
        if hdr_norm_cycle not in columns:
            output_columns.insert(0, hdr_norm_cycle)

    if normalize_capacity_on is not None:
        normalize_capacity_headers = [
            hdr_summary["normalized_charge_capacity"],
            hdr_summary["normalized_discharge_capacity"],
        ]
        output_columns = [
            col
            for col in output_columns
            if col
            not in [
                hdr_summary["charge_capacity"],
                hdr_summary["discharge_capacity"],
            ]
        ]
        output_columns.extend(normalize_capacity_headers)

    if group_it:
        g = b.pages.groupby("group")
        # this ensures that order is kept and grouping is correct
        # it is therefore ok to assume from now on that all the cells within a list belongs to the same group
        for gno, b_sub in g:
            cell_names_nest.append(list(b_sub.index))
            group_nest.append(gno)
    else:
        cell_names_nest.append(list(b.experiment.cell_names))
        group_nest.append(b.pages.group.to_list())

    for gno, cell_names in zip(group_nest, cell_names_nest):
        frames_sub = []
        keys_sub = []
        for cell_id in cell_names:
            logging.debug(f"Processing [{cell_id}]")
            group = b.pages.loc[cell_id, "group"]
            sub_group = b.pages.loc[cell_id, "sub_group"]
            try:
                c = b.experiment.data[cell_id]
                # print(c.data.summary.columns.sort_values())
            except KeyError as e:
                logging.debug(f"Could not load data for {cell_id}")
                logging.debug(f"{e}")
                raise e

            if not c.empty:
                if max_cycle is not None:
                    c = c.drop_from(max_cycle + 1)
                if normalize_capacity_on is not None:
                    if scale_by == "nom_cap":
                        if nom_cap is None:
                            scale_by = c.data.nom_cap
                        else:
                            scale_by = nom_cap
                    elif scale_by is None:
                        scale_by = 1.0

                    c = add_normalized_capacity(
                        c, norm_cycles=normalize_capacity_on, scale=scale_by
                    )

                if rate is not None:
                    s = select_summary_based_on_rate(
                        c,
                        rate=rate,
                        on=on,
                        rate_std=rate_std,
                        rate_column=rate_column,
                        inverse=inverse,
                        inverted=inverted,
                    )

                else:
                    s = c.data.summary

                if columns is not None:
                    s = s.loc[:, output_columns].copy()

                # somehow using normalized cycles (i.e. equivalent cycles) messes up the order of the index sometimes:
                if normalize_cycles and mode != "collector":
                    s = s.reset_index()

                # add group and subgroup
                if not group_it:
                    s = s.assign(group=group, sub_group=sub_group)

                frames_sub.append(s)
                keys_sub.append(cell_id)

        if group_it:
            if custom_group_labels is not None:
                if isinstance(custom_group_labels, dict):
                    if gno in custom_group_labels:
                        cell_id = custom_group_labels[gno]
                    else:
                        try:
                            cell_id = f"group-{gno:02d}"
                        except Exception:
                            cell_id = f"group-{gno}"
                elif isinstance(custom_group_labels, str):
                    try:
                        cell_id = f"{custom_group_labels}-group-{gno:02d}"
                    except Exception:
                        cell_id = f"{custom_group_labels}-group-{gno}"
            else:
                cell_id = list(
                    set(
                        [
                            "_".join(
                                k.split("_")[key_index_bounds[0]:key_index_bounds[1]]
                            )
                            for k in keys_sub
                        ]
                    )
                )[0]

            if mode == "collector":
                try:
                    s = _make_average(
                        frames_sub,
                        output_columns,
                    )
                except ValueError as e:
                    print("could not make average!")
                    print(e)
                else:
                    frames.append(s)
                    keys.append(cell_id)
            else:
                try:
                    s, cell_id = _make_average_legacy(
                        frames_sub,
                        keys_sub,
                        output_columns,
                        key_index_bounds=key_index_bounds,
                    )
                except ValueError as e:
                    print("could not make average!")
                    print(e)
                else:
                    frames.append(s)
                    keys.append(cell_id)
        else:
            frames.extend(frames_sub)
            keys.extend(keys_sub)

    if frames:
        if len(set(keys)) != len(keys):
            logging.info("Got several columns with same test-name")
            logging.info("Renaming.")
            used_names = []
            new_keys = []
            for name in keys:
                while True:
                    if name in used_names:
                        name += "x"
                    else:
                        break
                new_keys.append(name)
                used_names.append(name)
            keys = new_keys

        old_normalized_cycle_header = hdr_norm_cycle
        cycle_header = "cycle"
        normalized_cycle_header = "equivalent_cycle"
        group_header = "group"
        sub_group_header = "sub_group"
        cell_header = "cell"
        average_header_end = "_mean"
        std_header_end = "_std"

        cdf = pd.concat(
            frames, keys=keys, axis=0, names=[cell_header, cycle_header]
        )
        cdf = cdf.reset_index(drop=False)
        id_vars = [cell_header, cycle_header]
        if not group_it:
            id_vars.extend([group_header, sub_group_header])
        if normalize_cycles:
            cdf = cdf.rename(
                columns={old_normalized_cycle_header: normalized_cycle_header}
            )
        if mode == "collector":
            return cdf

        # if not using through collectors (i.e. using the old methodology instead):
        warnings.warn(
            "mode != collectors: This is the old way of doing things. Use the new way instead!"
        )
        if melt:
            cdf = cdf.reset_index(drop=False).melt(
                id_vars=hdr_summary.cycle_index, value_name="value"
            )
            melted_column_order = [
                "summary_header",
                "cell_name",
                hdr_summary.cycle_index,
                "value",
            ]

            if cell_type_split_position == "auto":
                cell_type_split_position = 1
                _pp = cdf.cell_name.str.split("_", expand=True).values[0]
                for _p in _pp[1:]:
                    if _p not in reserved_cell_label_names:
                        break
                    cell_type_split_position += 1

            if cell_type_split_position is not None:
                cdf = cdf.assign(
                    cell_type=cdf.cell_name.str.split("_", expand=True)[
                        cell_type_split_position
                    ]
                )
                melted_column_order.insert(-2, "cell_type")
            cdf = cdf.reindex(columns=melted_column_order)
        return cdf
    else:
        logging.info("Empty - nothing to concatenate!")
        return pd.DataFrame()


def create_rate_column(df, nom_cap, spec_conv_factor, column="current_avr"):
    """Adds a rate column to the dataframe (steps)."""

    col = abs(round(df[column] / (nom_cap / spec_conv_factor), 2))
    return col


def select_summary_based_on_rate(
    cell,
    rate=None,
    on=None,
    rate_std=None,
    rate_column=None,
    inverse=False,
    inverted=False,
    fix_index=True,
):
    """Select only cycles charged or discharged with a given rate.

    Parameters:
        cell (cellpy.CellpyCell)
        rate (float): the rate to filter on. Remark that it should be given
            as a float, i.e. you will have to convert from C-rate to
            the actual numeric value. For example, use rate=0.05 if you want
            to filter on cycles that has a C/20 rate.
        on (str): only select cycles if based on the rate of this step-type (e.g. on="charge").
        rate_std (float): allow for this inaccuracy in C-rate when selecting cycles
        rate_column (str): column header name of the rate column,
        inverse (bool): select steps that do not have the given C-rate.
        inverted (bool): select cycles that do not have the steps filtered by given C-rate.
        fix_index (bool): automatically set cycle indexes as the index for the summary dataframe if not already set.

    Returns:
        filtered summary (Pandas.DataFrame).
    """
    if on is None:
        on = ["charge"]
    else:
        if not isinstance(on, (list, tuple)):
            on = [on]

    if rate_column is None:
        rate_column = hdr_steps["rate_avr"]

    if on:
        on_column = hdr_steps["type"]

    if rate is None:
        rate = 0.05

    if rate_std is None:
        rate_std = 0.1 * rate

    cycle_number_header = hdr_summary["cycle_index"]

    step_table = cell.data.steps
    summary = cell.data.summary

    if summary.index.name != cycle_number_header:
        warnings.warn(
            f"{cycle_number_header} not set as index\n"
            f"Current index :: {summary.index}\n"
        )

        if fix_index:
            summary.set_index(cycle_number_header, drop=True, inplace=True)
        else:
            print(f"{cycle_number_header} not set as index!")
            print(f"Please, set the cycle index header as index before proceeding!")
            return summary

    if on:
        cycles_mask = (
            (step_table[rate_column] < (rate + rate_std))
            & (step_table[rate_column] > (rate - rate_std))
            & (step_table[on_column].isin(on))
        )
    else:
        cycles_mask = (step_table[rate_column] < (rate + rate_std)) & (
            step_table[rate_column] > (rate - rate_std)
        )

    if inverse:
        cycles_mask = ~cycles_mask

    filtered_step_table = step_table[cycles_mask]
    filtered_cycles = filtered_step_table[hdr_steps.cycle].unique()

    if inverted:
        filtered_index = summary.index.difference(filtered_cycles)
    else:
        filtered_index = summary.index.intersection(filtered_cycles)

    if filtered_index.empty:
        warnings.warn("EMPTY")

    return summary.loc[filtered_index, :]


def add_normalized_capacity(
    cell, norm_cycles=None, individual_normalization=False, scale=1.0
):
    """Add normalized capacity to the summary.

    Args:
        cell (CellpyCell): cell to add normalized capacity to.
        norm_cycles (list of ints): the cycles that will be used to find
            the normalization factor from (averaging their capacity)
        individual_normalization (bool): find normalization factor for both
            the charge and the discharge if true, else use normalization factor
            from charge on both charge and discharge.
        scale (float): scale of normalization (default is 1.0).

    Returns:
        cell (CellpyData) with added normalization capacity columns in
        the summary.
    """

    if norm_cycles is None:
        norm_cycles = [1, 2, 3, 4, 5]

    col_name_charge = hdr_summary["charge_capacity"]
    col_name_discharge = hdr_summary["discharge_capacity"]
    col_name_norm_charge = hdr_summary["normalized_charge_capacity"]
    col_name_norm_discharge = hdr_summary["normalized_discharge_capacity"]

    try:
        norm_val_charge = cell.data.summary.loc[norm_cycles, col_name_charge].mean()
    except KeyError as e:
        print(f"Oh no! Are you sure these cycle indexes exist?")
        print(f"  norm_cycles: {norm_cycles}")
        print(f"  cycle indexes: {list(cell.data.summary.index)}")
        raise KeyError from e
    if individual_normalization:
        norm_val_discharge = cell.data.summary.loc[
            norm_cycles, col_name_discharge
        ].mean()
    else:
        norm_val_discharge = norm_val_charge

    for col_name, norm_col_name, norm_value in zip(
        [col_name_charge, col_name_discharge],
        [col_name_norm_charge, col_name_norm_discharge],
        [norm_val_charge, norm_val_discharge],
    ):
        cell.data.summary[norm_col_name] = (
            scale * cell.data.summary[col_name] / norm_value
        )

    return cell


def load_and_save_resfile(filename, outfile=None, outdir=None, mass=1.00):
    """Load a raw data file and save it as cellpy-file.

    Args:
        mass (float): active material mass [mg].
        outdir (path): optional, path to directory for saving the hdf5-file.
        outfile (str): optional, name of hdf5-file.
        filename (str): name of the resfile.

    Returns:
        out_file_name (str): name of saved file.
    """
    warnings.warn(DeprecationWarning("This option will be removed in v.0.4.0"))
    d = CellpyCell()

    if not outdir:
        outdir = prms.Paths.cellpydatadir

    if not outfile:
        outfile = os.path.basename(filename).split(".")[0] + ".h5"
        outfile = os.path.join(outdir, outfile)

    print("filename:", filename)
    print("outfile:", outfile)
    print("outdir:", outdir)
    print("mass:", mass, "mg")

    d.from_raw(filename)
    d.set_mass(mass)
    d.make_step_table()
    d.make_summary()
    d.save(filename=outfile)
    d.to_csv(datadir=outdir, cycles=True, raw=True, summary=True)
    return outfile

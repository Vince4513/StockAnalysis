# -*- coding: utf-8 -*- #
"""
Company class
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from datetime import datetime

# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)

# ===========================================================================
# Company Class
# ===========================================================================


class Company:
    """Represent a company"""

    def __init__(self, **kwargs) -> None:
        # metadata
        self.name : str | None = kwargs.get('name', None)
        self.last_update: datetime | None = kwargs.get('last_update', datetime.now())

        # Ticket info
        self.actual_share_price  : float | None = kwargs.get('actual_share_price', None)
        self.sales               : float | None = kwargs.get('sales', None)
        self.nb_shares_issued    : int | None = kwargs.get('nb_shares_issued', None)

        # Balance sheet information
        self.current_assets      : float | None = kwargs.get('current_assets', None)
        self.current_liabilities : float | None = kwargs.get('current_liabilities', None)
        self.financial_debts     : float | None = kwargs.get('financial_debts', None)
        self.equity              : float | None = kwargs.get('equity', None)
        self.intangible_assets   : float | None = kwargs.get('intangible_assets', None)

        # Arrays
        self.net_income            : pd.DataFrame | None = kwargs.get('net_income', None)
        self.dividends             : pd.DataFrame | None = kwargs.get('dividends', None)
        self.net_earning_per_share : pd.DataFrame | None = kwargs.get('net_earning_per_share', None)
    # End def __init__

    # ===========================================================================
    # Magic Methods
    # ===========================================================================

    def __str__(self):
        return f"Company({self.name}: {self.last_update} - {self.actual_share_price:.2f}€)"

    # ===========================================================================
    # Accessors
    # ===========================================================================

    # @property
    # def name(self) -> np.ndarray:
    #     return self.name
    # # End def name

    # ===========================================================================
    # Public Methods
    # ===========================================================================



    # ===========================================================================
    # Private Methods
    # ===========================================================================
# End class Company
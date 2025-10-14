# gl_core/services/closing.py
import logging
from decimal import Decimal

from gl_core.models import Ledger, JournalEntry, JournalLine
from gl_core.models.account import AccountType

logger = logging.getLogger(__name__)

def close_year(ledger: Ledger, year: int) -> JournalEntry:
    logger.info(f"Starting year-end closing for year {year}")
    balances = ledger.get_trial_balance()
    closing_lines = []

    total_revenue = Decimal(0)
    total_expense = Decimal(0)

    for acc_code, balance in balances.items():
        acc = ledger.chart.get(acc_code)
        if acc.account_type == AccountType.REVENUE:
            net_amount = balance["credit"] - balance["debit"]
            if net_amount > 0:
                total_revenue += net_amount
                closing_lines.append(JournalLine(acc_code, debit=net_amount))
                logger.debug(f"Closing revenue account {acc_code}: {net_amount}")

        elif acc.account_type == AccountType.EXPENSE:
            net_amount = balance["debit"] - balance["credit"]
            if net_amount > 0:
                total_expense += net_amount
                closing_lines.append(JournalLine(acc_code, credit=net_amount))
                logger.debug(f"Closing expense account {acc_code}: {net_amount}")

    profit = total_revenue - total_expense
    if profit > 0:
        closing_lines.append(JournalLine("421", credit=profit))
        logger.info(f"Profit {profit} transferred to account 421")
    elif profit < 0:
        closing_lines.append(JournalLine("421", debit=abs(profit)))
        logger.info(f"Loss {abs(profit)} transferred to account 421")

    if not closing_lines:
        logger.warning(f"No revenue or expense accounts to close for year {year}")
        raise ValueError(f"No revenue or expense accounts to close for year {year}")

    logger.info(f"Closing entry has {len(closing_lines)} lines")

    closing_entry = JournalEntry(
        date=f"{year}-12-31",
        lines=closing_lines,
        description=f"Kết chuyển cuối năm {year}"
    )

    ledger.post(closing_entry)
    logger.info(f"Year-end closing completed for year {year}")
    return closing_entry
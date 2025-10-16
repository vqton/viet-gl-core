# gl_core/services/closing.py
import logging
from decimal import Decimal

from gl_core.models import Ledger, JournalEntry, JournalLine
from gl_core.models.account import AccountType

logger = logging.getLogger(__name__)

def _normalize_account_type(acc):
    """
    Ensure we can compare account type whether acc.account_type is enum or string.
    Return one of AccountType enum members or None.
    """
    acctype = getattr(acc, "account_type", None) or getattr(acc, "type", None) or None
    if acctype is None:
        return None
    # If already enum-like (AccountType), return it
    try:
        if isinstance(acctype, AccountType):
            return acctype
    except Exception:
        pass
    # If string, try to map
    if isinstance(acctype, str):
        normalized = acctype.strip().lower()
        if normalized in ("revenue", "income", "revenues"):
            return AccountType.REVENUE
        if normalized in ("expense", "expenses"):
            return AccountType.EXPENSE
        if normalized in ("asset",):
            return AccountType.ASSET
        if normalized in ("liability",):
            return AccountType.LIABILITY
        if normalized in ("equity", "owner's equity", "equity"):
            return AccountType.EQUITY
    return None

def close_year(ledger: Ledger, year: int) -> JournalEntry:
    """
    Year-end closing flow (TT133):
    1) Close revenue accounts -> create debit to revenue accounts, credit to 911
    2) Close expense accounts -> create credit to expense accounts, debit to 911
    3) After above, 911 will have net credit (profit) or net debit (loss)
    4) Transfer net 911 to 421 (Lợi nhuận sau thuế chưa phân phối) accordingly
    """
    logger.info(f"Starting year-end closing for year {year}")
    balances = ledger.get_trial_balance()
    closing_lines = []

    total_revenue = Decimal(0)
    total_expense = Decimal(0)

    # Step 1 & 2: close revenue and expense into 911
    for acc_code, balance in balances.items():
        acc = ledger.chart.get(acc_code)
        acc_type = _normalize_account_type(acc)
        if acc_type == AccountType.REVENUE:
            net_amount = Decimal(balance.get("credit", 0)) - Decimal(balance.get("debit", 0))
            if net_amount > 0:
                total_revenue += net_amount
                # Debit revenue account to zero it, Credit 911
                closing_lines.append(JournalLine(acc_code, debit=net_amount))
                closing_lines.append(JournalLine("911", credit=net_amount))
                logger.debug(f"Closing revenue account {acc_code}: {net_amount}")

        elif acc_type == AccountType.EXPENSE:
            net_amount = Decimal(balance.get("debit", 0)) - Decimal(balance.get("credit", 0))
            if net_amount > 0:
                total_expense += net_amount
                # Credit expense account to zero it, Debit 911
                closing_lines.append(JournalLine(acc_code, credit=net_amount))
                closing_lines.append(JournalLine("911", debit=net_amount))
                logger.debug(f"Closing expense account {acc_code}: {net_amount}")

    # After closing, compute net in 911
    net_911 = total_revenue - total_expense  # positive => credit balance in 911 (profit)

    if net_911 > 0:
        # 911 has net credit = profit -> debit 911, credit 421
        closing_lines.append(JournalLine("911", debit=net_911))
        closing_lines.append(JournalLine("421", credit=net_911))
        logger.info(f"Profit {net_911} transferred: 911 -> 421")
    elif net_911 < 0:
        # 911 has net debit = loss -> credit 911, debit 421 (or use loss account if desired)
        loss = abs(net_911)
        closing_lines.append(JournalLine("911", credit=loss))
        closing_lines.append(JournalLine("421", debit=loss))
        logger.info(f"Loss {loss} transferred: 911 -> 421")

    if not closing_lines:
        logger.warning(f"No revenue or expense accounts to close for year {year}")
        raise ValueError(f"No revenue or expense accounts to close for year {year}")

    logger.info(f"Closing entry has {len(closing_lines)} lines")

    closing_entry = JournalEntry(
        date=f"{year}-12-31",
        lines=closing_lines,
        description=f"Kết chuyển cuối năm {year} (TT133)"
    )

    ledger.post(closing_entry)
    logger.info(f"Year-end closing completed for year {year}")
    return closing_entry

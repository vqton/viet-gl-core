from decimal import Decimal


def allocate_promotion_revenue(
    total_invoice_value: Decimal,
    main_items_fair_value: Decimal,
    promo_items_fair_value: Decimal
) -> dict:
    """
    Phân bổ doanh thu cho hàng chính & hàng khuyến mãi.
    Theo hướng dẫn tại TK 511 TT 99.
    """
    total_fair = main_items_fair_value + promo_items_fair_value
    if total_fair == 0:
        return {"main": total_invoice_value, "promo": Decimal('0')}
    
    main_ratio = main_items_fair_value / total_fair
    return {
        "main": total_invoice_value * main_ratio,
        "promo": total_invoice_value * (1 - main_ratio)
    }
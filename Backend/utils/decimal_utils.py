from decimal import Decimal, ROUND_HALF_UP


ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")
THOUSAND = Decimal("1000")
CENT = Decimal("0.01")


def to_decimal(value) -> Decimal:
    """
    Convierte valores numéricos a Decimal sin heredar
    los errores binarios de los float.
    """
    if isinstance(value, Decimal):
        return value

    if value is None:
        return ZERO

    return Decimal(str(value))


def money(value: Decimal) -> Decimal:
    """
    Redondeo monetario a dos decimales.
    Usar únicamente en puntos de presentación o persistencia
    donde realmente se requiera redondear.
    """
    return to_decimal(value).quantize(
        CENT,
        rounding=ROUND_HALF_UP
    )


def thousands(value: Decimal) -> Decimal:
    """
    Redondeo al millar más cercano.
    Conserva la regla comercial que tenías en el motor.
    """
    return (
        to_decimal(value) / THOUSAND
    ).quantize(
        ZERO,
        rounding=ROUND_HALF_UP
    ) * THOUSAND
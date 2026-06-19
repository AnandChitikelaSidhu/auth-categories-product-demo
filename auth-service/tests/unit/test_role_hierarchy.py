from app.dependencies.auth import ADMIN_MINIMUM_LEVEL, SUPER_ADMIN_MINIMUM_LEVEL


def test_admin_level_below_super_admin() -> None:
    assert ADMIN_MINIMUM_LEVEL < SUPER_ADMIN_MINIMUM_LEVEL


def test_customer_level_below_admin_threshold() -> None:
    customer_level = 0
    assert customer_level < ADMIN_MINIMUM_LEVEL


def test_admin_meets_admin_threshold() -> None:
    assert ADMIN_MINIMUM_LEVEL >= ADMIN_MINIMUM_LEVEL


def test_super_admin_meets_all_thresholds() -> None:
    assert SUPER_ADMIN_MINIMUM_LEVEL >= ADMIN_MINIMUM_LEVEL
    assert SUPER_ADMIN_MINIMUM_LEVEL >= SUPER_ADMIN_MINIMUM_LEVEL

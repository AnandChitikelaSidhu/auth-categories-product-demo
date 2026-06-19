from app.dependencies.auth import ROLE_HIERARCHY
from app.models.user import UserRole


def test_role_hierarchy_orders_customer_below_admin() -> None:
    assert ROLE_HIERARCHY[UserRole.CUSTOMER] < ROLE_HIERARCHY[UserRole.ADMIN]


def test_role_hierarchy_orders_admin_below_super_admin() -> None:
    assert ROLE_HIERARCHY[UserRole.ADMIN] < ROLE_HIERARCHY[UserRole.SUPER_ADMIN]


def test_customer_cannot_meet_admin_threshold() -> None:
    assert ROLE_HIERARCHY[UserRole.CUSTOMER] < ROLE_HIERARCHY[UserRole.ADMIN]


def test_admin_meets_admin_threshold() -> None:
    assert ROLE_HIERARCHY[UserRole.ADMIN] >= ROLE_HIERARCHY[UserRole.ADMIN]


def test_super_admin_meets_all_thresholds() -> None:
    assert ROLE_HIERARCHY[UserRole.SUPER_ADMIN] >= ROLE_HIERARCHY[UserRole.ADMIN]
    assert ROLE_HIERARCHY[UserRole.SUPER_ADMIN] >= ROLE_HIERARCHY[UserRole.SUPER_ADMIN]

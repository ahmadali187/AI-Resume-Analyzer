from models.user import User
from extensions import db


def test_user_registration_role_is_user(client, app):
    """Test that registration strictly sets role='USER'."""
    res = client.post("/auth/register", data={
        "name": "Standard User",
        "email": "user@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="user@example.com").first()
        assert user is not None
        assert user.role == User.ROLE_USER
        assert user.is_super_admin() is False
        assert user.is_admin_user() is False


def test_rbac_admin_route_protection(client, app):
    """Test that regular users are blocked with 403 from admin routes."""
    # Register regular user
    client.post("/auth/register", data={
        "name": "Regular User",
        "email": "regular@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }, follow_redirects=True)

    # Login as regular user
    client.post("/auth/login", data={
        "email": "regular@example.com",
        "password": "password123"
    }, follow_redirects=True)

    # Attempt to access admin panel -> 403 Forbidden
    res = client.get("/admin/")
    assert res.status_code == 403


def test_superadmin_vs_admin_privileges(client, app):
    """Test privilege separation between ADMIN and SUPER_ADMIN."""
    with app.app_context():
        admin = User(name="Admin User", email="admin@example.com", role=User.ROLE_ADMIN, is_active=True)
        admin.set_password("adminpass")

        superadmin = User(name="Super Admin", email="super@example.com", role=User.ROLE_SUPER_ADMIN, is_active=True)
        superadmin.set_password("superpass")

        db.session.add_all([admin, superadmin])
        db.session.commit()

    # Login as ADMIN
    client.post("/auth/login", data={"email": "admin@example.com", "password": "adminpass"}, follow_redirects=True)

    # Admin CAN access /admin/ dashboard
    res_dash = client.get("/admin/")
    assert res_dash.status_code == 200

    # Admin CANNOT access /admin/logs -> 403 Forbidden
    res_logs = client.get("/admin/logs")
    assert res_logs.status_code == 403

    # Admin CANNOT access /admin/settings -> 403 Forbidden
    res_settings = client.get("/admin/settings")
    assert res_settings.status_code == 403

    client.get("/auth/logout")

    # Login as SUPER_ADMIN
    client.post("/auth/login", data={"email": "super@example.com", "password": "superpass"}, follow_redirects=True)

    # Super Admin CAN access /admin/logs & /admin/settings
    res_super_logs = client.get("/admin/logs")
    assert res_super_logs.status_code == 200

    res_super_set = client.get("/admin/settings")
    assert res_super_set.status_code == 200

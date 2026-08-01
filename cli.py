import click
from flask.cli import AppGroup
from extensions import db
from models.user import User
from models.admin_log import AdminLog

admin_cli = AppGroup("admin", help="Admin management CLI commands.")


@admin_cli.command("create-superadmin")
@click.option("--name", prompt="Super Admin Full Name", help="Name of Super Admin")
@click.option("--email", prompt="Super Admin Email", help="Email of Super Admin")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password")
def create_superadmin(name, email, password):
    """CLI command to safely create the system SUPER_ADMIN account."""
    email_clean = email.strip().lower()
    name_clean = name.strip()

    existing = User.query.filter_by(email=email_clean).first()
    if existing:
        if existing.role == User.ROLE_SUPER_ADMIN:
            click.echo(click.style(f"User '{email_clean}' is already a SUPER_ADMIN.", fg="yellow"))
            return
        existing.role = User.ROLE_SUPER_ADMIN
        existing.is_active = True
        existing.set_password(password)
        db.session.commit()
        click.echo(click.style(f"Updated existing user '{email_clean}' to SUPER_ADMIN.", fg="green"))
        AdminLog.log("CREATE_SUPERADMIN_CLI", user_id=existing.id, details=f"Promoted {email_clean} via CLI")
        return

    super_admin = User(
        name=name_clean,
        email=email_clean,
        role=User.ROLE_SUPER_ADMIN,
        is_active=True
    )
    super_admin.set_password(password)
    db.session.add(super_admin)
    db.session.commit()

    click.echo(click.style(f"SUPER_ADMIN '{email_clean}' created successfully!", fg="green"))
    AdminLog.log("CREATE_SUPERADMIN_CLI", user_id=super_admin.id, details=f"Created SuperAdmin {email_clean} via CLI")


def init_cli(app):
    """Registers CLI commands with the Flask application."""
    app.cli.add_command(admin_cli)

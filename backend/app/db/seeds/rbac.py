import csv
from pathlib import Path

from sqlalchemy import select

from backend.app.db.session import SessionLocal
from backend.app.models.permission import Permission
from backend.app.models.role import Role


CSV_PATH = Path(__file__).resolve().parents[4] / "Data" / "rbac_policy.csv"


def seed_rbac() -> None:
    with SessionLocal() as db:
        with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                role_name = row["role"].strip()
                intent = row["intent"].strip()
                allowed = row["allowed"].strip().lower() == "true"
                tool = row["tool"].strip()
                authorization_source = row["authorization_source"].strip()

                role = db.scalar(
                    select(Role).where(Role.name == role_name)
                )

                if role is None:
                    role = Role(name=role_name)
                    db.add(role)
                    db.flush()

                permission = db.scalar(
                    select(Permission).where(
                        Permission.role_id == role.id,
                        Permission.intent == intent,
                    )
                )

                if permission is None:
                    permission = Permission(
                        role_id=role.id,
                        intent=intent,
                        allowed=allowed,
                        tool=tool,
                        authorization_source=authorization_source,
                    )
                    db.add(permission)
                else:
                    permission.allowed = allowed
                    permission.tool = tool
                    permission.authorization_source = authorization_source

            db.commit()

        print("RBAC seed completed successfully.")


if __name__ == "__main__":
    seed_rbac()
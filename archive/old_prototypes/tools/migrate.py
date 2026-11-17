from src.app.infrastructure.database.migrator import migrate

if __name__ == "__main__":
    done = migrate()
    print("Applied:", done if done else "nothing (already up to date)")

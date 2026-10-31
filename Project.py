"""A small JSON-backed command-line inventory manager."""

import json
import math
import os
import tempfile
from pathlib import Path


INVENTORY_FILE = Path(__file__).with_name("inventory.json")
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "pass"
USER_USERNAME = "user"
USER_PASSWORD = "pass"


class InventoryError(Exception):
    """Raised when the saved inventory cannot be read or written safely."""


def load_inventory():
    """Read and validate inventory data from disk."""
    if not INVENTORY_FILE.exists():
        return {}

    try:
        with INVENTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise InventoryError(f"Could not read {INVENTORY_FILE.name}: {error}") from error

    if not isinstance(data, dict):
        raise InventoryError("Inventory data must be a JSON object.")

    for item_id, item in data.items():
        if (
            not isinstance(item_id, str)
            or not isinstance(item, dict)
            or not isinstance(item.get("name"), str)
            or not isinstance(item.get("quantity"), int)
            or isinstance(item.get("quantity"), bool)
            or item["quantity"] < 0
            or not isinstance(item.get("price"), (int, float))
            or isinstance(item.get("price"), bool)
            or not math.isfinite(item["price"])
            or item["price"] < 0
        ):
            raise InventoryError(f"Invalid saved data for item ID '{item_id}'.")

    return data


def save_inventory(inventory):
    """Write inventory atomically so an interrupted save keeps the old file."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=INVENTORY_FILE.parent,
            delete=False, suffix=".tmp"
        ) as file:
            temp_path = Path(file.name)
            json.dump(inventory, file, indent=2, ensure_ascii=False)
            file.write("\n")
        os.replace(temp_path, INVENTORY_FILE)
    except OSError as error:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        raise InventoryError(f"Could not save {INVENTORY_FILE.name}: {error}") from error


def prompt_nonnegative_int(message):
    while True:
        try:
            value = int(input(message))
            if value < 0:
                print("Enter zero or a positive whole number.")
                continue
            return value
        except ValueError:
            print("Enter a valid whole number.")


def prompt_nonnegative_float(message):
    while True:
        try:
            value = float(input(message))
            if not math.isfinite(value) or value < 0:
                print("Enter a finite, non-negative number.")
                continue
            return value
        except ValueError:
            print("Enter a valid number.")


def add_item(inventory):
    item_id = input("Enter item ID: ").strip()
    if not item_id:
        print("Item ID cannot be empty.")
        return
    if item_id in inventory:
        print("That item ID already exists.")
        return

    name = input("Enter name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    inventory[item_id] = {
        "name": name,
        "quantity": prompt_nonnegative_int("Enter quantity: "),
        "price": prompt_nonnegative_float("Enter price: "),
    }
    save_inventory(inventory)
    print("Item added!")


def update_item(inventory):
    item_id = input("Enter ID to update: ").strip()
    if item_id not in inventory:
        print("Item not found.")
        return

    inventory[item_id]["quantity"] = prompt_nonnegative_int("Enter new quantity: ")
    inventory[item_id]["price"] = prompt_nonnegative_float("Enter new price: ")
    save_inventory(inventory)
    print("Item updated!")


def remove_items(inventory):
    item_ids = input("Enter one or more IDs to remove (comma separated): ").split(",")
    removed = []
    for item_id in dict.fromkeys(value.strip() for value in item_ids if value.strip()):
        if item_id in inventory:
            del inventory[item_id]
            removed.append(item_id)
            print(f"Removed: {item_id}")
        else:
            print(f"Item not found: {item_id}")

    if removed:
        save_inventory(inventory)
    else:
        print("No items removed.")


def search_item(inventory):
    item_id = input("Enter ID to search: ").strip()
    item = inventory.get(item_id)
    if item is None:
        print("Item not found.")
        return

    print("\n--- Item Found ---")
    print(f"ID:       {item_id}")
    print(f"Name:     {item['name']}")
    print(f"Quantity: {item['quantity']}")
    print(f"Price:    {item['price']:.2f}")


def list_inventory(inventory):
    if not inventory:
        print("Inventory is empty.")
        return

    print("\n--- INVENTORY LIST ---")
    print(f"{'ID':<14} {'Name':<24} {'Quantity':>10} {'Price':>12}")
    print("-" * 64)
    for item_id, item in sorted(inventory.items()):
        print(
            f"{item_id:<14} {item['name']:<24} "
            f"{item['quantity']:>10} {item['price']:>12.2f}"
        )
    print("-" * 64)


def admin_menu(inventory):
    actions = {"1": add_item, "2": update_item, "3": remove_items,
               "4": search_item, "5": list_inventory}
    while True:
        print("\n=== ADMIN MENU ===")
        print("1. Add item\n2. Update item\n3. Remove item(s)")
        print("4. Search item\n5. List inventory\n6. Logout")
        choice = input("Enter your choice: ").strip()
        if choice == "6":
            print("Logging out (Admin)...")
            return
        action = actions.get(choice)
        if action:
            action(inventory)
        else:
            print("Invalid choice.")


def user_menu(inventory):
    while True:
        print("\n=== USER MENU ===")
        print("1. Search item\n2. List inventory\n3. Logout")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            search_item(inventory)
        elif choice == "2":
            list_inventory(inventory)
        elif choice == "3":
            print("Logging out (User)...")
            return
        else:
            print("Invalid choice.")


def login():
    username = input("Enter username: ").strip()
    password = input("Enter password: ")
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return "admin"
    if username == USER_USERNAME and password == USER_PASSWORD:
        return "user"
    print("Invalid username or password.")
    return None


def main():
    try:
        inventory = load_inventory()
        while True:
            print("\n=== LOGIN ===")
            role = login()
            if role == "admin":
                admin_menu(inventory)
            elif role == "user":
                user_menu(inventory)

            again = input("Press Enter to log in again, or type 'exit' to quit: ")
            if again.strip().lower() == "exit":
                print("Exiting program...")
                return
    except (InventoryError, EOFError, KeyboardInterrupt) as error:
        if isinstance(error, InventoryError):
            print(f"Error: {error}")
        else:
            print("\nProgram closed.")


if __name__ == "__main__":
    main()

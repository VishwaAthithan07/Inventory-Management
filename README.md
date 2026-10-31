# Inventory Manager

This is a small command-line inventory manager I made while learning Python. It lets you keep track of items and saves them to a JSON file, so your inventory is still there the next time you run the program.

## What it can do

- Add, update, remove, search for, and list items
- Check that item details are entered in the right format
- Give admins editing options and users read-only access
- Save your inventory in `inventory.json`

## Getting started

You’ll need Python 3.8 or newer. There are no extra packages to install.

Open a terminal in the project folder and run:

```bash
python inventory_manager.py
```

Use one of these demo logins:

|  Role  | Username | Password |
| ------ | -------- | -------- |
|  Admin |  `admin` |  `pass`  |
|  User  |  `user`  |  `pass`  |

The admin can make changes to the inventory. The user can search and view items.

## Your inventory file

The program creates `inventory.json` the first time you save an item. Keep that file if you want to keep your inventory. Delete it if you want to start over.

## A quick note about the logins

These are simple demo accounts for practicing. The passwords are written directly in the code, so don’t use them for anything sensitive or put this version online as a real inventory system.

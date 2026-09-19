"""Legacy retail customer-service application used for modernization practice.

Business problem: process product-return requests, calculate refunds, create
support cases, notify customers, and produce a daily operations report.

This training sample intentionally reflects accumulated legacy practices. It
must not be treated as production-ready code or connected to real customer data.
"""

import csv
import json
import sqlite3
import time
from datetime import datetime, timedelta


DATABASE_NAME = "customer_service.db"
LOG_FILE = "customer_service.log"
SUPPORT_EMAIL = "support@example.invalid"
DATABASE = None
CUSTOMER_CACHE = {}
DAILY_TOTALS = {"cases": 0, "refunds": 0, "refund_amount": 0.0}


def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = timestamp + " | " + str(message)
    print(line)
    with open(LOG_FILE, "a") as log_file:
        log_file.write(line + "\n")


def connect_database():
    global DATABASE
    if DATABASE is None:
        DATABASE = sqlite3.connect(DATABASE_NAME)
    return DATABASE


def find_customer(email):
    if email in CUSTOMER_CACHE:
        return CUSTOMER_CACHE[email]

    database = connect_database()
    query = (
        "SELECT id, name, email, loyalty_level, country, account_status "
        "FROM customers WHERE email = '" + email + "'"
    )
    row = database.execute(query).fetchone()
    if row is None:
        return None

    customer = {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "loyalty_level": row[3],
        "country": row[4],
        "account_status": row[5],
    }
    CUSTOMER_CACHE[email] = customer
    return customer


def load_order(order_number):
    database = connect_database()
    order = database.execute(
        "SELECT id, customer_id, order_number, order_date, status, "
        "shipping_amount, tax_amount FROM orders WHERE order_number = ?",
        (order_number,),
    ).fetchone()

    if order is None:
        return None

    items = database.execute(
        "SELECT id, sku, description, quantity, unit_price, returned_quantity "
        "FROM order_items WHERE order_id = ?",
        (order[0],),
    ).fetchall()

    return {
        "id": order[0],
        "customer_id": order[1],
        "order_number": order[2],
        "order_date": order[3],
        "status": order[4],
        "shipping_amount": order[5],
        "tax_amount": order[6],
        "items": items,
    }


def validate_return(customer, order, requested_items, reason):
    errors = []

    if customer is None:
        errors.append("Customer was not found")
    elif customer["account_status"] == "BLOCKED":
        errors.append("Customer account is blocked")

    if order is None:
        errors.append("Order was not found")
        return errors

    if customer is not None and order["customer_id"] != customer["id"]:
        errors.append("Order does not belong to this customer")

    order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
    return_window = 30
    if customer is not None and customer["loyalty_level"] == "GOLD":
        return_window = 60

    if datetime.now() > order_date + timedelta(days=return_window):
        errors.append("Return window has expired")

    if order["status"] not in ["DELIVERED", "PARTIALLY_RETURNED"]:
        errors.append("Order status does not permit a return")

    if reason == "":
        errors.append("A return reason is required")

    for requested in requested_items:
        matching_item = None
        for item in order["items"]:
            if item[1] == requested["sku"]:
                matching_item = item

        if matching_item is None:
            errors.append("Unknown SKU: " + requested["sku"])
        elif requested["quantity"] <= 0:
            errors.append("Quantity must be positive for " + requested["sku"])
        elif requested["quantity"] + matching_item[5] > matching_item[3]:
            errors.append("Return quantity is too high for " + requested["sku"])

    return errors


def calculate_refund(customer, order, requested_items, reason):
    subtotal = 0.0

    for requested in requested_items:
        for item in order["items"]:
            if item[1] == requested["sku"]:
                subtotal += float(item[4]) * requested["quantity"]

    restocking_fee = 0.0
    if reason in ["changed_mind", "ordered_wrong_item"]:
        restocking_fee = subtotal * 0.15

    if customer["loyalty_level"] == "GOLD":
        restocking_fee = 0.0

    shipping_refund = 0.0
    if reason in ["damaged", "wrong_item"]:
        shipping_refund = float(order["shipping_amount"])

    tax_refund = float(order["tax_amount"]) * (
        subtotal / get_original_order_subtotal(order)
    )
    total = subtotal + shipping_refund + tax_refund - restocking_fee

    return {
        "subtotal": round(subtotal, 2),
        "shipping": round(shipping_refund, 2),
        "tax": round(tax_refund, 2),
        "fee": round(restocking_fee, 2),
        "total": round(total, 2),
    }


def get_original_order_subtotal(order):
    total = 0.0
    for item in order["items"]:
        total += float(item[4]) * item[3]
    return total


def create_support_case(customer, order, reason, notes, refund):
    database = connect_database()
    case_number = "CASE-" + str(int(time.time()))
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    priority = "NORMAL"

    if customer["loyalty_level"] == "GOLD" or refund["total"] > 500:
        priority = "HIGH"

    database.execute(
        "INSERT INTO support_cases "
        "(case_number, customer_id, order_id, reason, notes, priority, status, "
        "refund_amount, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            case_number,
            customer["id"],
            order["id"],
            reason,
            notes,
            priority,
            "OPEN",
            refund["total"],
            created_at,
        ),
    )
    database.commit()
    DAILY_TOTALS["cases"] += 1
    return case_number


def update_inventory_and_order(order, requested_items):
    database = connect_database()
    all_items_returned = True

    for requested in requested_items:
        database.execute(
            "UPDATE inventory SET available_quantity = available_quantity + "
            + str(requested["quantity"])
            + " WHERE sku = '"
            + requested["sku"]
            + "'"
        )
        database.execute(
            "UPDATE order_items SET returned_quantity = returned_quantity + ? "
            "WHERE order_id = ? AND sku = ?",
            (requested["quantity"], order["id"], requested["sku"]),
        )

    for item in order["items"]:
        requested_quantity = 0
        for requested in requested_items:
            if requested["sku"] == item[1]:
                requested_quantity = requested["quantity"]
        if item[5] + requested_quantity < item[3]:
            all_items_returned = False

    status = "RETURNED" if all_items_returned else "PARTIALLY_RETURNED"
    database.execute(
        "UPDATE orders SET status = ? WHERE id = ?", (status, order["id"])
    )
    database.commit()


def issue_refund(customer, order, refund, case_number):
    gateway_request = {
        "customer": customer["email"],
        "order": order["order_number"],
        "amount": refund["total"],
        "reference": case_number,
    }
    write_log("Sending refund request: " + json.dumps(gateway_request))
    time.sleep(2)
    DAILY_TOTALS["refunds"] += 1
    DAILY_TOTALS["refund_amount"] += refund["total"]
    return "REFUND-" + str(int(time.time()))


def send_customer_email(customer, case_number, refund, refund_reference):
    subject = "Return request " + case_number
    body = (
        "Hello "
        + customer["name"]
        + ", your return was approved. Refund: $"
        + str(refund["total"])
        + ". Reference: "
        + refund_reference
    )
    write_log(
        "Email from "
        + SUPPORT_EMAIL
        + " to "
        + customer["email"]
        + " | "
        + subject
        + " | "
        + body
    )


def process_return_request(email, order_number, requested_items, reason, notes):
    write_log(
        "New return request for customer="
        + email
        + ", order="
        + order_number
        + ", notes="
        + notes
    )

    customer = find_customer(email)
    order = load_order(order_number)
    errors = validate_return(customer, order, requested_items, reason)

    if len(errors) > 0:
        write_log("Return rejected: " + "; ".join(errors))
        return {"success": False, "errors": errors}

    try:
        refund = calculate_refund(customer, order, requested_items, reason)
        case_number = create_support_case(
            customer, order, reason, notes, refund
        )
        update_inventory_and_order(order, requested_items)
        refund_reference = issue_refund(customer, order, refund, case_number)
        send_customer_email(customer, case_number, refund, refund_reference)
        return {
            "success": True,
            "case_number": case_number,
            "refund_reference": refund_reference,
            "refund": refund,
        }
    except Exception as error:
        write_log("Return processing failed: " + str(error))
        return {"success": False, "errors": ["Unexpected processing error"]}


def export_daily_report(output_path):
    database = connect_database()
    rows = database.execute(
        "SELECT case_number, reason, priority, status, refund_amount, created_at "
        "FROM support_cases WHERE date(created_at) = date('now')"
    ).fetchall()

    with open(output_path, "w", newline="") as report_file:
        writer = csv.writer(report_file)
        writer.writerow(
            ["case_number", "reason", "priority", "status", "refund", "created"]
        )
        for row in rows:
            writer.writerow(row)

    write_log("Daily report written to " + output_path)
    return DAILY_TOTALS

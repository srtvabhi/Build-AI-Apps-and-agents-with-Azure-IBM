# Use Case 4:(Demo) Developing and Testing a Custom Chat Application with PostgreSQL

## Objective

In this lab, you will:

1. Create an Azure Database for PostgreSQL Flexible Server in the Azure portal.
2. Connect to PostgreSQL from Azure Cloud Shell using Bash.
3. Create and populate three sample business tables.
4. Configure a local Python chat application to use GPT-5.
5. Ask natural-language questions about PostgreSQL from the VS Code terminal.
6. Verify that generated SQL is restricted to read-only queries.

> This implementation is a custom GPT-5 chat application using the OpenAI
> Responses API and local Python database tools. It does not create a persistent
> Microsoft Foundry Agent and does not use the PostgreSQL MCP tool.

## Architecture

```text
User in VS Code terminal
        |
        v
    chat_app.py
        |
        +-- Sends the question to the GPT-5 deployment
        |
        +-- Receives a schema or SQL tool request
                    |
                    v
                database.py
                    |
                    +-- Validates SELECT-only SQL
                    +-- Opens a TLS connection
                    +-- Uses a read-only transaction
                    +-- Limits output to 100 rows
                    |
                    v
        Azure Database for PostgreSQL
                    |
                    v
        Grounded answer displayed in the terminal
```

## Project files

```text
chat_app.py
database.py
requirements.txt
sample_questions.txt
LabGuide.md
```

---

# Task 1: Create Azure Database for PostgreSQL Flexible Server

## Step 1: Open the Azure portal

Open:

```text
https://portal.azure.com
```

## Step 2: Start server creation

1. Select **Create a resource**.
2. Search for **Azure Database for PostgreSQL Flexible Server**.
3. Select the service and then select **Create**.

## Step 3: Configure the server

Use the following lab values:

```text
Resource group: rg-foundry-lab
Server name: pg-foundry-demo-001
Region: East US 2, or an available region
PostgreSQL version: 16, or the available lab version
Workload type: Development
Compute tier: Burstable
Compute size: B1ms
Administrator username: pgadmin
Password: Create and securely save a strong password
```

The server name must be globally unique. If the example is unavailable, add a
unique suffix and use that same name later in `chat_app.py`.

## Step 4: Configure networking

1. Select **Public access (allowed IP addresses)**.
2. Enable access from Azure services if required for Cloud Shell.
3. Add your current client IP address for access from VS Code.
4. Keep TLS/SSL connectivity enabled.

Public network access is suitable for this guided lab. Production systems
should use narrower firewall rules or private networking.

## Step 5: Deploy

1. Select **Review + create**.
2. Validate the configuration.
3. Select **Create**.
4. Wait for deployment to complete.

---

# Task 2: Collect Connection Information

Open the deployed PostgreSQL resource and record:

```text
Server/FQDN: pg-foundry-demo-001.postgres.database.azure.com
Port: 5432
Database: postgres
Administrator username: pgadmin
SSL mode: require
```

Do not put the password in screenshots, lab documents, or GitHub.

---

# Task 3: Open Azure Cloud Shell

1. Select **Cloud Shell** from the Azure portal toolbar.
2. Select **Bash**.
3. Check the PostgreSQL client:

```bash
psql --version
```

Cloud Shell is ephemeral. Files and package changes may not persist after the
session ends, but data created in Azure PostgreSQL will persist.

---

# Task 4: Connect to PostgreSQL

Run:

```bash
psql "host=pg-foundry-demo-001.postgres.database.azure.com port=5432 dbname=postgres user=pgadmin sslmode=require"
```

Enter the administrator password when prompted. Do not add the password to the
command because it can be stored in terminal history.

A successful connection displays:

```text
postgres=>
```

If the PostgreSQL client and server have different major versions, `psql` may
show a warning. Basic SQL used in this lab normally works, but matching client
and server versions is recommended for advanced administration.

---

# Task 5: Create the Sample Tables

Run each statement separately and include its final semicolon.

## Customers table

```sql
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    city VARCHAR(100),
    email VARCHAR(100)
);
```

## Products table

```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    price NUMERIC(10,2)
);
```

## Orders table

```sql
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT,
    product_id INT,
    quantity INT,
    order_status VARCHAR(50)
);
```

Verify the tables:

```sql
\dt
```

---

# Task 6: Insert Sample Data

## Customers

```sql
INSERT INTO customers (customer_name, city, email)
VALUES
    ('John Smith', 'London', 'john@example.com'),
    ('Maria Garcia', 'Madrid', 'maria@example.com'),
    ('Raj Sharma', 'Delhi', 'raj@example.com');
```

## Products

```sql
INSERT INTO products (product_name, price)
VALUES
    ('Laptop', 1200),
    ('Mouse', 25),
    ('Keyboard', 80);
```

## Orders

```sql
INSERT INTO orders (customer_id, product_id, quantity, order_status)
VALUES
    (1, 1, 1, 'Completed'),
    (2, 2, 2, 'Pending'),
    (3, 3, 1, 'Pending');
```

---

# Task 7: Verify the Database

Run:

```sql
SELECT * FROM customers;
SELECT * FROM products;
SELECT * FROM orders;
```

Check pending orders:

```sql
SELECT *
FROM orders
WHERE order_status = 'Pending';
```

Test the relationship used by the chat application:

```sql
SELECT
    o.order_id,
    c.customer_name,
    p.product_name,
    o.quantity,
    p.price * o.quantity AS order_value,
    o.order_status
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
JOIN products AS p ON p.product_id = o.product_id
ORDER BY o.order_id;
```

Exit PostgreSQL:

```sql
\q
```

---

# Task 8: Open the Application in VS Code

Open the repository folder in VS Code, and then open a PowerShell terminal in:

```powershell
cd "Use case 4 - Developing and Testing a Custom Chat Application with PostgreSQL"
```

The application uses these files:

- `chat_app.py` contains GPT-5, endpoint, and PostgreSQL configuration.
- `database.py` reads the schema and executes protected read-only queries.
- `requirements.txt` lists the Python packages.
- `sample_questions.txt` contains questions supported by the sample schema.

---

# Task 9: Create the Python Virtual Environment

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

After activation, `(.venv)` should appear at the beginning of the terminal
prompt.

---

# Task 10: Configure the Application

Open `chat_app.py` and replace:

```python
AZURE_OPENAI_API_KEY = "PASTE_YOUR_AZURE_OPENAI_KEY_HERE"
```

and:

```python
"password": "PASTE_YOUR_POSTGRES_PASSWORD_HERE",
```

Verify that these non-secret values match your resources:

```python
AZURE_OPENAI_DEPLOYMENT = "gpt-5"
"host": "pg-foundry-demo-001.postgres.database.azure.com"
"port": 5432
"dbname": "postgres"
"user": "pgadmin"
"sslmode": "require"
```

Never commit `chat_app.py` after inserting real credentials. Rotate credentials
immediately if they are exposed in GitHub, terminal output, or shared messages.

---

# Task 11: Run and Test the Chat Application

Run:

```powershell
python chat_app.py
```

Expected startup output:

```text
PostgreSQL GPT-5 Chat (type 'exit' to stop)

You >
```

Try these questions:

```text
Show the tables available in the database.
Show every order with the customer name and product name.
How many orders are there for each order status?
Show all pending orders with customer, product, quantity, and order value.
Calculate the total order value for each customer.
Which products have the highest total ordered quantity?
Calculate the total value of completed orders.
```

For the supplied data, this question:

```text
How many orders are there for each order status?
```

should return:

```text
Completed: 1
Pending: 2
```

The response should also display the SQL used.

Enter `exit` to close the application, and then run `deactivate` to leave the
virtual environment.

---

# Troubleshooting

## The prompt changes to `postgres->`

`postgres->` means PostgreSQL is waiting for the rest of an unfinished SQL
statement. End the statement with `;`, or discard the current input buffer:

```sql
\r
```

## Syntax error near a backtick

Do not paste Markdown fence characters such as `` ``` `` into `psql`. Paste
only the SQL inside a code block.

## Password authentication failed

- Confirm the administrator username and password.
- In the interactive `psql` command, enter the password only when prompted.
- In `chat_app.py`, type the actual password exactly as created. Do not add a
  backslash before `@` unless the backslash is part of the password.

## Connection timeout or firewall error

- Add the current client IP to the PostgreSQL networking firewall rules.
- Allow Azure services when connecting from Cloud Shell.
- Confirm that the FQDN and port `5432` are correct.
- Keep `sslmode` set to `require`.

## Application reports that credentials are missing

Replace both `PASTE_YOUR...` values in `chat_app.py`, save the file, and run it
again.

---

# Expected Outcome

You have successfully:

- Created an Azure Database for PostgreSQL Flexible Server.
- Connected securely using Azure Cloud Shell.
- Created `customers`, `products`, and `orders` tables.
- Inserted and verified sample business data.
- Configured GPT-5 and PostgreSQL in the custom Python chat application.
- Asked natural-language questions from the VS Code terminal.
- Received grounded answers produced from read-only PostgreSQL queries.

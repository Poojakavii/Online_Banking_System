import mysql.connector


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="online_banking_system"
    )


# ---------------- REGISTER CUSTOMER ----------------

def register_customer(name, email, phone, password, address, dob, gender, account_type):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO customers
    (name,email,phone,password,address,dob,gender,account_type)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        name,
        email,
        phone,
        password,
        address,
        dob,
        gender,
        account_type
    )

    cursor.execute(sql, values)

    conn.commit()

    cursor.close()
    conn.close()


# ---------------- CUSTOMER LOGIN ----------------

def check_login(email, password):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT * FROM customers
    WHERE email=%s AND password=%s
    """

    cursor.execute(sql, (email, password))

    customer = cursor.fetchone()

    cursor.close()
    conn.close()

    return customer


# ---------------- GET CUSTOMER ----------------

def get_customer(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM customers WHERE customer_id=%s",
        (customer_id,)
    )

    customer = cursor.fetchone()

    cursor.close()
    conn.close()

    return customer
# ---------------- BENEFICIARY ----------------

def add_beneficiary(customer_id, name, bank_name, account_number, ifsc):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO beneficiaries
    (customer_id, name, bank_name, account_number, ifsc)
    VALUES (%s,%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        customer_id,
        name,
        bank_name,
        account_number,
        ifsc
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_beneficiaries(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM beneficiaries WHERE customer_id=%s",
        (customer_id,)
    )

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data
# ---------------- FUND TRANSFER ----------------

def add_transfer(customer_id, beneficiary_id, transfer_type, amount, remarks):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO transfers
    (customer_id, beneficiary_id, transfer_type, amount, remarks)
    VALUES (%s,%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        customer_id,
        beneficiary_id,
        transfer_type,
        amount,
        remarks
    ))

    # Also add transaction history
    sql2 = """
    INSERT INTO transactions
    (customer_id, transaction_type, amount, status)
    VALUES (%s,%s,%s,%s)
    """

    cursor.execute(sql2, (
        customer_id,
        "Fund Transfer",
        amount,
        "Completed"
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_transfers(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT
        t.transfer_id,
        b.name,
        t.transfer_type,
        t.amount,
        t.status,
        t.transfer_date

    FROM transfers t

    JOIN beneficiaries b

    ON t.beneficiary_id=b.beneficiary_id

    WHERE t.customer_id=%s

    ORDER BY t.transfer_id DESC
    """

    cursor.execute(sql, (customer_id,))

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data
# ---------------- FUND TRANSFER ----------------

def add_transfer(customer_id, beneficiary_id, transfer_type, amount, remarks):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO transfers
    (customer_id, beneficiary_id, transfer_type, amount, remarks)
    VALUES (%s,%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        customer_id,
        beneficiary_id,
        transfer_type,
        amount,
        remarks
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_transfers(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT
        t.*,
        b.name
    FROM transfers t
    JOIN beneficiaries b
    ON t.beneficiary_id=b.beneficiary_id
    WHERE t.customer_id=%s
    ORDER BY transfer_id DESC
    """

    cursor.execute(sql, (customer_id,))

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data
# ---------------- BILL PAYMENT ----------------

def add_bill_payment(customer_id, bill_type, consumer_number, provider, amount):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO bill_payments
    (customer_id, bill_type, provider, amount)
    VALUES (%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        customer_id,
        bill_type,
        provider,
        amount
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_bill_payments(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM bill_payments
        WHERE customer_id=%s
        ORDER BY bill_id DESC
        """,
        (customer_id,)
    )

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data
# ---------------- LOANS ----------------

def add_loan(customer_id, loan_type, amount, tenure, income, purpose):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO loans
    (customer_id, loan_type, amount, tenure, income, purpose)
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        customer_id,
        loan_type,
        amount,
        tenure,
        income,
        purpose
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_loans(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM loans
        WHERE customer_id=%s
        ORDER BY loan_id DESC
        """,
        (customer_id,)
    )

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data
# ---------------- FIXED DEPOSIT ----------------

def add_fixed_deposit(customer_id, amount, tenure, interest_rate):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO fixed_deposits
    (customer_id, amount, tenure, interest_rate)
    VALUES (%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        customer_id,
        amount,
        tenure,
        interest_rate
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_fixed_deposits(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM fixed_deposits
        WHERE customer_id=%s
        ORDER BY fd_id DESC
        """,
        (customer_id,)
    )

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data
# ---------------- TRANSACTIONS ----------------

def add_transaction(customer_id, transaction_type, amount, status):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO transactions
    (customer_id, transaction_type, amount, status)
    VALUES (%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        customer_id,
        transaction_type,
        amount,
        status
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_transactions(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE customer_id=%s
        ORDER BY transaction_id DESC
    """, (customer_id,))

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data
# ---------------- BILL PAYMENT ----------------

def add_bill_payment(customer_id, bill_type, provider, amount):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO bill_payments
    (customer_id, bill_type, provider, amount, status)
    VALUES (%s,%s,%s,%s,%s)
    """

    cursor.execute(sql,(
        customer_id,
        bill_type,
        provider,
        amount,
        "Paid"
    ))

    conn.commit()

    cursor.close()
    conn.close()
    # ---------------- BILL PAYMENT ----------------

def add_bill_payment(customer_id, bill_type, provider, amount):

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO bill_payments
    (customer_id, bill_type, provider, amount, status)
    VALUES (%s,%s,%s,%s,%s)
    """

    cursor.execute(sql,(
        customer_id,
        bill_type,
        provider,
        amount,
        "Paid"
    ))

    conn.commit()

    cursor.close()
    conn.close()



def get_bill_payments(customer_id):

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)


    cursor.execute(
        """
        SELECT * FROM bill_payments
        WHERE customer_id=%s
        ORDER BY payment_date DESC
        """,
        (customer_id,)
    )


    bills = cursor.fetchall()


    cursor.close()
    conn.close()

    return bills
# ---------------- DASHBOARD DATA ----------------

def get_dashboard_data(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    # Account balance
    cursor.execute(
        "SELECT balance FROM accounts WHERE customer_id=%s",
        (customer_id,)
    )

    account = cursor.fetchone()


    balance = 0

    if account:
        balance = account['balance']


    # Transaction count
    cursor.execute(
        "SELECT COUNT(*) AS total FROM transactions WHERE customer_id=%s",
        (customer_id,)
    )

    transactions = cursor.fetchone()['total']


    # Loan count
    cursor.execute(
        "SELECT COUNT(*) AS total FROM loans WHERE customer_id=%s",
        (customer_id,)
    )

    loans = cursor.fetchone()['total']


    # Fixed deposit count
    cursor.execute(
        "SELECT COUNT(*) AS total FROM fixed_deposits WHERE customer_id=%s",
        (customer_id,)
    )

    fd = cursor.fetchone()['total']


    cursor.close()
    conn.close()


    return {
        "balance": balance,
        "transactions": transactions,
        "loans": loans,
        "fd": fd
    }
# ---------------- DASHBOARD COUNT FUNCTIONS ----------------

def get_transaction_count(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM transactions WHERE customer_id=%s",
        (customer_id,)
    )

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count



def get_loan_count(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM loans WHERE customer_id=%s",
        (customer_id,)
    )

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count



def get_fd_count(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM fixed_deposits WHERE customer_id=%s",
        (customer_id,)
    )

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count



def get_recent_transactions(customer_id):

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM transactions
        WHERE customer_id=%s
        ORDER BY transaction_date DESC
        LIMIT 5
        """,
        (customer_id,)
    )

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data
# ---------------- ADMIN DASHBOARD ----------------

def admin_total_customers():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customers")

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total


def admin_total_loans():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM loans")

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total


def admin_total_transactions():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM transactions")

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total


def admin_total_fd():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM fixed_deposits")

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total
# ---------------- UPDATE CUSTOMER PROFILE ----------------

def update_customer(
    customer_id,
    name,
    email,
    phone,
    gender,
    address
):

    conn = get_db_connection()

    cursor = conn.cursor()

    sql = """
    UPDATE customers
    SET
    name=%s,
    email=%s,
    phone=%s,
    gender=%s,
    address=%s
    WHERE customer_id=%s
    """

    cursor.execute(
        sql,
        (
            name,
            email,
            phone,
            gender,
            address,
            customer_id
        )
    )

    conn.commit()

    cursor.close()

    conn.close()
    # ---------------- GET ALL CUSTOMERS (ADMIN) ----------------

def get_all_customers():

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY customer_id DESC
    """)

    customers = cursor.fetchall()

    cursor.close()

    conn.close()

    return customers
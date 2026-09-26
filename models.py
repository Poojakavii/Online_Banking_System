import mysql.connector

# ---------------- CHANGE PASSWORD ----------------

def update_password(customer_id, new_password):

    conn = get_db_connection()

    cursor = conn.cursor()


    cursor.execute("""
    UPDATE customers
    SET password=%s
    WHERE customer_id=%s
    """,
    (
        new_password,
        customer_id
    ))


    conn.commit()
    cursor.close()
    conn.close()

# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="online_banking_clean"
    )


# ---------------- REGISTER CUSTOMER ----------------

# ---------------- REGISTER CUSTOMER ----------------

# ---------------- REGISTER CUSTOMER ----------------

def register_customer(
    name,
    email,
    phone,
    password,
    address,
    dob,
    gender,
    account_type,
    bank_name,
    account_number,
    ifsc,
    balance
):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        # Check duplicate email
        cursor.execute("""
            SELECT customer_id
            FROM customers
            WHERE email=%s
        """, (email,))

        if cursor.fetchone():
            return False, "Email already registered"

        # Check duplicate account number
        cursor.execute("""
            SELECT customer_id
            FROM customers
            WHERE account_number=%s
        """, (account_number,))

        if cursor.fetchone():
            return False, "Account number already exists"

        # Insert customer
        cursor.execute("""
            INSERT INTO customers
            (
                name,
                email,
                phone,
                password,
                address,
                dob,
                gender,
                account_type,
                bank_name,
                account_number,
                ifsc,
                balance
            )
            VALUES
            (
                %s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s
            )
        """, (
            name,
            email,
            phone,
            password,
            address,
            dob,
            gender,
            account_type,
            bank_name,
            account_number,
            ifsc,
            balance
        ))

        conn.commit()

        return True, "Registration successful"

    except Exception:
        conn.rollback()
        raise

    finally:
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


# ================= BILL PAYMENT =================
def add_bill_payment(
    customer_id,
    bill_type,
    consumer_number,
    provider,
    amount
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        amount = float(amount)

        # Check customer balance
        cursor.execute("""
            SELECT balance
            FROM customers
            WHERE customer_id = %s
        """, (customer_id,))

        customer = cursor.fetchone()

        if customer is None:
            return False, "Customer not found"

        if float(customer["balance"]) < amount:
            return False, "Insufficient balance"

        # Deduct balance
        cursor.execute("""
            UPDATE customers
            SET balance = balance - %s
            WHERE customer_id = %s
        """, (amount, customer_id))

        # Save bill payment
        cursor.execute("""
            INSERT INTO bill_payments
            (
                customer_id,
                bill_type,
                consumer_number,
                provider,
                amount,
                status
            )
            VALUES
            (%s, %s, %s, %s, %s, 'Paid')
        """, (
            customer_id,
            bill_type,
            consumer_number,
            provider,
            amount
        ))

        # Save transaction
        cursor.execute("""
            INSERT INTO transactions
            (
                customer_id,
                transaction_type,
                amount,
                status
            )
            VALUES
            (%s, %s, %s, %s)
        """, (
            customer_id,
            "Bill Payment",
            amount,
            "Completed"
        ))

        conn.commit()

        return True, "Bill payment successful"

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

# ---------------- FUND TRANSFER ----------------
def add_transfer(customer_id, beneficiary_id, transfer_type, amount, remarks):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        amount = float(amount)

        if amount <= 0:
            return False, "Enter a valid amount."

        # Get sender
        cursor.execute("""
            SELECT *
            FROM customers
            WHERE customer_id = %s
        """, (customer_id,))

        sender = cursor.fetchone()

        if sender is None:
            return False, "Customer account not found."

        # Check balance
        if float(sender["balance"]) < amount:
            return False, "Insufficient balance."

        # Get beneficiary
        cursor.execute("""
            SELECT *
            FROM beneficiaries
            WHERE beneficiary_id = %s
              AND customer_id = %s
        """, (beneficiary_id, customer_id))

        beneficiary = cursor.fetchone()

        if beneficiary is None:
            return False, "Beneficiary not found."

        # Check whether beneficiary is an account inside this bank
        cursor.execute("""
            SELECT customer_id
            FROM customers
            WHERE account_number = %s
        """, (beneficiary["account_number"],))

        receiver = cursor.fetchone()

        # Deduct money from sender
        cursor.execute("""
            UPDATE customers
            SET balance = balance - %s
            WHERE customer_id = %s
        """, (amount, customer_id))

        # If receiver exists, credit receiver
        # If external account, money is simply recorded as an external transfer
        if receiver is not None:

            cursor.execute("""
                UPDATE customers
                SET balance = balance + %s
                WHERE customer_id = %s
            """, (amount, receiver["customer_id"]))

        # Save transfer
        cursor.execute("""
            INSERT INTO transfers
            (
                customer_id,
                beneficiary_id,
                transfer_type,
                amount,
                remarks,
                status
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """, (
            customer_id,
            beneficiary_id,
            transfer_type,
            amount,
            remarks,
            "Completed"
        ))

        # Save transaction
        cursor.execute("""
            INSERT INTO transactions
            (
                customer_id,
                transaction_type,
                amount,
                status
            )
            VALUES
            (%s, %s, %s, %s)
        """, (
            customer_id,
            "Fund Transfer",
            amount,
            "Completed"
        ))

        conn.commit()

        return True, "Transfer successful."

    except Exception as e:

        conn.rollback()

        print("TRANSFER ERROR:", e)

        return False, "Transfer failed."

    finally:

        cursor.close()
        conn.close()
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

    cursor.execute("""
        SELECT COUNT(*)
        FROM loans
        WHERE customer_id = %s
    """, (customer_id,))

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
# ---------------- UPDATE PROFILE ----------------

def update_customer(customer_id,name,email,phone,gender,address):

    conn=get_db_connection()

    cursor=conn.cursor()


    cursor.execute("""
    UPDATE customers
    SET 
    name=%s,
    email=%s,
    phone=%s,
    gender=%s,
    address=%s

    WHERE customer_id=%s
    """,
    (
        name,
        email,
        phone,
        gender,
        address,
        customer_id
    ))


    conn.commit()

    cursor.close()
    conn.close()



# ---------------- CHANGE PASSWORD ----------------

def update_password(customer_id,password):

    conn=get_db_connection()

    cursor=conn.cursor()


    cursor.execute("""
    UPDATE customers
    SET password=%s
    WHERE customer_id=%s
    """,
    (
        password,
        customer_id
    ))


    conn.commit()

    cursor.close()
    conn.close()
    # ---------------- GET TRANSFERS ----------------

def get_transfers(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            transfers.*,
            beneficiaries.name AS beneficiary_name
        FROM transfers
        JOIN beneficiaries
            ON transfers.beneficiary_id = beneficiaries.beneficiary_id
        WHERE transfers.customer_id=%s
        ORDER BY transfer_id DESC
    """, (customer_id,))

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data

def get_transfers(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                t.*,
                b.name AS beneficiary_name
            FROM transfers t
            LEFT JOIN beneficiaries b
                ON t.beneficiary_id = b.beneficiary_id
            WHERE t.customer_id = %s
            ORDER BY t.transfer_date DESC
        """, (customer_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def get_all_transfers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                t.transfer_id,
                t.customer_id,
                t.beneficiary_id,
                t.transfer_type,
                t.amount,
                t.remarks,
                t.status,
                t.transfer_date,
                c.name AS name,
                b.name AS beneficiary_name
            FROM transfers t
            JOIN customers c
                ON t.customer_id = c.customer_id
            LEFT JOIN beneficiaries b
                ON t.beneficiary_id = b.beneficiary_id
            ORDER BY t.transfer_id DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()
def get_bill_payments(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM bill_payments
            WHERE customer_id = %s
            ORDER BY payment_date DESC
        """, (customer_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

# ---------------- ADMIN TRANSFER APPROVAL ----------------

def approve_transfer_request(transfer_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE transfers
            SET status = 'Approved'
            WHERE transfer_id = %s
        """, (transfer_id,))

        conn.commit()

    finally:
        cursor.close()
        conn.close()


# ---------------- ADMIN LOAN APPROVAL ----------------

def approve_loan_request(loan_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE loans
            SET status = 'Approved'
            WHERE loan_id = %s
        """, (loan_id,))

        conn.commit()

    finally:
        cursor.close()
        conn.close()
# ---------------- ADMIN TRANSFER APPROVAL ----------------

def approve_transfer_request(transfer_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE transfers
            SET status = 'Approved'
            WHERE transfer_id = %s
        """, (transfer_id,))

        conn.commit()

    finally:
        cursor.close()
        conn.close()

# ---------------- ADMIN ALL LOANS ----------------

def get_all_loans():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                l.*,
                c.name
            FROM loans l
            JOIN customers c
                ON l.customer_id = c.customer_id
            ORDER BY l.loan_id DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

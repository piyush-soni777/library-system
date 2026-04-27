import sys
from datetime import date, timedelta
from db import execute_query, get_connection
import config
from mysql.connector import Error

# ── ANSI COLORS ──    
R  = "\033[0m"
B  = "\033[1m"
CY = "\033[36m"
GR = "\033[32m"
YL = "\033[33m"
RD = "\033[31m"
MG = "\033[35m"

# ─────────────────────────────────────────
#  DISPLAY HELPERS
# ─────────────────────────────────────────
def clear():
    print("\n" * 2)

def banner():
    print(CY + B)
    print("  ╔══════════════════════════════════════════╗")
    print("  ║        📚 LIBRARY MANAGEMENT SYSTEM      ║")
    print("  ║            Python + MySQL Edition        ║")
    print("  ╚══════════════════════════════════════════╝")
    print(R)

def menu():
    print(CY + B + "\n  ╔════════════════════════════════╗" + R)
    print(CY + B +   "  ║          MAIN MENU             ║" + R)
    print(CY + B +   "  ╠════════════════════════════════╣" + R)
    options = [
        ("1", "Book Management"),
        ("2", "Member Management"),
        ("3", "Issue a Book"),
        ("4", "Return a Book"),
        ("5", "Search Books"),
        ("6", "Overdue Books & Fines"),
        ("7", "Reports"),
        ("0", "Exit"),
    ]
    for num, label in options:
        print(f"  {CY+B}║{R}  {GR}[{num}]{R}  {label:<24}{CY+B}  ║{R}")
    print(CY + B +   "  ╚════════════════════════════════╝" + R)
    return input(YL + "\n  → Choice: " + R).strip()

def sec(title):
    print(f"\n{B+MG}  ── {title} ──{R}\n")

def success(msg): print(GR + f"\n  ✔  {msg}" + R)
def error(msg):   print(RD + f"\n  ✘  {msg}" + R)
def warn(msg):    print(YL + f"\n  ⚠  {msg}" + R)
def pause():      input(CY + "\n  Press ENTER to continue..." + R)

def table_header(cols):
    """Print a table header from list of (label, width) tuples."""
    sep = "+" + "+".join("-" * (w + 2) for _, w in cols) + "+"
    hdr = "|" + "|".join(f" {l:<{w}} " for l, w in cols) + "|"
    print(CY + sep + R)
    print(CY + hdr + R)
    print(CY + sep + R)
    return sep

def table_row(sep, vals, cols, color_fn=None):
    row = "|" + "|".join(f" {str(v):<{w}} " for (_, w), v in zip(cols, vals)) + "|"
    print((color_fn(row) if color_fn else row))

def table_footer(sep):
    print(CY + sep + R)

# ─────────────────────────────────────────
#  BOOK MANAGEMENT
# ─────────────────────────────────────────
def book_menu():
    while True:
        sec("Book Management")
        print(f"  {GR}[1]{R} Add Book")
        print(f"  {GR}[2]{R} View All Books")
        print(f"  {GR}[3]{R} Update Book")
        print(f"  {GR}[4]{R} Delete Book")
        print(f"  {GR}[0]{R} Back")
        ch = input(YL + "\n  → Choice: " + R).strip()
        if ch == "1": add_book()
        elif ch == "2": view_books()
        elif ch == "3": update_book()
        elif ch == "4": delete_book()
        elif ch == "0": break
        else: error("Invalid choice.")

def add_book():
    sec("Add New Book")
    title  = input("  Title   : ").strip()
    author = input("  Author  : ").strip()
    genre  = input("  Genre   : ").strip()
    isbn   = input("  ISBN    : ").strip()
    try:
        copies = int(input("  Copies  : ").strip())
    except ValueError:
        error("Invalid number."); return

    if not title or not author:
        error("Title and Author are required."); return

    try:
        execute_query(
            "INSERT INTO books (title, author, genre, isbn, total_copies, available) VALUES (%s,%s,%s,%s,%s,%s)",
            (title, author, genre or "General", isbn or None, copies, copies)
        )
        success(f'Book "{title}" added successfully!')
    except Error as e:
        error(f"Failed: {e}")
    pause()

def view_books(rows=None):
    sec("All Books")
    if rows is None:
        rows = execute_query("SELECT id, title, author, genre, total_copies, available FROM books ORDER BY id", fetch=True)
    if not rows:
        warn("No books found."); pause(); return

    cols = [("ID",4),("Title",30),("Author",22),("Genre",14),("Total",5),("Avail",5)]
    sep = table_header(cols)
    for r in rows:
        avail = r['available']
        color = GR if avail > 0 else RD
        vals  = [r['id'], r['title'][:30], r['author'][:22], r['genre'][:14], r['total_copies'], r['available']]
        table_row(sep, vals, cols, lambda row: color + row + R)
    table_footer(sep)
    print(f"\n  {B}Total: {len(rows)} book(s){R}")
    pause()

def update_book():
    sec("Update Book")
    try:
        bid = int(input("  Enter Book ID: ").strip())
    except ValueError:
        error("Invalid ID."); return
    rows = execute_query("SELECT * FROM books WHERE id=%s", (bid,), fetch=True)
    if not rows:
        error(f"Book ID {bid} not found."); pause(); return
    b = rows[0]
    print(YL + "  (Leave blank to keep current value)" + R)
    title  = input(f"  Title  [{b['title']}]: ").strip()  or b['title']
    author = input(f"  Author [{b['author']}]: ").strip() or b['author']
    genre  = input(f"  Genre  [{b['genre']}]: ").strip()  or b['genre']
    try:
        tc_in = input(f"  Copies [{b['total_copies']}]: ").strip()
        tc = int(tc_in) if tc_in else b['total_copies']
    except ValueError:
        tc = b['total_copies']

    execute_query(
        "UPDATE books SET title=%s, author=%s, genre=%s, total_copies=%s WHERE id=%s",
        (title, author, genre, tc, bid)
    )
    success(f"Book ID {bid} updated.")
    pause()

def delete_book():
    sec("Delete Book")
    try:
        bid = int(input("  Enter Book ID to delete: ").strip())
    except ValueError:
        error("Invalid ID."); return
    rows = execute_query("SELECT title FROM books WHERE id=%s", (bid,), fetch=True)
    if not rows:
        error(f"Book ID {bid} not found."); pause(); return
    confirm = input(YL + f'  Delete "{rows[0]["title"]}"? (y/n): ' + R).strip().lower()
    if confirm != 'y':
        print("  Cancelled."); pause(); return
    # Check if any issued
    issued = execute_query("SELECT id FROM issued_books WHERE book_id=%s AND status='issued'", (bid,), fetch=True)
    if issued:
        error("Cannot delete — book is currently issued to a member."); pause(); return
    execute_query("DELETE FROM books WHERE id=%s", (bid,))
    success("Book deleted.")
    pause()

# ─────────────────────────────────────────
#  MEMBER MANAGEMENT
# ─────────────────────────────────────────
def member_menu():
    while True:
        sec("Member Management")
        print(f"  {GR}[1]{R} Add Member")
        print(f"  {GR}[2]{R} View All Members")
        print(f"  {GR}[3]{R} Update Member")
        print(f"  {GR}[4]{R} Delete Member")
        print(f"  {GR}[0]{R} Back")
        ch = input(YL + "\n  → Choice: " + R).strip()
        if ch == "1": add_member()
        elif ch == "2": view_members()
        elif ch == "3": update_member()
        elif ch == "4": delete_member()
        elif ch == "0": break
        else: error("Invalid choice.")

def add_member():
    sec("Add New Member")
    name  = input("  Name   : ").strip()
    email = input("  Email  : ").strip()
    phone = input("  Phone  : ").strip()
    if not name or not email:
        error("Name and Email are required."); return
    try:
        execute_query(
            "INSERT INTO members (name, email, phone) VALUES (%s,%s,%s)",
            (name, email, phone or None)
        )
        success(f'Member "{name}" added!')
    except Error as e:
        error(f"Failed (email may already exist): {e}")
    pause()

def view_members():
    sec("All Members")
    rows = execute_query("SELECT id, name, email, phone, joined_on FROM members WHERE active=1 ORDER BY id", fetch=True)
    if not rows:
        warn("No members found."); pause(); return
    cols = [("ID",4),("Name",22),("Email",28),("Phone",14),("Joined",12)]
    sep  = table_header(cols)
    for r in rows:
        jd = str(r['joined_on'])[:10]
        table_row(sep, [r['id'], r['name'][:22], r['email'][:28], r['phone'] or '-', jd], cols)
    table_footer(sep)
    print(f"\n  {B}Total: {len(rows)} member(s){R}")
    pause()

def update_member():
    sec("Update Member")
    try:
        mid = int(input("  Enter Member ID: ").strip())
    except ValueError:
        error("Invalid ID."); return
    rows = execute_query("SELECT * FROM members WHERE id=%s", (mid,), fetch=True)
    if not rows:
        error(f"Member ID {mid} not found."); pause(); return
    m = rows[0]
    print(YL + "  (Leave blank to keep current value)" + R)
    name  = input(f"  Name  [{m['name']}]: ").strip()  or m['name']
    email = input(f"  Email [{m['email']}]: ").strip() or m['email']
    phone = input(f"  Phone [{m['phone']}]: ").strip() or m['phone']
    execute_query(
        "UPDATE members SET name=%s, email=%s, phone=%s WHERE id=%s",
        (name, email, phone, mid)
    )
    success(f"Member ID {mid} updated.")
    pause()

def delete_member():
    sec("Delete Member")
    try:
        mid = int(input("  Enter Member ID to delete: ").strip())
    except ValueError:
        error("Invalid ID."); return
    rows = execute_query("SELECT name FROM members WHERE id=%s", (mid,), fetch=True)
    if not rows:
        error(f"Member ID {mid} not found."); pause(); return
    confirm = input(YL + f'  Delete member "{rows[0]["name"]}"? (y/n): ' + R).strip().lower()
    if confirm != 'y':
        print("  Cancelled."); pause(); return
    active = execute_query("SELECT id FROM issued_books WHERE member_id=%s AND status='issued'", (mid,), fetch=True)
    if active:
        error("Cannot delete — member has books currently issued."); pause(); return
    execute_query("UPDATE members SET active=0 WHERE id=%s", (mid,))
    success("Member removed.")
    pause()

# ─────────────────────────────────────────
#  ISSUE BOOK  made by piyush
# ─────────────────────────────────────────
def issue_book():
    sec("Issue a Book")
    try:
        bid = int(input("  Book ID   : ").strip())
        mid = int(input("  Member ID : ").strip())
    except ValueError:
        error("Invalid input."); pause(); return

    # Check book
    book = execute_query("SELECT * FROM books WHERE id=%s", (bid,), fetch=True)
    if not book:
        error(f"Book ID {bid} not found."); pause(); return
    book = book[0]
    if book['available'] <= 0:
        error(f'"{book["title"]}" has no available copies.'); pause(); return

    # Check member
    member = execute_query("SELECT * FROM members WHERE id=%s AND active=1", (mid,), fetch=True)
    if not member:
        error(f"Member ID {mid} not found."); pause(); return
    member = member[0]

    # Check if already has this book
    already = execute_query(
        "SELECT id FROM issued_books WHERE book_id=%s AND member_id=%s AND status='issued'",
        (bid, mid), fetch=True
    )
    if already:
        error(f"{member['name']} already has this book."); pause(); return

    issue_date = date.today()
    due_date   = issue_date + timedelta(days=config.LOAN_DAYS)

    execute_query(
        "INSERT INTO issued_books (book_id, member_id, issue_date, due_date) VALUES (%s,%s,%s,%s)",
        (bid, mid, issue_date, due_date)
    )
    execute_query("UPDATE books SET available = available - 1 WHERE id=%s", (bid,))

    print(GR + "\n  ══════════ ISSUE SLIP ══════════" + R)
    print(f"  Book   : {book['title']}")
    print(f"  Author : {book['author']}")
    print(f"  Member : {member['name']}")
    print(f"  Issued : {issue_date}")
    print(B + f"  Due By : {due_date}" + R)
    print(GR + "  ════════════════════════════════" + R)
    pause()

# ─────────────────────────────────────────
#  RETURN BOOK made by piyushSoni
# ─────────────────────────────────────────
def return_book():
    sec("Return a Book")
    try:
        issue_id = int(input("  Enter Issue ID (from Reports): ").strip())
    except ValueError:
        error("Invalid ID."); pause(); return

    row = execute_query(
        """SELECT ib.*, b.title, b.id as bid, m.name as mname
           FROM issued_books ib
           JOIN books b ON b.id = ib.book_id
           JOIN members m ON m.id = ib.member_id
           WHERE ib.id=%s AND ib.status='issued'""",
        (issue_id,), fetch=True
    )
    if not row:
        error(f"Issue ID {issue_id} not found or already returned."); pause(); return
    r = row[0]

    return_date = date.today()
    due_date    = r['due_date']
    fine        = 0.0
    days_late   = (return_date - due_date).days
    if days_late > 0:
        fine = days_late * config.FINE_PER_DAY
        warn(f"Book is {days_late} day(s) overdue! Fine: ₹{fine:.2f}")

    execute_query(
        "UPDATE issued_books SET return_date=%s, fine=%s, status='returned' WHERE id=%s",
        (return_date, fine, issue_id)
    )
    execute_query("UPDATE books SET available = available + 1 WHERE id=%s", (r['bid'],))

    print(GR + "\n  ══════════ RETURN SLIP ══════════" + R)
    print(f"  Book      : {r['title']}")
    print(f"  Member    : {r['mname']}")
    print(f"  Issued On : {r['issue_date']}")
    print(f"  Due Date  : {due_date}")
    print(f"  Returned  : {return_date}")
    print(B + f"  Fine      : ₹{fine:.2f}" + R)
    print(GR + "  ═════════════════════════════════" + R)
    success("Book returned successfully.")
    pause()

# ─────────────────────────────────────────
#  SEARCH
# ─────────────────────────────────────────
def search_books():
    sec("Search Books")
    print(f"  {GR}[1]{R} Search by Title")
    print(f"  {GR}[2]{R} Search by Author")
    print(f"  {GR}[3]{R} Search by Genre")
    ch = input(YL + "\n  → Choice: " + R).strip()
    if ch not in ('1','2','3'):
        error("Invalid choice."); pause(); return
    field = {'1':'title','2':'author','3':'genre'}[ch]
    query = input(f"  Enter {field}: ").strip()
    rows  = execute_query(
        f"SELECT id, title, author, genre, total_copies, available FROM books WHERE {field} LIKE %s ORDER BY title",
        (f"%{query}%",), fetch=True
    )
    if not rows:
        warn(f'No books found for "{query}".'); pause(); return
    view_books(rows)

# ─────────────────────────────────────────
#  OVERDUE BOOKS
# ─────────────────────────────────────────
def overdue_books():
    sec("Overdue Books & Fines")
    today = date.today()
    rows  = execute_query(
        """SELECT ib.id, b.title, m.name, ib.issue_date, ib.due_date,
                  DATEDIFF(%s, ib.due_date) AS days_late,
                  DATEDIFF(%s, ib.due_date) * %s AS fine
           FROM issued_books ib
           JOIN books   b ON b.id = ib.book_id
           JOIN members m ON m.id = ib.member_id
           WHERE ib.status='issued' AND ib.due_date < %s
           ORDER BY ib.due_date""",
        (today, today, config.FINE_PER_DAY, today), fetch=True
    )
    if not rows:
        success("No overdue books! All returns on time. ✓"); pause(); return

    cols = [("ID",4),("Book",28),("Member",18),("Due Date",11),("Days Late",9),("Fine(₹)",8)]
    sep  = table_header(cols)
    total_fine = 0
    for r in rows:
        fine = float(r['fine'])
        total_fine += fine
        vals = [r['id'], r['title'][:28], r['name'][:18], str(r['due_date']), r['days_late'], f"{fine:.2f}"]
        table_row(sep, vals, cols, lambda row: RD + row + R)
    table_footer(sep)
    print(B + f"\n  Total Overdue: {len(rows)} book(s)  |  Total Fine: ₹{total_fine:.2f}" + R)
    pause()

# ─────────────────────────────────────────
#  REPORTS
# ─────────────────────────────────────────
def reports():
    sec("Reports")
    print(f"  {GR}[1]{R} Currently Issued Books")
    print(f"  {GR}[2]{R} Return History")
    print(f"  {GR}[3]{R} Library Statistics")
    print(f"  {GR}[0]{R} Back")
    ch = input(YL + "\n  → Choice: " + R).strip()

    if ch == '1':
        sec("Currently Issued Books")
        rows = execute_query(
            """SELECT ib.id, b.title, m.name, ib.issue_date, ib.due_date
               FROM issued_books ib
               JOIN books b   ON b.id = ib.book_id
               JOIN members m ON m.id = ib.member_id
               WHERE ib.status='issued' ORDER BY ib.due_date""",
            fetch=True
        )
        if not rows:
            warn("No books currently issued."); pause(); return
        cols = [("Issue ID",8),("Book",28),("Member",20),("Issued",11),("Due",11)]
        sep  = table_header(cols)
        today = date.today()
        for r in rows:
            overdue = r['due_date'] < today
            color   = RD if overdue else GR
            vals    = [r['id'], r['title'][:28], r['name'][:20], str(r['issue_date']), str(r['due_date'])]
            table_row(sep, vals, cols, lambda row: color + row + R)
        table_footer(sep)

    elif ch == '2':
        sec("Return History (Last 20)")
        rows = execute_query(
            """SELECT ib.id, b.title, m.name, ib.issue_date, ib.return_date, ib.fine
               FROM issued_books ib
               JOIN books b   ON b.id = ib.book_id
               JOIN members m ON m.id = ib.member_id
               WHERE ib.status='returned' ORDER BY ib.return_date DESC LIMIT 20""",
            fetch=True
        )
        if not rows:
            warn("No returns yet."); pause(); return
        cols = [("ID",4),("Book",28),("Member",18),("Issued",11),("Returned",11),("Fine₹",7)]
        sep  = table_header(cols)
        for r in rows:
            vals = [r['id'], r['title'][:28], r['name'][:18],
                    str(r['issue_date']), str(r['return_date']), f"{float(r['fine']):.2f}"]
            table_row(sep, vals, cols)
        table_footer(sep)

    elif ch == '3':
        sec("Library Statistics")
        stats = execute_query(
            """SELECT
               (SELECT COUNT(*) FROM books)               AS total_books,
               (SELECT SUM(available) FROM books)         AS available_copies,
               (SELECT COUNT(*) FROM members WHERE active=1) AS total_members,
               (SELECT COUNT(*) FROM issued_books WHERE status='issued') AS books_out,
               (SELECT COUNT(*) FROM issued_books WHERE status='issued' AND due_date < CURDATE()) AS overdue,
               (SELECT COALESCE(SUM(fine),0) FROM issued_books WHERE status='returned') AS fines_collected""",
            fetch=True
        )[0]
        items = [
            ("Total Books (titles)",  stats['total_books']),
            ("Copies Available",      stats['available_copies']),
            ("Registered Members",    stats['total_members']),
            ("Books Currently Out",   stats['books_out']),
            ("Overdue Books",         stats['overdue']),
            ("Total Fines Collected", f"₹{float(stats['fines_collected']):.2f}"),
        ]
        for label, val in items:
            color = RD if label == "Overdue Books" and int(stats['overdue']) > 0 else GR
            print(f"  {B}{label:<28}{R}: {color}{val}{R}")

    else:
        return
    pause()

# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────
def main():
    # Test DB connection first
    print(CY + "\n  Connecting to MySQL..." + R)
    try:
        conn = get_connection()
        conn.close()
        print(GR + "  ✔  Connected to library_db\n" + R)
    except Exception:
        print(RD + "\n  ✘  Could not connect. Please:" + R)
        print("     1. Start MySQL server")
        print("     2. Run setup_db.sql")
        print("     3. Update config.py with your password")
        sys.exit(1)
        
# piyushsoni
    banner()
    while True:
        ch = menu()
        if   ch == '1': book_menu()
        elif ch == '2': member_menu()
        elif ch == '3': issue_book()
        elif ch == '4': return_book()
        elif ch == '5': search_books()
        elif ch == '6': overdue_books()
        elif ch == '7': reports()
        elif ch == '0':
            print(CY + "\n  Dhanyawad! Library system band ho gayi. 📚\n" + R)
            sys.exit(0)
        else:
            error("Invalid choice. 0-7 ke beech choose karo.")

if __name__ == "__main__":
    main()

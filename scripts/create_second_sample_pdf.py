import pymupdf
from pathlib import Path

output_path = Path("data/sample_documents/dbms_transactions_sample.pdf")

doc = pymupdf.open()

page1 = doc.new_page()

text1 = """
DATABASE TRANSACTIONS AND SQL

1. ACID Properties

ACID is a set of four properties that ensure reliable database transactions.

Atomicity:
A transaction is treated as a single unit. Either all its operations
are completed or none of them are applied.

Consistency:
A transaction moves the database from one valid state to another
while maintaining database rules and constraints.

Isolation:
Concurrent transactions should not interfere with each other.
Each transaction should behave as if it were executed independently.

Durability:
Once a transaction is committed, its changes remain permanent,
even after a system failure.

2. Database Transactions

A transaction is a sequence of database operations performed
as one logical unit of work.

COMMIT permanently saves the changes made by a transaction.

ROLLBACK cancels uncommitted changes and restores the previous state.
"""

page1.insert_textbox(
    pymupdf.Rect(50, 50, 550, 750),
    text1,
    fontsize=11,
    lineheight=1.5
)

page2 = doc.new_page()

text2 = """
SQL COMMANDS AND INDEXING

3. SQL Commands

SELECT:
Retrieves records from a database table.

INSERT:
Adds new records to a database table.

UPDATE:
Modifies existing records in a database table.

DELETE:
Removes records from a database table.

CREATE TABLE:
Creates a new table in a database.

4. Database Indexing

A database index is a data structure that improves the speed
of data retrieval operations.

Indexes help databases find records without scanning every row
of a table.

A primary index is generally associated with the primary key
of a database table.

A secondary index provides an additional way to access records
using columns other than the primary key.

5. Advantages and Limitations of Indexing

Advantages:
- Improves data retrieval speed.
- Helps optimize search queries.
- Reduces the need for full table scans.

Limitations:
- Requires additional storage space.
- Can slow down INSERT, UPDATE and DELETE operations
  because indexes may need to be maintained.
"""

page2.insert_text(
    (50, 60),
    text2,
    fontsize=10,
    lineheight=1.4
)

doc.save(output_path)
doc.close()

print("Second DBMS PDF fixed successfully!")
print("Location:", output_path)

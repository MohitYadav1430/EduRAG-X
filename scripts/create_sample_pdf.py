import pymupdf
from pathlib import Path

output_path = Path("data/sample_documents/dbms_sample.pdf")

doc = pymupdf.open()

page1 = doc.new_page()

text1 = """
DATABASE MANAGEMENT SYSTEM (DBMS)

1. Introduction to DBMS

A Database Management System (DBMS) is software that allows users
to create, store, organize, retrieve, and manage data efficiently.

Examples of DBMS include MySQL, PostgreSQL, Oracle Database,
and Microsoft SQL Server.

2. Database Normalization

Database normalization is the process of organizing data into
related tables to reduce data redundancy and improve data integrity.

Data redundancy means storing the same information repeatedly.
Excessive redundancy wastes storage and can cause inconsistency.

3. First Normal Form (1NF)

A table satisfies First Normal Form when each cell contains
a single atomic value and there are no repeating groups.

4. Second Normal Form (2NF)

A table satisfies Second Normal Form when it is in 1NF and
every non-key attribute depends on the entire candidate key.
"""

page1.insert_textbox(
    pymupdf.Rect(50, 50, 550, 750),
    text1,
    fontsize=11,
    lineheight=1.5
)

page2 = doc.new_page()

text2 = """
DATABASE MANAGEMENT SYSTEM (DBMS)
CONTINUED

5. Third Normal Form (3NF)

A table satisfies Third Normal Form when it is in 2NF and
has no transitive dependency of non-key attributes on a key.

6. Primary Key

A primary key is a column or combination of columns that
uniquely identifies each record in a database table.

A primary key cannot contain duplicate or NULL values.

7. Foreign Key

A foreign key is a column or combination of columns that
references a primary key in another table.

It helps establish relationships between database tables.

8. Database Relationships

One-to-One: One record is associated with one record.

One-to-Many: One record can be associated with multiple records.

Many-to-Many: Multiple records can be associated with
multiple records through a junction table.

9. Benefits of Normalization

- Reduces data redundancy.
- Improves data consistency.
- Prevents update anomalies.
- Makes database structures easier to maintain.
"""

page2.insert_textbox(
    pymupdf.Rect(50, 50, 550, 750),
    text2,
    fontsize=11,
    lineheight=1.5
)

doc.save(output_path)
doc.close()

print("DBMS sample PDF created successfully!")
print("Location:", output_path)

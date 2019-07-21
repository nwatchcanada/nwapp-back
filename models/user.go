package models


import (
    "database/sql"
    "fmt"
    // "log"

    _ "github.com/lib/pq"
    "github.com/jmoiron/sqlx"
)


type User struct {
    Id            int64          `db:"id"`
    FirstName     sql.NullString `db:"first_name"`
    LastName      sql.NullString `db:"last_name"`
    Password      sql.NullString `db:"password"`
    Email         sql.NullString `db:"email"`
}


// Special Thanks:
// * https://jmoiron.github.io/sqlx/
// * http://wysocki.in/golang-sqlx/

/**
 *  Function will create the `users` table in the database.
 */
func CreateUserTable(db *sqlx.DB, dropExistingTable bool) {
    if dropExistingTable {
        drop_stmt := "DROP TABLE users;"
        results, err := db.Exec(drop_stmt)
        if err != nil {
            fmt.Println("UserDAO", results, err)
        }
    }

    // Special thanks:
    // * http://www.postgresqltutorial.com/postgresql-create-table/
    // * https://www.postgresql.org/docs/9.5/datatype.html

    stmt := `CREATE TABLE users (
        id bigserial PRIMARY KEY,
        first_name VARCHAR (50) NOT NULL,
        last_name VARCHAR (50) NOT NULL,
        password VARCHAR (255) NOT NULL,
        email VARCHAR (255) UNIQUE NOT NULL
    );`
    results, err := db.Exec(stmt)
    if err != nil {
        fmt.Println("UserDAO", results, err)
    }
    return
}



func FindUserByEmail(db *sqlx.DB, email string) (*User, bool) {
    user := User{} // The struct which will be populated from the database.

    // DEVELOPERS NOTE:
    // (1) Lookup the user based on the email.
    // (2) PostgreSQL uses an enumerated $1, $2, etc bindvar syntax
    err := db.Get(&user, "SELECT * FROM users WHERE email = $1", email)

    // Handling non existing item
    if err == sql.ErrNoRows {
        return nil, false
    } else if err != nil {
        panic(err)
    }

    return &user, true
}

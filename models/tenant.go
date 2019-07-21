package models


import (
    "database/sql"
    "fmt"
)


type Tenant struct {
    Id                int64          `db:"id"`
    Schema            sql.NullString `db:"schema"`
    Name              sql.NullString `db:"name"`
}


// Special Thanks:
// * https://jmoiron.github.io/sqlx/
// * http://wysocki.in/golang-sqlx/

/**
 *  Function will create the `tenants` table in the database.
 */
func CreateTenantTable(dropExistingTable bool) {
    if dropExistingTable {
        drop_stmt := "DROP TABLE tenants;"
        results, err := db.Exec(drop_stmt)
        if err != nil {
            fmt.Println("Tenant Model:", results, err)
        }
    }

    // Special thanks:
    // * http://www.postgresqltutorial.com/postgresql-create-table/
    // * https://www.postgresql.org/docs/9.5/datatype.html

    stmt := `CREATE TABLE tenants (
        id bigserial PRIMARY KEY,
        schema VARCHAR (63) UNIQUE NOT NULL,
        name VARCHAR (127) NOT NULL
    );`
    results, err := db.Exec(stmt)
    if err != nil {
        fmt.Println("Tenant Model", results, err)
    }
    return
}


/**
 *  Function will return the `tenant` struct if it exists in the database or
 *  return an error.
 */
func FindTenantById(id int64) (*Tenant, error) {
    tenant := Tenant{} // The struct which will be populated from the database.

    // DEVELOPERS NOTE:
    // (1) Lookup the tenant based on the `id`.
    // (2) PostgreSQL uses an enumerated $1, $2, etc bindvar syntax
    err := db.Get(&tenant, "SELECT * FROM tenants WHERE id = $1", id)

    // Handling non existing item
    if err == sql.ErrNoRows {
        return nil, nil
    } else if err != nil {
        return nil, err
    }

    return &tenant, nil
}


/**
 *  Function will return the `tenant` struct if it exists in the database or
 *  return an error.
 */
func FindTenantBySchema(schema string) (*Tenant, error) {
    tenant := Tenant{} // The struct which will be populated from the database.

    // DEVELOPERS NOTE:
    // (1) Lookup the tenant based on the schema.
    // (2) PostgreSQL uses an enumerated $1, $2, etc bindvar syntax
    err := db.Get(&tenant, "SELECT * FROM tenants WHERE schema = $1", schema)

    // Handling non existing item
    if err == sql.ErrNoRows {
        return nil, nil
    } else if err != nil {
        return nil, err
    }

    return &tenant, nil
}

/**
 *  Function will create a tenant, if validation passess, and reutrns the `tenant`
 *  struct else returns the error.
 */
func CreateTenant(schema string, name string) (*Tenant, error) {
    // Step 2: Generate SQL statement for creating a new `tenant` in `postgres`.
    statement := `INSERT INTO tenants (schema, name) VALUES ($1, $2)`

    // Step 3: Execute our SQL statement and either return our new tenant or
    //         our error.
    _, err := db.Exec(statement, schema, name)
    if err != nil {
        return nil, err
    }
    return FindTenantBySchema(schema)
}

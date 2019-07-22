package models


import (
    "database/sql"
    "fmt"

    // "github.com/jmoiron/sqlx"
)


type Tenant struct {
    Id                uint64          `db:"id"`
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
func FindTenantById(id uint64) (*Tenant, error) {
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


func fetchTenantsRoutine(page uint64, pageSize uint64, resultOp chan []Tenant) {
    t := []Tenant{}
    offset := (page - 1) * pageSize
    limit := pageSize

    // Make a paginated fetch to our data. Since we are assuming:
    // (1) no data record
    // (2) expecting the primary key IDs to be exactly sequential integers (incremented by 1)
    // (3) auto-increment will not be manually modified by programmer
    // As a result, we can use our tables `id` value as our offset. This idea was from:
    // https://developer.wordpress.com/2014/02/14/an-efficient-alternative-to-paging-with-sql-offsets/
    err := db.Select(&t, "SELECT * FROM tenants WHERE id > $1 LIMIT $2", offset, limit)
    if err != nil {
        panic(err)
    }

    // We are creating a `slice` of the array so we are `passing by reference`
    // instead of `passing by value`. Passing reference is more efficient then
    // passing by values - see "Memory Optmization" the link at
    // via https://golangbot.com/arrays-and-slices/
    resultOp <- t[:]
}

func countTotalTenantsRoutine(countOp chan uint64) {
    var count uint64
    _ = db.Get(&count, "SELECT count(*) FROM tenants")
    countOp <- count
}


/**
 *  Function will return paginated list of tenants.
 */
func FetchTenants(page uint64, pageSize uint64) ([]Tenant, uint64) {
    // Defensive Code: Catch programmer error.
    if page < 0 { panic("Page must start at 1.") }
    if pageSize < 0 { panic("pageSize must be at least 1.") }

    // Setup the `channels`.
    resultCh := make(chan []Tenant)
    countCh := make(chan uint64)

    // Run the following functions concurrently.
    go fetchTenantsRoutine(page, pageSize, resultCh)
    go countTotalTenantsRoutine(countCh)

    // Block the main function until we have results from our concurrently
    // running `goroutines`.
    tenants, count := <-resultCh, <-countCh

    // Return our data.
    return tenants, count
}

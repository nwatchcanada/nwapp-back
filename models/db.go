package models

import (
    "fmt"
    "log"

    _ "github.com/lib/pq"
    "github.com/jmoiron/sqlx"
)


/**
 * Package level global variable. All data access objects in our `models`
 * package will have access to this variable assuming the `InitDB` function
 * is called before any of those `models` get called.
 */
var db *sqlx.DB


/**
 *  Function initializes our connection with the `postgres` database for this
 *  web-application and saves the db connection instance in a global variable.
 */
func InitDB(dbHost, dbPort, dbUser, dbPassword, dbName string) (*sqlx.DB) {
    psqlInfo := fmt.Sprintf("host=%s port=%s user=%s "+ "password=%s dbname=%s sslmode=disable", dbHost, dbPort, dbUser, dbPassword, dbName)
    dbInstance, err := sqlx.Connect("postgres", psqlInfo)
    if err != nil {
       log.Fatalln(err)
    }
    err = dbInstance.Ping()
    if err != nil {
        panic(err)
    }
    fmt.Println("Database successfully connected!")
    db = dbInstance
    return db;
}

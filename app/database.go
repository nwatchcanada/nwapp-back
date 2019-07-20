package app

import (
    "fmt"
    "log"

    _ "github.com/lib/pq"
    "github.com/jmoiron/sqlx"
)


func InitDB(dbHost, dbPort, dbUser, dbPassword, dbName string) (*sqlx.DB) {
    psqlInfo := fmt.Sprintf("host=%s port=%s user=%s "+ "password=%s dbname=%s sslmode=disable", dbHost, dbPort, dbUser, dbPassword, dbName)
    db, err := sqlx.Connect("postgres", psqlInfo)
    if err != nil {
       log.Fatalln(err)
    }
    err = db.Ping()
    if err != nil {
        panic(err)
    }
    fmt.Println("Database successfully connected!")
    return db;
}

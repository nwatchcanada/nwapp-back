package app

import (
    "fmt"
    "log"

    _ "github.com/lib/pq"
    "github.com/jmoiron/sqlx"

    "github.com/nwatchcanada/nwapp-back/models"
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

    // // The following
    // results, err := db.Exec(models.CreateUserTableSQLStatement())
    // fmt.Println(results, err)
    // The following code will create our tables.
    models.CreateUserTable(db, false)

    
    return db;
}

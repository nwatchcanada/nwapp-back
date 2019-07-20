package main

import (
    "log"
    "os"
    "github.com/joho/godotenv"

    "github.com/nwatchcanada/nwapp-back/app"
)


/**
 *  Main entry point into our web-application.
 */
func main() {
    // We will load up all our environment settings variables from the `.env`
    // file and have it ready for our application.
    err := godotenv.Load()
    if err != nil {
        log.Fatal("Error loading .env file")
    }
    dbUsername := os.Getenv("DB_USERNAME")
    dbPassword := os.Getenv("DB_PASSWORD")
    dbName := os.Getenv("DB_NAME")
    appAddress := os.Getenv("APP_ADDRESS")

    // Initialize our application.
    a := app.App{}
    a.Initialize(dbUsername, dbPassword, dbName)

    // Start and run our application.
    a.Run(appAddress)
}

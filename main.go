package main

import (
    "log"
    "os"
    "runtime"
    "github.com/joho/godotenv"

    "github.com/nwatchcanada/nwapp-back/app"
)


// Initialize our applications shared functions.
func init() {
	runtime.GOMAXPROCS(runtime.NumCPU())  // Use all CPU cores
}


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
    dbHost := os.Getenv("DB_HOST")
    dbport := os.Getenv("DB_PORT")
    dbUser := os.Getenv("DB_USER")
    dbPassword := os.Getenv("DB_PASSWORD")
    dbName := os.Getenv("DB_NAME")
    appAddress := os.Getenv("APP_ADDRESS")

    // Initialize our application.
    a := app.App{}
    a.Initialize(dbHost, dbport, dbUser, dbPassword, dbName)

    // Start and run our application.
    a.Run(appAddress)
}

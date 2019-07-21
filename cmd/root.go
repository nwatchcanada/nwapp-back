package cmd

import (
    "fmt"
    "os"
    "log"
    "github.com/spf13/cobra"

    "github.com/joho/godotenv"
    "github.com/nwatchcanada/nwapp-back/app"
)

var rootCmd = &cobra.Command{
    Use:   "nwap-back",
    Short: "NWApp is an API web-service.",
    Long: `API web-service which powers the Neigbhourhood Watch Canada backend.`,
    Run: func(cmd *cobra.Command, args []string) {
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
    },
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}

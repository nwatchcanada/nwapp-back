package cmd

import (
    "fmt"
    "os"
    "github.com/spf13/cobra"

    "github.com/nwatchcanada/nwapp-back/app"
)

var rootCmd = &cobra.Command{
    Use:   "nwap-back",
    Short: "NWApp is an API web-service.",
    Long: `API web-service which powers the Neigbhourhood Watch Canada backend.`,
    Run: func(cmd *cobra.Command, args []string) {
        // Load up our `environment variables` from our operating system.
        dbHost := os.Getenv("NWAPP_DB_HOST")
        dbPort := os.Getenv("NWAPP_DB_PORT")
        dbUser := os.Getenv("NWAPP_DB_USER")
        dbPassword := os.Getenv("NWAPP_DB_PASSWORD")
        dbName := os.Getenv("NWAPP_DB_NAME")
        appAddress := os.Getenv("NWAPP_APP_ADDRESS")

        // Initialize our application.
        a := app.App{}
        a.Initialize(dbHost, dbPort, dbUser, dbPassword, dbName)

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

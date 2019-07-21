package cmd

import (
    "errors"
    "fmt"
    "os"
    "log"

    "github.com/spf13/cobra"
    "github.com/joho/godotenv"

    "github.com/nwatchcanada/nwapp-back/models"
)

/**
 *  go run main.go add_tenant "london" "Neighbourhood Watch Canada London"
 */

func init() {
    rootCmd.AddCommand(addTenantCmd)
}

var addTenantCmd = &cobra.Command{
    Use:   "add_tenant [FIELDS]",
    Short: "Creates a new tenant",
    Long:  `Command will create a new tenant in our application.`,
    Args: func(cmd *cobra.Command, args []string) error {
        if len(args) < 2 {
          return errors.New("requires the following fields: schema, name")
        }
        return nil
    },
    Run: func(cmd *cobra.Command, args []string) {
        // Get our user arguments.
        schema := args[0]
        name := args[1]

        // We will load up all our environment settings variables from the `.env`
        // file and have it ready for our application.
        err := godotenv.Load()
        if err != nil {
            log.Fatal("Error loading .env file")
        }
        dbHost := os.Getenv("DB_HOST")
        dbPort := os.Getenv("DB_PORT")
        dbUser := os.Getenv("DB_USER")
        dbPassword := os.Getenv("DB_PASSWORD")
        dbName := os.Getenv("DB_NAME")

        // Initialize and connect our database layer for the command.
        models.InitDB(dbHost, dbPort, dbUser, dbPassword, dbName)
        tenant, err := models.CreateTenant(schema, name)
        if err != nil {
            fmt.Println("Failed creating tenant!")
            fmt.Println(err)
        } else {
            fmt.Println("Tenant created with ID #", tenant.Id)
        }
    },
}

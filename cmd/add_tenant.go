package cmd

import (
    "errors"
    "fmt"
    "os"

    "github.com/spf13/cobra"

    "github.com/nwatchcanada/nwapp-back/models"
)

/**
 * DEVELOPERS RUN:
 * $ go run main.go add_tenant "london" "Neighbourhood Watch Canada London"
 *
 * DEVOPS RUN:
 * $ $GOBIN/nwapp-back add_tenant "london" "Neighbourhood Watch Canada London"
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

        // Load up our `environment variables` from our operating system.
        dbHost := os.Getenv("NWAPP_DB_HOST")
        dbPort := os.Getenv("NWAPP_DB_PORT")
        dbUser := os.Getenv("NWAPP_DB_USER")
        dbPassword := os.Getenv("NWAPP_DB_PASSWORD")
        dbName := os.Getenv("NWAPP_DB_NAME")
        // appAddress := os.Getenv("NWAPP_APP_ADDRESS")

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

package cmd

import (
    "errors"
    "fmt"
    "os"
    "strconv"

    "github.com/spf13/cobra"

    "github.com/nwatchcanada/nwapp-back/models"
)

/**
 * DEVELOPERS RUN:
 * $ go run main.go add_user "bart@mikasoftware.com" "Bart" "Mika" "123password" 1 "london" 1
 *
 * DEVOPS RUN:
 * $ $GOBIN/nwapp-back add_user "bart@mikasoftware.com" "Bart" "Mika" "123password" 1 "london" 1

/**
 *  g
 */

func init() {
    rootCmd.AddCommand(addUserCmd)
}

var addUserCmd = &cobra.Command{
    Use:   "add_user [FIELDS]",
    Short: "Creates a new user",
    Long:  `Command will create a new user in our application.`,
    Args: func(cmd *cobra.Command, args []string) error {
        if len(args) < 7 {
          return errors.New("requires the following fields: email, first name, last name, password, tenant id, tenant schema, group id")
        }
        return nil
    },
    Run: func(cmd *cobra.Command, args []string) {
        // Get our user arguments.
        email := args[0]
        firstName := args[1]
        lastName := args[2]
        password := args[3]
        tenantIdString := args[4]
        tenantSchema := args[5]
        groupIdString := args[6]

        // Minor modifications.
        tenantId, _ := strconv.ParseInt(tenantIdString, 10, 64)
        groupId, _ := strconv.ParseInt(groupIdString, 10, 64)

        // Load up our `environment variables` from our operating system.
        dbHost := os.Getenv("NWAPP_DB_HOST")
        dbPort := os.Getenv("NWAPP_DB_PORT")
        dbUser := os.Getenv("NWAPP_DB_USER")
        dbPassword := os.Getenv("NWAPP_DB_PASSWORD")
        dbName := os.Getenv("NWAPP_DB_NAME")
        // appAddress := os.Getenv("NWAPP_APP_ADDRESS")

        // Initialize and connect our database layer for the command.
        models.InitDB(dbHost, dbPort, dbUser, dbPassword, dbName)
        user, err := models.CreateUser(email, firstName, lastName, password, tenantId, tenantSchema, groupId)
        if err != nil {
            fmt.Println("Failed creating user!")
            fmt.Println(err)
        } else {
            fmt.Println("User created with ID #", user.Id)
        }
    },
}

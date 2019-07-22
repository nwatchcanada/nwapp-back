package cmd

import (
    "errors"
    "fmt"
    "os"
    "log"
    "strconv"

    "github.com/spf13/cobra"
    "github.com/joho/godotenv"

    "github.com/nwatchcanada/nwapp-back/models"
)

/**
 *  go run main.go add_user "bart@mikasoftware.com" "bart" "mika" "123password" 1 "london" 1
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
        user, err := models.CreateUser(email, firstName, lastName, password, tenantId, tenantSchema, groupId)
        if err != nil {
            fmt.Println("Failed creating user!")
            fmt.Println(err)
        } else {
            fmt.Println("User created with ID #", user.Id)
        }
    },
}

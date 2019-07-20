package main

import (
    "github.com/nwatchcanada/nwapp-back/app"
)


/**
 *  Main entry point into our web-application.
 */
func main() {


    a := app.App{}
    a.Initialize(user, password, dbname)
    a.Run(":8080")
}

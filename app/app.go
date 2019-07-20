package app

import (
    "fmt"
    "net/http"
    // "strings"
    "log"

    "github.com/gorilla/mux"
    "github.com/urfave/negroni"

    "github.com/nwatchcanada/nwapp-back/controllers"
)


/**
 *  Class used to store our web-application.
 */
type App struct {
    Router *mux.Router
}

/**
 *  Initialize the web-application with the database credentials.
 */
func (a *App) Initialize(user, password, dbname string) {
    a.Router = mux.NewRouter()
    a.Router.HandleFunc("/", controllers.GetVersion).Methods("GET")
}

/**
 *  Run the server.
 */
func (a *App) Run(addr string) {
    fmt.Println("Neighbourhood Watch Canada App is now running...")

    n := negroni.Classic() // Includes some default middlewares
    n.UseHandler(a.Router)

    err := http.ListenAndServe(addr, n)
	if err != nil {
		log.Fatal(err)
	}
}

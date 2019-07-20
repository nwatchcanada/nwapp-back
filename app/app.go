package app

import (
    "database/sql"
    "fmt"
    "net/http"
    // "strings"
    "log"

    _ "github.com/lib/pq"
    "github.com/gorilla/mux"
    "github.com/gorilla/handlers"
    "github.com/urfave/negroni"

    "github.com/nwatchcanada/nwapp-back/controllers"
    "github.com/nwatchcanada/nwapp-back/controllers/account"
)


/**
 *  Class used to store our web-application.
 */
type App struct {
    Router *mux.Router
    DB *sql.DB
}

/**
 *  Initialize the web-application with the database credentials.
 */
func (a *App) Initialize(dbHost, dbPort, dbUser, dbPassword, dbName string) {
    a.Router = mux.NewRouter()
    a.Router.HandleFunc("/hello", controllers.PostHello).Methods("OPTIONS","POST")
    a.Router.HandleFunc("/version", controllers.GetVersion).Methods("OPTIONS","GET")
    a.Router.HandleFunc("/api/login", account.PostLogin).Methods("OPTIONS","POST")

    psqlInfo := fmt.Sprintf("host=%s port=%s user=%s "+
       "password=%s dbname=%s sslmode=disable",
       dbHost, dbPort, dbUser, dbPassword, dbName)

    var db *sql.DB
    var err error

    db, err = sql.Open("postgres", psqlInfo)
    if err != nil {
        panic(err)
    }
    err = db.Ping()
    if err != nil {
        panic(err)
    }
    fmt.Println("Database successfully connected!")
    a.DB = db
}

/**
 *  Run the server.
 */
func (a *App) Run(addr string) {
    fmt.Println("Neighbourhood Watch Canada App is now running...")

    n := negroni.Classic() // Includes some default middlewares
    n.UseHandler(a.Router)

    // https://stackoverflow.com/questions/47309286/axios-does-not-send-post-to-golang-api
    // https://gist.github.com/marshyon/12d78db8ed8dfd3c242a9a94bb185917
    n2 := handlers.CORS(handlers.AllowedHeaders([]string{"X-Requested-With", "Content-Type", "Authorization"}),
    handlers.AllowedMethods([]string{"GET", "POST", "PUT", "HEAD", "OPTIONS"}),
    handlers.AllowedOrigins([]string{"*"}))(n)

    // Attach database closing when the app terminates.
    defer a.DB.Close()

    // Start our server.
    err := http.ListenAndServe(addr, n2)
	if err != nil {
		log.Fatal(err)
	}
}

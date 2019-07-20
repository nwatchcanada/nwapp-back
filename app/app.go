package app

import (
    "fmt"
    "net/http"

    "github.com/urfave/negroni"
)

type App struct {
    Router *mux.Router
}

func (a *App) Initialize(user, password, dbname string) {

}

func (a *App) Run(addr string) {
    mux := http.NewServeMux()
    mux.HandleFunc("/", func(w http.ResponseWriter, req *http.Request) {
      fmt.Fprintf(w, "Welcome to the home page!")
    })

    n := negroni.Classic() // Includes some default middlewares
    n.UseHandler(mux)

    http.ListenAndServe(addr, n)
}

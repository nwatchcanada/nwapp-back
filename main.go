package main

import (
    // "fmt"
    "net/http"
    // "strings"
    "log"

    "github.com/nwatchcanada/nwapp-back/controllers"
)


func main() {
    http.HandleFunc("/", controllers.SayhelloName) // set router
    err := http.ListenAndServe(":8080", nil) // set listen port
    if err != nil {
        log.Fatal("ListenAndServe: ", err)
    }
}

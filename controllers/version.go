package controllers

import (
    "fmt"
    "net/http"
)

/**
 *  Returns the version of the web-service.
 */
func GetVersion(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello astaxie!") // send data to client side
}

package controllers

import (
    // "fmt"
    "net/http"

    // "github.com/nwatchcanada/nwapp-back/models"
    // "github.com/nwatchcanada/nwapp-back/serializers"
)


func DashboardHandler(w http.ResponseWriter, r *http.Request) {
    schema := r.Context().Value("subdomain").(string)

    w.Write([]byte("It works!"+schema)) // Return our `[]byte` data.
}

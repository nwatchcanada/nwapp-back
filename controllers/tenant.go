package controllers

import (
    "fmt"
    "net/http"

    // "github.com/go-chi/chi"
    "github.com/nwatchcanada/nwapp-back/models"

    // "github.com/nwatchcanada/nwapp-back/serializers"
)


func TenantListHandler(w http.ResponseWriter, r *http.Request) {
    // STEP 1: Fetch our URL parameters saved by our "Paginator" middleware.
    page := r.Context().Value("pageParm").(uint64)

    // STEP 2: Fetch our objects.
    tenants, totalCount := models.FetchTenants(page, 50)

    fmt.Println(tenants, totalCount)

    // // Serialize our user data for API response output.
    // profileSerializer := serializers.ProfileSerializer{Request: r}
    // b := profileSerializer.Serialize(user, nil)
    // w.Write(b) // Return our `[]byte` data.
}

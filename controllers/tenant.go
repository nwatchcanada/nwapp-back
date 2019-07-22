package controllers

import (
    // "fmt"
    "net/http"

    "github.com/nwatchcanada/nwapp-back/models"
    "github.com/nwatchcanada/nwapp-back/serializers"
)


func TenantListHandler(w http.ResponseWriter, r *http.Request) {
    // STEP 1: Fetch our URL parameters saved by our "Paginator" middleware.
    page := r.Context().Value("pageParm").(uint64)
    pageSize := r.Context().Value("pageSizeParam").(uint64)

    // STEP 2: Fetch our objects.
    tenants, totalCount := models.FetchTenants(page, pageSize)

    // STEP 3: Create our context.
    c := make(map[string]interface{})
    c["count"] = totalCount
    c["page"] = page

    // STEP 4: Serialize our data for API response output.
    tenantListSerializer := serializers.TenantListSerializer{Request: r}
    b := tenantListSerializer.Serialize(tenants, c)

    // STEP 5: Output our data from the API.
    w.Write(b) // Return our `[]byte` data.
}

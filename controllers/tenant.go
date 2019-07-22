package controllers

import (
    "fmt"
    "net/http"
    "github.com/nwatchcanada/nwapp-back/models"
    // "github.com/nwatchcanada/nwapp-back/serializers"
)


func TenantListHandler(w http.ResponseWriter, r *http.Request) {
    tenants, totalCount := models.FetchTenants(1, 50)

    fmt.Println(tenants, totalCount)

    // // Extract the current email from the request context. It is important
    // // to note that this context must be AFTER the `ProfileCtx` middleware.
    // ctx := r.Context()
    // email := ctx.Value("userEmail").(string)
    //
    // // Lookup our user profile account.
    // user, _ := models.FindUserByEmail(email)
    //
    // // Serialize our user data for API response output.
    // profileSerializer := serializers.ProfileSerializer{Request: r}
    // b := profileSerializer.Serialize(user, nil)
    // w.Write(b) // Return our `[]byte` data.
}

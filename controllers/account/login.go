package account

import (
    // "fmt"
    "net/http"
    // "io/ioutil"
    // "encoding/json"

    "github.com/nwatchcanada/nwapp-back/utils"
    "github.com/nwatchcanada/nwapp-back/serializers"
)



func PostLogin(w http.ResponseWriter, r *http.Request) {
    // Set our header.
    w.Header().Set("Content-Type", "application/json")

    // Take our `request` and validate the credentials inputted by the user.
    // If the validation fails or we have any errors then we'll stop right
    // here and output our errors by the API.
    s := serializers.LoginSerializer{Request: r}
    user, hasError := s.Deserialize()
    if hasError {
        s.ErrorHandler.WriteBadRequestErrors(w)
        return
    }

    // Generate our access and refresh tokens and added them into our profile
    // serializer as a context..
    t, rf := utils.GenerateJWTToken(user.Email.String, user.GroupId, user.TenantSchema.String)
    context := make(map[string]string)
    context["AccessToken"] = t
    context["RefreshToken"] = rf

    // If we get to this line of code then we will be serializing our `User`
    // and returning our data.
    profileSerializer := serializers.ProfileSerializer{Request: r}
    b := profileSerializer.Serialize(user, context)
    w.Write(b) // Return our `[]byte` data.
}

//https://stackoverflow.com/questions/3316762/what-is-deserialize-and-serialize-in-json

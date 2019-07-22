package serializers

import (
    "fmt"
    "net/http"
//     "io/ioutil"
    "encoding/json"

    "github.com/nwatchcanada/nwapp-back/models"
)


type ProfileSerializer struct {
    Request *http.Request
}


/**
 *  The data-structure that we will be returning when the `user` is serialized.
 */
type ProfileResponse struct {
    Email        string `json:"email"`
    FirstName    string `json:"first_name"`
    LastName     string `json:"last_name"`
    TenantSchema string `json:"tenant_schema"`
    AccessToken  string `json:"access_token,omitempty"`
    RefreshToken string `json:"refresh_token,omitempty"`
    GroupId      uint8 `json:"group_id"`
}

/**
 *  Function will serialize the model `profile` data into a []byte format
 *  ready for output by our API as JSON data.
 */
func (s *ProfileSerializer) Serialize(user *models.User, context map[string]string) []byte {
    // Define the structure we will be outputting.
    profile := ProfileResponse{
        Email: user.Email.String,
        FirstName: user.FirstName.String,
        LastName: user.LastName.String,
        TenantSchema: user.TenantSchema.String,
        GroupId: user.GroupId,
    }

    // If a context exists then that let us look inside and see if we have
    // our JWT credentials in there.
    if context != nil {
        profile.AccessToken = context["AccessToken"]
        profile.RefreshToken = context["RefreshToken"]
    }

    // Serialize our data.
    b, err := json.Marshal(profile)

    // Defensive Code: Any marshaling errors are a result to programmer error.
    if err != nil {
        fmt.Println(err)
        fmt.Printf("%+v\n", b)
        panic(err)
    }

    // Return our []byte data ready for output by the API.
    return b
}

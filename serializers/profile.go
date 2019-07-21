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
    Email string `json:"email"`
    FirstName string `json:"first_name"`
    LastName string `json:"last_name"`
}

func (s *ProfileSerializer) Serialize(user *models.User ) ([]byte, error) {
    profile := ProfileResponse{
        Email: user.Email.String,
        FirstName: user.FirstName.String,
        LastName: user.LastName.String,
    }
    b, err := json.Marshal(profile)
    if err != nil {
        fmt.Println(err)
        fmt.Printf("%+v\n", b)
        return nil, err
    }
    return b, nil
}

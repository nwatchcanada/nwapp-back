package serializers

import (
    "errors"
    "fmt"
    "net/http"
    "io/ioutil"
    "encoding/json"

    "github.com/nwatchcanada/nwapp-back/models"
    "github.com/nwatchcanada/nwapp-back/utils"
)


/**
 *  Type used for our login serializer.
 */
type LoginSerializer struct {
    Request *http.Request
}


type LoginData struct {
    Email    string
    Password string
}


/**
 *  Function will deserialize the login credentials and lookup the `User` in
 *  the database and validate the password, if everything was a success then
 *  we will return our user model.
 */
func (s *LoginSerializer) Deserialize() (*models.User, error) {
    buf, err := ioutil.ReadAll(s.Request.Body)
    if err!=nil {
        return nil, err
    }

    var data LoginData

    // De-serialize bytes into our struct object.
    err = json.Unmarshal(buf, &data)
    if err != nil {
        fmt.Println(err)
        fmt.Printf("%+v\n", data)
        return nil, errors.New("Email does not exist.")
    }

    // Lookup our user.
    user, _ := models.FindUserByEmail(data.Email)

    var isCorrectPassword bool = utils.CheckPasswordHash(data.Password, user.PasswordHash.String)
    if isCorrectPassword {
        return user, nil
    } else {
        return nil, errors.New("Incorrect password.")
    }
}

package serializers

import (
    // "errors"
    // "fmt"
    "net/http"
    "io/ioutil"
    "encoding/json"

    "github.com/nwatchcanada/nwapp-back/models"
    "github.com/nwatchcanada/nwapp-back/utils"
)


/**
 * The login serializer data-structure.
 */
type LoginSerializer struct {
    Request *http.Request
    ErrorHandler *SerializerErrorHandler
}


/**
 *  The data-structure we want to format our user submitted to the API.
 */
type LoginRequest struct {
    Email    string
    Password string
}


/**
 *  Function will deserialize the login credentials and lookup the `User` in
 *  the database and validate the password, if everything was a success then
 *  we will return our user model.
 */
func (s *LoginSerializer) Deserialize() (*models.User, bool) {
    // Initialize our serializer error handler which will return errors
    // in the same manner that `Django REST Framework` returns.
    s.ErrorHandler = s.ErrorHandler.New()

    // Extract our binary data from the `request`.
    buf, err := ioutil.ReadAll(s.Request.Body)
    if err!=nil {
        s.ErrorHandler.Add("NonFieldError", "Invalid format received")
        return nil, true
    }

    var data LoginRequest

    // De-serialize bytes into our struct object.
    err = json.Unmarshal(buf, &data)
    if err != nil {
        s.ErrorHandler.Add("NonFieldError", "Missing fields.")
        return nil, true
    }

    // Lookup our user.
    user, _ := models.FindUserByEmail(data.Email)
    if user == nil {
        s.ErrorHandler.Add("Email", "Account does not exist for the email.")
        return nil, true
    }

    var isCorrectPassword bool = utils.CheckPasswordHash(data.Password, user.PasswordHash.String)
    if isCorrectPassword {
        return user, false
    } else {
        s.ErrorHandler.Add("Password", "Incorrect password.")
        return nil, true
    }
}

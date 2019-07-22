package account

import (
    "fmt"
    "net/http"
    "io/ioutil"
    "encoding/json"

    "github.com/dgrijalva/jwt-go"

    "github.com/nwatchcanada/nwapp-back/models"
    "github.com/nwatchcanada/nwapp-back/utils"
    "github.com/nwatchcanada/nwapp-back/serializers"
)


type TokenRequest struct {
    RefreshToken string `json:"refresh_token,omitempty"`
}


/**
 *  API endpoint used to refresh the access token given a valid refresh token
 *  is inputted by the user.
 */
func RefreshTokenHandler(w http.ResponseWriter, r *http.Request) {
    // STEP 1: Get our byte data array.
    buf, err := ioutil.ReadAll(r.Body)

    // STEP 2: Deserialize bytes into our struct object.
    var tokenReq TokenRequest
    err = json.Unmarshal(buf, &tokenReq)
    if err != nil {
        fmt.Println(err)
    }

    // STEP 3: Confirm it's valid.
    token, isValid := utils.VerifyToken(tokenReq.RefreshToken)
    if isValid == false {
        w.WriteHeader(http.StatusUnauthorized) // Note: Refresh token expired.
        return
    }

    // https://github.com/go-chi/jwtauth/blob/master/jwtauth.go#L191

    // STEP 4: Get the claims data from our refresh token.
    var claims jwt.MapClaims
    if tokenClaims, ok := token.Claims.(jwt.MapClaims); ok {
		claims = tokenClaims
	} else {
		panic(fmt.Sprintf("jwtauth: unknown type of Claims: %T", token.Claims))
	}

    // STEP 5: Extract email and find the user.
    email := claims["email"].(string)
    user, _ := models.FindUserByEmail(email)

    // STEP 6: Generate our new access and refresh token.
    t, rf := utils.GenerateJWTToken(user.Email.String, user.GroupId, user.TenantSchema.String)
    context := make(map[string]string)
    context["AccessToken"] = t
    context["RefreshToken"] = rf

    // STEP 7:
    // If we get to this line of code then we will be serializing our `User`
    // and returning our data.
    profileSerializer := serializers.ProfileSerializer{Request: r}
    b := profileSerializer.Serialize(user, context)
    w.Write(b) // Return our `[]byte` data.
}

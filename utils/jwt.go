package utils

import (
    "context"
    "time"
    "github.com/dgrijalva/jwt-go"
    "github.com/go-chi/jwtauth"
)

// Our variables.
var tokenAuth *jwtauth.JWTAuth
var mySigningKey []byte

// Function will either lazily create and return the JWT token authority object,
// or return the JWT token authority if it was previously created.
func GetJWTTokenAuthority() *jwtauth.JWTAuth {
    // Get our applications secret signing key by lazily loading it if
    // we haven't already lazily loaded it yet.
    if mySigningKey == nil {
        secretString := "My secret string which I need to change"
        mySigningKey = []byte(secretString)
    }

    if tokenAuth != nil {
        return tokenAuth
    }

    // Generate our token signing authority.
	tokenAuth = jwtauth.New("HS256", mySigningKey, nil)

    // Return our toke authority.
    return tokenAuth
}

// Function will generate a unique JWT token with the claims data of holding
// the `userID` paramter.
func GenerateJWTToken(email string, groupId uint8, tenantSchema string) (string, string) {
    // Get our JWT token authority.
    myTokenAuth := GetJWTTokenAuthority()

    // Create our claims data for the JWT token.
    claims := jwt.MapClaims{
        "email": email,
        "groupId": groupId,
        "tenantSchema": tenantSchema,
        "exp": time.Now().Add(time.Minute * 15).Unix(), // MAKE SHORT-LIVED
    }

    // Generate our new JWT token.
    _, accessTokenString, _ := myTokenAuth.Encode(claims)

    // Create our claims data for the JWT token.
    refreshClaims := jwt.MapClaims{
        "email": email,
        "exp": time.Now().Add(time.Hour * 24).Unix(), // MAKE LONG-LIVED
    }

    // Generate our new JWT token.
    _, refreshTokenString, _ := myTokenAuth.Encode(refreshClaims)

    // Return our new JWT token.
    return accessTokenString, refreshTokenString
}


// Function used to create a new context with the JWT authenticated `claims`
// already attached to the context. This function should be used in unit tests.
func NewContextWithJWTToken(token string) context.Context {
    // SPECIAL THANKS:
    // https://github.com/go-chi/jwtauth/blob/master/jwtauth.go

    // STEP 1: Get JWT Authority.
    ja := GetJWTTokenAuthority()

    // STEP 2: Generate our token
    token_obj, err := ja.Decode(token)

    // STEP 3: Create our context were the user is logged and attach it to
    //         our request.
    ctx := context.Background()
    ctx = jwtauth.NewContext(ctx, token_obj, err)
    return ctx
}


// Function used to extract the `email` from the JWT token that was passed in
// by the JWT middleware when a successful authentication happened.
func GetJWTClaimsFromContext(ctx context.Context) (string, string, uint8) {
    // Fetch the claims based on what the JWT token was encoded and
    // encrypted with. We will extrac the user ID value and look it up.
    _, claims, _ := jwtauth.FromContext(ctx)
	rawEmail := claims["email"]
    rawTenantSchema := claims["tenantSchema"]
    rawGroupId := claims["groupId"]

    var groupId float64 = rawGroupId.(float64) // Set to default format.
    var gid uint8 = uint8(groupId)

    return rawEmail.(string), rawTenantSchema.(string),  gid
}

/**
 *  Modified from: https://github.com/go-chi/jwtauth/blob/master/jwtauth.go#L88
 */
func VerifyToken(tokenStr string) (*jwt.Token, bool) {
    // Get our JWT token authority.
    ja := GetJWTTokenAuthority()

    // Verify the token
	token, err := ja.Decode(tokenStr)
	if err != nil {
        return nil, false
    }

    if token == nil || !token.Valid {
		return nil, false
	}

	// // Verify signing algorithm
	// if token.Method != ja.signer {
	// 	return false
	// }

    return token, true
}

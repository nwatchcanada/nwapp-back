package serializers

import (
    "net/http"
    "encoding/json"
)

/**
 * The purpose of this code is to provide our serializers a way output errors
 * exactly how it is done in the `Django REST Framework`. This code is to be
 * used by our serializers and our API will returns errors in same manner as
 * if we were using `Django REST Framework`.
 */


/**
 *  Structure which will hold the dictionary (a.k.a. "map") of errors to return.
 *  This data structure is consistent with our error handling code in `ReactJS`.
 */
type SerializerErrorHandler struct {
    Errors map[string]string `json:"errors"`
}


/**
 *  Function intializes our API error handler.
 */
func (e *SerializerErrorHandler) New() (*SerializerErrorHandler) {
    err := SerializerErrorHandler{
        Errors: make(map[string]string),
    }
    return &err
}


/**
 *  Function adds an "error" to our error handler.
 */
func (e *SerializerErrorHandler) Add(key, value string) {
    e.Errors[key] = value
}


/**
 *  Function serializes the errors it is handling to be binary output data
 *  which can be passed out by our API.
 */
func (e *SerializerErrorHandler) Serialize() []byte {
    b, err := json.Marshal(e.Errors)
    if err != nil { // Defensive code
        panic(err)
    }
    return b
}


/**
 *  Function writes `400 Bad Request` error to our response and the dictionary
 *  (a.k.a. "map") of all the errors occured in our serializer to the API
 *  output. This is a convience function so you don't have to write this code
 *  every time.
 */
func (s *SerializerErrorHandler) WriteBadRequestErrors(w http.ResponseWriter) {
    b := s.Serialize()
    w.WriteHeader(http.StatusBadRequest)
    w.Write(b)
}

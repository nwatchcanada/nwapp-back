package controllers

import (
    "fmt"
    "net/http"
"io/ioutil";"log"
    "github.com/vmihailenco/msgpack"
    "github.com/ugorji/go/codec"
)

// https://stackoverflow.com/questions/53546967/convert-from-and-to-messagepack

/**
 *  Returns the version of the web-service.
 */
func GetVersion(w http.ResponseWriter, r *http.Request) {
    type Item struct {
		Version string
        LastUpdate string
	}

	b, err := msgpack.Marshal(&Item{
        Version: "0.0.1",
        LastUpdate: "July, 23, 2019",
    })
	if err != nil {
		panic(err)
	}

    w.WriteHeader(http.StatusOK)
    w.Header().Set("Content-Type", "application/msgpack")
    w.Write(b)

	// var item Item
	// err = msgpack.Unmarshal(b, &item)
	// if err != nil {
	// 	panic(err)
	// }
	// fmt.Println(item.Foo)
	// // Output: bar
}

/**
 *  Returns the posted name, function used for API developers to write test code
 *  to confirm our API service works.
 */
func PostHello(w http.ResponseWriter, r *http.Request) {
    //
    // READ FROM REQUEST
    //
    // STEP 1: Get our binary data from the request.
    buf, err := ioutil.ReadAll(r.Body)
    if err!=nil {log.Fatal("request",err)}
    fmt.Println("BUF", buf) // For debugging purposes only.

    // STEP 2: Create the map we will be converting our data to.
    decoded := make(map[string]string)

    // STEP 3: Convert our binary data to Golang map structure and error if anything bad happens.
    dec := codec.NewDecoderBytes(buf, new(codec.MsgpackHandle))
    if err := dec.Decode(&decoded); err != nil {
        panic(err)
    }
    fmt.Printf("Decoded: %v\n", decoded["name"]) // for debugging purpsoes only.

    //
    // WRITE FOR RESPNSE
    //
    var data []byte
    original := map[string]string{"message": "Hi!"}
    enc := codec.NewEncoderBytes(&data, new(codec.MsgpackHandle))
    if err := enc.Encode(&original); err != nil {
        panic(err)
    }
    fmt.Printf("Encoded: %v\n", data) // for debugging purpsoes only.



    w.WriteHeader(http.StatusOK)
    w.Header().Set("Content-Type", "application/msgpack")
    w.Write(data)

}

package utils

import (
    "golang.org/x/crypto/bcrypt"
)

/**
 *  The following password utility functions are used to help the programmer
 *  handle hashing passwords using the `brypt` algorithm.
 */


func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	return string(bytes), err
}

func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

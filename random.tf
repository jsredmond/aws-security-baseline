# Used to create random numbers
resource "random_id" "my-random-id" {
  byte_length = 8
}
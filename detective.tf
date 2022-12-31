# Enable AWS Detective
resource "aws_detective_graph" "detective" {
  tags = {
    Name = "${var.env}_detective"
  }
}
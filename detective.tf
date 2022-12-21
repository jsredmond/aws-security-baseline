# Enable AWS Detective
resource "aws_detective_graph" "my-detective" {
  tags = {
    Name = "${var.prefix_name}-detective"
  }
}
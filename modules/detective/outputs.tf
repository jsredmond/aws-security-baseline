# Detective Module Outputs

output "graph_id" {
  description = "The ID of the Detective graph"
  value       = aws_detective_graph.main.id
}

output "graph_arn" {
  description = "The ARN of the Detective graph"
  value       = aws_detective_graph.main.graph_arn
}

package test

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/hashicorp/hcl/v2"
	"github.com/hashicorp/hcl/v2/hclparse"
	"github.com/hashicorp/hcl/v2/hclsyntax"
	"github.com/stretchr/testify/assert"
)

// TestOutputAggregation verifies Property 17:
// For any root-level output, the output SHALL reference a value from a child module output.
//
// **Feature: terraform-modularization, Property 17: Output aggregation**
// **Validates: Requirements 4.5**
func TestOutputAggregation(t *testing.T) {
	t.Parallel()

	rootDir := ".."

	// Parse root outputs.tf
	outputsTfPath := filepath.Join(rootDir, "outputs.tf")
	outputsContent, err := os.ReadFile(outputsTfPath)
	assert.NoError(t, err, "Should be able to read outputs.tf")

	parser := hclparse.NewParser()
	outputsFile, diags := parser.ParseHCL(outputsContent, "outputs.tf")
	assert.False(t, diags.HasErrors(), "outputs.tf should parse without errors")

	if outputsFile == nil || outputsFile.Body == nil {
		t.Fatal("outputs.tf body is nil")
	}

	// Extract output blocks
	bodyContent, _, diags := outputsFile.Body.PartialContent(&hcl.BodySchema{
		Blocks: []hcl.BlockHeaderSchema{
			{Type: "output", LabelNames: []string{"name"}},
		},
	})
	assert.False(t, diags.HasErrors(), "Should extract output blocks")

	violations := []string{}
	outputsChecked := 0

	// For each output
	for _, outputBlock := range bodyContent.Blocks {
		if outputBlock.Type != "output" {
			continue
		}

		outputName := outputBlock.Labels[0]
		outputsChecked++

		// Get output attributes
		attrs, diags := outputBlock.Body.JustAttributes()
		if diags.HasErrors() {
			t.Logf("Warning: Could not extract attributes from output %s", outputName)
			continue
		}

		// Get the value attribute
		valueAttr, exists := attrs["value"]
		if !exists {
			violations = append(violations, "Output "+outputName+" is missing value attribute")
			continue
		}

		// Check if the value references a module output or is a conditional with module outputs
		referencesModule := false

		// Check for direct module reference: module.name.output
		if scopeExpr, ok := valueAttr.Expr.(*hclsyntax.ScopeTraversalExpr); ok {
			if len(scopeExpr.Traversal) >= 2 {
				rootName := scopeExpr.Traversal.RootName()
				if rootName == "module" {
					referencesModule = true
				}
			}
		}

		// Check for conditional expression: var.enable ? module.name.output : null
		if condExpr, ok := valueAttr.Expr.(*hclsyntax.ConditionalExpr); ok {
			// Check true result
			if scopeExpr, ok := condExpr.TrueResult.(*hclsyntax.ScopeTraversalExpr); ok {
				if len(scopeExpr.Traversal) >= 2 {
					rootName := scopeExpr.Traversal.RootName()
					if rootName == "module" {
						referencesModule = true
					}
				}
			}

			// Also check if it's an index expression like module.name[0].output
			if indexExpr, ok := condExpr.TrueResult.(*hclsyntax.IndexExpr); ok {
				if scopeExpr, ok := indexExpr.Collection.(*hclsyntax.ScopeTraversalExpr); ok {
					if len(scopeExpr.Traversal) >= 1 {
						rootName := scopeExpr.Traversal.RootName()
						if rootName == "module" {
							referencesModule = true
						}
					}
				}
			}
		}

		if !referencesModule {
			violations = append(violations,
				"Output "+outputName+" does not reference a module output (should reference module.*.output)")
		}
	}

	t.Logf("Checked %d outputs", outputsChecked)

	// Assert no violations found
	if len(violations) > 0 {
		t.Errorf("Output aggregation violations found:\n%s",
			strings.Join(violations, "\n"))
	}
}

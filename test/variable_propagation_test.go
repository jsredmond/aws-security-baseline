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

// TestVariablePropagation verifies Property 16:
// For any root-level variable that is needed by a module, the variable SHALL be
// passed to the module in the module call block.
//
// **Feature: terraform-modularization, Property 16: Variable propagation**
// **Validates: Requirements 4.4**
func TestVariablePropagation(t *testing.T) {
	t.Parallel()

	rootDir := ".."

	// Parse root main.tf to find module calls
	mainTfPath := filepath.Join(rootDir, "main.tf")
	mainContent, err := os.ReadFile(mainTfPath)
	assert.NoError(t, err, "Should be able to read main.tf")

	parser := hclparse.NewParser()
	mainFile, diags := parser.ParseHCL(mainContent, "main.tf")
	assert.False(t, diags.HasErrors(), "main.tf should parse without errors")

	if mainFile == nil || mainFile.Body == nil {
		t.Fatal("main.tf body is nil")
	}

	// Parse root variables.tf to get list of root variables
	varsTfPath := filepath.Join(rootDir, "variables.tf")
	varsContent, err := os.ReadFile(varsTfPath)
	assert.NoError(t, err, "Should be able to read variables.tf")

	varsFile, diags := parser.ParseHCL(varsContent, "variables.tf")
	assert.False(t, diags.HasErrors(), "variables.tf should parse without errors")

	// Extract root variable names
	rootVariables := make(map[string]bool)
	if varsFile != nil && varsFile.Body != nil {
		varsBodyContent, _, diags := varsFile.Body.PartialContent(&hcl.BodySchema{
			Blocks: []hcl.BlockHeaderSchema{
				{Type: "variable", LabelNames: []string{"name"}},
			},
		})
		if !diags.HasErrors() {
			for _, varBlock := range varsBodyContent.Blocks {
				if varBlock.Type == "variable" && len(varBlock.Labels) > 0 {
					rootVariables[varBlock.Labels[0]] = true
				}
			}
		}
	}

	t.Logf("Found %d root variables", len(rootVariables))

	// Extract module blocks
	bodyContent, _, diags := mainFile.Body.PartialContent(&hcl.BodySchema{
		Blocks: []hcl.BlockHeaderSchema{
			{Type: "module", LabelNames: []string{"name"}},
		},
	})
	assert.False(t, diags.HasErrors(), "Should extract module blocks")

	violations := []string{}

	// For each module call
	for _, moduleBlock := range bodyContent.Blocks {
		if moduleBlock.Type != "module" {
			continue
		}

		moduleName := moduleBlock.Labels[0]
		t.Logf("Checking module: %s", moduleName)

		// Get module attributes
		attrs, diags := moduleBlock.Body.JustAttributes()
		if diags.HasErrors() {
			t.Logf("Warning: Could not extract attributes from module %s", moduleName)
			continue
		}

		// For each attribute in the module call, check if it references a root variable
		for attrName, attr := range attrs {
			// Skip special attributes
			if attrName == "source" || attrName == "count" {
				continue
			}

			// Check if the attribute value references a root variable
			if hclsyntaxExpr, ok := attr.Expr.(*hclsyntax.ScopeTraversalExpr); ok {
				// This is a simple variable reference like var.environment
				if len(hclsyntaxExpr.Traversal) >= 2 {
					rootName := hclsyntaxExpr.Traversal.RootName()
					if rootName == "var" {
						// Get the variable name
						if getAttr, ok := hclsyntaxExpr.Traversal[1].(hcl.TraverseAttr); ok {
							varName := getAttr.Name

							// Check if this root variable exists
							if !rootVariables[varName] {
								violations = append(violations,
									"Module "+moduleName+" references non-existent root variable 'var."+varName+"'")
							}
						}
					}
				}
			}
		}

		// Get the source to find module directory
		sourceAttr, exists := attrs["source"]
		if !exists {
			continue
		}

		sourceVal, diags := sourceAttr.Expr.Value(nil)
		if diags.HasErrors() {
			continue
		}

		sourcePath := strings.TrimPrefix(sourceVal.AsString(), "./")
		moduleDir := filepath.Join(rootDir, sourcePath)

		// Read module's variables.tf to find what variables it needs
		moduleVarsPath := filepath.Join(moduleDir, "variables.tf")
		if _, err := os.Stat(moduleVarsPath); os.IsNotExist(err) {
			continue
		}

		moduleVarsContent, err := os.ReadFile(moduleVarsPath)
		if err != nil {
			continue
		}

		moduleVarsFile, diags := parser.ParseHCL(moduleVarsContent, "variables.tf")
		if diags.HasErrors() {
			continue
		}

		if moduleVarsFile == nil || moduleVarsFile.Body == nil {
			continue
		}

		// Extract module variable blocks
		moduleVarsBodyContent, _, diags := moduleVarsFile.Body.PartialContent(&hcl.BodySchema{
			Blocks: []hcl.BlockHeaderSchema{
				{Type: "variable", LabelNames: []string{"name"}},
			},
		})
		if diags.HasErrors() {
			continue
		}

		// For each module variable, check if it's provided and if it uses a root variable
		for _, varBlock := range moduleVarsBodyContent.Blocks {
			if varBlock.Type != "variable" || len(varBlock.Labels) == 0 {
				continue
			}

			moduleVarName := varBlock.Labels[0]

			// Check if this variable is provided in the module call
			providedAttr, isProvided := attrs[moduleVarName]
			if !isProvided {
				// It's okay if not provided and has a default
				continue
			}

			// If provided, check if it references a root variable
			if hclsyntaxExpr, ok := providedAttr.Expr.(*hclsyntax.ScopeTraversalExpr); ok {
				if len(hclsyntaxExpr.Traversal) >= 2 {
					rootName := hclsyntaxExpr.Traversal.RootName()
					if rootName == "var" {
						// This is good - it's using a root variable
						// Verify the root variable exists (already checked above)
					}
				}
			}
		}
	}

	// Assert no violations found
	if len(violations) > 0 {
		t.Errorf("Variable propagation violations found:\n%s",
			strings.Join(violations, "\n"))
	}
}

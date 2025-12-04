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

// TestModuleIndependence verifies Property 33:
// For any two independent module calls in the root module, neither module call
// SHALL have a depends_on referencing the other module.
//
// **Feature: terraform-modularization, Property 33: Module independence**
// **Validates: Requirements 9.5**
func TestModuleIndependence(t *testing.T) {
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

	// Extract module blocks
	bodyContent, _, diags := mainFile.Body.PartialContent(&hcl.BodySchema{
		Blocks: []hcl.BlockHeaderSchema{
			{Type: "module", LabelNames: []string{"name"}},
		},
	})
	assert.False(t, diags.HasErrors(), "Should extract module blocks")

	// Collect all module names
	moduleNames := make(map[string]bool)
	for _, moduleBlock := range bodyContent.Blocks {
		if moduleBlock.Type == "module" && len(moduleBlock.Labels) > 0 {
			moduleNames[moduleBlock.Labels[0]] = true
		}
	}

	t.Logf("Found %d modules", len(moduleNames))

	violations := []string{}

	// For each module call, check for depends_on
	for _, moduleBlock := range bodyContent.Blocks {
		if moduleBlock.Type != "module" {
			continue
		}

		moduleName := moduleBlock.Labels[0]

		// Get module attributes
		attrs, diags := moduleBlock.Body.JustAttributes()
		if diags.HasErrors() {
			continue
		}

		// Check for depends_on attribute
		dependsOnAttr, hasDependsOn := attrs["depends_on"]
		if !hasDependsOn {
			// No depends_on, which is good
			continue
		}

		// Parse the depends_on value to see what it references
		// depends_on is typically a list/tuple expression
		if tupleExpr, ok := dependsOnAttr.Expr.(*hclsyntax.TupleConsExpr); ok {
			for _, elem := range tupleExpr.Exprs {
				// Check if element is a module reference
				if scopeExpr, ok := elem.(*hclsyntax.ScopeTraversalExpr); ok {
					if len(scopeExpr.Traversal) >= 1 {
						rootName := scopeExpr.Traversal.RootName()
						if rootName == "module" {
							// This module depends on another module
							// Get the referenced module name
							if len(scopeExpr.Traversal) >= 2 {
								if getAttr, ok := scopeExpr.Traversal[1].(hcl.TraverseAttr); ok {
									referencedModule := getAttr.Name

									// Check if the referenced module exists
									if moduleNames[referencedModule] {
										violations = append(violations,
											"Module "+moduleName+" has depends_on referencing module "+referencedModule+
												" - independent modules should not have artificial dependencies")
									}
								}
							}
						}
					}
				}
			}
		}
	}

	// Assert no violations found
	if len(violations) > 0 {
		t.Errorf("Module independence violations found:\n%s",
			strings.Join(violations, "\n"))
	}
}

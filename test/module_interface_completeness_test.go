package test

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/hashicorp/hcl/v2"
	"github.com/hashicorp/hcl/v2/hclparse"
	"github.com/stretchr/testify/assert"
)

// TestModuleInterfaceCompleteness verifies Property 3:
// For any module call in the root module, all required variables for that module
// SHALL be provided in the module call block.
//
// **Feature: terraform-modularization, Property 3: Module interface completeness**
// **Validates: Requirements 1.4**
func TestModuleInterfaceCompleteness(t *testing.T) {
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

	violations := []string{}

	// For each module call
	for _, moduleBlock := range bodyContent.Blocks {
		if moduleBlock.Type != "module" {
			continue
		}

		moduleName := moduleBlock.Labels[0]
		t.Logf("Checking module: %s", moduleName)

		// Get the source attribute to find the module directory
		attrs, diags := moduleBlock.Body.JustAttributes()
		if diags.HasErrors() {
			t.Logf("Warning: Could not extract attributes from module %s", moduleName)
			continue
		}

		sourceAttr, exists := attrs["source"]
		if !exists {
			violations = append(violations, "Module "+moduleName+" is missing source attribute")
			continue
		}

		// Get source value
		sourceVal, diags := sourceAttr.Expr.Value(nil)
		if diags.HasErrors() {
			t.Logf("Warning: Could not evaluate source for module %s", moduleName)
			continue
		}

		sourcePath := sourceVal.AsString()
		// Remove ./ prefix if present
		sourcePath = strings.TrimPrefix(sourcePath, "./")

		// Construct full path to module
		moduleDir := filepath.Join(rootDir, sourcePath)

		// Read module's variables.tf to find required variables
		moduleVarsPath := filepath.Join(moduleDir, "variables.tf")
		if _, err := os.Stat(moduleVarsPath); os.IsNotExist(err) {
			t.Logf("Warning: Module %s has no variables.tf", moduleName)
			continue
		}

		varsContent, err := os.ReadFile(moduleVarsPath)
		if err != nil {
			t.Logf("Warning: Could not read variables.tf for module %s", moduleName)
			continue
		}

		varsFile, diags := parser.ParseHCL(varsContent, "variables.tf")
		if diags.HasErrors() {
			t.Logf("Warning: Could not parse variables.tf for module %s", moduleName)
			continue
		}

		if varsFile == nil || varsFile.Body == nil {
			continue
		}

		// Extract variable blocks
		varsBodyContent, _, diags := varsFile.Body.PartialContent(&hcl.BodySchema{
			Blocks: []hcl.BlockHeaderSchema{
				{Type: "variable", LabelNames: []string{"name"}},
			},
		})
		if diags.HasErrors() {
			t.Logf("Warning: Could not extract variables from module %s", moduleName)
			continue
		}

		// Check each variable to see if it's required (no default)
		for _, varBlock := range varsBodyContent.Blocks {
			if varBlock.Type != "variable" {
				continue
			}

			varName := varBlock.Labels[0]

			// Check if variable has a default value
			varAttrs, diags := varBlock.Body.JustAttributes()
			if diags.HasErrors() {
				continue
			}

			_, hasDefault := varAttrs["default"]

			// If no default, it's required
			if !hasDefault {
				// Check if this required variable is provided in the module call
				_, providedInCall := attrs[varName]
				if !providedInCall {
					violations = append(violations,
						"Module "+moduleName+" requires variable '"+varName+"' but it is not provided in the module call")
				}
			}
		}
	}

	// Assert no violations found
	if len(violations) > 0 {
		t.Errorf("Module interface completeness violations found:\n%s",
			strings.Join(violations, "\n"))
	}
}

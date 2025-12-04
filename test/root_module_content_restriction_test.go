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

// TestRootModuleContentRestriction verifies Property 14:
// For any resource in the root module, the resource SHALL be one of:
// module calls, provider configuration, backend configuration, or data sources.
// Service-specific resources SHALL NOT be in the root module.
//
// **Feature: terraform-modularization, Property 14: Root module content restriction**
// **Validates: Requirements 4.1**
func TestRootModuleContentRestriction(t *testing.T) {
	t.Parallel()

	rootDir := ".."

	// List of allowed resource types in root module
	allowedBlocks := map[string]bool{
		"module":    true,
		"provider":  true,
		"terraform": true, // For backend and required_providers
		"data":      true,
		"variable":  true,
		"output":    true,
		"locals":    true,
	}

	// Service-specific resource prefixes that should NOT be in root
	forbiddenResourcePrefixes := []string{
		"aws_cloudtrail",
		"aws_config",
		"aws_guardduty",
		"aws_detective",
		"aws_securityhub",
		"aws_s3_bucket",
		"aws_kms_key",
		"aws_iam_role",
		"aws_iam_policy",
		"aws_cloudwatch",
		"aws_sns_topic",
		"random_id",
	}

	// Get all .tf files in root directory (excluding .old files)
	files, err := filepath.Glob(filepath.Join(rootDir, "*.tf"))
	assert.NoError(t, err, "Should be able to list .tf files")

	parser := hclparse.NewParser()
	violations := []string{}

	for _, file := range files {
		// Skip .old files
		if strings.HasSuffix(file, ".old") {
			continue
		}

		filename := filepath.Base(file)

		// Read file content
		content, err := os.ReadFile(file)
		if err != nil {
			t.Logf("Warning: Could not read file %s: %v", filename, err)
			continue
		}

		// Parse HCL file
		parsedFile, diags := parser.ParseHCL(content, filename)
		if diags.HasErrors() {
			t.Logf("Warning: Could not parse file %s: %v", filename, diags)
			continue
		}

		if parsedFile == nil || parsedFile.Body == nil {
			continue
		}

		// Get the body schema
		bodyContent, _, diags := parsedFile.Body.PartialContent(&hcl.BodySchema{
			Blocks: []hcl.BlockHeaderSchema{
				{Type: "resource", LabelNames: []string{"type", "name"}},
				{Type: "module", LabelNames: []string{"name"}},
				{Type: "provider", LabelNames: []string{"name"}},
				{Type: "terraform"},
				{Type: "data", LabelNames: []string{"type", "name"}},
				{Type: "variable", LabelNames: []string{"name"}},
				{Type: "output", LabelNames: []string{"name"}},
				{Type: "locals"},
			},
		})

		if diags.HasErrors() {
			t.Logf("Warning: Could not extract content from %s: %v", filename, diags)
			continue
		}

		// Check each block
		for _, block := range bodyContent.Blocks {
			blockType := block.Type

			// Check if block type is allowed
			if !allowedBlocks[blockType] {
				violations = append(violations,
					"File "+filename+" contains disallowed block type '"+blockType+"'")
				continue
			}

			// If it's a resource block, check if it's a forbidden service resource
			if blockType == "resource" && len(block.Labels) >= 1 {
				resourceType := block.Labels[0]

				// Check if this is a forbidden service-specific resource
				for _, prefix := range forbiddenResourcePrefixes {
					if strings.HasPrefix(resourceType, prefix) {
						violations = append(violations,
							"File "+filename+" contains service-specific resource '"+resourceType+"' which should be in a module")
						break
					}
				}
			}
		}
	}

	// Assert no violations found
	if len(violations) > 0 {
		t.Errorf("Root module content restriction violations found:\n%s",
			strings.Join(violations, "\n"))
	}
}

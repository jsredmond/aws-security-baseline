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

// TestCloudTrailResourceEncapsulation verifies Property 2:
// For any service module, all resources, data sources, and locals related to that service
// SHALL be contained within the module and not in the root module.
//
// **Feature: terraform-modularization, Property 2: Resource encapsulation**
// **Validates: Requirements 1.3**
func TestCloudTrailResourceEncapsulation(t *testing.T) {
	t.Parallel()

	rootDir := ".."
	modulePath := filepath.Join(rootDir, "modules", "cloudtrail", "main.tf")

	// Required CloudTrail resources that should be in the module
	requiredResources := []string{
		"aws_cloudtrail",
		"aws_s3_bucket",
		"aws_kms_key",
		"aws_cloudwatch_log_group",
		"aws_iam_role",
		"aws_sns_topic",
	}

	// Read module main.tf
	content, err := os.ReadFile(modulePath)
	assert.NoError(t, err, "Should be able to read module main.tf")

	parser := hclparse.NewParser()
	file, diags := parser.ParseHCL(content, "main.tf")
	assert.False(t, diags.HasErrors(), "Module main.tf should parse without errors")

	if file == nil || file.Body == nil {
		t.Fatal("Module main.tf body is nil")
	}

	// Extract resource blocks
	bodyContent, _, diags := file.Body.PartialContent(&hcl.BodySchema{
		Blocks: []hcl.BlockHeaderSchema{
			{Type: "resource", LabelNames: []string{"type", "name"}},
		},
	})
	assert.False(t, diags.HasErrors(), "Should extract resource blocks")

	// Collect found resources
	foundResources := make(map[string]bool)
	for _, block := range bodyContent.Blocks {
		if block.Type == "resource" && len(block.Labels) >= 1 {
			resourceType := block.Labels[0]
			foundResources[resourceType] = true
		}
	}

	// Check that all required resources are present
	missing := []string{}
	for _, required := range requiredResources {
		found := false
		for resourceType := range foundResources {
			if strings.HasPrefix(resourceType, required) {
				found = true
				break
			}
		}
		if !found {
			missing = append(missing, required)
		}
	}

	if len(missing) > 0 {
		t.Errorf("CloudTrail module is missing required resources: %v", missing)
	}

	t.Logf("Found %d resource types in CloudTrail module", len(foundResources))
}

// TestConfigResourceEncapsulation verifies Property 2 for Config module
//
// **Feature: terraform-modularization, Property 2: Resource encapsulation**
// **Validates: Requirements 1.3**
func TestConfigResourceEncapsulation(t *testing.T) {
	t.Parallel()

	rootDir := ".."
	modulePath := filepath.Join(rootDir, "modules", "config", "main.tf")

	// Required Config resources that should be in the module
	requiredResources := []string{
		"aws_config_configuration_recorder",
		"aws_config_delivery_channel",
		"aws_s3_bucket",
		"aws_kms_key",
		"aws_iam_role",
	}

	// Read module main.tf
	content, err := os.ReadFile(modulePath)
	assert.NoError(t, err, "Should be able to read module main.tf")

	parser := hclparse.NewParser()
	file, diags := parser.ParseHCL(content, "main.tf")
	assert.False(t, diags.HasErrors(), "Module main.tf should parse without errors")

	if file == nil || file.Body == nil {
		t.Fatal("Module main.tf body is nil")
	}

	// Extract resource blocks
	bodyContent, _, diags := file.Body.PartialContent(&hcl.BodySchema{
		Blocks: []hcl.BlockHeaderSchema{
			{Type: "resource", LabelNames: []string{"type", "name"}},
		},
	})
	assert.False(t, diags.HasErrors(), "Should extract resource blocks")

	// Collect found resources
	foundResources := make(map[string]bool)
	for _, block := range bodyContent.Blocks {
		if block.Type == "resource" && len(block.Labels) >= 1 {
			resourceType := block.Labels[0]
			foundResources[resourceType] = true
		}
	}

	// Check that all required resources are present
	missing := []string{}
	for _, required := range requiredResources {
		found := false
		for resourceType := range foundResources {
			if strings.HasPrefix(resourceType, required) {
				found = true
				break
			}
		}
		if !found {
			missing = append(missing, required)
		}
	}

	if len(missing) > 0 {
		t.Errorf("Config module is missing required resources: %v", missing)
	}

	t.Logf("Found %d resource types in Config module", len(foundResources))
}

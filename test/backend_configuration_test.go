package test

import (
	"os"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

// Feature: terraform-modularization, Property 18: Backend S3 configuration
// Validates: Requirements 5.2
// Property: For any backend configuration, the configuration SHALL specify S3 as the backend type
// and SHALL include encrypt = true.
func TestBackendS3Configuration(t *testing.T) {
	t.Parallel()

	backendFilePath := "../backend.tf"

	// Check that backend.tf exists
	t.Run("Backend_file_exists", func(t *testing.T) {
		_, err := os.Stat(backendFilePath)
		assert.NoError(t, err, "backend.tf file should exist in root module")
	})

	// Read backend.tf content
	content, err := os.ReadFile(backendFilePath)
	if err != nil {
		t.Fatalf("Failed to read backend.tf: %v", err)
	}
	contentStr := string(content)

	// Check that backend type is "s3"
	t.Run("Backend_type_is_s3", func(t *testing.T) {
		assert.Contains(t, contentStr, `backend "s3"`, "Backend configuration should specify S3 as the backend type")
	})

	// Check that encryption is enabled
	t.Run("Encryption_enabled", func(t *testing.T) {
		assert.Contains(t, contentStr, "encrypt = true", "Backend configuration should have encrypt = true")
	})
}

// Feature: terraform-modularization, Property 19: Backend DynamoDB configuration
// Validates: Requirements 5.3
// Property: For any backend configuration, the configuration SHALL specify a dynamodb_table for state locking.
func TestBackendDynamoDBConfiguration(t *testing.T) {
	t.Parallel()

	backendFilePath := "../backend.tf"

	// Read backend.tf content
	content, err := os.ReadFile(backendFilePath)
	if err != nil {
		t.Fatalf("Failed to read backend.tf: %v", err)
	}
	contentStr := string(content)

	// Check that dynamodb_table is mentioned (even if commented for partial config)
	t.Run("DynamoDB_table_referenced", func(t *testing.T) {
		assert.Contains(t, contentStr, "dynamodb_table", "Backend configuration should reference dynamodb_table for state locking")
	})
}

// Feature: terraform-modularization, Property 21: Backend variable usage
// Validates: Requirements 5.5
// Property: For any backend configuration, bucket names and table names SHALL use variables
// or partial configuration, not hardcoded values.
func TestBackendVariableUsage(t *testing.T) {
	t.Parallel()

	backendFilePath := "../backend.tf"

	// Read backend.tf content
	content, err := os.ReadFile(backendFilePath)
	if err != nil {
		t.Fatalf("Failed to read backend.tf: %v", err)
	}
	contentStr := string(content)

	// Check that there are no hardcoded bucket names (pattern: bucket = "some-bucket-name")
	t.Run("No_hardcoded_bucket_name", func(t *testing.T) {
		// Look for uncommented lines with bucket = "literal-string"
		lines := strings.Split(contentStr, "\n")
		for _, line := range lines {
			trimmed := strings.TrimSpace(line)
			// Skip comments
			if strings.HasPrefix(trimmed, "#") {
				continue
			}
			// Check if line contains bucket = "something"
			if strings.Contains(trimmed, `bucket = "`) && !strings.HasPrefix(trimmed, "#") {
				t.Errorf("Found hardcoded bucket name in backend configuration: %s", trimmed)
			}
		}
	})

	// Check that there are no hardcoded DynamoDB table names
	t.Run("No_hardcoded_dynamodb_table", func(t *testing.T) {
		lines := strings.Split(contentStr, "\n")
		for _, line := range lines {
			trimmed := strings.TrimSpace(line)
			// Skip comments
			if strings.HasPrefix(trimmed, "#") {
				continue
			}
			// Check if line contains dynamodb_table = "something"
			if strings.Contains(trimmed, `dynamodb_table = "`) && !strings.HasPrefix(trimmed, "#") {
				t.Errorf("Found hardcoded DynamoDB table name in backend configuration: %s", trimmed)
			}
		}
	})

	// Check that documentation mentions partial configuration or variables
	t.Run("Partial_configuration_documented", func(t *testing.T) {
		hasPartialConfigDoc := strings.Contains(contentStr, "partial configuration") ||
			strings.Contains(contentStr, "backend-config") ||
			strings.Contains(contentStr, "-backend-config")
		assert.True(t, hasPartialConfigDoc, "Backend configuration should document the use of partial configuration or backend-config flags")
	})

	// Check that example backend config file exists
	t.Run("Example_backend_config_exists", func(t *testing.T) {
		examplePath := "../backend-config.hcl.example"
		_, err := os.Stat(examplePath)
		assert.NoError(t, err, "backend-config.hcl.example file should exist to guide users")
	})
}

// Additional test: Verify backend-config.hcl.example structure
func TestBackendConfigExample(t *testing.T) {
	t.Parallel()

	examplePath := "../backend-config.hcl.example"

	// Check that example file exists
	_, err := os.Stat(examplePath)
	if err != nil {
		t.Skip("backend-config.hcl.example does not exist, skipping example validation")
	}

	// Read example file content
	content, err := os.ReadFile(examplePath)
	if err != nil {
		t.Fatalf("Failed to read backend-config.hcl.example: %v", err)
	}
	contentStr := string(content)

	// Check that example includes required fields
	t.Run("Example_includes_bucket", func(t *testing.T) {
		assert.Contains(t, contentStr, "bucket", "Example backend config should include bucket parameter")
	})

	t.Run("Example_includes_key", func(t *testing.T) {
		assert.Contains(t, contentStr, "key", "Example backend config should include key parameter")
	})

	t.Run("Example_includes_region", func(t *testing.T) {
		assert.Contains(t, contentStr, "region", "Example backend config should include region parameter")
	})

	t.Run("Example_includes_dynamodb_table", func(t *testing.T) {
		assert.Contains(t, contentStr, "dynamodb_table", "Example backend config should include dynamodb_table parameter")
	})
}

// Test that .gitignore excludes backend-config.hcl
func TestBackendConfigGitignore(t *testing.T) {
	t.Parallel()

	gitignorePath := "../.gitignore"

	// Read .gitignore content
	content, err := os.ReadFile(gitignorePath)
	if err != nil {
		t.Fatalf("Failed to read .gitignore: %v", err)
	}
	contentStr := string(content)

	t.Run("Backend_config_in_gitignore", func(t *testing.T) {
		assert.Contains(t, contentStr, "backend-config.hcl", ".gitignore should exclude backend-config.hcl to prevent committing sensitive information")
	})
}

// Test that backend.tf is properly formatted
func TestBackendFormatting(t *testing.T) {
	t.Parallel()

	backendFilePath := "../backend.tf"

	// Check that file exists
	_, err := os.Stat(backendFilePath)
	if err != nil {
		t.Skip("backend.tf does not exist, skipping formatting test")
	}

	// Check file is readable
	t.Run("Backend_file_readable", func(t *testing.T) {
		content, err := os.ReadFile(backendFilePath)
		assert.NoError(t, err, "backend.tf should be readable")
		assert.NotEmpty(t, content, "backend.tf should not be empty")
	})
}

// Integration test: Verify backend configuration structure
func TestBackendConfigurationStructure(t *testing.T) {
	t.Parallel()

	backendFilePath := "../backend.tf"

	content, err := os.ReadFile(backendFilePath)
	if err != nil {
		t.Fatalf("Failed to read backend.tf: %v", err)
	}
	contentStr := string(content)

	// Check that terraform block exists
	t.Run("Terraform_block_exists", func(t *testing.T) {
		assert.Contains(t, contentStr, "terraform {", "backend.tf should contain a terraform block")
	})

	// Check that backend block is inside terraform block
	t.Run("Backend_inside_terraform_block", func(t *testing.T) {
		// Simple check: backend "s3" should appear after terraform {
		terraformIndex := strings.Index(contentStr, "terraform {")
		backendIndex := strings.Index(contentStr, `backend "s3"`)

		if terraformIndex == -1 {
			t.Error("terraform block not found")
		}
		if backendIndex == -1 {
			t.Error("backend block not found")
		}
		if terraformIndex != -1 && backendIndex != -1 {
			assert.Greater(t, backendIndex, terraformIndex, "backend block should be inside terraform block")
		}
	})

	// Check that documentation is present
	t.Run("Documentation_present", func(t *testing.T) {
		hasComments := strings.Contains(contentStr, "#") || strings.Contains(contentStr, "//")
		assert.True(t, hasComments, "backend.tf should include documentation comments")
	})
}

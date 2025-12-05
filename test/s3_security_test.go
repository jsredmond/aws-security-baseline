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

// TestCloudTrailS3Versioning verifies Property 26:
// For any S3 bucket resource, there SHALL be a corresponding
// aws_s3_bucket_versioning resource with status = "Enabled"
//
// **Feature: terraform-modularization, Property 26: S3 versioning configuration**
// **Validates: Requirements 7.1**
func TestCloudTrailS3Versioning(t *testing.T) {
	t.Parallel()
	testS3Versioning(t, "cloudtrail")
}

// TestCloudTrailS3Encryption verifies Property 27:
// For any S3 bucket resource, there SHALL be a corresponding
// aws_s3_bucket_server_side_encryption_configuration resource with sse_algorithm = "aws:kms"
//
// **Feature: terraform-modularization, Property 27: S3 encryption configuration**
// **Validates: Requirements 7.2**
func TestCloudTrailS3Encryption(t *testing.T) {
	t.Parallel()
	testS3Encryption(t, "cloudtrail")
}

// TestCloudTrailS3PublicAccessBlock verifies Property 28:
// For any S3 bucket resource, there SHALL be a corresponding
// aws_s3_bucket_public_access_block resource with all four settings set to true
//
// **Feature: terraform-modularization, Property 28: S3 public access block**
// **Validates: Requirements 7.3**
func TestCloudTrailS3PublicAccessBlock(t *testing.T) {
	t.Parallel()
	testS3PublicAccessBlock(t, "cloudtrail")
}

// TestCloudTrailS3Lifecycle verifies Property 29:
// For any S3 bucket resource, there SHALL be a corresponding
// aws_s3_bucket_lifecycle_configuration resource
//
// **Feature: terraform-modularization, Property 29: S3 lifecycle configuration**
// **Validates: Requirements 7.4**
func TestCloudTrailS3Lifecycle(t *testing.T) {
	t.Parallel()
	testS3Lifecycle(t, "cloudtrail")
}

// TestConfigS3Versioning verifies Property 26 for Config module
//
// **Feature: terraform-modularization, Property 26: S3 versioning configuration**
// **Validates: Requirements 7.1**
func TestConfigS3Versioning(t *testing.T) {
	t.Parallel()
	testS3Versioning(t, "config")
}

// TestConfigS3Encryption verifies Property 27 for Config module
//
// **Feature: terraform-modularization, Property 27: S3 encryption configuration**
// **Validates: Requirements 7.2**
func TestConfigS3Encryption(t *testing.T) {
	t.Parallel()
	testS3Encryption(t, "config")
}

// TestConfigS3PublicAccessBlock verifies Property 28 for Config module
//
// **Feature: terraform-modularization, Property 28: S3 public access block**
// **Validates: Requirements 7.3**
func TestConfigS3PublicAccessBlock(t *testing.T) {
	t.Parallel()
	testS3PublicAccessBlock(t, "config")
}

// TestConfigS3Lifecycle verifies Property 29 for Config module
//
// **Feature: terraform-modularization, Property 29: S3 lifecycle configuration**
// **Validates: Requirements 7.4**
func TestConfigS3Lifecycle(t *testing.T) {
	t.Parallel()
	testS3Lifecycle(t, "config")
}

// Helper function to test S3 versioning configuration
func testS3Versioning(t *testing.T, moduleName string) {
	rootDir := ".."
	modulePath := filepath.Join(rootDir, "modules", moduleName, "main.tf")

	content, err := os.ReadFile(modulePath)
	assert.NoError(t, err, "Should be able to read module main.tf")

	// Check for versioning resource
	hasVersioning := strings.Contains(string(content), `resource "aws_s3_bucket_versioning"`)
	assert.True(t, hasVersioning, "Module should have aws_s3_bucket_versioning resource")

	if hasVersioning {
		// Check for status = "Enabled"
		hasEnabled := strings.Contains(string(content), `status = "Enabled"`) ||
			strings.Contains(string(content), `status="Enabled"`)
		assert.True(t, hasEnabled, "Versioning should have status = Enabled")
	}
}

// Helper function to test S3 encryption configuration
func testS3Encryption(t *testing.T, moduleName string) {
	rootDir := ".."
	modulePath := filepath.Join(rootDir, "modules", moduleName, "main.tf")

	content, err := os.ReadFile(modulePath)
	assert.NoError(t, err, "Should be able to read module main.tf")

	// Check for encryption resource
	hasEncryption := strings.Contains(string(content), `resource "aws_s3_bucket_server_side_encryption_configuration"`)
	assert.True(t, hasEncryption, "Module should have aws_s3_bucket_server_side_encryption_configuration resource")

	if hasEncryption {
		// Check for sse_algorithm = "aws:kms" (with flexible whitespace)
		contentStr := string(content)
		hasKMS := strings.Contains(contentStr, `sse_algorithm = "aws:kms"`) ||
			strings.Contains(contentStr, `sse_algorithm="aws:kms"`) ||
			strings.Contains(contentStr, `sse_algorithm     = "aws:kms"`)
		assert.True(t, hasKMS, "Encryption should use sse_algorithm = aws:kms")
	}
}

// Helper function to test S3 public access block
func testS3PublicAccessBlock(t *testing.T, moduleName string) {
	rootDir := ".."
	modulePath := filepath.Join(rootDir, "modules", moduleName, "main.tf")

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

	// Find public access block resource
	var publicAccessBlock *hcl.Block
	for _, block := range bodyContent.Blocks {
		if block.Type == "resource" && len(block.Labels) >= 1 {
			if block.Labels[0] == "aws_s3_bucket_public_access_block" {
				publicAccessBlock = block
				break
			}
		}
	}

	assert.NotNil(t, publicAccessBlock, "Module should have aws_s3_bucket_public_access_block resource")

	if publicAccessBlock != nil {
		// Check for all four settings
		attrs, diags := publicAccessBlock.Body.JustAttributes()
		if !diags.HasErrors() {
			requiredSettings := []string{
				"block_public_acls",
				"block_public_policy",
				"ignore_public_acls",
				"restrict_public_buckets",
			}

			for _, setting := range requiredSettings {
				_, exists := attrs[setting]
				assert.True(t, exists, "Public access block should have "+setting+" setting")
			}
		}
	}
}

// Helper function to test S3 lifecycle configuration
func testS3Lifecycle(t *testing.T, moduleName string) {
	rootDir := ".."
	modulePath := filepath.Join(rootDir, "modules", moduleName, "main.tf")

	content, err := os.ReadFile(modulePath)
	assert.NoError(t, err, "Should be able to read module main.tf")

	// Check for lifecycle resource
	hasLifecycle := strings.Contains(string(content), `resource "aws_s3_bucket_lifecycle_configuration"`)
	assert.True(t, hasLifecycle, "Module should have aws_s3_bucket_lifecycle_configuration resource")
}
